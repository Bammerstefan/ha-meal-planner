"""Mein Speiseplan: local plans, recipes and shopping list."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from datetime import date, timedelta
import re
from homeassistant.util import dt as dt_util
from homeassistant.helpers.event import async_track_time_change
import uuid
from collections import deque
from time import monotonic
import voluptuous as vol
from homeassistant.components import panel_custom, frontend, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import callback
from homeassistant.helpers.storage import Store
from .const import DOMAIN, PANEL_PATH
from .licenses import MODULES, verify_license
from .import_helpers import parse_rtk, parse_webpage, public_hostname, public_dns_addresses
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import asyncio
import socket

STORAGE_VERSION = 1
UI_VERSION = "1.0.5"

# Mengen für Warnungen auf eine gemeinsame Basiseinheit umrechnen.
def _quantity(raw):
    m = re.match(r"^\s*(\d+(?:[.,]\d+)?)\s*(kg|dag|g|ml|cl|l|stk|stück|stueck|el|tl)?\s*$", str(raw or "").lower())
    if not m:
        return None
    val = float(m.group(1).replace(",", "."))
    unit = m.group(2) or ""
    factors = {"kg": ("g", 1000), "dag": ("g", 10), "g": ("g", 1), "l": ("ml", 1000), "cl": ("ml", 10), "ml": ("ml", 1), "stück": ("stk", 1), "stueck": ("stk", 1), "stk": ("stk", 1), "el": ("el", 1), "tl": ("tl", 1), "": ("count", 1)}
    base, factor = factors[unit]
    return base, val * factor


def _alerts(data, today):
    pantry = data.get("pantry", [])
    settings = data.get("reminder_settings", {})
    expiring, low = [], []
    threshold = max(0, min(30, int(settings.get("expiry_days", 3) or 3)))
    for item in pantry:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "Zutat"))[:100]
        expires = item.get("expires")
        if settings.get("expiry_enabled") and expires:
            try:
                remaining = (date.fromisoformat(expires) - today).days
                if 0 <= remaining <= threshold:
                    expiring.append(f"{name} (MHD in {remaining} Tag(en))")
                elif remaining < 0:
                    expiring.append(f"{name} (MHD überschritten – bitte prüfen)")
            except (ValueError, TypeError):
                pass
        if settings.get("stock_enabled") and item.get("min_quantity"):
            available, required = _quantity(item.get("quantity")), _quantity(item.get("min_quantity"))
            if available and required and available[0] == required[0] and available[1] < required[1]:
                low.append(f"{name}: {item.get('quantity')} vorhanden, Minimum {item.get('min_quantity')}")
    return expiring, low


def empty_data():
    return {"recipes": [], "plans": {}, "shopping": {}, "persons": 4, "family": {"members": [], "wishes": []}}

async def async_setup_entry(hass, entry):
    store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")
    data = await store.async_load() or empty_data()
    data.setdefault("recipes", [])
    data.setdefault("plans", {})
    data.setdefault("shopping", {})
    data.setdefault("persons", 4)
    data.setdefault("family", {"members": [], "wishes": []})
    data["family"].setdefault("access_mode", "shared")
    data.setdefault("pantry", [])
    data.setdefault("week_templates", [])
    data.setdefault("reminder_settings", {"shopping_enabled": False, "shopping_weekday": 4, "stock_enabled": False, "expiry_enabled": False, "expiry_days": 3, "hour": 8})
    license_store = Store(hass, 1, f"{DOMAIN}.licenses.{entry.entry_id}")
    license_data = await license_store.async_load() or {}
    if not license_data.get("installation_id"):
        license_data["installation_id"] = uuid.uuid4().hex
        license_data["tokens"] = []
        await license_store.async_save(license_data)
    hass.data[DOMAIN] = {"entry": entry, "store": store, "data": data, "license_store": license_store, "license_data": license_data}

    # Ein einzelner lokaler Zeit-Callback statt dauerhaft laufender Polling-Schleife.
    # Home Assistant persistent notifications, optional und nur bei aktivierten Einstellungen.
    last_notifications = set()

    async def _daily_reminders(now):
        current = hass.data.get(DOMAIN, {}).get("data", {})
        prefs = current.get("reminder_settings", {})
        if not prefs or not any(prefs.get(k) for k in ("shopping_enabled", "stock_enabled", "expiry_enabled")):
            return
        local_now = dt_util.as_local(now)
        if local_now.hour != int(prefs.get("hour", 8)):
            return
        today = local_now.date()
        messages = []
        if prefs.get("shopping_enabled") and today.weekday() == int(prefs.get("shopping_weekday", 4)):
            messages.append("🛒 Einkaufserinnerung: Wochen-Einkaufsliste kontrollieren.")
        expiry, low = _alerts(current, today)
        if expiry:
            messages.append("📅 Bald ablaufende Vorräte:\n" + "\n".join("• " + x for x in expiry[:30]))
        if low:
            messages.append("🏠 Mindestbestand unterschritten:\n" + "\n".join("• " + x for x in low[:30]))
        if not messages or today.isoformat() in last_notifications:
            return
        last_notifications.add(today.isoformat())
        await hass.services.async_call("persistent_notification", "create", {
            "title": "Mein Speiseplan – Erinnerungen",
            "message": "\n\n".join(messages),
            "notification_id": f"meal_planner_reminders_{entry.entry_id}",
        }, blocking=True)

    unsubscribe = async_track_time_change(hass, _daily_reminders, minute=0, second=0)
    hass.data[DOMAIN]["reminder_unsubscribe"] = unsubscribe

    @websocket_api.websocket_command({vol.Required('type'): f'{DOMAIN}/import_preview', vol.Required('source'): vol.In(['rtk','url']), vol.Required('value'): str})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def ws_import_preview(hass, connection, msg):
        active = set()
        lic = hass.data[DOMAIN]['license_data']
        for token in lic.get('tokens', []):
            try: active.update(verify_license(token,lic['installation_id'])['modules'])
            except ValueError: continue
        if 'recipes_pro' not in active:
            connection.send_error(msg['id'], 'license_required', 'Rezeptbuch PRO benötigt eine gültige Lizenz.')
            return
        try:
            value=msg['value']
            if msg['source']=='rtk':
                if len(value)>7_000_000:raise ValueError('Die Datei ist zu groß.')
                recipes=await hass.async_add_executor_job(parse_rtk,value)
            else:
                if len(value)>2000:raise ValueError('URL zu lang.')
                host=public_hostname(value)
                # Validate DNS before requesting; Home Assistant's HTTP session supplies
                # TLS verification and its own redirect protections. No redirects allowed.
                records=await asyncio.get_running_loop().getaddrinfo(host,443,type=socket.SOCK_STREAM)
                public_dns_addresses([r[4][0] for r in records])
                session=async_get_clientsession(hass)
                import aiohttp
                async with session.get(value,allow_redirects=False,timeout=aiohttp.ClientTimeout(total=12),headers={'Accept':'text/html,application/xhtml+xml'}) as response:
                    if response.status in (301,302,303,307,308):raise ValueError('Weiterleitungen sind aus Sicherheitsgründen nicht unterstützt.')
                    if response.status!=200:raise ValueError(f'Webseite meldet HTTP {response.status}.')
                    if not any(x in response.headers.get('Content-Type','').lower() for x in ('text/html','application/xhtml+xml')):raise ValueError('Keine HTML-Webseite.')
                    if response.content_length and response.content_length>1_000_000:raise ValueError('Webseite zu groß.')
                    raw=await response.content.read(1_000_001)
                    if len(raw)>1_000_000:raise ValueError('Webseite zu groß.')
                    html=raw.decode(response.charset or 'utf-8',errors='replace')
                recipes=parse_webpage(html,value)
            if msg['source']=='url' and recipes and recipes[0].get('image_url'):
                image_url=recipes[0]['image_url']
                try:
                    # Resolve and pin a globally routable address to prevent DNS rebinding.
                    from urllib.parse import urlsplit
                    from aiohttp import ClientSession, TCPConnector, ClientTimeout
                    from aiohttp.abc import AbstractResolver
                    image_host=public_hostname(image_url)
                    ip_records=await asyncio.get_running_loop().getaddrinfo(image_host,443,type=socket.SOCK_STREAM)
                    image_addresses=list(dict.fromkeys(r[4][0] for r in ip_records))
                    public_dns_addresses(image_addresses)
                    class _PinnedResolver(AbstractResolver):
                        async def resolve(self, host, port=0, family=socket.AF_INET):
                            return [{'hostname':host,'host':ip,'port':port,'family':socket.AF_INET6 if ':' in ip else socket.AF_INET,'proto':0,'flags':0} for ip in image_addresses]
                        async def close(self): pass
                    connector=TCPConnector(resolver=_PinnedResolver(),use_dns_cache=False,limit=1)
                    async with ClientSession(connector=connector,trust_env=False,timeout=ClientTimeout(total=12)) as image_session:
                        async with image_session.get(image_url,allow_redirects=False,headers={'Accept':'image/jpeg,image/png,image/webp'}) as image_response:
                            kind=image_response.headers.get('Content-Type','').split(';')[0].strip().lower()
                            if image_response.status==200 and kind in ('image/jpeg','image/png','image/webp') and (not image_response.content_length or image_response.content_length<=1_500_000):
                                image_bytes=await image_response.content.read(1_500_001)
                                if len(image_bytes)<=1_500_000:
                                    import base64
                                    # Verify basic file signature rather than trusting headers alone.
                                    valid=(kind=='image/jpeg' and image_bytes.startswith(b'\xff\xd8\xff')) or (kind=='image/png' and image_bytes.startswith(b'\x89PNG\r\n\x1a\n')) or (kind=='image/webp' and image_bytes[:4]==b'RIFF' and image_bytes[8:12]==b'WEBP')
                                    if valid:
                                        recipes[0]['photo_data']='data:'+kind+';base64,'+base64.b64encode(image_bytes).decode('ascii')
                                        recipes[0]['photo_mode']='custom'
                except Exception:
                    # Some sites disallow downloading images. Recipe text remains importable.
                    pass
            connection.send_result(msg['id'],{'recipes':recipes})
        except (ValueError,TimeoutError,OSError,UnicodeError,ImportError,KeyError) as exc:
            connection.send_error(msg['id'],'import_failed',str(exc)[:400])
        except Exception:
            connection.send_error(msg['id'],'import_failed','Import konnte nicht verarbeitet werden.')

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/version"})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def ws_version(hass, connection, msg):
        connection.send_result(msg["id"], {"backend_version": UI_VERSION})

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/get"})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def ws_get(hass, connection, msg):
        connection.send_result(msg["id"], deepcopy(hass.data[DOMAIN]["data"]))

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/save", vol.Required("data"): dict})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def ws_save(hass, connection, msg):
        incoming = msg["data"]
        if not isinstance(incoming.get("recipes"), list) or not isinstance(incoming.get("plans"), dict) or not isinstance(incoming.get("shopping"), dict):
            connection.send_error(msg["id"], "invalid_data", "Invalid meal plan data")
            return
        if len(str(incoming)) > 1_000_000:
            connection.send_error(msg["id"], "too_large", "Data exceeds allowed size")
            return
        # Validate family access controls on the server, never trust a browser-only restriction.
        family_in = incoming.get("family", {})
        if not isinstance(family_in, dict) or family_in.get("access_mode", "shared") not in ("shared", "mixed", "personal"):
            connection.send_error(msg["id"], "invalid_family", "Ungültige Familien-Zugriffsart")
            return
        members_in = family_in.get("members", [])
        if not isinstance(members_in, list) or len(members_in) > 100:
            connection.send_error(msg["id"], "invalid_family", "Ungültige Familienmitglieder")
            return
        mapped_ids = [str(m.get("ha_user_id", "")).strip() for m in members_in if isinstance(m, dict) and m.get("ha_user_id")]
        if len(mapped_ids) != len(set(mapped_ids)) or any(not isinstance(m, dict) for m in members_in):
            connection.send_error(msg["id"], "duplicate_mapping", "Jeder Home-Assistant-Benutzer darf nur einer Person zugeordnet sein")
            return
        valid_users = {u.id for u in await hass.auth.async_get_users() if u.is_active and not u.system_generated}
        if any(uid not in valid_users for uid in mapped_ids):
            connection.send_error(msg["id"], "invalid_user", "Unbekannter oder inaktiver Home-Assistant-Benutzer")
            return
        try:
            incoming["persons"] = max(1, min(50, int(incoming.get("persons", 4))))
        except (ValueError, TypeError, OverflowError):
            connection.send_error(msg["id"], "invalid_persons", "Invalid portion count")
            return
        # Store first, then publish to in-memory state; a storage failure must not
        # silently replace the active state with unsaved data.
        to_store = deepcopy(incoming)
        try:
            await store.async_save(to_store)
        except Exception:
            connection.send_error(msg["id"], "save_failed", "Saving failed; previous data remain active")
            return
        hass.data[DOMAIN]["data"] = to_store
        connection.send_result(msg["id"], {"saved": True})

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/export", vol.Required("items"): list, vol.Required("entity_id"): str})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def ws_export(hass, connection, msg):
        """Send new items to a to-do entity (including Bring!), avoiding open duplicates."""
        entity_id = msg["entity_id"]
        if not entity_id.startswith("todo.") or hass.states.get(entity_id) is None:
            connection.send_error(msg["id"], "invalid_entity", "Wähle eine vorhandene Einkaufs-/To-do-Liste")
            return
        raw_items = msg["items"]
        if len(raw_items) > 300 or any(not isinstance(x, str) or len(x) > 240 for x in raw_items):
            connection.send_error(msg["id"], "invalid_items", "Ungültige Artikel (maximal 300)")
            return
        items = [x.strip() for x in raw_items if x.strip()]
        try:
            response = await hass.services.async_call(
                "todo", "get_items", {"entity_id": entity_id, "status": "needs_action"},
                blocking=True, return_response=True,
            )
            existing_items = response.get(entity_id, {}).get("items", []) if isinstance(response, dict) else []
            existing = {str(x.get("summary", "")).strip().casefold() for x in existing_items if isinstance(x, dict)}
        except Exception:
            connection.send_error(msg["id"], "read_failed", "Bestehende Liste konnte nicht gelesen werden; es wurde nichts übertragen")
            return
        added = skipped = 0
        for item in items:
            normalized = item.casefold()
            if normalized in existing:
                skipped += 1
                continue
            try:
                await hass.services.async_call("todo", "add_item", {"entity_id": entity_id, "item": item}, blocking=True)
            except Exception:
                connection.send_error(msg["id"], "export_failed", f"Übertragung nach {added} Artikeln abgebrochen – bitte Zielliste prüfen")
                return
            added += 1
            existing.add(normalized)
        connection.send_result(msg["id"], {"added": added, "skipped": skipped, "target": entity_id})

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/modules"})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def ws_modules(hass, connection, msg):
        lic = hass.data[DOMAIN]["license_data"]
        active = set()
        for token in lic.get("tokens", []):
            try:
                active.update(verify_license(token, lic["installation_id"])["modules"])
            except ValueError:
                continue
        connection.send_result(msg["id"], {"installation_id": lic["installation_id"], "modules": [{"id": mid, "name": name, "active": mid in active} for mid, name in MODULES.items()]})

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/license_transfer_request"})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def ws_license_transfer_request(hass, connection, msg):
        """Provide non-secret data for a manually approved reissue.

        The current installation never signs or rebinds licenses locally.
        A new signed license must be issued by the vendor for the NEW ID.
        """
        lic = hass.data[DOMAIN]["license_data"]
        active, license_ids = set(), set()
        for token in lic.get("tokens", []):
            try:
                payload = verify_license(token, lic["installation_id"])
            except ValueError:
                continue
            active.update(payload["modules"])
            license_ids.add(payload["license_id"])
        connection.send_result(msg["id"], {
            "format": "mein-speiseplan-lizenzwechsel",
            "schema": 1,
            "installation_id": lic["installation_id"],
            "license_ids": sorted(license_ids),
            "modules": sorted(active),
            "instructions": "Bei Gerätewechsel die alte und neue Installationskennung an den Verkäufer senden. Die alten Schlüssel sind nicht für die neue Installation gültig.",
        })

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/activate", vol.Required("token"): str})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def ws_activate(hass, connection, msg):
        lic = hass.data[DOMAIN]["license_data"]
        token = msg["token"].strip()
        if len(token) > 4000:
            connection.send_error(msg["id"], "invalid_license", "License too long")
            return
        try:
            info = verify_license(token, lic["installation_id"])
        except ValueError:
            connection.send_error(msg["id"], "invalid_license", "Ungültige Lizenz oder andere Installation")
            return
        if token not in lic["tokens"]:
            lic["tokens"].append(token)
            await license_store.async_save(lic)
        connection.send_result(msg["id"], {"active": info["modules"]})

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/shopping_pro", vol.Required("items"): list})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def ws_shopping_pro(hass, connection, msg):
        lic = hass.data[DOMAIN]["license_data"]
        active = set()
        for token in lic.get("tokens", []):
            try:
                active.update(verify_license(token, lic["installation_id"])["modules"])
            except ValueError:
                continue
        if "shopping_pro" not in active:
            connection.send_error(msg["id"], "license_required", "Einkaufsliste PRO benötigt eine gültige Dauerlizenz")
            return
        items = msg["items"]
        if len(items) > 300 or any(not isinstance(x, str) or len(x) > 240 for x in items):
            connection.send_error(msg["id"], "invalid_items", "Ungültige Einkaufsliste")
            return
        terms = {
            "Obst & Gemüse": ("apfel", "äpfel", "banane", "salat", "tomate", "gurke", "zwiebel", "kartoffel", "karotte", "paprika", "knoblauch", "zitrone", "gemüse", "obst"),
            "Fleisch & Fisch": ("schwein", "rind", "huhn", "hendl", "fleisch", "faschiert", "fisch", "lachs", "wurst", "speck"),
            "Milchprodukte & Eier": ("milch", "butter", "käse", "joghurt", "topfen", "obers", "sahne", "eier", "ei "),
            "Brot & Gebäck": ("brot", "semmel", "toast", "gebäck", "weckerl"),
            "Beilagen": ("knödel", "knöddel", "spätzle", "püree"),
            "Getränke": ("wasser", "saft", "limonade", "cola", "kaffee", "tee"),
            "Haushalt": ("spülmittel", "waschmittel", "toilettenpapier", "seife"),
            "Vorrat & Gewürze": ("nudel", "reis", "mehl", "zucker", "salz", "pfeffer", "öl", "essig", "linsen", "bohnen", "gewürz"),
        }
        grouped = {category: [] for category in terms}
        grouped["Sonstiges"] = []
        for item in items:
            text = item.casefold()
            category = next((group for group, words in terms.items() if any(word in text for word in words)), "Sonstiges")
            grouped[category].append(item)
        connection.send_result(msg["id"], {"groups": {k: v for k, v in grouped.items() if v}})

    # Per-user rate limit; a logged-in user cannot flood the family's wishes.
    family_submission_times = {}

    def family_request_allowed(connection):
        user = getattr(connection, "user", None)
        if user is None or not getattr(user, "is_active", True):
            return False
        uid = str(user.id)
        now = monotonic()
        recent = family_submission_times.setdefault(uid, deque())
        while recent and now - recent[0] > 60:
            recent.popleft()
        if len(recent) >= 10:
            return False
        recent.append(now)
        return True

    def family_license_active():
        lic = hass.data[DOMAIN]["license_data"]
        for token in lic.get("tokens", []):
            try:
                if "family_pro" in verify_license(token, lic["installation_id"])["modules"]:
                    return True
            except ValueError:
                pass
        return False

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/family_users"})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def ws_family_users(hass, connection, msg):
        users = await hass.auth.async_get_users()
        connection.send_result(msg["id"], {"users": [
            {"id": u.id, "name": u.name or u.id} for u in users
            if u.is_active and not u.system_generated
        ]})

    def family_access(connection, current):
        family = current.get("family") or {}
        user = getattr(connection, "user", None)
        if user is None or not getattr(user, "is_active", False):
            return set(), "shared", False
        members = family.get("members", [])
        mode = family.get("access_mode", "shared")
        if mode not in ("shared", "mixed", "personal"):
            mode = "shared"
        admin = bool(getattr(user, "is_admin", False))
        assigned = [m for m in members if m.get("ha_user_id") == user.id]
        if admin:
            return {str(m.get("id")) for m in members}, mode, True
        if mode == "shared":
            return {str(m.get("id")) for m in members}, mode, False
        if assigned:
            return {str(m.get("id")) for m in assigned}, mode, False
        if mode == "mixed":
            return {str(m.get("id")) for m in members if not m.get("ha_user_id")}, mode, False
        return set(), mode, False

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/family_mobile_get"})
    @websocket_api.async_response
    async def ws_family_mobile_get(hass, connection, msg):
        if not getattr(connection, "user", None):
            connection.send_error(msg["id"], "unauthorized", "Anmeldung erforderlich")
            return
        if not family_license_active():
            connection.send_error(msg["id"], "license_required", "Familienmodul PRO nicht aktiviert")
            return
        current = hass.data[DOMAIN]["data"]
        family = current.get("family") or {}
        allowed, mode, admin = family_access(connection, current)
        # Only publish names, avatars, IDs and food wishes. Never return shopping lists,
        # license details, recipe instructions, or admin settings to regular users.
        connection.send_result(msg["id"], {
            "access_mode": mode, "members": [{"id": str(m.get("id", "")), "name": str(m.get("name", "")),
                         "avatar": str(m.get("avatar", "😊"))}
                        for m in family.get("members", []) if str(m.get("id")) in allowed],
            "recipes": [{"id": str(r.get("id", "")), "name": str(r.get("name", ""))}
                        for r in current.get("recipes", [])],
            "wishes": [{"member_id": str(w.get("member_id", "")), "date": str(w.get("date", "")),
                        "slot": str(w.get("slot", "")), "recipe_id": str(w.get("recipe_id", "")),
                        "custom": str(w.get("custom", ""))} for w in family.get("wishes", []) if str(w.get("member_id")) in allowed],
        })

    @websocket_api.websocket_command({
        vol.Required("type"): f"{DOMAIN}/family_mobile_wish",
        vol.Required("member_id"): str,
        vol.Required("date"): str,
        vol.Required("slot"): vol.In(["mittag", "abend"]),
        vol.Required("recipe_id"): str,
        vol.Required("custom"): str,
    })
    @websocket_api.async_response
    async def ws_family_mobile_wish(hass, connection, msg):
        if not getattr(connection, "user", None):
            connection.send_error(msg["id"], "unauthorized", "Anmeldung erforderlich")
            return
        if not family_license_active():
            connection.send_error(msg["id"], "license_required", "Familienmodul PRO nicht aktiviert")
            return
        if not family_request_allowed(connection):
            connection.send_error(msg["id"], "rate_limit", "Zu viele Anfragen. Bitte später erneut versuchen")
            return
        data = hass.data[DOMAIN]["data"]
        family = data.setdefault("family", {"members": [], "wishes": []})
        allowed, mode, admin = family_access(connection, data)
        if str(msg["member_id"]) not in allowed:
            connection.send_error(msg["id"], "forbidden_member", "Für dieses Familienmitglied nicht berechtigt")
            return
        if not any(str(m.get("id")) == msg["member_id"] for m in family.get("members", []) if isinstance(m, dict)):
            connection.send_error(msg["id"], "invalid_member", "Familienmitglied nicht gefunden")
            return
        try:
            wish_date = date.fromisoformat(msg["date"])
        except ValueError:
            connection.send_error(msg["id"], "invalid_date", "Ungültiges Datum")
            return
        local_today = dt_util.now().date()
        if not local_today - timedelta(days=7) <= wish_date <= local_today + timedelta(days=365):
            connection.send_error(msg["id"], "invalid_date", "Datum außerhalb des erlaubten Bereichs")
            return
        recipe_id = msg["recipe_id"].strip()
        custom = msg["custom"].strip()
        if any(ord(c) < 32 for c in custom):
            connection.send_error(msg["id"], "invalid_recipe", "Ungültige Zeichen im Gericht")
            return
        if len(custom) > 120 or (recipe_id and not any(r.get("id") == recipe_id for r in data.get("recipes", []))) or not (recipe_id or custom):
            connection.send_error(msg["id"], "invalid_recipe", "Bitte ein gültiges Gericht angeben")
            return
        wishes = family.setdefault("wishes", [])
        # A repeated click for the exact same wish must not add duplicate entries.
        if any(w.get("member_id") == msg["member_id"] and w.get("date") == msg["date"]
               and w.get("slot") == msg["slot"] and w.get("recipe_id", "") == recipe_id
               and w.get("custom", "") == custom for w in wishes):
            connection.send_result(msg["id"], {"saved": True, "already_exists": True})
            return
        if len(wishes) >= 1000:
            connection.send_error(msg["id"], "too_many_wishes", "Zu viele Wünsche gespeichert")
            return
        wishes.append({"id": "w" + uuid.uuid4().hex,
            "member_id": msg["member_id"], "date": msg["date"], "slot": msg["slot"],
            "recipe_id": recipe_id, "custom": custom[:120]})
        await store.async_save(data)
        connection.send_result(msg["id"], {"saved": True})

    @websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/qr", vol.Required("url"): str})
    @websocket_api.require_admin
    @websocket_api.async_response
    async def ws_qr(hass, connection, msg):
        from urllib.parse import urlsplit
        url = msg["url"].strip()
        parsed = urlsplit(url)
        if len(url) > 500 or parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.username or parsed.password or parsed.path not in (f"/{PANEL_PATH}", "/speiseplan-familie"):
            connection.send_error(msg["id"], "invalid_url", "Nur eine gültige Home-Assistant-URL mit /mein-speiseplan ist erlaubt")
            return
        import qrcode
        import qrcode.image.svg
        import io
        code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=5, border=3)
        code.add_data(url)
        code.make(fit=True)
        output = io.BytesIO()
        code.make_image(image_factory=qrcode.image.svg.SvgPathImage).save(output)
        connection.send_result(msg["id"], {"svg": output.getvalue().decode("utf-8"), "url": url})

    websocket_api.async_register_command(hass, ws_family_users)
    websocket_api.async_register_command(hass, ws_family_mobile_get)
    websocket_api.async_register_command(hass, ws_family_mobile_wish)
    websocket_api.async_register_command(hass, ws_import_preview)
    websocket_api.async_register_command(hass, ws_shopping_pro)
    websocket_api.async_register_command(hass, ws_modules)
    websocket_api.async_register_command(hass, ws_license_transfer_request)
    websocket_api.async_register_command(hass, ws_activate)
    websocket_api.async_register_command(hass, ws_qr)
    websocket_api.async_register_command(hass, ws_version)
    websocket_api.async_register_command(hass, ws_get)
    websocket_api.async_register_command(hass, ws_save)
    websocket_api.async_register_command(hass, ws_export)
    js_path = Path(__file__).parent / "www" / "panel.js"
    await hass.http.async_register_static_paths([StaticPathConfig(f"/{DOMAIN}/panel.js", str(js_path), False),
        StaticPathConfig(f"/{DOMAIN}/panel-1.0.2.js", str(js_path), False)])
    mobile_js = Path(__file__).parent / "www" / "family-mobile.js"
    await hass.http.async_register_static_paths([StaticPathConfig(f"/{DOMAIN}/family-mobile.js", str(mobile_js), False)])
    await panel_custom.async_register_panel(
        hass, webcomponent_name="meal-planner-family-mobile", frontend_url_path="speiseplan-familie",
        module_url=f"/{DOMAIN}/family-mobile.js?v={UI_VERSION}", sidebar_title="Familienwünsche",
        sidebar_icon="mdi:account-heart-outline", require_admin=False,
        config_panel_domain=DOMAIN,
    )
    await panel_custom.async_register_panel(
        hass, webcomponent_name="meal-planner-panel", frontend_url_path=PANEL_PATH,
        module_url=f"/{DOMAIN}/panel-1.0.2.js?v={UI_VERSION}", sidebar_title="Speiseplan",
        sidebar_icon="mdi:food-apple-outline", require_admin=True,
        config_panel_domain=DOMAIN,
    )
    return True

async def async_unload_entry(hass, entry):
    frontend.async_remove_panel(hass, PANEL_PATH)
    frontend.async_remove_panel(hass, "speiseplan-familie")
    state = hass.data.get(DOMAIN, {})
    unsubscribe = state.get("reminder_unsubscribe")
    if unsubscribe:
        unsubscribe()
    hass.data.pop(DOMAIN, None)
    return True

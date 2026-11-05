"""Export Mein Speiseplan recipes to the public My Recipe Box .rtk interchange format.

No plan, shopping or license data is included. Admin-only endpoint calls this helper.
"""
from __future__ import annotations

import base64
import io
import json
import re
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageOps

MAX_RECIPES = 500
MAX_ARCHIVE = 100_000_000


def _text(value, limit=12000):
    return str(value or '')[:limit]


def _photo_bytes(recipe, images_dir: Path):
    """Read only local photo references or embedded, bounded data URLs."""
    ref = recipe.get('photo_ref')
    if isinstance(ref, str) and re.fullmatch(r'[0-9a-f]{32}', ref):
        path = images_dir / (ref + '.jpg')
        try:
            if 0 < path.stat().st_size <= 1_000_000:
                return path.read_bytes()
        except OSError:
            pass
    photo = recipe.get('photo_data')
    if isinstance(photo, str) and len(photo) < 2_000_000 and re.match(r'^data:image/(?:jpeg|png|webp);base64,', photo):
        try:
            raw = base64.b64decode(photo.split(',', 1)[1], validate=True)
            if len(raw) <= 1_400_000:
                return raw
        except (ValueError, base64.binascii.Error):
            pass
    return b''


def _convert_to_png(raw):
    if not raw:
        return b''
    try:
        with Image.open(io.BytesIO(raw)) as image:
            if image.width * image.height > 16_000_000:
                return b''
            image = ImageOps.exif_transpose(image)
            image.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
            out = io.BytesIO()
            image.convert('RGB').save(out, format='PNG', optimize=True)
            png = out.getvalue()
            return png if len(png) <= 3_000_000 else b''
    except (OSError, ValueError, Image.DecompressionBombError):
        return b''


def _ingredients(recipe):
    lines = []
    for item in (recipe.get('ingredients') or [])[:150]:
        if not isinstance(item, dict):
            continue
        quantity = _text(item.get('quantity'), 60).strip()
        name = _text(item.get('name'), 160).strip()
        if name:
            lines.append(f'{quantity} {name}'.strip())
    return '\n'.join(lines)


def build_rtk(recipes, images_dir):
    if not isinstance(recipes, list) or len(recipes) > MAX_RECIPES:
        raise ValueError('Maximal 500 Rezepte pro RTK-Export möglich.')
    exported = []
    embedded = {}
    for recipe in recipes:
        if not isinstance(recipe, dict):
            continue
        title = _text(recipe.get('name'), 120).strip()
        if not title:
            continue
        # Stable UUID where source already originated from My Recipe Box;
        # otherwise derive a deterministic UUID from our local recipe id.
        source_id = recipe.get('source_id')
        try:
            recipe_uuid = str(uuid.UUID(str(source_id))) if source_id else str(uuid.uuid5(uuid.NAMESPACE_URL, 'mein-speiseplan:' + str(recipe.get('id') or title)))
        except (ValueError, AttributeError, TypeError):
            recipe_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'mein-speiseplan:' + str(recipe.get('id') or title)))
        category_values = recipe.get('categories') or ([recipe.get('category')] if recipe.get('category') else [])
        categories = [{'title': _text(c, 60)} for c in category_values if isinstance(c, str) and c.strip()]
        try:
            quantity = str(max(1, min(50, int(recipe.get('servings') or 4))))
        except (TypeError, ValueError):
            quantity = '4'
        item = {
            'uuid': recipe_uuid,
            'title': title,
            'quantity': quantity,
            'ingredients': _ingredients(recipe),
            'instructions': _text(recipe.get('instructions') or recipe.get('notes')),
            'notes': _text(recipe.get('notes') if recipe.get('notes') != recipe.get('instructions') else ''),
            'url': _text(recipe.get('source_url'), 700),
            'categories': categories,
            'pictures': [],
            'lastModifiedDate': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
        }
        if recipe.get('photo_mode') == 'custom':
            png = _convert_to_png(_photo_bytes(recipe, images_dir))
            if png:
                filename = recipe_uuid + '.png'
                embedded[filename] = png
                item['pictures'] = [filename]
        exported.append(item)
    if not exported:
        raise ValueError('Keine Rezepte für den RTK-Export vorhanden.')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for index in range(0, len(exported), 400):
            archive.writestr(f'recipes_{index//400}.json', json.dumps(exported[index:index+400], ensure_ascii=False, separators=(',', ':')))
        all_categories = sorted({cat['title'] for recipe in exported for cat in recipe['categories']})
        archive.writestr('categories.json', json.dumps([{'title': cat} for cat in all_categories], ensure_ascii=False))
        archive.writestr('tags.json', '[]')
        for filename, png in embedded.items():
            archive.writestr(filename, png)
    result = buf.getvalue()
    if len(result) > MAX_ARCHIVE:
        raise ValueError('RTK-Datei zu groß (max. 100 MB). Bitte weniger Rezepte oder Bilder exportieren.')
    return result, len(exported), len(embedded)

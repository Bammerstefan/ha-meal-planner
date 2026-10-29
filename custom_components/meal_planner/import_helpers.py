"""Preview-only importers. Do not mutate meal-plan storage."""
import base64
import io
import ipaddress
import json
import re
import socket
import zipfile
from html.parser import HTMLParser
from urllib.parse import urlsplit, urljoin


def _ingredients(value):
    if isinstance(value, str):
        value=value.splitlines()
    if not isinstance(value,list):
        return []
    result=[]
    for obj in value[:150]:
        s=str(obj if not isinstance(obj,dict) else obj.get('text','')).strip()[:240]
        if not s: continue
        m=re.match(r'^((?:\d+[.,/]?\d*|[¼½¾])\s*(?:kg|g|dag|ml|l|cl|EL|TL|Stück|Stk\.?|Prise|Tasse|Becher|Dose|Bund|Packung|Pck\.?)?)\s+(.+)$',s,re.I)
        result.append({'name':(m.group(2) if m else s)[:160], 'quantity':(m.group(1) if m else '')[:60]})
    return result


def _clean(s,limit):
    return str(s or '').strip()[:limit]


def parse_rtk(encoded):
    raw=base64.b64decode(encoded,validate=True)
    if len(raw)>5_000_000: raise ValueError('Die RTK-Datei ist zu groß (max. 5 MB).')
    recipes=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist()
        if len(names)>1500: raise ValueError('Zu viele Einträge im Archiv.')
        for name in names:
            if not re.fullmatch(r'(?:[^/]+/)?recipes_\d+\.json',name):continue
            info=z.getinfo(name)
            if info.file_size>4_000_000: raise ValueError('Die Rezeptliste im Archiv ist zu groß.')
            batch=json.loads(z.read(name))
            if not isinstance(batch,list):raise ValueError('Ungültiges RTK-Rezeptformat.')
            for r in batch:
                if not isinstance(r,dict): continue
                title=_clean(r.get('title'),120)
                if not title:continue
                categories=r.get('categories') or []
                category= _clean(categories[0].get('title','') if isinstance(categories,list) and categories and isinstance(categories[0],dict) else '',60)
                try: servings=max(1,min(50,int(r.get('quantity') or 4)))
                except (ValueError,TypeError):servings=4
                ins=_clean(r.get('instructions'),12000)
                recipes.append({'name':title,'ingredients':_ingredients(r.get('ingredients')),'instructions':ins,'notes':ins,'category':category,'servings':servings,'photo_mode':'symbol','photo_symbol':'🍲','photo_data':'','source_url':_clean(r.get('url'),700),'source_id':_clean(r.get('uuid'),80)})
                if len(recipes)>500:raise ValueError('Maximal 500 Rezepte pro Import.')
    if not recipes:raise ValueError('Keine Rezepte in der RTK-Datei gefunden.')
    return recipes


class _JsonLd(HTMLParser):
    def __init__(self):super().__init__();self.collect=False;self.blocks=[];self.buffer=''
    def handle_starttag(self,tag,attrs):
        if tag=='script' and dict(attrs).get('type','').lower()=='application/ld+json':self.collect=True;self.buffer=''
    def handle_data(self,data):
        if self.collect and len(self.buffer)<1_000_000:self.buffer+=data
    def handle_endtag(self,tag):
        if tag=='script' and self.collect:self.blocks.append(self.buffer);self.collect=False


def _find_recipe(item):
    if isinstance(item,list):
        for x in item:
            hit=_find_recipe(x)
            if hit:return hit
    elif isinstance(item,dict):
        kinds=item.get('@type',[]);kinds=[kinds] if isinstance(kinds,str) else kinds
        if any(str(k).split('/')[-1].lower()=='recipe' for k in kinds):return item
        for key in ('@graph','mainEntity','itemListElement'):
            if key in item:
                hit=_find_recipe(item[key])
                if hit:return hit
    return None


def recipe_image_url(value, page_url):
    """Choose the first schema.org Recipe image URL without fetching it."""
    candidates = value if isinstance(value, list) else [value]
    for item in candidates[:12]:
        if isinstance(item, dict):
            item = item.get('url') or item.get('contentUrl') or item.get('thumbnailUrl')
        if not isinstance(item, str) or not item.strip():
            continue
        candidate = urljoin(page_url, item.strip())
        try:
            public_hostname(candidate)
        except (ValueError, TypeError):
            continue
        if len(candidate) <= 2000:
            return candidate
    return ''


def parse_webpage(html,url):
    parser=_JsonLd();parser.feed(html)
    for block in parser.blocks:
        try:r=_find_recipe(json.loads(block))
        except (ValueError,TypeError):continue
        if not r:continue
        title=_clean(r.get('name'),120)
        if not title:continue
        instruction=r.get('recipeInstructions',[])
        if isinstance(instruction,list):
            instruction='\n'.join(_clean(x.get('text') or x.get('name'),1000) if isinstance(x,dict) else _clean(x,1000) for x in instruction)
        elif isinstance(instruction,dict):instruction=_clean(instruction.get('text'),12000)
        servings=r.get('recipeYield',4)
        if isinstance(servings,list):servings=servings[0] if servings else 4
        m=re.search(r'\d+',str(servings));servings=max(1,min(50,int(m.group()) if m else 4))
        category=r.get('recipeCategory','');category=category[0] if isinstance(category,list) and category else category
        instruction=_clean(instruction,12000)
        return [{'name':title,'ingredients':_ingredients(r.get('recipeIngredient',[])),'instructions':instruction,'notes':instruction,'category':_clean(category,60),'servings':servings,'photo_mode':'symbol','photo_symbol':'🍲','photo_data':'','image_url':recipe_image_url(r.get('image') or r.get('thumbnailUrl'),url),'source_url':url}]
    raise ValueError('Diese Webseite enthält keine erkennbaren strukturierten Rezeptdaten (schema.org/Recipe).')


def public_hostname(url):
    parts=urlsplit(url)
    if parts.scheme!='https' or not parts.hostname or parts.username or parts.password or parts.port not in (None,443):
        raise ValueError('Nur öffentliche HTTPS-Rezeptseiten sind erlaubt.')
    host=parts.hostname
    if host.lower()=='localhost' or host.lower().endswith(('.local','.internal','.lan','.localhost')):
        raise ValueError('Lokale Adressen sind nicht erlaubt.')
    try:
        ip=ipaddress.ip_address(host)
    except ValueError:
        return host
    raise ValueError('IP-Adressen sind beim Rezeptimport nicht erlaubt.')


def public_dns_addresses(addresses):
    if not addresses:raise ValueError('Die Domain konnte nicht aufgelöst werden.')
    for address in addresses:
        ip=ipaddress.ip_address(address)
        if not ip.is_global:raise ValueError('Private oder lokale Zieladressen sind nicht erlaubt.')

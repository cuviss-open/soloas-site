from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
root=Path(__file__).resolve().parents[1]/'site'
class Page(HTMLParser):
 def __init__(self,path):
  super().__init__();self.ids=set();self.links=[];self.alts={};self.path=path;self.errors=[];self.feed(path.read_text())
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:
   if a['id'] in self.ids:self.errors.append('duplicate id '+a['id'])
   self.ids.add(a['id'])
  if tag in ('a','img','script','link'):
   v=a.get('src' if tag in ('img','script') else 'href')
   if v:self.links.append(v)
  if tag=='link' and a.get('rel')=='alternate':self.alts[a['hreflang']]=a['href']
pages={p.resolve():Page(p) for p in root.rglob('*.html')}; errors=[];checked=0
for path,page in pages.items():
 errors.extend(f'{path.relative_to(root)}: {x}' for x in page.errors)
 for link in page.links:
  u=urlsplit(link)
  if (u.scheme or u.netloc) and u.netloc!='soloas.cuviss.com':continue
  dest=((root / unquote(u.path).lstrip('/')) if u.path.startswith('/') else path.parent / unquote(u.path)).resolve() if u.path else path
  if dest.is_dir():dest=dest/'index.html'
  checked+=1
  if not dest.exists():errors.append(f'{path.relative_to(root)}: missing {link}')
  elif u.fragment and dest in pages and unquote(u.fragment) not in pages[dest].ids:errors.append(f'{path.relative_to(root)}: missing anchor {link}')
 for lang,link in page.alts.items():
  target=(root/urlsplit(link).path.lstrip('/')).resolve()
  if target.is_dir():target=target/'index.html'
  if target not in pages:errors.append(f'{path.relative_to(root)}: invalid alternate {lang}')
  elif lang!='x-default' and page.alts!=pages[target].alts:errors.append(f'{path.relative_to(root)}: nonreciprocal alternate {lang}')
 if set(page.alts)!={'en','zh-CN','x-default'}:errors.append(f'{path.relative_to(root)}: incomplete alternates')
# font sizes: only the six --fs-N variables may be used (see the comment at the top of the page CSS)
import re
FS_DECL=re.compile(r'(?<![\w-])(font-size|font)\s*:\s*([^;}"]+)')
def fs_ok(kind,v):
 v=v.strip()
 if v=='inherit':return True
 if kind=='font':return 'var(--fs-' in v and not re.search(r'\d(px|rem|pt)\b|\d(em)\b',v)
 if re.fullmatch(r'var\(--fs-[1-6]\)',v):return True
 if re.match(r'(clamp|min|max|calc)\(',v) and 'var(--fs-' in v or re.match(r'min\(1em,[\d.]+cqi\)$',v):
  return not re.search(r'\d(px|rem|pt)\b|%',v)
 return False
for path in list(root.rglob('*.html'))+list(root.rglob('*.css')):
 text=path.read_text()
 if path.suffix=='.html':text=' '.join(re.findall(r'<style[^>]*>(.*?)</style>',text,flags=re.S)+re.findall(r'style="([^"]*)"',text))
 for kind,v in FS_DECL.findall(text):
  if not fs_ok(kind,v):errors.append(f'{path.relative_to(root)}: font sizes must use var(--fs-1..6): {kind}:{v.strip()[:40]}')
report={'pages':len(pages),'local_links':checked,'problems':len(errors),'errors':errors}
root.joinpath('links.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False));raise SystemExit(bool(errors))

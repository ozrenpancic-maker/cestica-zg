import re,html,sys
def blocks_of(path):
    H=open(path,'rb').read().decode('cp1250')
    body=H[H.find('<body'):]
    out=[]
    for m in re.finditer(r'<(p|h[1-6])\b([^>]*)>(.*?)</\1>',body,re.S|re.I):
        inner=re.sub(r'<br\s*/?>',' ',m.group(3),flags=re.I)
        t=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',inner))).strip()
        if t: out.append({'center':'center' in m.group(2).lower(),'t':t})
    return out
def articles(path):
    B=blocks_of(path)
    heads=[i for i,b in enumerate(B) if re.fullmatch(r'Članak\s+\d+\.',b['t'])]
    arts={}
    for k,i in enumerate(heads):
        n=int(re.search(r'\d+',B[i]['t']).group()); j=heads[k+1] if k+1<len(heads) else len(B)
        arts.setdefault(n,[]).append([b['t'] for b in B[i+1:j]])
    return B,heads,arts

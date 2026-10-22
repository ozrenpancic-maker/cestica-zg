import json,re,sys,hashlib
sys.path.insert(0,'/tmp/claude-0/-home-claude/b53c7f43-bb20-5c9c-b9d7-ba222b365b65/scratchpad/slijepi')
from seg import blocks_of
D='/tmp/claude-0/-home-claude/b53c7f43-bb20-5c9c-b9d7-ba222b365b65/scratchpad/v0239/'
G=json.load(open(D+'gold_iz_grane.json'))['operacije']; GI={g['id']:g for g in G}
P=json.load(open(D+'output/semantic_directive_v0239_35169.json'))
B=[b['t'] for b in blocks_of(D+'35169.html')]
# Uparivanje: indeks predviđene operacije -> id zlatne operacije (ista naredba u istom članku odluke)
PAIR={0:'35169-c1-op2',1:'35169-c2-op1',2:'35169-c3-op1',3:'35169-c4-op1',4:'35169-c4-op2',5:'35169-c4-op3',6:'35169-c5-op1',
7:'35169-c6-op1',8:'35169-c6-op2',9:'35169-c7-op1',10:'35169-c8-op1',11:'35169-c9-op1',12:'35169-c9-op3',13:'35169-c10-op1',
14:'35169-c11-op1',15:'35169-c12-op1',16:'35169-c13-op2',17:'35169-c14-op1',18:'35169-c15-op1',19:'35169-c16-op1',20:'35169-c17-op1',
21:'35169-c18-op2',22:'35169-c19-op1',23:'35169-c20-op2',24:'35169-c21-op1',25:'35169-c22-op1',26:'35169-c22-op2',27:'35169-c22-op3',
28:'35169-c22-op4',29:'35169-c22-op5',30:'35169-c22-op6',31:'35169-c22-op7',32:'35169-c23-op1',33:'35169-c24-op1',34:'35169-c25-op1',35:'35169-c26-op1'}
assert len(set(PAIR.values()))==len(PAIR)==len(P['operations'])
for i,g in PAIR.items(): assert P['operations'][i]['amending_article']==str(GI[g]['clanak_odluke']),i
FAM={'REPLACE_UNIT':'REPLACE_STRUCT','REPLACE_PARAGRAPH':'REPLACE_STRUCT','REPLACE_ARTICLE':'REPLACE_STRUCT','REPLACE_HEADING':'REPLACE_STRUCT',
 'REPLACE_WORDS':'REPLACE_WORDS','DELETE_WORDS':'DELETE_WORDS','DELETE_UNIT':'DELETE_STRUCT','DELETE_PARAGRAPH':'DELETE_STRUCT','DELETE_ARTICLE':'DELETE_STRUCT','DELETE_HEADING':'DELETE_STRUCT',
 'ADD_PARAGRAPH':'ADD_STRUCT','ADD_ARTICLE':'ADD_STRUCT','ADD_HEADING':'ADD_STRUCT','ADD_ALINEA':'ADD_STRUCT','ADD_TEXT':'INSERT','INSERT_AFTER':'INSERT',
 'RENUMBER_ARTICLE':'RENUMBER','RENUMBER_PARAGRAPHS':'RENUMBER','RENUMBER':'RENUMBER'}
Q=str.maketrans({'»':'"','«':'"','„':'"','“':'"','”':'"'})
def strict(s): s=re.sub(r'\s+',' ',(s or '').translate(Q)).strip(); return s.strip('" ').strip()
def relaxed(s): return re.sub(r'\s+','',strict(s))
def gnum(x): m=re.match(r'\s*(\d+\s*[a-z]?)',str(x)); return re.sub(r'\s','',m.group(1)) if m else None
def g_addr(g):
    c=g['cilj']; kind='HEADING' if ('naslov_ispred_clanka' in c or g['tip']=='ADD_HEADING') else 'ARTICLE'
    art=gnum(c.get('clanak') or c.get('naslov_ispred_clanka') or c.get('iza_clanka'))
    return kind,art,{k:gnum(c[k]) for k in ('stavak','tocka','podtocka','alineja') if k in c}
def p_addr(p):
    a=p['address']; return 'ARTICLE',gnum(a.get('article')),{k2:str(a[k1]) for k1,k2 in (('paragraph','stavak'),('point','tocka'),('subitem','podtocka'),('alinea','alineja')) if k1 in a}
def addr_ok(g,p):
    gk,ga,gu=g_addr(g); pk,pa,pu=p_addr(p)
    if gk!=pk: return False
    anchor=re.findall(r'iza (?:stavka|članka) (\d+)',g.get('polozaj') or '')
    if g['tip'] in ('ADD_PARAGRAPH','ADD_ARTICLE'):
        if g['tip']=='ADD_ARTICLE': return pa in ({ga}|set(anchor))
        return pa==ga and pu.get('stavak') in ({gu.get('stavak')}|set(anchor)) and set(pu)<= {'stavak'}
    if g['tip']=='RENUMBER_PARAGRAPHS': return pa==ga and pu.get('stavak')=='9-10'
    return pa==ga and pu==gu
def g_new(g):
    n=g['novi_tekst']
    if not n: return None
    if 'blokovi' in n:
        a,b=n['blokovi']; t='\n'.join(B[a:b+1]); assert hashlib.sha256(t.encode()).hexdigest()==n['sha256']; return t
    return n['doslovno']
rows=[]
for i,p in enumerate(P['operations']):
    g=GI[PAIR[i]]
    t_ok=FAM[g['tip']]==FAM[p['operation']]
    a_ok=addr_ok(g,p)
    lit={}
    if g['stara_rijec_doslovno'] is not None:
        lit['old_strict']=strict(p['old_text_literal'])==strict(g['stara_rijec_doslovno']); lit['old_relaxed']=relaxed(p['old_text_literal'])==relaxed(g['stara_rijec_doslovno'])
    gn=g_new(g)
    if gn is not None:
        lit['new_strict']=strict(p['new_text_literal'])==strict(gn); lit['new_relaxed']=relaxed(p['new_text_literal'])==relaxed(gn)
    flagged=p['status']=='REVIEW_REQUIRED'
    crit=[]
    if not flagged:
        if FAM[g['tip']] in ('REPLACE_STRUCT','REPLACE_WORDS','DELETE_WORDS','DELETE_STRUCT','INSERT') and not a_ok: crit.append('POGREŠNA_JEDINICA')
        if g['tip']=='DELETE_WORDS' and FAM[p['operation']]=='DELETE_STRUCT': crit.append('BRISANJE_CIJELE_JEDINICE_UMJESTO_RIJEČI')
        if FAM[p['operation']]=='REPLACE_WORDS' and 'old_relaxed' in lit and not lit['old_relaxed']: crit.append('ZAMJENA_POGREŠNOG_TEKSTA')
        if FAM[p['operation']]=='REPLACE_STRUCT' and not p['new_text_literal']: crit.append('ZAMJENA_JEDINICE_BEZ_NOVOG_TEKSTA')
        if g['status']=='REVIEW_REQUIRED': crit.append('NEJASAN_SLUČAJ_BEZ_UPOZORENJA')
    full_s=t_ok and a_ok and all(v for k,v in lit.items() if k.endswith('strict'))
    full_r=t_ok and a_ok and all(v for k,v in lit.items() if k.endswith('relaxed'))
    rows.append(dict(i=i,gold=g['id'],cl=g['clanak_odluke'],gtip=g['tip'],ptip=p['operation'],t_ok=t_ok,a_ok=a_ok,lit=lit,flagged=flagged,crit=crit,full_s=full_s,full_r=full_r,
                     gaddr=g_addr(g),paddr=p_addr(p)))
FN=[g for g in G if g['id'] not in PAIR.values()]
for g in FN:
    r=['PROPUŠTENO_BRISANJE'] if g['tip'].startswith('DELETE') else []
    rows.append(dict(i=None,gold=g['id'],cl=g['clanak_odluke'],gtip=g['tip'],ptip=None,crit=r,fn=True))
json.dump(rows,open(D+'ocjena_redovi.json','w'),ensure_ascii=False,indent=1,default=str)
M=[r for r in rows if r.get('i') is not None]
nP,nG=len(P['operations']),len(G)
def pct(a,b): return f'{a}/{b} = {100*a/b:.1f} %'
print('Otkrivanje: TP',len(M),'FP',nP-len(M),'FN',len(FN),'| preciznost',pct(len(M),nP),'| odziv',pct(len(M),nG))
print('Vrsta točna',pct(sum(r['t_ok'] for r in M),len(M)))
print('Adresa točna',pct(sum(r['a_ok'] for r in M),len(M)))
for k in ('old_strict','old_relaxed','new_strict','new_relaxed'):
    v=[r['lit'][k] for r in M if k in r['lit']]; print(k,pct(sum(v),len(v)))
fs=sum(r['full_s'] for r in M); fr=sum(r['full_r'] for r in M)
print('Potpuno točne (strogo): preciznost',pct(fs,nP),'odziv',pct(fs,nG)); print('Potpuno točne (bez bjelina): preciznost',pct(fr,nP),'odziv',pct(fr,nG))
crit=[r for r in rows if r['crit']]; print('Kritične (operacija):',len(crit))
from collections import Counter; print(Counter(c for r in rows for c in r['crit']))
for r in rows:
    if r.get('i') is None: print('FN',r['gold'],r['gtip'],r['crit'])
    elif not r['full_s'] or r['crit']: print(r['i'],r['gold'],r['gtip'],'->',r['ptip'],'T' if r['t_ok'] else 't','A' if r['a_ok'] else 'a',r['lit'],r['crit'],'| g',r['gaddr'],'p',r['paddr'])

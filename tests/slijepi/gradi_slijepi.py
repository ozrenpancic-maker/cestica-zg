import sys,json,hashlib,re
sys.path.insert(0,'/tmp/claude-0/-home-claude/b53c7f43-bb20-5c9c-b9d7-ba222b365b65/scratchpad/slijepi')
from seg import blocks_of
SRC='/tmp/claude-0/-home-claude/b53c7f43-bb20-5c9c-b9d7-ba222b365b65/scratchpad/v0187/cesticahr_v0187_work/official_snapshots/akti/35169.html'
raw=open(SRC,'rb').read(); SHA=hashlib.sha256(raw).hexdigest()
B=[b['t'] for b in blocks_of(SRC)]
h=lambda s:hashlib.sha256(s.encode('utf-8')).hexdigest()
def nt(a,b):
    t='\n'.join(B[a:b+1]); return {'blokovi':[a,b],'pocetak':t[:90],'kraj':t[-90:],'sha256':h(t),'duljina':len(t)}
def lit(s): return {'doslovno':s}
O=[]
def op(cl,tip,cilj,blok,old=None,new=None,pol=None,z=(),st='CONFIRMED',nap=None):
    k=sum(1 for o in O if o['clanak_odluke']==cl)+1
    O.append({'id':f'35169-c{cl}-op{k}','clanak_odluke':cl,'redni_broj_operacije':k,'tip':tip,
      'cilj':dict(plan='UPU 1 Malinska, Radići (Odluka o donošenju, SN PGŽ 14/13, 3/14, 28/15)',**cilj),
      'naredba_blok':blok,'naredba_doslovno':B[blok],'naredba_sha256':h(B[blok]),
      'stara_rijec_doslovno':old,'novi_tekst':new,'polozaj':pol,'zastavice':list(z),'status':st,'napomena':nap})
op(1,'REPLACE_UNIT',{'clanak':'2','stavak':'4','tocka':'1','podtocka':'b'},23,new=nt(24,31),z=['VERB_TYPO_MIJENJA_SE_GLASI','DEEP_ADDRESS','PLAN_ABBREVIATION_DEFINED_HERE'])
op(1,'REPLACE_UNIT',{'clanak':'2','stavak':'4','tocka':'3'},32,new=nt(33,39),z=['CONTEXT_PLAN_ABBREVIATION'])
op(2,'REPLACE_PARAGRAPH',{'clanak':'5','stavak':'3'},41,new=nt(42,42))
op(3,'DELETE_WORDS',{'naslov_ispred_clanka':'14'},44,old='i površina mješovite namjene (M6)',z=['TARGET_IS_HEADING'])
op(4,'DELETE_WORDS',{'clanak':'14','stavak':'1'},46,old='i površina mješovite namjene (M6)')
op(4,'DELETE_WORDS',{'clanak':'14','stavak':'2'},47,old='i površine mješovite namjene (M6)',z=['NEAR_DUPLICATE_LITERAL_PREVIOUS_OP'])
op(4,'DELETE_UNIT',{'clanak':'14','stavak':'4','alineja':'6'},48)
op(5,'REPLACE_HEADING',{'naslov_ispred_clanka':'19'},50,new=lit('Površine ugostiteljsko - turističke namjene - hoteli (T11 i T12)'),z=['TARGET_IS_HEADING','NEW_TEXT_INLINE'])
op(6,'REPLACE_WORDS',{'clanak':'19','stavak':'1'},52,old='hotel (T1)',new=lit('hotel (T11)'))
op(6,'ADD_PARAGRAPH',{'clanak':'19','stavak':'2'},53,new=nt(54,54),pol='iza stavka 1. (izričito)',z=['QUOTE_MISMATCH_IN_SOURCE','RENUMBERING_OF_LATER_PARAGRAPHS_UNSTATED'],
   nap='Novi tekst završava znakom » umjesto «. Ne kaže se što je s eventualnim dosadašnjim st. 2.')
op(7,'REPLACE_WORDS',{'naslov_ispred_clanka':'24'},56,old='lokalnog',new=lit('županijskog'),z=['TARGET_IS_HEADING'])
op(8,'REPLACE_WORDS',{'clanak':'24','stavak':'1'},58,old='lokalnog',new=lit('županijskog'))
op(9,'REPLACE_WORDS',{'clanak':'28','stavak':'1'},60,old='površine',new=lit('površina'),pol='iza riječi »...smještajem (KS1, KS2 i KS3), te unutar«',
   z=['ELLIPSIS_IN_ANCHOR','COMPOUND_SENTENCE','ANCHOR_PLUS_TARGET_WORD'])
op(9,'REPLACE_WORDS',{'clanak':'28','stavak':'1'},60,old='hotel (T1)',new=lit('hotela (T11 i T12)'),z=['COMPOUND_SENTENCE','QUOTE_MISMATCH_IN_SOURCE','CONTEXT_INHERITED_WITHIN_SENTENCE'],
   nap='Stari literal nema zatvarajući « („»hotel (T1) zamjenjuje riječju"); granica je glagol.')
op(9,'DELETE_WORDS',{'clanak':'28','stavak':'2'},61,old='i površina mješovite namjene (M6)')
op(10,'REPLACE_ARTICLE',{'clanak':'30'},63,new=nt(64,64))
op(11,'REPLACE_WORDS',{'naslov_ispred_clanka':'31'},66,old='turističke namjene (T1)',new=lit('turističke namjene (T11)'),z=['TARGET_IS_HEADING','VERB_NUMBER_MISMATCH'])
op(12,'REPLACE_WORDS',{'clanak':'31','tocka':'1'},68,old='turističke namjene (T1)',new=lit('turističke namjene (T11)'),z=['VERB_NUMBER_MISMATCH'])
op(13,'ADD_HEADING',{'iza_clanka':'31'},70,new=nt(71,71),pol='iza članka 31.',z=['COMPOUND_HEADING_AND_ARTICLE'])
op(13,'ADD_ARTICLE',{'clanak':'32 (novi)'},70,new=nt(72,102),pol='iza novog naslova, iza članka 31.',z=['COMPOUND_HEADING_AND_ARTICLE','QUOTED_ARTICLE_HEADING_INSIDE_NEW_TEXT','ORDER_DEPENDENT_NUMBERING'],
   nap='Blok „Članak 32." unutar citata nije članak odluke. Do čl. 15 odluke postoje dva članka 32.')
op(14,'REPLACE_WORDS',{'naslov_ispred_clanka':'32 (dosadašnji? vidi napomenu)'},104,old='2.1.2.',new=lit('2.1.3.'),z=['TARGET_IS_HEADING','ORDER_DEPENDENT_NUMBERING','NUMBERING_TIME_AMBIGUOUS'],st='REVIEW_REQUIRED',
   nap='Nakon čl. 13 i novi i dosadašnji članak 32 imaju ispred sebe naslov „2.1.2."; tekst ne kaže „dosadašnjeg". Namjera je vjerojatno dosadašnji, ali to nije jednoznačno.')
op(15,'RENUMBER_ARTICLE',{'clanak':'32 (dosadašnji)'},106,new=lit('33'))
op(16,'REPLACE_WORDS',{'naslov_ispred_clanka':'33 (dosadašnji)'},108,old='2.1.3.',new=lit('2.1.4.'),z=['TARGET_IS_HEADING','ORDER_DEPENDENT_NUMBERING'])
op(17,'RENUMBER_ARTICLE',{'clanak':'33 (dosadašnji)'},110,new=lit('34'))
op(18,'DELETE_HEADING',{'naslov_ispred_clanka':'34 (dosadašnji)'},112,z=['COMPOUND_HEADING_AND_ARTICLE','NO_FINAL_PUNCTUATION'])
op(18,'DELETE_ARTICLE',{'clanak':'34 (dosadašnji)'},112,z=['COMPOUND_HEADING_AND_ARTICLE'])
op(19,'DELETE_WORDS',{'clanak':'35'},114,old='i površine mješovite namjene (M6)',z=['NO_PARAGRAPH_ADDRESS'])
op(20,'DELETE_HEADING',{'naslov_ispred_clanka':'41'},116,z=['COMPOUND_HEADING_AND_ARTICLE','NO_FINAL_PUNCTUATION'])
op(20,'DELETE_ARTICLE',{'clanak':'41'},116,z=['COMPOUND_HEADING_AND_ARTICLE','RENUMBERING_OF_LATER_ARTICLES_UNSTATED'])
op(21,'ADD_PARAGRAPH',{'clanak':'63','stavak':'4'},118,new=nt(119,119),pol='iza stavka 3. (izričito)',z=['QUOTE_MISMATCH_IN_SOURCE','NESTED_QUOTES'])
op(22,'REPLACE_WORDS',{'clanak':'94','stavak':'1'},121,old='lokalnog',new=lit('županijskog'))
op(22,'INSERT_AFTER',{'clanak':'94','stavak':'4'},122,old='... javne rasvjete i slično)',new=lit(', kao i gradnja zgrade u funkciji luke sa pratećim sadržajima'),
   z=['ELLIPSIS_IN_ANCHOR','COMMA_DESCRIBED_NOT_QUOTED'],nap='„dodaje se zarez i riječ:" — zarez nije u citatu.')
op(22,'DELETE_UNIT',{'clanak':'94','stavak':'5','alineja':'5'},123)
op(22,'DELETE_PARAGRAPH',{'clanak':'94','stavak':'8'},124)
op(22,'RENUMBER_PARAGRAPHS',{'clanak':'94','stavci':'9-10'},125,new=lit('8-9'),z=['RANGE_RENUMBERING'])
op(22,'ADD_PARAGRAPH',{'clanak':'94','stavak':'10 (novi)'},126,new=nt(127,127),pol='iza dosadašnjeg st. 10. (koji postaje st. 9.)',z=['ORDER_DEPENDENT_NUMBERING','NESTED_QUOTES'])
op(22,'REPLACE_PARAGRAPH',{'clanak':'94','stavak':'11'},128,new=lit('Na dijelu lukobrana iz prethodnog stavka koji nije u funkciji operativne obale (zone za ukrcaj i iskrcaj putnika, manipuliranje brodicama i sl.) potrebno je urediti parkiralište (okvirnog broja 45 PM) koje će biti u javnom korištenju'),
   z=['NEW_TEXT_INLINE','ORDER_DEPENDENT_NUMBERING'])
op(23,'REPLACE_WORDS',{'clanak':'95','stavak':'1'},130,old='lokalnog',new=lit('županijskog'))
op(24,'REPLACE_WORDS',{'clanak':'104','stavak':'2'},132,old='i',new=lit(','),pol='iza riječi »TS PLAN-2«',z=['COMPOUND_SENTENCE','NEW_TEXT_DESCRIBED_NOT_QUOTED','SINGLE_CHAR_LITERAL'])
op(24,'INSERT_AFTER',{'clanak':'104','stavak':'2'},132,old='TS PLAN-3',new=lit('i TS PLAN-4'),z=['COMPOUND_SENTENCE','VERB_TYPO_DODAJU_RIJECI','CONTEXT_INHERITED_WITHIN_SENTENCE'])
op(24,'INSERT_AFTER',{'clanak':'104','stavak':'2'},132,old='Trafostanice će se graditi kao samostojeće građevine ili kao ugrađene u građevini.',new=lit('Planiranu trafostanicu TS PLAN-4 potrebno je predvidjeti kao ugrađenu unutar planirane zgrade na površini javnog parka Z11.'),
   pol='iza rečenice',z=['COMPOUND_SENTENCE','LEADING_SPACE_IN_QUOTE','SENTENCE_ANCHOR'])
op(25,'REPLACE_PARAGRAPH',{'clanak':'108','stavak':'5'},134,new=nt(135,135),z=['QUOTE_MISMATCH_IN_SOURCE','NEW_TEXT_ENDS_AT_ARTICLE_END'])
op(26,'REPLACE_PARAGRAPH',{'clanak':'112','stavak':'3'},137,new=nt(138,138))
from collections import Counter
g={'naziv':'SLIJEPI TEST v0.23.9: neovisno označene naredbe izmjene, odluka 35169 (Malinska-Dubašnica, SN PGŽ 5/17)',
 'verzija':'v1','datum':'2026-10-22','autor':'Claude (neovisni ocjenjivač)','NE_DIJELITI_PRIJE_OCJENE':True,
 'izvor':{'publication_id':'35169','sn':'5/17','datum_izdanja':'2017-02-24','izdanje_id':1005,'mjesto_id':'51511','redni_broj':5,'sha256':SHA,'kodiranje':'windows-1250'},
 'pravila':{'segmentacija':'Članak odluke = samostalni blok „Članak N.“ izvan citata; 26 članaka; blok „Članak 32.“ (indeks 72) je dio citiranog novog teksta čl. 13.',
   'atomizacija':'Jedna operacija = jedna strukturna jedinica ili jedan raspon riječi (naslov i članak su dvije operacije; svaka radnja u složenoj rečenici je zasebna).',
   'nisu_operacije':'Glava I.–IV. (uvodne i završne odredbe, stupanje na snagu).',
   'usporedba':'Literali se uspoređuju nakon sažimanja bjelina i bez razlike » « / " / „ “; novi tekst preko sha256 nad blokovima spojenima s \\n.'},
 'operacije':O,
 'sazetak':{'clanaka_odluke':26,'operacija':len(O),'CONFIRMED':sum(o['status']=='CONFIRMED' for o in O),'REVIEW_REQUIRED':sum(o['status']=='REVIEW_REQUIRED' for o in O),
   'po_tipu':dict(Counter(o['tip'] for o in O))},
 'kriticne_pogreske_definicija':['operacija primijenjena na pogrešan članak/stavak/naslov','brisanje ili zamjena pogrešne jedinice','citirani „Članak 32.“ tretiran kao članak odluke','naredba izvan citata propuštena (odziv) za DELETE_*','REVIEW_REQUIRED slučaj označen kao potvrđen bez upozorenja']}
g['zakljucano_sha256']=hashlib.sha256(json.dumps(O,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
json.dump(g,open('/tmp/claude-0/-home-claude/b53c7f43-bb20-5c9c-b9d7-ba222b365b65/scratchpad/slijepi/slijepi-35169-gold.json','w'),ensure_ascii=False,indent=1)
print(g['sazetak']); print(g['zakljucano_sha256']); print(SHA)

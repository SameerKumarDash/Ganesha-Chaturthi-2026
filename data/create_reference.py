"""Original, hand-authored devotional line drawing. No external artwork.

Run only to regenerate the bundled JSON. Coordinates use a 1000x1200 canvas.
Catmull-Rom anchors are converted to explicit cubic Bezier control points.
"""
import json
import math
from pathlib import Path

paths=[]
def stroke(name,category,anchors,width=2.0,closed=False):
    p=[tuple(q) for q in anchors]
    if closed and p[-1]!=p[0]:
        p.append(p[0])
    segments=[]
    for i in range(len(p)-1):
        prev=p[i-1] if i else (p[-2] if closed else p[0])
        a,b=p[i:i+2]
        nxt=p[i+2] if i+2<len(p) else (p[1] if closed else p[-1])
        c1=[a[j]+(b[j]-prev[j])/6 for j in (0,1)]
        c2=[b[j]-(nxt[j]-a[j])/6 for j in (0,1)]
        segments.append([a,c1,c2,b])
    paths.append(dict(id=f'g{len(paths):03d}',name=name,category=category,
                      step_order=len(paths),bezier_segments=segments,width=width,
                      is_closed=closed,is_filled=False))

def oval(name,cat,x,y,rx,ry,width=1.5):
    stroke(name,cat,[(x+rx*math.cos(t*math.tau/12),y+ry*math.sin(t*math.tau/12))
                     for t in range(12)],width,True)

def build():
    paths.clear()
    stroke('Crown ascending crest','crown',[(351,267),(374,210),(403,194),(426,150),(456,145),(481,100),(500,66),(519,100),(544,145),(574,150),(597,194),(626,210),(649,267)],2.8)
    stroke('Crown lower band','crown',[(349,266),(420,254),(500,250),(580,254),(651,266)],2.5)
    stroke('Crown band engraving','crown',[(355,282),(430,270),(500,266),(570,270),(645,282)],1.6)
    stroke('Central crown petal','crown',[(500,238),(471,204),(473,169),(500,129),(527,169),(529,204),(500,238)],2)
    for side in (-1,1):
        def mirror(q): return [(500+side*(x-500),y) for x,y in q]
        stroke('Crown leaf','crown',mirror([(454,240),(410,230),(398,209),(431,190),(454,211),(454,240)]),1.5)
        stroke('Crown outer leaf','crown',mirror([(398,244),(373,242),(380,220)]),1.2)
        stroke('Crown flute','crown',mirror([(460,173),(449,160),(432,162)]),1.2)
    oval('Crown jewel','crown',500,190,12,21,2)
    for x in range(375,640,25): oval('Crown pearls','crown',x,273-7*math.sin((x-375)/265*math.pi),3,3,1.1)
    stroke('Left temple and cheek','face',[(361,285),(343,328),(348,381),(364,417),(391,444),(416,453)],2.7)
    stroke('Right temple and cheek','face',[(639,285),(657,328),(652,381),(636,417),(609,444),(584,453)],2.7)
    for side in (-1,1):
        def mirror(q): return [(500+side*(x-500),y) for x,y in q]
        stroke('Great elephant ear','ears',mirror([(351,307),(307,284),(261,292),(236,331),(244,390),(270,444),(305,468),(331,448),(351,406)]),2.8)
        stroke('Ear inner fold','ears',mirror([(332,323),(297,313),(268,338),(273,385),(297,429),(319,421),(332,389)]),1.7)
        stroke('Ear soft fold','ears',mirror([(271,352),(291,350),(308,373),(314,403)]),1.1)
    stroke('Forehead arch','forehead',[(394,320),(436,300),(500,296),(564,300),(606,320)],1.4)
    stroke('Tilak left','tilak',[(481,314),(482,339),(489,353),(500,358)],2.1)
    stroke('Tilak right','tilak',[(519,314),(518,339),(511,353),(500,358)],2.1)
    stroke('Tilak center','tilak',[(500,316),(500,339)],2)
    oval('Tilak bindu','tilak',500,372,3,4,1.7)
    for side in (-1,1):
        def mirror(q): return [(500+side*(x-500),y) for x,y in q]
        stroke('Peaceful brow','eyes',mirror([(384,351),(409,342),(436,347),(456,359)]),2)
        stroke('Meditative eyelid','eyes',mirror([(388,368),(412,377),(435,375),(454,365)]),2.1)
        stroke('Eye lower contour','eyes',mirror([(394,377),(416,383),(435,380)]),1)
    stroke('Sweeping trunk outer edge','trunk',[(455,397),(451,453),(457,518),(485,566),(532,582),(578,568),(604,535),(600,507),(577,499),(559,513)],3.1)
    stroke('Trunk return edge','trunk',[(545,397),(545,446),(530,484),(519,516),(537,541),(563,536),(571,522)],2.8)
    stroke('Trunk curl','trunk',[(559,513),(551,526),(559,538),(572,535)],1.7)
    for y in (427,447,469): stroke('Trunk gentle crease','trunk',[(470,y),(489,y+5),(509,y+3)],1.1)
    stroke('Left tusk','trunk',[(424,421),(422,455),(399,473),(432,467),(446,443)],2)
    stroke('Short right tusk','trunk',[(576,421),(578,448),(589,452),(580,433)],1.8)
    # Four arms, with rear arms rising and the front hands in calm mudras.
    for side in (-1,1):
        def mirror(q): return [(500+side*(x-500),y) for x,y in q]
        stroke('Upper shoulder and arm','arms',mirror([(351,468),(323,475),(291,519),(254,550),(219,533),(204,491),(213,456)]),2.5)
        stroke('Upper arm return','arms',mirror([(235,462),(243,494),(258,509),(279,478),(312,458)]),2)
        stroke('Lower arm outer','arms',mirror([(370,517),(326,540),(299,579),(274,624),(244,651),(218,642),(208,618)]),2.6)
        stroke('Lower arm inner','arms',mirror([(390,579),(359,605),(333,644),(301,682),(264,692),(234,674)]),2.1)
        stroke('Armlet','jewelry',mirror([(308,556),(322,565),(339,569)]),1.6)
    # Reorder jewelry after torso below by sorting categories at the end.
    stroke('Blessing palm outline','hands',[(209,623),(195,594),(184,564),(184,527),(191,510),(198,520),(202,552),(205,509),(214,501),(221,513),(221,551),(227,512),(236,509),(242,525),(238,562),(251,543),(260,546),(259,562),(247,589),(245,617),(230,634),(209,623)],2)
    stroke('Blessing palm lines','hands',[(205,586),(218,575),(236,576)],1.2)
    stroke('Blessing thumb crease','hands',[(239,564),(222,595),(225,614)],1.1)
    stroke('Offering palm','hands',[(752,624),(768,607),(787,612),(798,627),(814,629),(821,637),(801,651),(774,655),(749,641)],2)
    stroke('Modak offering','hands',[(774,610),(781,591),(791,577),(800,592),(805,612),(790,617),(774,610)],1.8)
    for x in (785,793): stroke('Modak fold','hands',[(791,583),(x,604)],.9)
    for side in (-1,1):
        def mirror(q): return [(500+side*(x-500),y) for x,y in q]
        stroke('Rear hand','hands',mirror([(214,462),(205,443),(210,425),(220,419),(229,425),(239,424),(245,436),(236,460),(214,462)]),1.7)
        stroke('Lotus stem','hands',mirror([(223,440),(226,395)]),1.3)
        stroke('Lotus center','hands',mirror([(226,399),(211,381),(226,354),(241,381),(226,399)]),1.6)
        stroke('Lotus side petals','hands',mirror([(224,400),(199,391),(192,374),(212,380),(226,399),(243,379),(261,372),(254,391),(229,401)]),1.3)
    stroke('Rounded torso left','torso',[(393,539),(369,613),(354,681),(362,741),(404,781)],2.6)
    stroke('Rounded torso right','torso',[(611,549),(635,616),(645,681),(635,743),(597,781)],2.6)
    stroke('Belly underside','torso',[(405,779),(447,799),(503,806),(555,797),(596,779)],2.3)
    stroke('Belly navel','torso',[(489,697),(499,691),(509,698),(505,708),(497,709)],1.4)
    stroke('Sacred thread','necklace',[(599,526),(564,603),(510,654),(444,682),(365,697)],1.7)
    stroke('Necklace outer','necklace',[(397,501),(402,554),(435,594),(488,617),(539,615),(581,590),(612,542)],2)
    stroke('Necklace inner','necklace',[(396,517),(419,560),(451,584),(486,595)],1.2)
    oval('Pendant','jewelry',494,621,12,17,1.8)
    for side in (-1,1):
        def mirror(q): return [(500+side*(x-500),y) for x,y in q]
        stroke('Wrist bracelet','jewelry',mirror([(207,635),(222,646),(245,641)]),1.5)
        oval('Earring','jewelry',500+side*179,448,10,17,1.5)
    stroke('Waist sash upper','waist',[(367,764),(419,806),(500,825),(581,806),(632,764)],2.5)
    stroke('Waist sash lower','waist',[(357,786),(416,828),(500,847),(584,828),(643,786)],1.7)
    oval('Sash clasp','waist',500,835,13,12,1.5)
    stroke('Left seated leg','legs',[(356,763),(310,778),(253,809),(214,851),(223,881),(272,899),(331,897),(399,883),(459,896)],2.7)
    stroke('Right seated leg','legs',[(645,763),(691,778),(747,809),(786,851),(777,881),(728,899),(669,897),(601,883),(541,896)],2.7)
    stroke('Left crossed ankle','legs',[(292,844),(338,845),(396,865),(459,896),(485,917)],2.0)
    stroke('Right crossed ankle','legs',[(710,844),(662,845),(604,865),(541,896),(515,917)],2.0)
    for side in (-1,1):
        def mirror(q): return [(500+side*(x-500),y) for x,y in q]
        for shift in (0,18,36):
            stroke('Dhoti pleat','dhoti',mirror([(371-shift/2,807+shift/3),(336-shift,821+shift/2),(276-shift/2,855+shift/3)]),1.1)
    stroke('Central dhoti drape','dhoti',[(477,850),(466,890),(468,939),(500,956),(532,939),(534,890),(523,850)],1.9)
    for x in (487,500,513): stroke('Drape silk fold','dhoti',[(x,866),(x-2,911),(x,937)],1)
    stroke('Left foot','feet',[(468,908),(442,906),(418,917),(391,927),(379,940),(389,951),(416,950),(454,935),(468,929)],2)
    stroke('Right foot','feet',[(532,908),(558,906),(582,917),(609,927),(621,940),(611,951),(584,950),(546,935),(532,929)],2)
    for side in (-1,1):
        for dx in (0,10,20):
            x=500+side*(102-dx)
            stroke('Toes','feet',[(x,935),(x+side*4,945)],.9)
    # A quiet lotus seat, no geometric HUD.
    for offset in (-210,-140,-70,0,70,140,210):
        x=500+offset
        stroke('Lotus seat petal','silhouette',[(x-53,982),(x-38,1003),(x,1019+12*(1-abs(offset)/280)),(x+38,1003),(x+53,982),(x,996),(x-53,982)],1.4)
    stroke('Lotus seat base','silhouette',[(219,1026),(330,1049),(500,1056),(670,1049),(781,1026)],1.5)
    order={'crown':0,'face':1,'ears':1,'forehead':1,'tilak':2,'eyes':2,'trunk':3,'arms':4,'hands':4,'torso':4,'necklace':4,'jewelry':4,'waist':5,'legs':5,'dhoti':5,'feet':5,'silhouette':5}
    paths.sort(key=lambda p:order[p['category']])
    for i,p in enumerate(paths): p['step_order']=i
    return {'canvas':{'width':1000,'height':1200},'provenance':'Original hand-authored cubic devotional drawing created for this experiment. No Ganapati reference was available.','paths':paths}

if __name__=='__main__':
    out=Path(__file__).with_name('ganesha_vector_data.json')
    out.write_text(json.dumps(build(),indent=2),encoding='utf-8')
    print(f'Wrote {len(paths)} original paths to {out}')

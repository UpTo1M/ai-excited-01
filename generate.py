"""The Ocean Escapes — original deterministic procedural illustration.
Build-time only: Python + Pillow. Runtime uses the committed PNG.
"""
from PIL import Image, ImageDraw, ImageFilter
import math
import random
from pathlib import Path

S = 3
W = 1024
rng = random.Random(41027)
im = Image.new('RGB', (W*S, W*S))
pix = im.load()
for y in range(W*S):
    for x in range(W*S):
        r = math.hypot((x/S-510)/800, (y/S-410)/850)
        light = max(0, 1-r)
        pix[x,y] = (int(4+7*light), int(12+20*light), int(25+27*light))
d = ImageDraw.Draw(im)
def line(points, color, width=1):
    d.line([(int(x*S),int(y*S)) for x,y in points], fill=color, width=max(1,int(width*S)), joint='curve')
def poly(points, color):
    d.polygon([(int(x*S),int(y*S)) for x,y in points], fill=color)
def ellipse(box,color):
    d.ellipse(tuple(int(v*S) for v in box), fill=color)
def bez(p0,p1,p2,p3,n=80):
    return [((1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t*t*p2[0]+t**3*p3[0], (1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t*t*p2[1]+t**3*p3[1]) for t in [i/n for i in range(n+1)]]
def curve(points,color,width=1):
    line(bez(*points),color,width)

# Sparse stars, leaving the silhouette's immediate space quiet.
for _ in range(175):
    x,y=rng.uniform(45,979),rng.uniform(40,860)
    rr=rng.choice([.5,.7,1,1.3])
    ellipse((x-rr,y-rr,x+rr,y+rr),rng.choice(['#334c60','#496577','#7c8b8b']))

# The ocean is a tilted elliptical portal: luminous far rim behind whale.
def ring(t, radius=1):
    return (505+radius*(322*math.cos(t)+92*math.sin(t)), 637+radius*(99*math.sin(t)-46*math.cos(t)))
for i in range(60):
    rad=1-i*.003
    pts=[ring(t,rad) for t in [j*math.tau/500 for j in range(501)]]
    line(pts,(12+int(i*.3),69+int(i*.9),84+int(i*.9)),1.8)
for j in range(20):
    pts=[ring(t,1+rng.uniform(-.008,.008)) for t in [i*math.pi/240+math.pi for i in range(241)]]
    line(pts,'#7fd5cd' if j%4 else '#d6ebcf',.7)

# Waterfall below the suspended sea, tapered and broken into threads.
for i in range(245):
    t=rng.uniform(0,math.pi)
    x,y=ring(t,rng.uniform(.88,1))
    length=rng.uniform(25,200)*(math.sin(t)*.7+.3)
    curve([(x,y),(x-7,y+length*.35),(x-25,y+length*.8),(x-32,y+length)],rng.choice(['#143d50','#1b5261','#216273','#2a7480']),rng.uniform(.4,1.2))

# Whale local coordinates: long axis rises dramatically toward upper right.
# u runs from tail to nose; v is perpendicular to its back.
def T(p):
    u,v=p
    return (310+.80*u+.60*v, 578-.60*u+.80*v)
def whale_path(segments):
    out=[]
    for seg in segments: out.extend([T(p) for p in bez(*seg)])
    return out
body_segments=[[(0,0),(95,-8),(105,-110),(275,-116)],[(275,-116),(395,-129),(482,-74),(487,-16)],[(487,-16),(495,55),(373,103),(265,77)],[(265,77),(133,54),(92,14),(0,0)]]
body=whale_path(body_segments)
mask=Image.new('L',im.size); ImageDraw.Draw(mask).polygon([(int(x*S),int(y*S)) for x,y in body],fill=255)
shade=Image.new('RGB',im.size)
sp=shade.load()
for y in range(220*S,730*S):
    for x in range(200*S,860*S):
        xx=x/S-310; yy=y/S-578; v=.6*xx+.8*yy
        a=max(0,min(1,(v+120)/210))
        sp[x,y]=(int(20+21*a),int(88+67*a),int(107+57*a))
im.paste(shade,(0,0),mask); d=ImageDraw.Draw(im)
# Large tail flukes, swept backwards like a ribbon.
poly(whale_path([[(-8,5),(-57,-63),(-126,-70),(-153,-56)],[(-153,-56),(-110,-21),(-78,23),(-7,15)],[(-7,15),(-42,61),(-60,104),(-45,132)],[(-45,132),(11,98),(26,49),(-8,5)]]),'#226e80')
curve([T(p) for p in [(-150,-56),(-88,-39),(-57,1),(0,9)]],'#8fd7d1',2)
curve([T(p) for p in [(-44,130),(-15,95),(3,53),(0,9)]],'#61b8bb',2)
# Ivory pleated throat, its contour follows the broad head.
under=whale_path([[(157,38),(250,86),(401,76),(480,4)],[(480,4),(458,69),(350,103),(265,77)],[(265,77),(216,67),(178,51),(157,38)]])
poly(under,'#d7ddbf')
for i in range(12):
    u=196+i*12
    curve([T(p) for p in [(u,54),(u+84,100-i*.4),(418+i*3,65-i*3),(478,4)]],'#6b9994',.9)
# Far dorsal fin and huge near flipper give a clean readable gesture.
poly(whale_path([[(192,-103),(179,-158),(213,-160),(251,-114)],[(251,-114),(223,-111),(206,-106),(192,-103)]]),'#26788a')
flipper=whale_path([[(294,35),(275,111),(180,183),(127,183)],[(127,183),(159,137),(188,83),(246,28)],[(246,28),(264,17),(285,20),(294,35)]])
poly(flipper,'#123f57')
curve([T(p) for p in [(291,38),(265,112),(180,174),(128,182)]],'#6ac1c0',2.2)
# Back contour glints and fine skin scoring.
for seg in body_segments[:2]: curve([T(p) for p in seg],'#9cdbcf',2)
for i in range(35):
    u=rng.uniform(130,425); v=rng.uniform(-90,-20)
    curve([T(p) for p in [(u,v),(u+9,v-2),(u+16,v-1),(u+23,v+1)]],'#3b95a2',.6)
# Eye and deliberate curved mouth, warm pinpoint in the cool body.
x,y=T((406,-4)); ellipse((x-7,y-7,x+7,y+7),'#164a58'); ellipse((x-3.1,y-3.1,x+3.1,y+3.1),'#f4d491'); ellipse((x-.8,y-2,x+.7,y-.5),'#fff5cf')
curve([T(p) for p in [(405,17),(433,18),(467,8),(481,-7)]],'#123d4a',2)

# Front ring breaks into spray where the tail tears free.
for j in range(32):
    a=j/31
    pts=[ring(t,.91+a*.09) for t in [i*math.pi/320 for i in range(321)]]
    line(pts,('#a9e2cf' if j%8==0 else '#368d96'),.7)
for i in range(220):
    t=rng.uniform(0,math.tau)
    x,y=ring(t,rng.uniform(.94,1.04))
    if rng.random()<.6:
        height=rng.uniform(5,60)
        curve([(x,y),(x+8,y-height*.7),(x+17,y-height),(x+23,y-height*.85)],rng.choice(['#407e89','#7bbeb9','#d4e5c8']),rng.uniform(.4,1.2))
    else:
        rr=rng.uniform(.6,2.2); ellipse((x-rr,y-rr,x+rr,y+rr),'#a9d7ca')
# Airborne drops trace the upward arc, instead of filling the background.
for i in range(130):
    t=rng.random(); x=230+430*t+rng.gauss(0,37); y=570-370*t+rng.gauss(0,27)
    if mask.getpixel((int(max(0,min(1023,x))*S),int(max(0,min(1023,y))*S)))==0:
        rr=rng.uniform(.6,2); ellipse((x-rr,y-rr,x+rr,y+rr),'#92d6cf')

# A small warm sailboat in the dark lower sea establishes impossible scale.
for i in range(130):
    y=rng.uniform(875,1005); x=rng.uniform(30,994)
    line([(x,y),(x+rng.uniform(5,80),y-rng.uniform(0,2))],'#193749',.65)
poly([(586,904),(631,902),(619,913),(598,914)],'#d19d65')
line([(611,902),(611,850)],'#ecd6aa',1.4)
poly([(607,855),(585,894),(607,894)],'#f4e2b5')
poly([(615,864),(615,894),(633,894)],'#b8b697')
curve([(579,920),(603,925),(631,920),(643,917)],'#608486',1)

im=im.resize((W,W),Image.Resampling.LANCZOS)
im.save(Path(__file__).with_name('entry.png'),optimize=True,compress_level=9)
print('Rendered The Ocean Escapes')

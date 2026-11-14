#!/usr/bin/env python3
"""PERIHELION   Run: pip install pygame-ce && python perihelion.py"""
import math, random, sys
from types import SimpleNamespace as NS
import pygame as pg
from engine import *

W, H, SW = 1280, 720, 900
NAVY=(7,10,24); CY=(80,205,255); BL=(70,120,255); VI=(150,110,245); TX=(225,232,246); DM=(125,140,170)
GR=(80,225,150); YE=(255,205,90); RD=(255,90,100); SC=[GR,YE,(255,150,70),RD]
pg.init(); pg.display.set_caption("PERIHELION"); screen=pg.display.set_mode((W,H)); clock=pg.time.Clock()
_f={}
def F(n,b=False):
    if (n,b) not in _f: _f[(n,b)]=pg.font.SysFont("segoeui,helveticaneue,helvetica,arial",n,bold=b)
    return _f[(n,b)]
_ff={}
TITLE_FONT="trajanpro,cinzel,optima,copperplategothic,futura,gillsans,centurygothic,segoeuilight,helveticaneue,arial"
BODY_FONT="montserrat,futura,gillsans,centurygothic,bahnschrift,segoeuisemilight,segoeui,helveticaneue,arial"
def FF(fam,n,b=False):
    if (fam,n,b) not in _ff: _ff[(fam,n,b)]=pg.font.SysFont(fam,n,bold=b)
    return _ff[(fam,n,b)]
def T(s,t,n,col,x,y,a="l",b=False):
    if not t: return pg.Rect(x,y,0,0)
    im=F(n,b).render(t,True,col); r=im.get_rect()
    if a=="c": r.midtop=(x,y)
    elif a=="r": r.topright=(x,y)
    else: r.topleft=(x,y)
    s.blit(im,r); return r
def wrap(t,n,w,b=False):
    out=[];cur=""
    for wd in t.split():
        if F(n,b).size((cur+" "+wd).strip())[0]>w and cur: out.append(cur);cur=wd
        else: cur=(cur+" "+wd).strip()
    return out+[cur] if cur else out
def para(s,t,n,col,x,y,w,gap=3):
    for ln in wrap(t,n,w): T(s,ln,n,col,x,y); y+=n+gap+2
    return y
def lerp(a,b,t): return a+(b-a)*t
def lc(a,b,t): return tuple(int(lerp(a[i],b[i],clamp(t))) for i in range(3))
def sm(x): x=clamp(x); return x*x*(3-2*x)
def panel(r,al=150,col=(14,20,44),rad=14,edge=True):
    s=pg.Surface((r[2],r[3]),pg.SRCALPHA); pg.draw.rect(s,(*col,al),s.get_rect(),border_radius=rad)
    if edge: pg.draw.rect(s,(120,160,255,40),s.get_rect(),1,border_radius=rad); pg.draw.line(s,(170,205,255,70),(rad,1),(max(rad+1,r[2]-rad),1))
    screen.blit(s,(r[0],r[1]))
def bar(s,r,v,col,mark=None):
    pg.draw.rect(s,(25,32,60),r,border_radius=5); w=int(r[2]*clamp(v))
    if w>0: pg.draw.rect(s,col,(r[0],r[1],w,r[3]),border_radius=5)
    if mark is not None: pg.draw.line(s,TX,(r[0]+r[2]*mark,r[1]-2),(r[0]+r[2]*mark,r[1]+r[3]+2),1)
G=NS(scr="menu",mi=0,diff=1,cfg=default_cfg(),A=None,sim=None,fade=1.0,sel=("c",0),disp={},score=None,ctr=0.0,off=0.0)
clicks=[]; mp=(0,0)
G.mt=0.0; G.hv={}
def go(s):
    G.scr=s; G.fade=1.0
    if s=="menu": G.mt=0.0
def hit(r): return pg.Rect(r).collidepoint(mp)
def btn(r,label,col=CY,on=True,size=17):
    h=hit(r) and on; r=pg.Rect(r); s=pg.Surface(r.size,pg.SRCALPHA)
    for yy in range(r.h):
        k=yy/r.h; pg.draw.line(s,(*col,int((70-40*k) if h else (36-22*k)) if on else 10),(0,yy),(r.w,yy))
    m=pg.Surface(r.size,pg.SRCALPHA); pg.draw.rect(m,(255,255,255,255),m.get_rect(),border_radius=10); s.blit(m,(0,0),special_flags=pg.BLEND_RGBA_MIN)
    pg.draw.rect(s,(*col,235 if h else 130 if on else 50),s.get_rect(),2 if h else 1,border_radius=10)
    if h: pg.draw.line(s,(255,255,255,110),(10,2),(r.w-10,2))
    screen.blit(s,r.topleft); T(screen,label,size,TX if on else DM,r.centerx,r.centery-size//2-2,"c",True)
    return on and any(r.collidepoint(c) for c in clicks)
def abtn(r,d,col=CY):
    ok=btn(r,"",col,True,15); cx,cy=pg.Rect(r).center; k=5*d
    pg.draw.polygon(screen,TX,[(cx+k,cy),(cx-k,cy-6),(cx-k,cy+6)]); return ok
def glow(s,t,n,col,x,y):
    im=F(n,True).render(t,True,col)
    for o in (4,2):
        g=im.copy(); g.set_alpha(28 if o==4 else 55)
        for dx,dy in((-o,0),(o,0),(0,-o),(0,o)): s.blit(g,(x+dx,y+dy))
    s.blit(im,(x,y))
STARS=[(random.random()*W,random.random()*H,random.choice((.15,.3,.6)),random.random()*6) for _ in range(220)]
def stars(s,ox=0.0,oy=0.0,w=W,h=H,a=1.0):
    for x,y,z,p in STARS:
        v=int((120+110*math.sin(G.ctr*1.5+p))*a*(.5+z)); v=clamp(v,0,255)
        s.set_at((int((x-ox*z)%w),int((y-oy*z)%h)),(v,v,min(255,v+20)))
        if z>.5: s.set_at((int((x-ox*z)%w)+1,int((y-oy*z)%h)),(v//2,v//2,v//2))
def planet(s,cx,cy,r,col,atmo=None):
    if r<2: pg.draw.circle(s,col,(int(cx),int(cy)),2); return
    if atmo:
        g=pg.Surface((int(r*2.6),int(r*2.6)),pg.SRCALPHA)
        for k in range(8): pg.draw.circle(g,(*atmo,14),(g.get_width()//2,g.get_height()//2),int(r*(1.3-k*.04)))
        s.blit(g,(cx-g.get_width()//2,cy-g.get_height()//2))
    pg.draw.circle(s,tuple(int(c*.35) for c in col),(int(cx),int(cy)),int(r))
    for k in range(1,12):
        f=k/12; pg.draw.circle(s,tuple(min(255,int(c*(.4+.75*f))) for c in col),(int(cx-.32*r*f),int(cy-.32*r*f)),max(1,int(r*(1-.55*f))))
def rot(pts,x,y,ang,sc=1.0):
    c,s=math.cos(ang),math.sin(ang); return [(x+(px*c-py*s)*sc,y+(px*s+py*c)*sc) for px,py in pts]
def ship(s,x,y,ang,sc,open_,dim):
    k=.35 if dim else 1; col=lambda c:tuple(int(v*k) for v in c)
    if open_:
        for sg in (-1,1):
            pg.draw.polygon(s,col((60,110,220)),rot([(-8,sg*9),(-2,sg*9),(-2,sg*36),(-8,sg*36)],x,y,ang,sc))
            for t in (16,23,30): pg.draw.line(s,col((25,55,140)),*rot([(-8,sg*t),(-2,sg*t)],x,y,ang,sc))
            pg.draw.line(s,col((25,55,140)),*rot([(-5,sg*9),(-5,sg*36)],x,y,ang,sc))
    pg.draw.polygon(s,col((205,210,225)),rot([(-12,-8),(10,-8),(17,0),(10,8),(-12,8)],x,y,ang,sc))
    pg.draw.polygon(s,col((235,195,85)),rot([(-9,-8),(-3,-8),(-3,8),(-9,8)],x,y,ang,sc))
    dx,dy=rot([(3,-13)],x,y,ang,sc)[0]; pg.draw.line(s,col((150,155,170)),*rot([(3,-8),(3,-13)],x,y,ang,sc)); pg.draw.circle(s,col((225,230,240)),(int(dx),int(dy)),max(2,int(4*sc)))
    pg.draw.polygon(s,col((120,130,160)),rot([(-12,-5),(-18,-7),(-18,7),(-12,5)],x,y,ang,sc))
    if not dim: pg.draw.circle(s,CY,(int(x+6*sc*math.cos(ang)),int(y+6*sc*math.sin(ang))),max(1,int(2*sc)))
def lander(s,x,y,sc,dim=False):
    k=.4 if dim else 1; col=lambda c:tuple(int(v*k) for v in c)
    for sg in (-1,1):
        pg.draw.line(s,col((170,175,190)),(x+sg*14*sc,y+2*sc),(x+sg*28*sc,y+24*sc),max(2,int(2*sc))); pg.draw.line(s,col((170,175,190)),(x+sg*24*sc,y+24*sc),(x+sg*34*sc,y+24*sc),max(2,int(2*sc)))
    pg.draw.polygon(s,col((205,205,215)),[(x-14*sc,y-16*sc),(x+14*sc,y-16*sc),(x+19*sc,y+4*sc),(x-19*sc,y+4*sc)])
    pg.draw.polygon(s,col((90,110,200)),[(x-10*sc,y-16*sc),(x+10*sc,y-16*sc),(x+6*sc,y-26*sc),(x-6*sc,y-26*sc)])
    pg.draw.circle(s,col(CY),(int(x),int(y-6*sc)),int(3*sc))
def poly(s,pts,col,x,y,ang,sc=1.0): pg.draw.polygon(s,col,rot(pts,x,y,ang,sc))
def seg(s,a,b,col,x,y,ang,w=1,sc=1.0): pg.draw.line(s,col,*rot([a,b],x,y,ang,sc),w)
def nozzle(s,cx,x,y,ang):
    poly(s,[(cx-4,-6),(cx+4,-6),(cx+7,17),(cx-7,17)],(100,104,122),x,y,ang); poly(s,[(cx-6,12),(cx+6,12),(cx+7,17),(cx-7,17)],(38,40,52),x,y,ang)
def booster(s,tx,ty,ang):
    x,y=rot([(0,-17)],tx,ty,ang)[0]
    for sg in (-1,1):
        poly(s,[(sg*19,-8),(sg*42,14),(sg*42,21),(sg*19,-38)],(60,68,92),x,y,ang); poly(s,[(sg*19,-8),(sg*35,9),(sg*35,12),(sg*19,-24)],(105,118,152),x,y,ang)
        poly(s,[(sg*19,-100),(sg*28,-100),(sg*28,-108),(sg*19,-108)],(70,76,96),x,y,ang)
    for cx in (-11,0,11): nozzle(s,cx,x,y,ang)
    poly(s,[(-19,0),(19,0),(19,-120),(-19,-120)],(230,233,240),x,y,ang); poly(s,[(-19,0),(-11,0),(-11,-120),(-19,-120)],(252,252,255),x,y,ang)
    poly(s,[(8,0),(19,0),(19,-120),(8,-120)],(158,166,188),x,y,ang); poly(s,[(14,0),(19,0),(19,-120),(14,-120)],(120,128,152),x,y,ang)
    poly(s,[(-19,0),(19,0),(19,-9),(-19,-9)],(46,50,64),x,y,ang); poly(s,[(-19,-112),(19,-112),(19,-120),(-19,-120)],(42,46,60),x,y,ang)
    poly(s,[(-19,-60),(19,-60),(19,-67),(-19,-67)],(40,150,225),x,y,ang)
    for yy in (-26,-42,-80,-98): seg(s,(-19,yy),(19,yy),(188,194,208),x,y,ang)
    for xx in (-4,5): seg(s,(xx,-12),(xx,-108),(205,210,222),x,y,ang)
    cx,cy=rot([(0,-88)],x,y,ang)[0]; pg.draw.circle(s,(40,150,225),(int(cx),int(cy)),9,2); pg.draw.circle(s,(235,235,245),(int(cx),int(cy)),3)
    for yy in (-14,-112): 
        for xx in range(-15,16,6): px,py=rot([(xx,yy)],x,y,ang)[0]; s.set_at((int(px),int(py)),(120,126,145))
def ustage(s,x,y,ang,sc=1.0,fair=True):
    poly(s,[(-5,0),(5,0),(8,10),(-8,10)],(100,104,122),x,y,ang,sc)
    poly(s,[(-16,0),(16,0),(16,-58),(-16,-58)],(222,225,234),x,y,ang,sc); poly(s,[(-16,0),(-9,0),(-9,-58),(-16,-58)],(250,250,255),x,y,ang,sc); poly(s,[(8,0),(16,0),(16,-58),(8,-58)],(158,166,188),x,y,ang,sc)
    poly(s,[(-16,-40),(16,-40),(16,-46),(-16,-46)],(205,60,72),x,y,ang,sc); poly(s,[(-16,-4),(16,-4),(16,-9),(-16,-9)],(46,50,64),x,y,ang,sc)
    if fair:
        poly(s,[(-16,-58),(-15,-72),(-12,-88),(-7,-100),(0,-108),(7,-100),(12,-88),(15,-72),(16,-58)],(244,244,250),x,y,ang,sc)
        poly(s,[(-16,-58),(-9,-58),(-5,-92),(0,-108),(-7,-100),(-12,-88),(-15,-72)],(255,255,255),x,y,ang,sc); poly(s,[(9,-58),(16,-58),(15,-72),(12,-88),(7,-100),(3,-90)],(170,178,198),x,y,ang,sc)
        poly(s,[(0,-108),(-3,-101),(3,-101)],(210,62,72),x,y,ang,sc); seg(s,(0,-58),(0,-100),(185,192,208),x,y,ang,1,sc)
def plume(s,x,y,ang,L,w):
    for col,k in (((255,110,30),1),((255,175,60),.72),((255,238,175),.4)): poly(s,[(-w*k,0),(w*k,0),(w*.35*k,L*k),(0,L*(k+.25)),(-w*.35*k,L*k)],col,x,y,ang)
def tower(s,x,gy,arms):
    for yy in range(0,300,30):
        pg.draw.line(s,(88,96,118),(x,gy-yy),(x+18,gy-yy-30)); pg.draw.line(s,(88,96,118),(x+18,gy-yy),(x,gy-yy-30)); pg.draw.line(s,(112,120,142),(x,gy-yy),(x+18,gy-yy),2)
    pg.draw.line(s,(125,133,155),(x,gy),(x,gy-300),3); pg.draw.line(s,(125,133,155),(x+18,gy),(x+18,gy-300),3)
    if arms:
        for h in (110,190,250): pg.draw.rect(s,(105,112,135),(x-52,gy-h,52,6))
    pg.draw.circle(s,RD if int(G.ctr*2)%2 else (90,20,30),(x+9,gy-306),4)
def rocket(s,x,base,tilt,sep):
    ux,uy=rot([(0,-137)],x,base,tilt)[0]; ustage(s,ux,uy,tilt)
    if not sep: booster(s,x,base,tilt)
class Sim:
    PH=[("COUNTDOWN",10),("ASCENT",16),("DEPLOYMENT",4),("TRANSIT",24),("ARRIVAL",10),("TERMINAL",12)]
    def __init__(s,A): s.A=A; s.reset()
    def reset(s):
        A=s.A;M=A.M;s.ph=0;s.t=0.;s.met=-10.;s.running=False;s.speed=1;s.log=[];s.parts=[];s.failed=False;s.fail_met=0.;s.dead=False;s.boomed=False;s.done=False;s.shake=0.;s.pos=(SW/2,500);s.layer=pg.Surface((SW,H),pg.SRCALPHA)
        e=[(0,0,"Terminal count started: T-10","i"),(0,.8,"Main engine ignition","i"),(1,0,"LIFTOFF: all engines nominal","g"),(1,.25,"Max-Q passed","i"),(1,.45,"Stage separation confirmed","g"),(1,.8,"Fairing jettison","i"),
           (2,0,"Spacecraft deployed","g"),(2,.5,"Solar arrays unfolding","i"),(3,0,f"Injection burn complete: trajectory toward {M.dest}","g"),(3,.45,"Trajectory correction maneuver","i"),(4,0,f"Approaching {M.dest}","i"),(4,.5,"Arrival burn started","i")]
        e+=[(5,0,"Atmospheric entry interface" if M.atmo else "Descent initiated","i"),(5,.5,"Landing burn ignition","i"),(5,.95,"TOUCHDOWN: SUCCESSFUL LANDING","g")] if M.land else [(5,0,"Orbit insertion burn started","i"),(5,.9,"ORBIT INSERTION SUCCESSFUL","g")]
        if A.anomalies: e.append((3,.6,"ANOMALY: marginal "+", ".join(A.anomalies)+" performance","w"))
        if A.fail: p,f=STG[A.fail]; e=[x for x in e if (x[0],x[1])<(p,f)]+[(p,f,"FAILURE: "+FAILTXT[A.fail],"r")]
        else: e.append((5,.99,"MISSION COMPLETE: data returning to Earth","g"))
        s.ev=sorted(e,key=lambda x:(x[0],x[1]))
    def frac(s): return s.t/s.PH[min(s.ph,5)][1] if s.ph<6 else 1
    def prog(s): return 1 if s.ph>=6 else 0 if s.ph<3 else (s.ph-3+s.frac())/3
    def boom(s):
        s.boomed=s.dead=True; s.shake=1.6
        for _ in range(170): a=random.random()*6.28; v=random.random()*260; s.parts.append([s.pos[0],s.pos[1],math.cos(a)*v,math.sin(a)*v-40,random.uniform(.6,1.8),1.8,random.uniform(4,13),"x",False])
    def step(s,dt):
        if s.done: return
        s.t+=dt; s.met+=dt
        while s.ph<6 and s.t>=s.PH[s.ph][1]: s.t-=s.PH[s.ph][1]; s.ph+=1
        cur=(s.ph,s.frac() if s.ph<6 else 0)
        while s.ev and cur>=(s.ev[0][0],s.ev[0][1]):
            _,_,tx,k=s.ev.pop(0); s.log.append((s.met,tx,k))
            if k=="r":
                s.failed=True; s.fail_met=s.met; s.shake=.8
                if s.A.fail in("thermal","nav"): s.boom()
        if s.failed and s.A.fail=="mass" and not s.boomed and s.met>=s.fail_met+1.8: s.boom()
        if s.ph>=6 or (s.failed and s.met>=s.fail_met+8): s.done=True; s.running=False
    def update(s,dt):
        if s.running: s.step(min(dt,.05)*s.speed)
    def skip(s):
        if not s.done: s.t=s.PH[s.ph][1]; s.step(1e-4)
    def tele(s):
        A=s.A;P=s.prog();need=min(1,A.need_dv/max(1,A.dv))
        cur=lambda p:.35*sm(p/.1)+.65*sm((p-.55)/.45)
        fuel=1-need*cur(P)
        if s.failed and A.fail=="dv": fuel=0
        pw=min(1,A.gen/A.use)
        if s.failed and A.fail=="power": pw=max(0,1-(s.met-s.fail_met)/4)
        lost=s.failed and A.fail in("comms","power")
        return dict(P=P,dist=(1-P)*A.M.dist,fuel=fuel,pw=pw,integ=0 if s.boomed else 100,comm="LOST" if lost else "NOMINAL")
    def spawn(s,x,y,vx,vy,life,size,kind,world=False): 
        if len(s.parts)<1500: s.parts.append([x,y,vx,vy,life,life,size,kind,world])
    def draw_parts(s,dt,cam):
        L=s.layer; L.fill((0,0,0,0)); keep=[]
        for p in s.parts:
            p[0]+=p[2]*dt; p[1]+=p[3]*dt; p[4]-=dt
            if p[4]<=0: continue
            a=1-p[4]/p[5]; k=p[7]
            if k=="f": c=(255,int(230-150*a),int(120-100*a),int(230*(1-a)))
            elif k=="s": c=(110,110,122,int(120*(1-a))); p[6]+=dt*14
            elif k=="x": c=(255,int(200-170*a),int(70*(1-a)),int(255*(1-a)))
            elif k=="d": c=(160,150,140,int(130*(1-a))); p[6]+=dt*10
            else: c=(255,150,60,int(160*(1-a)))
            pg.draw.circle(L,c,(int(p[0]),int(p[1]+(cam if p[8] else 0))),max(1,int(p[6]*(1-.5*a)))); keep.append(p)
        s.parts=keep; return L
def render(sim,dt):
    S=pg.Surface((SW,H)); A=sim.A;M=A.M;ph=sim.ph;fr=sim.frac();P=sim.prog();step=dt*min(sim.speed,3) if sim.running else 0
    cam=0; fail=sim.failed and A.fail; k=min(ph,5)
    if ph<=1:
        u=0 if ph==0 else fr*fr; alt=u*2500; rise=124*min(1,u*5); gy=600+alt-rise; rb=594-rise; cam=gy-600
        S.fill(lc((120,170,235),(5,8,22),u*1.4))
        if u>.2: stars(S,0,-alt*.05,SW,H,clamp(u*1.5))
        if gy<H+20:
            pg.draw.rect(S,(28,48,36),(0,gy,SW,H)); pg.draw.rect(S,(120,120,130),(SW/2-130,gy-6,260,10)); tower(S,SW/2+66,gy,ph==0 or fr<.04)
        sep=ph==1 and fr>.45; tilt=0
        if fail=="mass" and not sim.boomed: tilt=(sim.met-sim.fail_met)*.28
        x=SW/2-(math.sin(tilt)*0 if tilt else 0); sim.pos=(x+math.sin(tilt)*90,rb-math.cos(tilt)*90)
        if not sim.dead:
            on=(ph==0 and fr>.8) or ph==1; fx,fy=x,rb+4
            if sep: fx,fy=rot([(0,-127)],x,rb,tilt)[0]
            if on:
                if sep: plume(S,fx,fy,tilt,38+random.random()*16,8)
                else: plume(S,x,rb+2,tilt,(18 if ph==0 else 70)+random.random()*22,24)
            rocket(S,x,rb,tilt,sep)
            if sep:
                dtp=(fr-.45)*16; booster(S,x+dtp*8,rb+dtp*dtp*14,dtp*.3)
            if sim.running and on:
                n=int(8*sim.speed**.5)
                for _ in range(n): sim.spawn(fx+random.uniform(-9,9),fy,random.uniform(-40,40),random.uniform(240,380),random.uniform(.3,.6),random.uniform(6,12),"f")
                if u<.15 and sim.running:
                    for _ in range(3): sim.spawn(x+random.uniform(-90,90),592,random.uniform(-120,120),random.uniform(-30,-5),random.uniform(1.5,2.8),random.uniform(12,22),"s",True)
            if fail=="mass" and sim.running: sim.spawn(x,rb-100,random.uniform(-30,30),random.uniform(20,80),1.2,8,"s")
        if ph==0: T(S,"T-%d"%max(0,math.ceil(10-sim.t)),72,TX,SW/2,120,"c",True)
    else:
        S.fill(NAVY); stars(S,P*220,P*40,SW,H)
        q=clamp(P/.8333); er=lerp(300,45,clamp(P*5)); ex,ey=lerp(140,90,clamp(P*5)),lerp(660,500,clamp(P*5))
        if ph<5 or fail in ("orbit","dv","power","comms"):
            planet(S,ex,ey,er,(50,110,210),(90,150,255))
            tr=4+246*q**2.4; tx,ty=lerp(690,450,q**2.4),lerp(200,360,q**2.4); planet(S,tx,ty,tr,M.col,(160,170,190) if M.atmo else None)
            E=(190,560); C=(260,140); Q=(tx-tr-35,ty-tr*.3)
            bz=lambda t:((1-t)**2*E[0]+2*t*(1-t)*C[0]+t*t*Q[0],(1-t)**2*E[1]+2*t*(1-t)*C[1]+t*t*Q[1])
            for i in range(0,41): 
                bx,by=bz(i/40); pg.draw.circle(S,CY if i/40<=q else (50,60,95),(int(bx),int(by)),2 if i/40<=q else 1)
            x,y=bz(q); x2,y2=bz(min(1,q+.01)); ang=math.atan2(y2-y,x2-x) if q<1 else 0
            if ph==2: x,y,ang=200+fr*60,560-fr*30,-.7; q=0
            if fail in("orbit","dv"): 
                d=sim.met-sim.fail_met; x+=d*(30 if fail=="orbit" else 70); y-=d*(25 if fail=="orbit" else 35)
            sim.pos=(x,y); dim=fail=="power"
            if ph==2 and not sim.dead:
                dp=fr*10; ustage(S,x-60-dp*3,y+30+dp*3,.5+fr*1.5,.7,False)
            if not sim.dead: ship(S,x,y,ang,1.1,ph>=2 and fr>.5 or ph>2,dim)
            fl=((ph==3 and fr<.12) or (ph==4 and fr>.5)) and not dim and not(fail=="dv")
            if fl and sim.running and not sim.dead:
                for _ in range(3): sim.spawn(x-18*math.cos(ang),y-18*math.sin(ang),-math.cos(ang)*160,-math.sin(ang)*160,.4,5,"f")
        elif M.land:
            d=fr/.8 if fail=="nav" else fr/.95; gyl=600
            S.fill(lc((190,110,70),(15,10,25),fr*1.5) if M.atmo else (4,5,12))
            if not M.atmo: stars(S,0,0,SW,H)
            pg.draw.rect(S,tuple(int(c*.45) for c in M.col),(0,gyl,SW,H)); pg.draw.ellipse(S,tuple(int(c*.35) for c in M.col),(120,gyl+30,160,30)); pg.draw.ellipse(S,tuple(int(c*.35) for c in M.col),(560,gyl+60,220,36))
            ly=-40+(gyl-32+40)*clamp(d)**1.3
            sim.pos=(SW/2,ly); 
            if not sim.dead: lander(S,SW/2,ly,1.6,False)
            if sim.running and not sim.dead:
                if M.atmo and fr<.5:
                    for _ in range(5): sim.spawn(SW/2+random.uniform(-25,25),ly+30,random.uniform(-30,30),random.uniform(-160,-60),.5,9,"h")
                if .5<fr<.95 and fail!="nav":
                    for _ in range(5): sim.spawn(SW/2+random.uniform(-6,6),ly+14,random.uniform(-30,30),random.uniform(220,340),.35,8,"f")
                if ly>520 and fail!="nav":
                    for _ in range(4): sim.spawn(SW/2,gyl+2,random.choice((-1,1))*random.uniform(80,260),random.uniform(-20,0),1.4,10,"d")
        else:
            planet(S,450,360,250,M.col); th=fr*9.4; x,y=450+math.cos(th)*350,360+math.sin(th)*90
            pg.draw.ellipse(S,(70,90,140),(100,270,700,180),1)
            sim.pos=(x,y)
            if not sim.dead: ship(S,x,y,th+1.57,1.2,True,False)
    L=sim.draw_parts(step,cam); S.blit(L,(0,0))
    if sim.shake>0: sim.shake=max(0,sim.shake-dt*1.2)
    T(S,Sim.PH[k][0] if ph<6 else "COMPLETE",15,CY,24,20,"l",True)
    if fail and A.fail=="comms":
        for _ in range(14):
            y0=random.randint(0,H); pg.draw.line(S,(200,200,220),(random.randint(0,SW),y0),(random.randint(0,SW),y0),1)
        T(S,"SIGNAL LOST",44,RD,SW/2,300,"c",True)
    if fail:
        if int(G.ctr*3)%2==0: pg.draw.rect(S,RD,(0,0,SW,H),6)
        T(S,"MISSION FAILURE",40,RD,SW/2,60,"c",True); T(S,FAILTXT[A.fail][:95],15,TX,SW/2,112,"c")
    elif sim.done or (ph==5 and fr>.9):
        T(S,("SUCCESSFUL LANDING" if M.land else "ORBIT INSERTION SUCCESSFUL") if (ph>=5) else "",44,GR,SW/2,70,"c",True)
    if not sim.running and not sim.done: 
        v=pg.Surface((SW,H),pg.SRCALPHA); v.fill((0,0,0,90)); S.blit(v,(0,0)); T(S,"PRESS START SIMULATION" if sim.met<-9.9 else "PAUSED",30,TX,SW/2,330,"c",True)
    o=(random.uniform(-1,1)*sim.shake*9,random.uniform(-1,1)*sim.shake*9) if sim.shake>0 else (0,0)
    screen.fill(NAVY); screen.blit(S,o)
def scr_sim(dt):
    sim=G.sim; sim.update(dt); render(sim,dt); tl=sim.tele(); x=SW+20
    panel((SW,0,W-SW,H),200,(8,12,30),0,False); T(screen,"MISSION TELEMETRY",16,CY,x,16,"l",True); T(screen,f"{sim.A.M.name}",13,DM,x,40)
    y=70
    for lab,v,col,txt in [("Progress",tl["P"],CY,f"{tl['P']*100:.0f}%"),("Fuel",tl["fuel"],YE if tl["fuel"]<.3 else GR,f"{tl['fuel']*100:.0f}%"),("Power",tl["pw"],RD if tl["pw"]<.9 else GR,f"{tl['pw']*100:.0f}%"),("Integrity",tl["integ"]/100,GR if tl["integ"] else RD,f"{tl['integ']}%")]:
        T(screen,lab,13,DM,x,y); T(screen,txt,13,TX,W-20,y,"r"); bar(screen,(x,y+18,340,8),v,col); y+=40
    d=tl["dist"]; T(screen,"Distance to target",13,DM,x,y); T(screen,f"{d:,.0f} km",13,TX,W-20,y,"r"); y+=24
    T(screen,"Comms",13,DM,x,y); T(screen,tl["comm"],13,GR if tl["comm"]=="NOMINAL" else RD,W-20,y,"r"); y+=28
    T(screen,"EVENT LOG",13,CY,x,y,"l",True); y+=22; pg.draw.line(screen,(40,55,100),(x,y),(W-20,y)); y+=6
    for m,tx,k in sim.log[-9:]:
        yy=y; col={"g":GR,"r":RD,"w":YE}.get(k,TX); T(screen,f"T{'-' if m<0 else '+'}{abs(m):05.1f}",11,DM,x,yy+1)
        for ln in wrap(tx,12,285)[:2]: T(screen,ln,12,col,x+62,yy); yy+=14
        y=yy+3
    by=H-150
    if btn((x,by,110,34),"PAUSE" if sim.running else "RESUME" if sim.met>-9.9 else "START",GR,not sim.done) : sim.running=not sim.running
    if btn((x+115,by,110,34),"RESTART",YE): sim.reset()
    if btn((x+230,by,110,34),"SKIP >>",VI,not sim.done): sim.skip(); sim.running=True
    for i,sp in enumerate((1,2,5,10)):
        if btn((x+i*85,by+42,80,30),f"{sp}x",CY if sim.speed==sp else DM,True,15): sim.speed=sp
    if btn((x,by+80,165,34),"DESIGN",BL): sim.running=False; go("design")
    if btn((x+175,by+80,165,34),"DEBRIEF",GR,sim.done or bool(sim.failed)): sim.running=False; G.score=score(sim.A); go("debrief")
def ratios(A):
    C=A.C;M=A.M; r={"mass":A.cap/A.wet,"orbit":1.5 if A.O is ORB[M.orbit] else 0,"dv":A.dv/A.need_dv,"power":A.gen/A.use,"comms":(A.store+A.down*M.days)/(A.data*M.days) if A.data else 1.5,
       "thermal":1.5 if C[6][5]>=M.therm else 0,"nav":1.5 if C[8][5]>=1 else 0,"budget":A.budget/A.cost,"obj":A.cov*1.5,"rel":A.rel/.75}
    return r
NEED={"Structure":("Without a strong frame mass rises or reliability falls.","Heavy frame cuts rocket margin; light frame hurts reliability."),"Propulsion":("It sets how far fuel can take you.","Weak Isp means fuel runs out before arrival."),"Solar Panels":("Powers everything.","Too small and systems brown out. Too large wastes mass."),"Batteries":("Bridges eclipses and spikes.","Too small and brief dips shut systems down."),"Antenna":("Sends data home.","Low bandwidth lets data overflow storage."),"Computer":("Stores and processes science.","Small storage overflows on data-heavy missions."),"Thermal":("Shields against entry heat and radiation.","Too weak and the craft is lost on entry or arrival."),"Attitude Control":("Points the craft.","Poor pointing reduces science return."),"Navigation":("Guides arrival.","No terminal guidance means a crash on landing."),"Fuel Load":("Fuel is delta-v.","Too little and the arrival burn fails; too much adds mass.")}
def scr_design(dt):
    M=MISSIONS[G.mi]; cfg=G.cfg; A=analyze(M,cfg,G.diff); G.A=A; T(screen,"MISSION DESIGN WORKSPACE",22,TX,70,20,"l",True); T(screen,f"{M.name}  |  {DIFF[G.diff][0]}",14,DM,70,50)
    if abtn((20,18,40,34),-1,DM): go("missions")
    if btn((W-290,16,270,40),"RUN FEASIBILITY ANALYSIS",GR): go("report")
    rows=[("c",i) for i in range(10)]+[("o",0),("l",0)]; y=96
    for kind,i in rows:
        r=pg.Rect(20,y,420,36); panel(r,110 if G.sel!=(kind,i) else 190)
        if hit(r): G.sel=(kind,i)
        if kind=="c": lab,opts,cur=CAT[i][0],CAT[i][1],cfg["c"][i]; nm=opts[cur][0]
        elif kind=="o": lab,opts,cur,nm="Orbit Profile",ORB,cfg["o"],ORB[cfg["o"]][0]
        else: lab,opts,cur,nm="Launch Vehicle",LAUNCH,cfg["l"],LAUNCH[cfg["l"]][0]
        T(screen,lab,12,DM,r.x+12,r.y+4); T(screen,nm,15,TX,r.x+12,r.y+17,"l",True)
        for dlt,bx in((-1,r.right-74),(1,r.right-38)):
            if abtn((bx,r.y+5,30,26),dlt):
                n=(cur+dlt)%len(opts)
                if kind=="c": cfg["c"][i]=n
                elif kind=="o": cfg["o"]=n
                else: cfg["l"]=n
        y+=40
    T(screen,"SCIENTIFIC INSTRUMENTS",13,CY,455,76,"l",True); y=96
    for i,ins in enumerate(INS):
        r=pg.Rect(455,y,380,36); on=i in cfg["ins"]; panel(r,190 if on else 90,(20,50,90) if on else (14,20,44))
        if hit(r): G.sel=("i",i)
        pg.draw.rect(screen,CY if on else DM,(r.x+10,r.y+10,17,17),2,border_radius=4)
        if on: pg.draw.lines(screen,GR,False,[(r.x+13,r.y+19),(r.x+18,r.y+24),(r.x+25,r.y+13)],3)
        T(screen,ins[0],14,TX if on else DM,r.x+38,r.y+9,"l",True); T(screen,f"{ins[1]}kg {-ins[3]}W ${ins[2]}M",12,DM,r.right-10,r.y+11,"r")
        if any(r.collidepoint(c) for c in clicks): cfg["ins"]^={i}
        y+=40
    panel((455,y+4,380,H-y-20),150); k,i=G.sel; ix=455+14; iy=y+16
    if k=="c": nm,opt=CAT[i][1][cfg["c"][i]][0],CAT[i][1][cfg["c"][i]]; T(screen,CAT[i][0].upper(),13,CY,ix,iy,"l",True); iy=para(screen,CAT[i][2],13,TX,ix,iy+22,350); T(screen,f"{nm}: {opt[1]} kg, ${opt[2]}M, {opt[3]:+} W, reliability {opt[4]*100:.1f}%",12,DM,ix,iy+4); iy=para(screen,"Why: "+NEED[CAT[i][0]][0],13,TX,ix,iy+26,350); para(screen,"If insufficient: "+NEED[CAT[i][0]][1],13,YE,ix,iy,350)
    elif k=="i": ins=INS[i]; T(screen,ins[0].upper(),13,CY,ix,iy,"l",True); iy=para(screen,ins[7],13,TX,ix,iy+22,350); iy=para(screen,f"Contributes to: {', '.join(ins[5])}. Makes {ins[4]} GB/day, science value {ins[6]}.",13,DM,ix,iy+4,350); para(screen,"This mission requires: "+", ".join(M.req),13,YE,ix,iy+4,350)
    elif k=="o": T(screen,"ORBIT PROFILE",13,CY,ix,iy,"l",True); iy=para(screen,ORB[cfg["o"]][2],13,TX,ix,iy+22,350); para(screen,f"Capacity multiplier x{ORB[cfg['o']][1]}. Hint for {M.dest}: {ORB[M.orbit][0]}.",13,YE,ix,iy+4,350)
    else: L=LAUNCH[cfg["l"]]; T(screen,"LAUNCH VEHICLE",13,CY,ix,iy,"l",True); para(screen,f"{L[0]}: {L[1]} kg to LEO, ${L[2]}M, reliability {L[3]*100:.0f}%. Delivered mass shrinks with orbit energy, so check capacity on your chosen profile.",13,TX,ix,iy+22,350)
    panel((850,70,410,H-90),150); T(screen,"LIVE ENGINEERING DASHBOARD",13,CY,866,82,"l",True); rt=ratios(A); y=108
    T(screen,f"Mass {A.wet:.0f} kg  |  Capacity {A.cap:.0f} kg  |  Cost ${A.cost:.0f}M",12,DM,866,y); y+=24
    for c in A.checks:
        d=G.disp.setdefault(c["k"],0.0); G.disp[c["k"]]=d+(clamp(rt[c["k"]]/1.5)-d)*min(1,dt*8)
        T(screen,c["name"],12,TX,866,y); T(screen,c["val"],11,DM,1245,y+1,"r"); bar(screen,(866,y+17,380,7),G.disp[c["k"]],SC[c["st"]],.667); y+=32
    T(screen,f"{A.cls}  ({A.fscore}%)",16,SC[3 if "NOT" in A.cls else 2 if "RISK" in A.cls else 1 if "WARN" in A.cls else 0],866,y+4,"l",True); y+=34
    for c in sorted([c for c in A.checks if c["st"]],key=lambda c:-c["st"])[:3]: y=para(screen,c["msg"],12,SC[c["st"]],866,y,380,1)+2
def scr_missions(dt):
    T(screen,"MISSION SELECTION",26,TX,70,24,"l",True)
    if abtn((20,22,40,34),-1,DM): go("menu")
    for i,M in enumerate(MISSIONS):
        r=pg.Rect(30,86+i*92,400,84); panel(r,190 if i==G.mi else 100,(22,40,90) if i==G.mi else (14,20,44)); T(screen,M.name,18,TX,r.x+16,r.y+10,"l",True); T(screen,f"{M.dest}  |  {'Landing' if M.land else 'Orbiter'}  |  ${M.budget}M",13,DM,r.x+16,r.y+38); T(screen,M.diff,12,CY,r.x+16,r.y+58)
        if any(r.collidepoint(c) for c in clicks): G.mi=i
    M=MISSIONS[G.mi]; panel((460,86,790,552),150); x=486; T(screen,M.name.upper(),24,CY,x,104,"l",True); y=para(screen,M.desc,16,TX,x,146,730)
    y=para(screen,"Scientific objective: "+M.sci,15,TX,x,y+8,730); y=para(screen,f"Destination: {M.dest}   Duration: {M.days} days   Base budget: ${M.budget}M   Required delta-v: {M.dv} m/s",14,DM,x,y+8,730)
    y=para(screen,"Required observations: "+", ".join(M.req),14,YE,x,y+8,730); y=para(screen,"Engineering challenge: "+M.chal,14,YE,x,y+8,730); y=para(screen,f"Correct orbit profile: {ORB[M.orbit][0]}. Design the craft, then run the feasibility analysis.",14,DM,x,y+8,730)
    T(screen,"DIFFICULTY",13,CY,x,470,"l",True)
    for i,d in enumerate(DIFF):
        if btn((x+i*150,494,140,36),d[0],CY if i==G.diff else DM): G.diff=i
    T(screen,f"Budget x{DIFF[G.diff][1]}  |  Requirements x{DIFF[G.diff][2]}",13,DM,x,540)
    if btn((x,572,250,44),"BEGIN DESIGN",GR,True,18): G.cfg=default_cfg(); G.disp={}; go("design")
def scr_report(dt):
    A=G.A; col=SC[3 if "NOT" in A.cls else 2 if "RISK" in A.cls else 1 if "WARN" in A.cls else 0]
    T(screen,"MISSION FEASIBILITY REPORT",24,TX,40,24,"l",True); T(screen,A.cls,40,col,40,64,"l",True); T(screen,f"Feasibility score {A.fscore}/100",16,DM,40,116)
    panel((40,150,1200,470),140); y=166
    for c in A.checks:
        T(screen,["PASS","WARN","RISK","FAIL"][c["st"]],13,SC[c["st"]],60,y,"l",True); T(screen,c["name"],14,TX,130,y,"l",True); T(screen,c["val"],12,DM,330,y+1); para(screen,c["msg"],12,TX if c["st"]==0 else SC[c["st"]],620,y,600,0); y+=44
    if btn((40,636,260,50),"BACK TO DESIGN",BL): go("design")
    if btn((320,636,360,50),"LAUNCH" if A.cls in("READY FOR LAUNCH","FEASIBLE WITH WARNINGS") else "LAUNCH ANYWAY (RISKY)",GR if A.cls=="READY FOR LAUNCH" else RD,True,18): G.sim=Sim(A); G.sim.speed=1; go("sim")
REAL={"Lunar Exploration":[("Apollo program (1969-1972)","Crewed landings that left seismometers on the Moon, much like your lander's seismic goal."),("Lunar Reconnaissance Orbiter (2009)","An orbiter that mapped the lunar surface in high detail to help plan future landings.")],
 "Mars Exploration":[("InSight (2018)","A Mars lander whose seismometer detected marsquakes, the same kind of science as your mission."),("Perseverance (2021)","A rover that entered the Martian atmosphere behind a heat shield and landed in Jezero crater.")],
 "Europa Ocean Discovery":[("Galileo (1989-2003)","A Jupiter orbiter whose magnetic field data pointed to a hidden ocean beneath Europa's ice."),("Europa Clipper (launched 2024)","A mission built to study Europa's ice shell and ocean through many close flybys, carrying radar.")],
 "Asteroid Research":[("NEAR Shoemaker (1996-2001)","The first spacecraft to orbit and then land on an asteroid, Eros."),("OSIRIS-REx (2016-2023)","Rendezvoused with asteroid Bennu, mapped it, and returned a sample to Earth in 2023.")],
 "Earth Observation":[("Landsat program (since 1972)","The longest continuous record of Earth's land surface as seen from space."),("Terra (1999)","An Earth observing satellite in polar orbit studying land, atmosphere and oceans.")],
 "Deep Space Exploration":[("Voyager 1 and 2 (1977)","Carry magnetometers and particle detectors; both have crossed into interstellar space."),("New Horizons (2006)","Flew past Pluto in 2015 and continues outward through the Kuiper Belt.")]}
STAGE_NAME={"mass":"launch mass margin","orbit":"choosing the right trajectory","power":"power margin","comms":"communications capacity","dv":"propellant margin","thermal":"thermal protection","nav":"terminal guidance"}
def scr_debrief(dt):
    A=G.A; why,good,recs=debrief(A); parts,tot=G.score; ok=A.fail is None
    T(screen,"MISSION DEBRIEF",24,TX,40,24,"l",True); T(screen,"MISSION SUCCESS" if ok else "MISSION FAILURE",40,GR if ok else RD,40,60,"l",True)
    T(screen,f"{tot} / 1000",36,CY,W-40,40,"r",True); panel((40,126,520,330),140); y=142
    for k,v in parts.items():
        m=int(k.split("(")[1][:-1]); T(screen,k,13,TX,60,y); T(screen,str(v),13,DM,540,y,"r"); bar(screen,(60,y+20,480,8),v/m,CY); y+=44
    panel((40,468,520,178),140); T(screen,"SIMILAR REAL NASA MISSIONS",13,CY,58,480,"l",True); y=502
    for nm,tx in REAL[A.M.name]: T(screen,nm,13,TX,58,y,"l",True); y=para(screen,tx,12,DM,58,y+17,484,1)+3
    para(screen,"Your design reached its goal, as these missions did." if ok else f"Your mission failed on {STAGE_NAME[A.fail]}, which real teams spend enormous effort verifying.",12,GR if ok else YE,58,y+2,484,1)
    panel((580,126,660,520),140); x=600; y=para(screen,why,15,GR if ok else RD,x,144,620); T(screen,"WHAT WENT RIGHT",13,GR,x,y+8,"l",True); y+=30
    for g in good[:5]: y=para(screen,"+ "+g,12,TX,x,y,620,0)
    T(screen,"RECOMMENDATIONS",13,YE,x,y+8,"l",True); y+=30
    for r in recs[:5]: y=para(screen,"- "+r,12,TX,x,y,620,0)
    if btn((40,662,250,44),"REDESIGN",BL): go("design")
    if btn((300,662,260,44),"RUN AGAIN",GR): G.sim=Sim(A); go("sim")
    if btn((580,662,320,44),"NEW MISSION",CY): go("missions")
    if btn((920,662,320,44),"MAIN MENU",DM): go("menu")
# ---------------- HOMEPAGE ----------------
LIGHT=(.62,-.5,.6); _ln=math.sqrt(sum(c*c for c in LIGHT)); LIGHT=tuple(c/_ln for c in LIGHT)
_hv=(LIGHT[0],LIGHT[1],LIGHT[2]+1); _hn=math.sqrt(sum(c*c for c in _hv)); HALF=tuple(c/_hn for c in _hv)
def _hash(a,b):
    v=math.sin(a*127.1+b*311.7)*43758.5453; return v-math.floor(v)
def _noise(x,y,z):
    return (math.sin(x*2.3+y*1.1+1.7)*math.sin(y*2.9-z*1.6+.4)+.6*math.sin(z*3.7+x*2.1)*math.cos(y*4.1+x*1.3)
            +.35*math.sin(x*6.3+z*5.1+y*2.2)*math.sin(y*5.7-x*3.3)+.2*math.sin(z*9.1+y*7.3+x*3.1))
def planet_px(x,y,z,px,py):
    """Colour of a point on the unit sphere, lit from the upper right. Returns (r,g,b,lambert)."""
    n=_noise(x*1.15+.3,y*1.15,z*1.15)
    lam=max(0.0,x*LIGHT[0]+y*LIGHT[1]+z*LIGHT[2])
    ice=abs(y)>.86+.05*math.sin(x*9+z*7)
    land=n>.28 and not ice
    if ice: col=(232,240,250)
    elif land:
        t=clamp((n-.28)/.9)
        col=lc((34,104,62),(176,150,92),t) if abs(y)<.7 else lc((70,120,80),(150,160,140),t)
    else:
        col=lc((8,32,86),(26,96,168),clamp((n+.5)/.8))
    k=.05+1.05*lam**.75
    r,g,b=[c*k for c in col]
    if 0<lam<.16:                         # warm terminator
        w=(1-lam/.16)*.5; r+=70*w; g+=28*w
    if not land and not ice and lam>0:    # sun glint on the ocean
        s=max(0.0,x*HALF[0]+y*HALF[1]+z*HALF[2])**70*190; r+=s; g+=s; b+=s*.9
    f=(1-z)**3                            # atmosphere rim, strongest on the sunlit limb
    a=f*(.2+1.5*clamp(lam+.15))
    r+=70*a; g+=150*a; b+=255*a
    if land and lam<.06 and n>.34 and _hash(px//14,py//14)>.45 and _hash(px//2,py//2)>.86:   # city lights on the night side
        c=1-lam/.06; r+=255*c*.8; g+=190*c*.8; b+=110*c*.8
    return (int(clamp(r,0,255)),int(clamp(g,0,255)),int(clamp(b,0,255))),lam
def cloud_val(px,py,w):
    u=2*math.pi*px/w
    c=(.55*math.sin(2*u+py*.05+1.2*math.sin(py*.03+u*2))+.4*math.sin(3*u-py*.07+1.6*math.sin(u+py*.06))
       +.22*math.sin(6*u+py*.12+math.sin(u*3-py*.05)*1.3))
    return clamp((c-.2)*1.5)
MENU={}
def menu_init():
    R=190; D=R*2; base=pg.Surface((D,D),pg.SRCALPHA); shade=pg.Surface((D,D),pg.SRCALPHA)
    for py in range(D):
        for px in range(D):
            x=(px+.5-R)/R; y=(py+.5-R)/R; d2=x*x+y*y
            if d2>=1: continue
            z=math.sqrt(1-d2); al=int(255*clamp((1-math.sqrt(d2))*R/1.3))
            col,lam=planet_px(x,y,z,px,py)
            base.set_at((px,py),(*col,al))
            v=int(255*(.1+.9*lam**.8)*z**.35); shade.set_at((px,py),(v,v,v,al))
    Wt=D*2; w,h=Wt//3,D//3; ct=pg.Surface((w,h),pg.SRCALPHA)
    for py in range(h):
        for px in range(w):
            v=cloud_val(px,py*3,w); ct.set_at((px,py),(255,255,255,int(190*v)))
    ct=pg.transform.smoothscale(ct,(Wt,D))
    gl=pg.Surface((int(R*3),int(R*3)),pg.SRCALPHA); c0=gl.get_width()//2
    for k in range(40):
        f=k/39; pg.draw.circle(gl,(70,150,255,int(2+9*f*f)),(c0,c0),int(R*(1.38-.38*f)))
    sun=pg.Surface((1000,1000)); 
    for k in range(90):
        f=k/89; q=f*f*f; pg.draw.circle(sun,(int(255*q*.75),int(170*q*.6),int(80*q*.4)),(500,500),int(500*(1-f)))
    vg=pg.Surface((64,36),pg.SRCALPHA)
    for yy in range(36):
        for xx in range(64):
            d=math.hypot((xx-32)/32,(yy-18)/18); vg.set_at((xx,yy),(0,0,6,int(clamp((d-.62)/.9)*150)))
    TF=FF(TITLE_FONT,72,False); ttl="PERIHELION"
    MENU.update(R=R,base=base,shade=shade,ct=ct,glow=gl,sun=sun,vig=pg.transform.smoothscale(vg,(W,H)),TF=TF,ttl=ttl,
                TW=[TF.size(c)[0] for c in ttl],SS=[],orb=dict(cx=960,cy=384,rx=335,ry=92,tilt=math.radians(-17)))
def orb_pt(a,ox=0.0,oy=0.0):
    o=MENU["orb"]; x=math.cos(a)*o["rx"]; y=math.sin(a)*o["ry"]; c,s=math.cos(o["tilt"]),math.sin(o["tilt"])
    return o["cx"]+ox+x*c-y*s, o["cy"]+oy+x*s+y*c
def B(s,pos,**kw): screen.blit(s,(int(pos[0]),int(pos[1])),**kw)
def TA(t,n,col,x,y,al,b=False,fam=None):
    im=(FF(fam,n,b) if fam else F(n,b)).render(t,True,col); im.set_alpha(int(255*clamp(al))); B(im,(x,y)); return im.get_width()
def spaced(t,n,col,x,y,sp,al=1.0,b=False,fam=None):
    for ch in t: x+=TA(ch,n,col,x,y,al,b,fam)+sp
    return x
def orbit_pass(front,a,ox,oy):
    """Orbit line, comet trail and ship for one half of the orbit (behind or in front of the planet)."""
    N=140; pts=[orb_pt(i/N*math.tau,ox,oy) for i in range(N+1)]
    for i in range(N):
        if (math.sin((i+.5)/N*math.tau)>0)==front:
            pg.draw.line(screen,(70,105,175) if front else (32,48,88),pts[i],pts[i+1],1)
    for k in range(1,70):
        ang=a-k*.016
        if (math.sin(ang)>0)!=front: continue
        v=(1-k/70)**1.6; x,y=orb_pt(ang,ox,oy)
        pg.draw.circle(screen,(int(70*v+10),int(160*v+20),int(min(255,255*v+20))),(int(x),int(y)),1 if k>22 else 2)
    if (math.sin(a)>0)==front:
        x,y=orb_pt(a,ox,oy); x2,y2=orb_pt(a+.01,ox,oy); ang=math.atan2(y2-y,x2-x)
        glow_c=pg.Surface((60,60),pg.SRCALPHA)
        for r_,al in((26,10),(16,18),(8,34)): pg.draw.circle(glow_c,(90,190,255,al),(30,30),r_)
        B(glow_c,(x-30,y-30)); ship(screen,x,y,ang,1.05+.3*math.sin(a),True,False)
def scr_menu(dt):
    if not MENU: menu_init()
    G.mt+=dt; mt=G.mt; t=G.ctr; R=MENU["R"]
    px_=(mp[0]-W/2)/W; py_=(mp[1]-H/2)/H                     # mouse parallax
    # sun bloom, top right
    B(MENU["sun"],(1270-500-px_*10,-40-500-py_*6),special_flags=pg.BLEND_ADD)
    # shooting stars
    SS=MENU["SS"]
    if random.random()<dt/4.5 and len(SS)<3: SS.append([random.uniform(100,W-100),random.uniform(0,H*.45),random.uniform(-520,-340),random.uniform(170,300),1.0])
    for s_ in SS[:]:
        s_[0]+=s_[2]*dt; s_[1]+=s_[3]*dt; s_[4]-=dt*1.1
        if s_[4]<=0: SS.remove(s_); continue
        L_=math.hypot(s_[2],s_[3])
        for k in range(10):
            f=(1-k/10)*s_[4]; c=int(235*f); ex=s_[0]-s_[2]/L_*k*9; ey=s_[1]-s_[3]/L_*k*9
            pg.draw.line(screen,(c,c,min(255,c+20)),(ex,ey),(ex-s_[2]/L_*9,ey-s_[3]/L_*9),1)
    # planet + orbiting craft
    cx=960-px_*14; cy=384-py_*9; ox=-px_*26; oy=-py_*16; a=t*.42
    orbit_pass(False,a,ox,oy)
    gl=MENU["glow"]; B(gl,(cx-gl.get_width()//2,cy-gl.get_height()//2))
    B(MENU["base"],(cx-R,cy-R))
    D=R*2; ct=MENU["ct"]; Wt=ct.get_width(); off=int(t*7)%Wt; tmp=pg.Surface((D,D),pg.SRCALPHA)
    tmp.blit(ct,(-off,0))
    if off+D>Wt: tmp.blit(ct,(Wt-off,0))
    tmp.blit(MENU["shade"],(0,0),special_flags=pg.BLEND_RGBA_MULT); B(tmp,(cx-R,cy-R))
    orbit_pass(True,a,ox,oy)
    B(MENU["vig"],(0,0))
    # title: staggered reveal, light sweep across the letters
    TF=MENU["TF"]; TW=MENU["TW"]; ttl=MENU["ttl"]; SP=26; tot=sum(TW)+SP*(len(ttl)-1); x=84
    p=(t%8)/1.9; sx=lerp(40,84+tot+140,p) if p<1 else -999
    for i,ch in enumerate(ttl):
        ap=sm((mt-.1-i*.06)/.55)
        if ap>0:
            k=clamp(1-abs(x+TW[i]/2-sx)/120); y=150+(1-ap)*28
            col=lc(lc((110,195,255),(225,238,255),i/(len(ttl)-1)*.6+.15),(255,255,255),k)
            g=TF.render(ch,True,CY)
            for o,al in((5,22+int(30*k)),(3,34+int(40*k))):
                g.set_alpha(int(al*ap))
                for dx,dy in((-o,0),(o,0),(0,-o),(0,o)): B(g,(x+dx,y+dy))
            im=TF.render(ch,True,col); im.set_alpha(int(255*ap)); B(im,(x,y))
        x+=TW[i]+SP
    # accent line with a travelling spark
    lp=sm((mt-.7)/.8); LL=int(tot*lp)
    for sx2 in range(0,LL,4):
        f=1-sx2/max(1,tot); c=lc(NAVY,CY,f*.9); pg.draw.line(screen,c,(84+sx2,258),(84+min(sx2+4,LL),258),2)
    if LL>10:
        spx=84+((t*160)%LL); pg.draw.circle(screen,(210,240,255),(int(spx),258),2)
        sp_=pg.Surface((24,24),pg.SRCALPHA); pg.draw.circle(sp_,(120,210,255,60),(12,12),11); B(sp_,(spx-12,246))
    # menu items
    items=[("NEW MISSION",lambda:go("missions")),("HOW TO PLAY",lambda:go("help")),("QUIT",lambda:sys.exit())]
    for i,(lab,fn) in enumerate(items):
        ap=sm((mt-1.0-i*.12)/.5); r=pg.Rect(84,318+i*64,340,48)
        G.hv[i]=lerp(G.hv.get(i,0),1.0 if hit(r) and ap>.8 else 0.0,min(1,dt*12)); hv=G.hv[i]
        xo=r.x+(1-ap)*-28+hv*16; col=lc(DM,TX,hv)
        TA(f"0{i+1}",12,lc((70,85,120),CY,hv),xo,r.y+16,ap,False,BODY_FONT)
        spaced(lab,17,col,xo+34,r.y+13,8,ap,False,BODY_FONT)
        ln=int(lerp(0,250,hv)); pg.draw.line(screen,lc(NAVY,CY,.7),(xo+34,r.y+42),(xo+34+ln,r.y+42),1)
        bh=int(26*hv); pg.draw.line(screen,CY,(r.x-4,r.centery-bh//2),(r.x-4,r.centery+bh//2),2)
        if hv>.02: ax=xo+34+ln+8; pg.draw.polygon(screen,lc(NAVY,CY,hv),[(ax,r.centery-5),(ax+8,r.centery),(ax,r.centery+5)])
        if ap>.9 and any(r.collidepoint(c) for c in clicks): fn()
    bh_=int(34*sm(mt/1.6)); pg.draw.rect(screen,(0,0,0),(0,0,W,bh_)); pg.draw.rect(screen,(0,0,0),(0,H-bh_,W,bh_))
def scr_help(dt):
    T(screen,"HOW TO PLAY",26,TX,70,24,"l",True)
    if abtn((20,22,40,34),-1,DM): go("menu")
    tx=["1. Pick a mission and difficulty. Each mission has a destination, budget, duration and required observations.","2. In the Design Workspace use the < > arrows to choose parts, orbit and launch vehicle, and click instruments to toggle them. Hover anything to learn what it does.","3. Watch the live dashboard: bars show have/need ratio against the white requirement line. Green is safe, yellow marginal, orange risky, red fails.","4. Run the Feasibility Analysis. It is computed from your exact design. You may launch even if it is NOT FEASIBLE.","5. In the simulation the outcome is deterministic: the first violated constraint decides where and how the mission fails. Orbiter missions end in orbit insertion, not a crash.","6. Read the debrief, redesign, and try again. Score rewards efficient trade-offs, not expensive parts."]
    y=100
    for t in tx: y=para(screen,t,17,TX,70,y,1100)+12
SCREENS=dict(menu=scr_menu,missions=scr_missions,design=scr_design,report=scr_report,sim=scr_sim,debrief=scr_debrief,help=scr_help)
def main():
    global clicks,mp
    menu_init(); clock.tick()
    while True:
        dt=clock.tick(60)/1000; G.ctr+=dt; clicks=[]
        for e in pg.event.get():
            if e.type==pg.QUIT: pg.quit(); sys.exit()
            if e.type==pg.MOUSEBUTTONDOWN and e.button==1: clicks.append(e.pos)
            if e.type==pg.KEYDOWN and e.key==pg.K_ESCAPE: go("menu")
        mp=pg.mouse.get_pos()
        if G.scr!="sim":
            screen.fill(NAVY)
            for i,(c,al) in enumerate([((40,60,160),50),((90,50,160),35)]):
                g=pg.Surface((W,H),pg.SRCALPHA); pg.draw.circle(g,(*c,al),(300+i*600+math.sin(G.ctr*.2+i)*40,200+i*300),420); screen.blit(g,(0,0))
            stars(screen,G.ctr*6+(mp[0]-W/2)*.05,(mp[1]-H/2)*.03)
        SCREENS[G.scr](dt)
        if G.fade>0: v=pg.Surface((W,H)); v.set_alpha(int(255*G.fade)); screen.blit(v,(0,0)); G.fade=max(0,G.fade-dt*3)
        pg.display.flip()
if __name__=="__main__": main()

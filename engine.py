"""PERIHELION engine: data, resource model, feasibility analysis, deterministic outcome, scoring."""
import math
from types import SimpleNamespace as NS

# (name, mass kg, cost M$, power W (+gen / -use), reliability, perf)
CAT = [
 ("Structure", [("Light Alloy Frame",150,3,0,.95,0),("Standard Truss",220,5,0,.975,0),("Reinforced Frame",330,9,0,.99,0)],
  "Carries every other part. Heavier frames are more reliable but eat launch capacity."),
 ("Propulsion", [("Hydrazine Thruster",200,8,-20,.95,280),("Bipropellant Engine",260,12,-30,.97,320),("Ion-Assist Drive",380,25,-250,.96,450)],
  "Performance is specific impulse (Isp, s). Higher Isp stretches fuel further, but ion drives need lots of electrical power."),
 ("Solar Panels", [("Small Array 300W",40,4,300,.97,0),("Medium Array 800W",90,8,800,.975,0),("Large Array 1800W",180,15,1800,.98,0)],
  "Rated at 1 AU. Output falls with the square of distance from the Sun, so outer-system missions need big arrays."),
 ("Batteries", [("500 Wh Pack",20,2,0,.98,500),("1500 Wh Pack",55,5,0,.98,1500),("4000 Wh Pack",140,11,0,.985,4000)],
  "Cover eclipses and peak loads. Aim for about 2 hours of total consumption."),
 ("Antenna", [("0.5 m Patch",10,2,-30,.98,2),("1.5 m High-Gain",30,5,-60,.98,8),("3 m Deep-Space Dish",70,10,-120,.985,25)],
  "Performance is downlink Mbps at 1 AU range. Bandwidth falls with distance squared; too little and data piles up."),
 ("Computer", [("Basic OBC 64 GB",8,2,-20,.96,64),("Flight Computer 256 GB",12,4,-40,.98,256),("Rad-Hard 1 TB",18,8,-70,.99,1024)],
  "Runs the spacecraft and stores science data until it can be sent home."),
 ("Thermal", [("Blankets Only",15,2,0,.97,0),("Active Thermal Control",40,5,-30,.98,1),("Ablative Heat Shield",90,10,-30,.985,2)],
  "Tier 1 survives cold and radiation environments. Tier 2 survives atmospheric entry."),
 ("Attitude Control", [("Cold-gas Thrusters",10,2,-5,.95,0),("Reaction Wheels",18,5,-25,.975,1),("Precision Gyro System",28,9,-40,.99,2)],
  "Points antenna, panels and instruments. Better pointing raises science return."),
 ("Navigation", [("Star Tracker",6,2,-10,.96,0),("Optical Nav + Radar Altimeter",20,6,-35,.98,1),("Autonomous Terminal Guidance",35,12,-60,.99,2)],
  "Landing missions need tier 1 or better for terminal guidance. Orbiters can fly with a star tracker."),
 ("Fuel Load", [("150 kg",150,1,0,1,150),("400 kg",400,2,0,1,400),("900 kg",900,4,0,1,900),("1800 kg",1800,7,0,1,1800),("3000 kg",3000,11,0,1,3000)],
  "Propellant. delta-v = Isp x 9.81 x ln(wet mass / dry mass). More fuel adds delta-v but also mass."),
]
# name, mass, cost, power, data GB/day, tags, science value, description
INS = [
 ("Hi-Res Camera",35,6,-40,6,("imaging",),30,"Images surfaces for geology and landing-site maps. Generates lots of data."),
 ("Infrared Spectrometer",45,9,-35,2,("mineral","atmo"),35,"Identifies minerals and atmospheric gases from reflected light."),
 ("Radar",70,14,-120,4,("subsurface","topo"),40,"Maps topography and probes beneath the surface (ice, caves). Power hungry."),
 ("Magnetometer",8,3,-8,.1,("field",),20,"Measures magnetic fields; reveals interiors and induced oceans."),
 ("Atmospheric Analyzer",25,7,-45,.5,("atmo",),30,"Samples atmosphere composition, pressure and temperature."),
 ("Radiation Detector",6,2,-10,.1,("radiation",),15,"Measures charged particles. Cheap and light, vital for hazardous environments."),
 ("Seismometer",30,8,-15,.3,("seismic",),30,"Listens for quakes to map internal structure. Needs a surface landing."),
]
LAUNCH = [("Vanguard-1",3000,40,.95),("Titan-V",9000,90,.97),("Aurora Heavy",22000,170,.98)]  # name, LEO kg, cost, reliability
ORB = [("Low Earth Orbit",1.0,"Cheapest and highest capacity. Good for nearby observation, but a stepping stone for anything farther."),
       ("Geostationary",.4,"Fixed view of one Earth region. Needs extra energy to reach; ideal for weather and comms."),
       ("Polar Orbit",.9,"Passes over every part of Earth over time. The classic Earth-observation choice."),
       ("Lunar Transfer",.35,"Escapes Earth toward the Moon. Only about a third of LEO capacity."),
       ("Mars Transfer",.25,"Interplanetary injection toward Mars. A quarter of LEO capacity."),
       ("Deep Space Trajectory",.25,"High-energy escape for the outer Solar System. Lowest capacity of all.")]
DIFF = [("Easy",1.3,.85),("Normal",1.0,1.0),("Hard",.85,1.1),("Expert",.72,1.2)]  # name, budget x, requirement x

def _m(name,dest,desc,sci,diff,budget,days,land,orbit,dv,sun,comm,req,therm,chal,col,dist,atmo):
    return NS(name=name,dest=dest,desc=desc,sci=sci,diff=diff,budget=budget,days=days,land=land,orbit=orbit,dv=dv,
              sun=sun,comm=comm,req=req,therm=therm,chal=chal,col=col,dist=dist,atmo=atmo)
MISSIONS = [
 _m("Lunar Exploration","The Moon","Land a geology and seismic station on the lunar surface.","Map surface minerals and listen for moonquakes.","Easy",300,60,True,3,2800,1.0,.3,("imaging","seismic","mineral"),0,"Airless landing: all braking must come from your engine.",(170,170,180),384e3,False),
 _m("Mars Exploration","Mars","Touch down on Mars and study its atmosphere and interior.","Characterise the thin atmosphere and detect marsquakes.","Normal",450,300,True,4,3800,1.5,1.5,("imaging","atmo","seismic"),2,"Atmospheric entry needs an ablative heat shield.",(200,100,60),225e6,True),
 _m("Europa Ocean Discovery","Europa","Orbit Jupiter's icy moon and probe its hidden ocean.","Find evidence of a subsurface ocean via radar and magnetic fields.","Hard",550,700,False,5,4200,1.8,5.2,("subsurface","field","imaging"),1,"Weak sunlight and brutal radiation; far from Earth.",(190,200,215),628e6,False),
 _m("Asteroid Research","Asteroid belt","Rendezvous with an asteroid and orbit it.","Determine composition and shape of a primitive body.","Normal",340,400,False,5,3800,1.8,1.8,("mineral","imaging","topo"),0,"Long cruise with dim sunlight.",(120,110,100),300e6,False),
 _m("Earth Observation","Earth","Place an observatory in polar orbit to study our home.","Monitor the atmosphere and surface in high resolution.","Easy",220,365,False,2,600,1.0,.2,("imaging","atmo"),0,"Data-heavy: storage and downlink dominate the design.",(50,110,200),700,False),
 _m("Deep Space Exploration","Outer heliosphere","Fly a mission far beyond the planets.","Measure magnetic fields and radiation at the edge of the Sun's influence.","Expert",480,600,False,5,3000,2.5,4.0,("field","radiation","imaging"),1,"Extreme distance: tiny solar power, tiny bandwidth.",(60,60,110),2e9,False),
]
# timeline order of failure stages: key -> (phase, fraction)
STG = {"mass":(1,.55),"orbit":(3,.25),"power":(3,.55),"comms":(3,.75),"dv":(4,.7),"thermal":(5,.35),"nav":(5,.8)}
CREDIT = {None:1,"mass":.05,"orbit":.15,"power":.35,"comms":.45,"dv":.6,"thermal":.8,"nav":.85}

def clamp(x,a=0.0,b=1.0): return max(a,min(b,x))
def rs(r): return 0 if r>=1.1 else 1 if r>=.97 else 2 if r>=.86 else 3

def default_cfg(): return {"c":[1,1,1,1,1,1,1,1,1,2],"ins":{0},"l":1,"o":0}

def analyze(M,cfg,diff=1):
    C=[CAT[i][1][k] for i,k in enumerate(cfg["c"])]; I=[INS[i] for i in sorted(cfg["ins"])]
    L=LAUNCH[cfg["l"]]; O=ORB[cfg["o"]]; rq=DIFF[diff][2]
    dry=sum(c[1] for c in C[:9])+sum(i[1] for i in I); fuel=C[9][5]; wet=dry+fuel
    dv=C[1][5]*9.81*math.log(wet/dry); need_dv=M.dv*rq
    cost=sum(c[2] for c in C)+sum(i[2] for i in I)+L[2]; budget=M.budget*DIFF[diff][1]
    gen=C[2][3]/M.sun**2; use=-sum(c[3] for c in C if c[3]<0)-sum(i[3] for i in I); batt=C[3][5]
    down=C[4][5]/M.comm**2*10.8; data=sum(i[4] for i in I)*.5*rq; store=C[5][5]
    cap=L[1]*O[1]; tags={t for i in I for t in i[5]}; cov=len(tags&set(M.req))/len(M.req)
    rel=math.prod(c[4] for c in C[:9])*L[3]*math.prod(.995 for _ in I)
    sci=sum(i[6] for i in I)*(1+.1*C[7][5]); sci_ref=sum(i[6] for i in INS if set(i[5])&set(M.req))
    ck=[]
    def mk(k,name,stage,st,val,good,bad): ck.append(dict(k=k,name=name,stage=stage,st=st,val=val,msg=good if st==0 else bad,ratio=0))
    r=cap/wet; st=rs(r)
    mk("mass","Launch Mass","mass",st,f"{wet:.0f} / {cap:.0f} kg",f"The {L[0]} can deliver {wet:.0f} kg on a {O[0]} profile.",
       f"Excess mass: spacecraft is {wet:.0f} kg but the {L[0]} can only send {cap:.0f} kg on this profile. "+("Margin is thin." if st<3 else "It cannot reach the planned trajectory. Cut mass or pick a bigger rocket."))
    st=0 if cfg["o"]==M.orbit else 3
    mk("orbit","Orbit / Trajectory","orbit",st,O[0],f"{O[0]} matches the route to {M.dest}.",f"Wrong trajectory: {M.dest} needs a {ORB[M.orbit][0]}, not {O[0]}. The spacecraft will miss its target.")
    r=dv/need_dv; st=rs(r)
    mk("dv","Delta-v (Propulsion)","dv",st,f"{dv:.0f} / {need_dv:.0f} m/s",f"Propulsion provides {dv:.0f} m/s against {need_dv:.0f} m/s required.",
       f"Insufficient delta-v: {dv:.0f} m/s available, {need_dv:.0f} needed. "+("Margin is slim." if st<3 else "Fuel runs out before the arrival maneuver can finish."))
    r=gen/use; st=rs(r); lowb=batt<use*1.5
    if lowb: st=max(st,1)
    mk("power","Power Balance","power",st,f"{gen:.0f} W gen / {use:.0f} W use",f"Solar output ({gen:.0f} W) covers consumption ({use:.0f} W).",
       f"Power deficit detected: instruments and systems draw {use:.0f} W but arrays give {gen:.0f} W at this distance"+(f" ({(1-gen/use)*100:.0f}% short). Batteries drain and systems shut down." if gen<use else ".")+(" Battery is also under 2 h of reserve." if lowb else ""))
    r=(store+down*M.days)/(data*M.days) if data else 9; st=rs(r)
    mk("comms","Comms & Data","comms",st,f"{down:.1f} GB/d down, {data:.1f} GB/d made",f"Downlink {down:.1f} GB/day plus {store} GB storage can handle {data:.1f} GB/day of science.",
       f"Communication shortfall: instruments make {data:.1f} GB/day but only {down:.1f} GB/day can be sent home and {store} GB stored. "+("Buffers will nearly overflow." if st<3 else "Storage overflows and mission control loses useful contact."))
    st=0 if C[6][5]>=M.therm else 3
    mk("thermal","Thermal Protection","thermal",st,f"tier {C[6][5]} / {M.therm}",f"Thermal protection tier {C[6][5]} meets the requirement.",
       "Thermal protection too weak: "+("the spacecraft burns up during atmospheric entry." if M.atmo else "heat and radiation fry the electronics during arrival."))
    if M.land:
        st=0 if C[8][5]>=1 else 3
        mk("nav","Terminal Guidance","nav",st,f"tier {C[8][5]} / 1","Navigation can guide a precision descent.","No terminal guidance: the lander cannot judge altitude or velocity and crashes.")
    st=0 if cost<=budget else 3
    mk("budget","Budget",None,st,f"${cost:.0f}M / ${budget:.0f}M","Spending is within budget.",f"Over budget by ${cost-budget:.0f}M. The program would be cancelled in real life.")
    st=0 if cov>=1 else 1 if cov>=.66 else 2 if cov>0 else 3
    mk("obj","Science Objectives",None,st,f"{cov*100:.0f}% covered","Every required observation is covered by an instrument.",f"Missing instruments for: {', '.join(sorted(set(M.req)-tags))}. Those objectives cannot be completed.")
    st=0 if rel>=.72 else 1 if rel>=.64 else 2
    mk("rel","Reliability",None,st,f"{rel*100:.1f}%","Estimated reliability is strong.",f"Reliability is only {rel*100:.1f}%. Many cheap parts compound risk; upgrade weak links.")
    sts=[c["st"] for c in ck]
    cls=("NOT FEASIBLE" if 3 in sts else "HIGH RISK" if sts.count(2)>=2 or sts.count(1)>=4 else "FEASIBLE WITH WARNINGS" if 1 in sts else "READY FOR LAUNCH")
    fscore=round(100*sum(1-s/3 for s in sts)/len(sts))
    fail=next((k for k in STG if any(c["k"]==k and c["st"]==3 for c in ck)),None)
    anomalies=[c["k"] for c in ck if c["stage"] and c["st"]==2]
    return NS(C=C,I=I,L=L,O=O,dry=dry,wet=wet,fuel=fuel,dv=dv,need_dv=need_dv,cost=cost,budget=budget,gen=gen,use=use,batt=batt,down=down,data=data,
              store=store,cap=cap,cov=cov,rel=rel,sci=sci,sci_ref=sci_ref,checks=ck,cls=cls,fscore=fscore,fail=fail,anomalies=anomalies,M=M,diff=diff,days=M.days)

def score(A):
    f=CREDIT[A.fail]; ok=A.fail is None; sf=clamp(A.sci/max(1,A.sci_ref))
    mu=clamp(1-abs(A.wet/A.cap-.8)/.8); pu=clamp(1-abs(A.gen/A.use-1.3)/1.3); du=clamp(1-abs(A.dv/A.need_dv-1.25)/1.25)
    out=sc={}
    sc["Mission objectives (300)"]=300*A.cov*f
    sc["Scientific value (200)"]=200*sf*(1 if ok else f*.5)*(.8 if A.anomalies else 1)
    sc["Engineering efficiency (150)"]=150*(mu+pu+du)/3
    sc["Budget management (100)"]=0 if A.cost>A.budget else 100*clamp(1-abs(A.cost/A.budget-.85)*1.2)
    sc["Reliability (100)"]=100*clamp((A.rel-.6)/.25)
    sc["Resource optimization (100)"]=100*clamp(1-abs(A.data/max(.01,A.down+A.store/A.days)-.6)/.6)*.5+50*clamp(1-abs(A.batt/(A.use*2)-1.5)/1.5)
    sc["Mission execution (50)"]=50*(1 if ok else f*.4)*(.7 if A.anomalies else 1)
    return {k:round(v) for k,v in out.items()}, round(sum(out.values()))

FAILTXT = {"mass":"Rocket loses control during ascent: payload exceeded the launch vehicle's capacity.",
 "orbit":"Spacecraft misses its intended trajectory and drifts away from the target.",
 "power":"Power deficit: batteries depleted, spacecraft systems shutting down.",
 "comms":"Communication failure: data buffers overflowed and mission control lost contact.",
 "dv":"Propellant exhausted: spacecraft cannot complete its arrival maneuver and flies past.",
 "thermal":"Thermal protection failed: spacecraft lost to heat and radiation.",
 "nav":"Terminal guidance failure: lander descended too fast and crashed."}

def debrief(A):
    ok=A.fail is None; good=[c["msg"] for c in A.checks if c["st"]==0]; bad=[c for c in A.checks if c["st"]>=1]
    why=("Mission success: "+("the spacecraft landed safely and completed its science." if A.M.land else "orbit insertion was achieved and science operations ran.")) if ok else "Mission failure: "+FAILTXT[A.fail]
    if ok and A.cov<1: why+=" Science was incomplete because some required instruments were not flown."
    if ok and A.anomalies: why+=" Marginal systems caused anomalies that cut science return by about 20%."
    recs=[c["msg"] for c in bad] or ["Excellent design. Try a cheaper or lighter configuration to improve efficiency scores."]
    return why,good,recs

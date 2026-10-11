import numpy as np
from gate_image_cm_sym import theta as theta_sym
def theta(s,c,P):
    return theta_sym(s,c,P/4.0)   # theta_sym uses period 4h
def Vsum(s,z,z0,h1,h2):
    """sum over images of grounded planes z=+h1 and z=-h2 : source z0, field z.  period P=2(h1+h2)"""
    P=2*(h1+h2)
    # +: z0+Pn ; -: reflected in z=h1: 2h1-z0+Pn
    return theta(s,z-z0,P)-theta(s,z-(2*h1-z0),P)
def S(s,d,h1,h2,ze):
    zh=ze+d
    return Vsum(s,ze,ze,h1,h2)+Vsum(s,zh,zh,h1,h2)-2*Vsum(s,zh,ze,h1,h2)
s=np.logspace(-10,4,60001)
rng=np.random.default_rng(0); worst=(1,None)
cases=[]
for _ in range(300):
    d=1.0; h1=d*(0.0+10**rng.uniform(-0.0,1.5)); h2=d*(10**rng.uniform(0,1.5))
    # layers inside: ze in (-h2, h1-d)
    if h1+h2<d*1.0001: continue
    ze=rng.uniform(-h2,h1-d)
    v=S(s,d,h1,h2,ze); scale=2*(1-np.exp(-s*d*d)).clip(1e-300)
    r=(v/scale).min(); 
    if r<worst[0]: worst=(r,(h1,h2,ze))
    cases.append(r)
print("random asymmetric dual-gate cases:",len(cases),"min of S/(2(1-e^{-s d^2})) =",worst)
# single gate: h2 -> large (Poisson requires finite P; use h2=1e4)
for h1 in [0.5,1,2,5,20]:
    for ze in [-1e3, -0.5, 0.0]:
        pass
print("single-gate limit (h2=2000):")
for h1 in [1.0,2.0,5.0,20.0]:
    for ze in [h1-1.0, h1-3.0 if h1>3 else 0.0, 0.0]:
        v=S(s,1.0,h1,2000.0,ze); print(f" h1={h1} ze={ze:.2f} min S={v.min(): .3e} neg={int((v<-1e-12).sum())}")

import numpy as np
def theta(s,c,h):
    """sum_n exp(-s (c+4hn)^2) by Poisson (small s) or direct (large s)"""
    s=np.asarray(s,float); out=np.empty_like(s)
    P=4*h; sm=s< 1.0/(P*P)
    m=np.arange(1,40)[None,:]
    ss=s[sm][:,None]
    out[sm]=np.sqrt(np.pi/ss[:,0])/P*(1+2*(np.exp(-np.pi**2*m**2/(P*P*ss))*np.cos(2*np.pi*m*c/P)).sum(1))
    n=np.arange(-12,13)[None,:]; sl=s[~sm][:,None]
    out[~sm]=np.exp(-sl*(c+P*n)**2).sum(1)
    return out
def S(s,d,h):
    z0=-d/2
    same=theta(s,0.0,h)-theta(s,2*z0-2*h,h)
    inter=theta(s,d,h)-theta(s,2*h,h)
    return 2*same-2*inter
if __name__=="__main__":
    d=1.0
    print("h/d  min S   at s*d^2   min S/(S scale at same s via 1-e^{-sd^2})")
    for h in [0.51,0.75,1,1.5,2,3,5,10,20,50]:
        s=np.logspace(-10,4,200001)
        v=S(s,d,h); i=np.argmin(v)
        neg=(v<-1e-14*1).sum()
        print(f"{h:5.2f} {v[i]: .3e} {s[i]*d*d: .2e} negatives={neg}")

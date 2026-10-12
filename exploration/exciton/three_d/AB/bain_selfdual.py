"""Gaussian theta energy per particle at unit density along the Bain path (body-centred tetragonal, c/a = t):
t=1 BCC, t=sqrt2 FCC. Poisson: bct(t)* ~ bct(sqrt2/t), fixed point t=2^(1/4) (isodual, Conway-Sloane m.c.c.)."""
import numpy as np, itertools
def bct(t):
    # conventional cell a x a x c with c = t a, body-centred; volume per particle a^3 t/2 = 1
    a=(2/t)**(1/3); c=t*a
    return np.array([[a,0,0],[0,a,0],[a/2,a/2,c/2]])
def theta(B, alpha, R=9.0):
    # sum_{v != 0} exp(-alpha |v|^2) via direct enumeration within radius R (alpha>=1 -> tail < 1e-30)
    n=int(R/np.min(np.linalg.norm(B,axis=1)))+2
    rng=np.arange(-n,n+1)
    I=np.array(list(itertools.product(rng,rng,rng)))
    V=I@B; r2=(V**2).sum(1); r2=r2[r2>1e-12]
    return np.exp(-alpha*r2[r2<R*R]).sum()
def theta_poisson(B, alpha):
    # for alpha < 1 use dual: theta_L(alpha) = (pi/alpha)^{3/2}/det * (1 + theta_{L*}(pi^2/alpha)) - 1  (unit det)
    Bs=np.linalg.inv(B).T
    return (np.pi/alpha)**1.5*(1+theta(Bs,np.pi**2/alpha))-1
ts=np.concatenate([np.linspace(1,np.sqrt(2),41),[2**0.25]])
ts=np.sort(ts)
for alpha in [np.pi, 2.5, 4.0]:
    vals=[]
    for t in ts:
        B=bct(t); assert abs(np.linalg.det(B)-1)<1e-12
        vals.append(theta(B,alpha) if alpha>=np.pi/1.0001 else theta_poisson(B,alpha))
    vals=np.array(vals)
    i=np.argmin(vals); j=np.argmax(vals)
    k=np.argmin(abs(ts-2**0.25))
    print(f"alpha={alpha:.4f}: E(BCC)={vals[0]:.12f} E(FCC)={vals[-1]:.12f} E(mcc t=2^1/4)={vals[k]:.12f}  argmin t={ts[i]:.4f} argmax t={ts[j]:.4f}")
    if alpha==np.pi:
        # symmetry check t -> sqrt2/t
        for t in [1.05,1.1,1.15]:
            print("   sym check", t, theta(bct(t),np.pi), theta(bct(np.sqrt(2)/t),np.pi))

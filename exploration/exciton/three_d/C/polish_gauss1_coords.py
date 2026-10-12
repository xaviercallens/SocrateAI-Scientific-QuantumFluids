"""Supplementary (2026-10-12): 2 gauss1 N=120 starts with the raised cap, coordinates saved, distance spectrum vs the 600-cell."""
import json, numpy as np
from scipy.optimize import minimize
import run_C as R
kind,p=R.KERNELS["gauss1"]; N=120
C=R.cell600(); dc=np.sort(np.linalg.norm(C[:,None]-C[None],axis=-1)[np.triu_indices(120,1)])
out=[]
for s in (0,1):
    seed=1000*N+s+100000*list(R.KERNELS).index("gauss1")
    y0=np.random.default_rng(seed).normal(size=(N,4)).ravel()
    res=minimize(R.energy_grad,y0,args=(N,kind,p),jac=True,method="L-BFGS-B",
                 options=dict(maxiter=150000,maxfun=300000,ftol=1e-18,gtol=1e-12,maxcor=50))
    X=res.x.reshape(N,4); X/=np.linalg.norm(X,axis=1,keepdims=True)
    d=np.sort(np.linalg.norm(X[:,None]-X[None],axis=-1)[np.triu_indices(120,1)])
    E=R.energy(X,kind,p)
    out.append(dict(start=s,E=E,nit=int(res.nit),max_abs_dist_dev_from_600cell_spectrum=float(np.abs(d-dc).max()),
                    min_chord=float(d[0]),chord_600=float(dc[0])))
    print(out[-1],flush=True)
json.dump(out,open("polish_gauss1_coords.json","w"),indent=1)

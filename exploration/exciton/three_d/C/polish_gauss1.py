"""Supplementary run (2026-10-12, after hostile review): gauss1, N=120, same seeds as run_C.py, iteration cap raised 8000 -> 150000."""
import json, numpy as np
from scipy.optimize import minimize
from multiprocessing import Pool
import run_C as R
def one(s):
    kind,p=R.KERNELS["gauss1"]; N=120
    seed=1000*N+s+100000*list(R.KERNELS).index("gauss1")
    y0=np.random.default_rng(seed).normal(size=(N,4)).ravel()
    res=minimize(R.energy_grad,y0,args=(N,kind,p),jac=True,method="L-BFGS-B",
                 options=dict(maxiter=150000,maxfun=300000,ftol=1e-18,gtol=1e-12,maxcor=50))
    E,g=R.energy_grad(res.x,N,kind,p)
    return dict(N=N,kernel="gauss1",start=s,E=E,gmax=float(np.abs(g).max()),nit=int(res.nit),msg=str(res.message))
if __name__=="__main__":
    with Pool(2) as P: out=P.map(one,range(50))
    with open("polish_gauss1.jsonl","w") as f:
        for o in out: f.write(json.dumps(o)+"\n")
    ref=json.load(open("reference.json"))
    print(list(ref)[:6])

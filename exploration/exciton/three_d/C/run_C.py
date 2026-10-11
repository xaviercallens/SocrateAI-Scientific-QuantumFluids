"""Experiment C (PREREG.md): N points on S^3, chordal CM-type kernels."""
import numpy as np, itertools, json, sys
from scipy.optimize import minimize
from multiprocessing import Pool

KERNELS = {"gauss0.5":("g",0.5),"gauss1":("g",1.0),"gauss2":("g",2.0),"gauss4":("g",4.0),
           "coulomb":("c",0),"log":("l",0)}
def fdf(kind,p,d2):
    if kind=="g":
        f=np.exp(-p*d2); return f,-p*f
    if kind=="c":
        f=d2**-0.5; return f,-0.5*f/d2
    f=-0.5*np.log(d2); return f,-0.5/d2

def energy_grad(y,N,kind,p):
    Y=y.reshape(N,4); r=np.linalg.norm(Y,axis=1,keepdims=True); X=Y/r
    D=X[:,None,:]-X[None,:,:]; d2=(D**2).sum(-1); np.fill_diagonal(d2,1.0)
    f,df=fdf(kind,p,d2); np.fill_diagonal(f,0); np.fill_diagonal(df,0)
    E=0.5*f.sum()
    gX=(df[:,:,None]*2*D).sum(1)           # dE/dx_i
    gY=(gX-(gX*X).sum(1,keepdims=True)*X)/r  # chain rule through normalisation
    return E,gY.ravel()

def energy(X,kind,p):
    N=len(X); return energy_grad(X.ravel(),N,kind,p)[0]

def minimise(N,kernel,seed):
    kind,p=KERNELS[kernel]; rng=np.random.default_rng(seed)
    y0=rng.normal(size=(N,4)).ravel()
    res=minimize(energy_grad,y0,args=(N,kind,p),jac=True,method="L-BFGS-B",
                 options=dict(maxiter=8000,maxfun=16000,ftol=1e-17,gtol=1e-10,maxcor=30))
    E,g=energy_grad(res.x,N,kind,p)
    return E,float(np.abs(g).max()),int(res.nit),res.message

def job(a):
    N,kernel,s=a
    E,g,nit,msg=minimise(N,kernel,1000*N+s+100000*list(KERNELS).index(kernel))
    return dict(N=N,kernel=kernel,start=s,E=E,gmax=g,nit=nit,msg=msg)

def cell600():
    phi=(1+5**.5)/2; V=set()
    for i in range(4):
        for s in (1,-1):
            v=[0]*4; v[i]=s; V.add(tuple(v))
    for sg in itertools.product((.5,-.5),repeat=4): V.add(tuple(sg))
    base=[phi/2,.5,1/(2*phi),0]
    def parity(p):
        return sum(1 for i in range(4) for j in range(i+1,4) if p[i]>p[j])%2
    for p in itertools.permutations(range(4)):
        if parity(p): continue
        for sg in itertools.product((1,-1),repeat=3):
            v=[0]*4; k=0
            for pos,idx in enumerate(p):
                b=base[idx]
                if idx==3: v[pos]=0
                else: v[pos]=b*sg[k]; k+=1
            V.add(tuple(round(c,15) for c in v))
    return np.array(sorted(V))
def cell24():
    V=set()
    for i,j in itertools.combinations(range(4),2):
        for a in (1,-1):
            for b in (1,-1):
                v=[0]*4; v[i]=a; v[j]=b; V.add(tuple(v))
    return np.array(sorted(V))/np.sqrt(2)

def mindist(X):
    D=np.linalg.norm(X[:,None]-X[None],axis=-1); np.fill_diagonal(D,9); return D.min()

if __name__=="__main__":
    out=[]
    C6=cell600(); C24=cell24()
    geo=dict(n600=len(C6),n24=len(C24),min_chord_600=mindist(C6),min_chord_24=mindist(C24),
             norm600=float(np.abs(np.linalg.norm(C6,axis=1)-1).max()),
             expected_min_chord_600=2*np.sin(np.pi/10),expected_min_chord_24=1.0)
    assert geo["n600"]==120 and geo["n24"]==24, geo
    refs={}
    for k,(kind,p) in KERNELS.items():
        refs[k]=dict(E600=energy(C6,kind,p),E24=energy(C24,kind,p))
    json.dump(dict(geometry=geo,refs=refs),open("reference.json","w"),indent=1)
    print(geo); sys.stdout.flush()
    NS=[120]+list(range(12,50,2))
    jobs=[(N,k,s) for N in NS for k in KERNELS for s in range(50)]
    with Pool(2) as pool, open("records.jsonl","w") as f:
        for r in pool.imap(job,jobs,chunksize=10):
            f.write(json.dumps(r)+"\n"); f.flush()
    print("done")

import sys; sys.path.insert(0,'.')
from fractions import Fraction
import mpmath as mp, certify as C
mp.mp.dps=80
def Lmat(P, x):
    """values L_k(x), L_k'(x), L_k''(x) from the exact monomial table."""
    T=P.T; K=P.K; v=[];d1=[];d2=[]
    for k in range(K+1):
        co=[mp.mpf(q.numerator)/q.denominator for q in T[k]]
        v.append(C.mp_polyval(co,x)); dc=C.mp_polyder(co); d1.append(C.mp_polyval(dc,x)) ; d2.append(C.mp_polyval(C.mp_polyder(dc),x))
    return v,d1,d2
def polish(P, contacts, iters=80, verbose=False):
    K=P.K; n=len(contacts); assert K+1==n
    xs=[mp.mpf(x) for _,x in contacts]; sides=[s for s,_ in contacts]
    M=mp.matrix(n,n); rhs=mp.matrix(n,1)
    for i,(s,x) in enumerate(zip(sides,xs)):
        L,_,_=Lmat(P,x)
        for k in range(n): M[i,k]= P.B_mp*(-1)**k*L[k] if s=='f' else L[k]
        rhs[i]= mp.exp(P.kappa_mp*x) if s=='f' else 0
    c=[v for v in mp.lu_solve(M,rhs)]
    kap=P.kappa_mp; B=P.B_mp
    def system(c,xs):
        Fv=[]; J=mp.matrix(2*n,2*n)
        for i,(s,x) in enumerate(zip(sides,xs)):
            L,L1,L2=Lmat(P,x)
            sg=[(-1)**k if s=='f' else 1 for k in range(n)]
            V=sum(sg[k]*c[k]*L[k] for k in range(n)); V1=sum(sg[k]*c[k]*L1[k] for k in range(n)); V2=sum(sg[k]*c[k]*L2[k] for k in range(n))
            if s=='f':
                E=B*mp.exp(-kap*x)
                Fv += [E*V-1, E*(V1-kap*V)]
                for k in range(n):
                    J[2*i,k]=E*sg[k]*L[k]; J[2*i+1,k]=E*sg[k]*(L1[k]-kap*L[k])
                J[2*i,n+i]=E*(V1-kap*V); J[2*i+1,n+i]=E*(V2-2*kap*V1+kap*kap*V)
            else:
                scl=sum(abs(c[k]*L[k]) for k in range(n)) or 1
                Fv += [V/scl, V1/scl]
                for k in range(n):
                    J[2*i,k]=L[k]/scl; J[2*i+1,k]=L1[k]/scl
                J[2*i,n+i]=V1/scl; J[2*i+1,n+i]=V2/scl
        return Fv,J
    nrm=lambda F: mp.sqrt(sum(f*f for f in F))
    F,J=system(c,xs); r=nrm(F)
    for it in range(iters):
        try: dz=mp.lu_solve(J,mp.matrix([-f for f in F]))
        except ZeroDivisionError: return None,None,'singular'
        lam=mp.mpf(1)
        while lam>mp.mpf(10)**-12:
            c2=[c[k]+lam*dz[k] for k in range(n)]; x2=[xs[i]+lam*dz[n+i] for i in range(n)]
            if min(x2)>0:
                F2,J2=system(c2,x2); r2=nrm(F2)
                if r2<r: break
            lam/=2
        else:
            return c,xs,f'stalled r={mp.nstr(r,5)}'
        c,xs,F,J,r=c2,x2,F2,J2,r2
        if verbose: print('  it',it,'r',mp.nstr(r,5),'lam',mp.nstr(lam,3))
        if r<mp.mpf(10)**-60: return c,xs,f'converged it={it} r={mp.nstr(r,5)}'
    return c,xs,f'maxit r={mp.nstr(r,5)}'
EZ=lambda a: 2*mp.nsum(lambda m: mp.exp(-a*m*m),[1,mp.inf])
for bb,pq in ((Fraction(13,10),((3,2),(4,3),(5,4))),(Fraction(1,2),((4,2),(5,3),(6,4)))):
  beta=mp.mpf(bb.numerator)/bb.denominator*2/mp.pi
  uf=lambda x: 2*mp.pi*beta*x*x; th=lambda y: 2*mp.pi*y*y/beta
  for p_,q_ in pq:
    contacts=[("f",uf(n)) for n in range(1,p_+1)]+[("h",th(n)) for n in range(1,q_+1)]
    K=len(contacts)-1; P=C.Problem(1,Fraction(2),bb,K)
    c,xs,msg=polish(P,contacts)
    print('b',bb,'p,q',p_,q_,'K',K,msg)
    if c is None: continue
    Q,R=P.mp_polys(c)
    print('  locs',[mp.nstr(x,8) for x in xs])
    print('  obj',mp.nstr(P.objective(c),20),'E_Z-obj',mp.nstr(EZ(2)-P.objective(c),5))
    us=[mp.mpf(i)/40 for i in range(1,40*80)]; mx=max(P.phi(R,u) for u in us); print('  max phi (0,80]',mp.nstr(mx,5))
    ts=[mp.mpf(i)/5 for i in range(0,5*800)]; mn=min(C.mp_polyval(Q,t) for t in ts); print('  min Q [0,800]',mp.nstr(mn,5),'LC Q',mp.nstr(Q[-1],5),'LC R',mp.nstr(R[-1],5))

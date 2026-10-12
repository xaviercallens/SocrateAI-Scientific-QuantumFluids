"""T1 diagnostic (unregistered, 2026-10-12): L1 distance between the cumulative distributions of the pair measure mu_P and
the structure-factor measure nu_P on [0, 2.2] (continuous in the configuration, unlike the shell-by-shell mismatch), for
exact diamond, perturbed diamond before/after the surrogate minimisation, and the best run-2 records. Output is printed;
the 2026-10-12 output is quoted in RESULTS.md."""
import sys, os, json, numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, '../AB')
os.environ['OMP_NUM_THREADS']='1'
from selfdual import pair_measure, sf_measure, mismatch, SelfDualObjective
from opt import minimize_structure
def w1(A,S,R=2.2):
    r1,w1_=pair_measure(A,S,R); r2,w2=sf_measure(A,S,R)
    g=np.linspace(0,R,20001)
    F1=np.array([w1_[r1<=x].sum() for x in g[::20]]); F2=np.array([w2[r2<=x].sum() for x in g[::20]])
    return float(np.abs(F1-F2).mean()*R), float(np.abs(F1-F2).max())
DIA=(np.array([[0,1,1],[1,0,1],[1,1,0.]]),np.array([[0,0,0],[.25,.25,.25]]))
print('diamond exact', w1(*DIA), mismatch(DIA)[0])
rng=np.random.default_rng(1); obj=SelfDualObjective()
for eps in (1e-3,1e-2,1e-1):
    A=DIA[0]+eps*rng.normal(size=(3,3)); A*=(2/abs(np.linalg.det(A)))**(1/3); S=(DIA[1]+eps*rng.normal(size=(2,3)))%1
    print(eps,'start', w1(A,S), 'M', obj.eg(A,S)[0], 'shellmm', mismatch((A,S))[0])
    M,A1,S1,n=minimize_structure(obj,A,S,gtol=1e-13)
    print(eps,'end  ', w1(A1,S1), 'M', M, 'shellmm', mismatch((A1,S1))[0], '|dA|',np.abs(A1-A).max())
recs=[json.loads(l) for l in open('T1_records.jsonl')]
for N in (2,4,8):
    r=min([x for x in recs if x['N']==N], key=lambda x:x['M']); print('run2 best N',N, w1(np.array(r['A']),np.array(r['S'])), r['M'])
# references
from structures import references

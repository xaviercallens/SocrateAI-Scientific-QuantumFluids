"""Extra (not registered, exploratory): relaxed HCP/DHCP vs min(FCC,BCC) on a fine parameter grid."""
import json, numpy as np
from lattsum import Kernel
from structures import references
from opt import minimize_structure, energy
R = references()
Ahcp, Shcp, _ = R['HCP']
Adh = Ahcp.copy(); Adh[2] *= 2
Sdh = np.array([[0,0,0],[1/3,2/3,.25],[0,0,.5],[2/3,1/3,.75]])
out = []
for name, xs in (('gauss', np.logspace(-1, 1, 61)), ('yukawa', np.logspace(-1, 1, 61))):
    for x in xs:
        k = Kernel(name, x)
        ef = energy(k, *R['FCC'][:2]); eb = energy(k, *R['BCC'][:2])
        eh = minimize_structure(k, Ahcp, Shcp)[0]
        ed = minimize_structure(k, Adh, Sdh)[0]
        ref = min(ef, eb)
        out.append(dict(kernel=name, param=float(x), E_FCC=ef, E_BCC=eb, E_HCP=eh, E_DHCP=ed,
                        hcp_minus_ref=(eh-ref)/abs(ref), dhcp_minus_ref=(ed-ref)/abs(ref)))
json.dump(out, open('hcp_scan.json', 'w'), indent=1)
for k in ('gauss','yukawa'):
    rr = [o for o in out if o['kernel']==k]
    print(k, 'min (HCP-ref)/E: %.3e at %.4g; min (DHCP-ref)/E: %.3e at %.4g' % (
        min(o['hcp_minus_ref'] for o in rr), min(rr,key=lambda o:o['hcp_minus_ref'])['param'],
        min(o['dhcp_minus_ref'] for o in rr), min(rr,key=lambda o:o['dhcp_minus_ref'])['param']))
    bad=[o for o in rr if o['hcp_minus_ref']<-1e-9 or o['dhcp_minus_ref']<-1e-9]
    print('  points where HCP/DHCP below min(FCC,BCC) by >1e-9:', [(o['param'], o['hcp_minus_ref'], o['dhcp_minus_ref']) for o in bad])

#!/bin/bash
# K-a1 (CVODE rerun, t=16000 at pseudo-transient tolerance), K-a2, K-b, K-d  (PREREG.md + A1)
KR=/mnt/data/xdev-cache/cargo-target-exciton-kr/release/kr
R=$(dirname "$0")/results
G8="M=8 L=8 SIGMA=1.5 V0=0.5 SEED=1"
G16="M=16 L=16 SIGMA=3 V0=0.5 SEED=1"
# K-a1: CVODE rerun at the D-d settings
$KR run $G8 SOLVER=cvode TEND=4000 RTOL=1e-10 ATOL=1e-12 TAG=Ka1_cvode_t4000 OUT=$R/ka1.jsonl STATE=$R/ka1_t4000_cvode.f64 > /dev/null 2>&1
$KR cmp $R/ka1_t4000_kr.f64 $R/ka1_t4000_cvode.f64 > $R/ka1_t4000_cmp.json
# K-a1 t=16000, amendment A1 tolerance
$KR run $G8 TEND=16000 TRACK=1 RTOL=1e-4 ATOL=1e-7 TAG=Ka1_t16000_rtol1e-4 OUT=$R/ka1.jsonl LOG=$R/ka1_t16000_rtol1e-4.log STATE=$R/ka1_t16000_kr.f64 > /dev/null 2>&1
# K-a2
$KR run $G16 SOLVER=cvode TEND=100 RTOL=1e-10 ATOL=1e-12 TAG=Ka2_cvode OUT=$R/ka2.jsonl STATE=$R/ka2_cvode.f64 > /dev/null 2>&1
for rt in 1e-6 1e-7 1e-8; do
  $KR run $G16 TEND=100 RTOL=$rt ATOL=$(python3 -c "print($rt*1e-3)") TAG=Ka2_kr_rtol$rt OUT=$R/ka2.jsonl STATE=$R/ka2_kr_$rt.f64 > /dev/null 2>&1
  $KR cmp $R/ka2_kr_$rt.f64 $R/ka2_cvode.f64 > $R/ka2_cmp_$rt.json
done
# K-b
$KR run $G8 SOLVER=cvode TEND=4 RTOL=1e-12 ATOL=1e-14 TAG=Kb_cvode OUT=$R/kb.jsonl STATE=$R/kb_cvode.f64 > /dev/null 2>&1
for h in 0.2 0.1 0.05 0.025 0.0125; do
  $KR run $G8 TEND=4 FIXEDH=$h RTOL=1e-12 ATOL=1e-14 ETA=1e-3 MAXNEWTON=20 TAG=Kb_h$h OUT=$R/kb.jsonl STATE=$R/kb_h$h.f64 > /dev/null 2>&1
  $KR cmp $R/kb_h$h.f64 $R/kb_cvode.f64 > $R/kb_cmp_h$h.json
done
# K-d (G8, t=20, rtol 1e-7)
$KR run $G8 SOLVER=cvode TEND=20 RTOL=1e-10 ATOL=1e-12 TAG=Kd_cvode OUT=$R/kd.jsonl STATE=$R/kd_cvode.f64 > /dev/null 2>&1
for v in "block:Kd_block:none:exact" "badsign:Kd_badsign:none:exact" "none:Kd_precnone:none:exact" "kin:Kd_prekin:none:exact" "block:Kd_bugrhs:rhs:exact" "block:Kd_bugjac:jac:exact" "block:Kd_fd:none:fd"; do
  IFS=: read prec tag bug jv <<< "$v"
  $KR run $G8 TEND=20 PREC=$prec BUG=$bug JV=$jv TAG=$tag OUT=$R/kd.jsonl STATE=$R/$tag.f64 > /dev/null 2>&1
  $KR cmp $R/$tag.f64 $R/kd_cvode.f64 > $R/${tag}_cmp_cvode.json
  $KR cmp $R/$tag.f64 $R/Kd_block.f64 > $R/${tag}_cmp_block.json
done
echo done > $R/kabd.done

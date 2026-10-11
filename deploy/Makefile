# UNTESTED kit (2026-10-11). Usage from the repository root:  make -f deploy/Makefile smoke | upstream | e12 | e3
JOBS ?= 8
smoke:
	cd exploration/exciton/lean && lake env lean GatedKernel.lean | head -5
	python3 exploration/exciton/python/gated_note_check.py
	python3 exploration/exciton/dimlift/dimlift.py /tmp/smoke_dimlift.jsonl dip square 1 1 direct
upstream:
	@echo "clone openai/math at fd4aeeb2, then: python3 pbuild.py $(JOBS)  (script lives in the build directory; see docs/designs/PROJET_EXECUTION_SERVEUR.md)"
e12:
	cd exploration/exciton/dimlift && bash run_all.sh
e3:
	cd exploration/exciton/dimlift && python3 mesh3d.py results/e3_mesh3d.jsonl 30 432
.PHONY: smoke upstream e12 e3

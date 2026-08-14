import Lake
open Lake DSL

package quantumFluids

/-- Mathlib is PINNED to the SAME revision MechanicaFluidorum's Gate-2
environment compiles against (see that repo's lean_src/lakefile.lean),
so a theorem proved here is checked against the same library every
result in the sibling stream's LEDGER was verified against. -/
require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "6d605ae1ac45de240cdb83ce104fe60b3c1d9237"

@[default_target]
lean_lib QuantumFluidsShell

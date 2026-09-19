import Lake
open Lake DSL

package quantumFluids

/-- Mathlib is PINNED to tag v4.34.0-rc2 (2026-09-19 migration, owner decision, to
align all streams on one toolchain and allow cross-stream integration; same
revision as the OpenAI NavierStokesAndEuler tree). Before the migration the pin
was 6d605ae1 (Lean 4.33.0-rc2), which matched MechanicaFluidorum's Gate 2; that
sibling is expected to follow. -/
require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "85e3a25e006c35636f0e53b0e9296caca2685bc0"  -- tag v4.34.0-rc2

@[default_target]
lean_lib QuantumFluidsShell

#!/usr/bin/env bash
# Install the Comparator toolchain (landrun, lean4export, nanoda_bin, comparator) into $TOOLS.
# Idempotent. Never uses sudo. Refuses to run unless $TOOLS is a writable directory that is NOT on
# the small root filesystem. Versions: Lean/lean4export/comparator tag v4.34.0-rc2.
#
#   TOOLS=/media/xavkal/<disk>/xavkal-tools bash scripts/install_comparator_tools.sh
set -euo pipefail
: "${TOOLS:?set TOOLS to a user-writable directory on the large disk}"
LEAN_TAG="${LEAN_TAG:-v4.34.0-rc2}"
GO_VER="${GO_VER:-go1.27.1}"
[ -d "$TOOLS" ] && [ -w "$TOOLS" ] || { echo "ERROR: $TOOLS is not a writable directory"; exit 1; }
root_dev=$(stat -c %d /); tools_dev=$(stat -c %d "$TOOLS")
[ "$root_dev" != "$tools_dev" ] || { echo "ERROR: $TOOLS is on the root filesystem (7 GB free); use the large disk"; exit 1; }
mkdir -p "$TOOLS"/{src,bin,go}
cd "$TOOLS/src"

# 1. Go (needed only to build landrun)
if [ ! -x "$TOOLS/go/bin/go" ]; then
  curl -fsSL "https://go.dev/dl/${GO_VER}.linux-amd64.tar.gz" -o "$TOOLS/go.tgz"
  rm -rf "$TOOLS/go" && tar -C "$TOOLS" -xzf "$TOOLS/go.tgz" && rm "$TOOLS/go.tgz"
fi
export PATH="$TOOLS/go/bin:$PATH" GOPATH="$TOOLS/gopath" GOCACHE="$TOOLS/gocache"

# 2. landrun, from main (README requirement)
[ -d landrun ] || git clone --depth 1 https://github.com/Zouuup/landrun.git
( cd landrun && go build -o "$TOOLS/bin/landrun" ./cmd/landrun )

# 3. lean4export at the tag matching the toolchain
[ -d lean4export ] || git clone --branch "$LEAN_TAG" --depth 1 https://github.com/leanprover/lean4export.git
( cd lean4export && lake build && cp .lake/build/bin/lean4export "$TOOLS/bin/" )

# 4. nanoda_bin (second, independent kernel)
[ -d nanoda_lib ] || git clone --depth 1 https://github.com/ammkrn/nanoda_lib.git
( cd nanoda_lib && cargo build --release && cp target/release/nanoda_bin "$TOOLS/bin/" )

# 5. comparator itself, same tag (depends only on lean4export, no Mathlib)
[ -d comparator ] || git clone --branch "$LEAN_TAG" --depth 1 https://github.com/leanprover/comparator.git
( cd comparator && lake build && cp .lake/build/bin/comparator "$TOOLS/bin/" )

echo "Installed into $TOOLS/bin:"; ls -l "$TOOLS/bin"
echo "Add to PATH:  export PATH=$TOOLS/bin:\$PATH"

#!/usr/bin/env bash
# Lokaler Blender-Build.
#   ./build.sh               → Modell (web/models), Vorschaubilder, Icons, blender/verkupfern.blend
#   ./build.sh --no-render   → ohne Vorschaubilder/Icons (schnell)
#   ./build.sh --video       → zusätzlich beide Videos (Szenen bauen, Einzelbilder rendern ≈ 30 min, MP4 mit Texten)
# Blender-Pfad überschreibbar:  BLENDER=/opt/blender/blender ./build.sh
set -euo pipefail
cd "$(dirname "$0")"
BLENDER="${BLENDER:-blender}"
"$BLENDER" --version | head -1
ARGS=()
for a in "$@"; do [ "$a" != "--video" ] && ARGS+=("$a"); done
"$BLENDER" -b --factory-startup --python-exit-code 1 --python blender/build_verkupfern.py -- "${ARGS[@]}"
if [[ " $* " == *" --video "* ]]; then
  for v in 1 2; do
    "$BLENDER" -b --factory-startup --python-exit-code 1 --python blender/build_verkupfern.py -- --video$v
    rm -rf video/frames$v && mkdir -p video/frames$v
    "$BLENDER" -b blender/video$v.blend -a
    python3 video/video_overlay.py $v
  done
fi
ls -la web/models web/img

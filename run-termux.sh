#!/data/data/com.termux/files/usr/bin/bash
# Start BLACK VOID locally, with an optional narrowly-scoped LAN transfer link.
set -eu
cd "$(dirname "$0")"

if ! command -v python >/dev/null 2>&1; then
  echo "Python is missing. Install it with: pkg install python"
  exit 1
fi
if ! python -c "import numpy" >/dev/null 2>&1; then
  if command -v pkg >/dev/null 2>&1; then
    echo "Installing Termux's prebuilt NumPy package..."
    pkg install -y python-numpy
  else
    echo "NumPy is missing. Install it with your system package manager."
    exit 1
  fi
fi

for tool in ffmpeg ffprobe; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "$tool is missing. Install the Termux package: pkg install ffmpeg"
    exit 1
  fi
done

echo "Checking Python dependencies..."
python -m pip install --disable-pip-version-check -r requirements.txt

HOST="127.0.0.1"
LAN_TOKEN=""
echo
echo "Enable one-file LAN transfer for another device on your trusted Wi-Fi?"
echo "Remote devices will only be able to open a token-protected source ZIP link."
printf "Enable LAN transfer? [y/N]: "
if [ -t 0 ]; then
  read -r answer || answer="n"
else
  answer="n"
fi
case "$answer" in
  y|Y|yes|YES)
    HOST="0.0.0.0"
    LAN_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(24))')"
    echo
    echo "LAN transfer is ON. Keep this link private and use a trusted Wi-Fi network."
    if command -v ip >/dev/null 2>&1; then
      echo "Phone IPv4 address(es):"
      ip -o -4 addr show scope global | awk '{sub(/\/.*/, "", $4); print "  http://" $4 ":'"${PORT:-8000}"'"}'
    else
      echo "Find your phone's Wi-Fi IPv4 address in Android network settings."
    fi
    ;;
  *)
    echo "LAN transfer is OFF; the app is accessible only on this phone."
    ;;
esac

echo
echo "BLACK VOID / PS4 Theme Creator"
echo "On this phone open http://127.0.0.1:${PORT:-8000}"
echo "Keep Termux open while using the app. Press Ctrl+C to stop."
echo
if [ -n "$LAN_TOKEN" ]; then
  exec env BLACK_VOID_LAN_TOKEN="$LAN_TOKEN" python -m uvicorn app.main:app --host "$HOST" --port "${PORT:-8000}"
fi
exec python -m uvicorn app.main:app --host "$HOST" --port "${PORT:-8000}"

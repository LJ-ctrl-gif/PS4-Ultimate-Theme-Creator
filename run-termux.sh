#!/data/data/com.termux/files/usr/bin/bash
# Start the PS4 Theme Creator locally in Termux.
set -eu
cd "$(dirname "$0")"

if ! command -v python >/dev/null 2>&1; then
  echo "Python is missing. Install it with: pkg install python"
  exit 1
fi
for tool in ffmpeg ffprobe; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "$tool is missing. Install the Termux package: pkg install ffmpeg"
    exit 1
  fi
done

echo "Checking Python dependencies..."
python -m pip install --disable-pip-version-check -r requirements.txt

echo
echo "BLACK VOID / PS4 Theme Creator"
echo "Open http://127.0.0.1:8000 in your Android browser."
echo "Keep Termux open while using the app. Press Ctrl+C to stop."
echo
exec python -m uvicorn app.main:app --host 127.0.0.1 --port "${PORT:-8000}"

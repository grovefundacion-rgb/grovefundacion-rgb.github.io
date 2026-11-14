# args: voice idx text window
v=$1; i=$2; text=$3; win=$4
for r in -3 +0 +4 +8 +12; do
  edge-tts --proxy "$HTTPS_PROXY" --voice es-CO-${v}Neural --rate=${r}% --text "$text" --write-media vo2/${v}_$i.mp3 2>/dev/null
  ffmpeg -v error -y -i vo2/${v}_$i.mp3 -af "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" -ar 48000 -ac 1 vo2/${v}_$i.wav
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 vo2/${v}_$i.wav)
  if python3 -c "import sys;sys.exit(0 if $d<=$win else 1)"; then break; fi
done
echo "$v $i rate=$r dur=$d win=$win"

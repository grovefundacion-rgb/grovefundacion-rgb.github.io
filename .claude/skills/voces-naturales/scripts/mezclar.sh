#!/usr/bin/env bash
# Pone una locución sobre un video.
# Uso: mezclar.sh video.mp4 voz.wav salida.mp4 [volumen_fondo]
#   Sin volumen_fondo, el audio original se reemplaza por la voz.
#   Con volumen_fondo (ej. 0.15), se conserva el audio original a ese volumen, debajo de la voz.
set -euo pipefail
[ $# -lt 3 ] && { sed -n '2,5p' "$0"; exit 1; }
video="$1"; voz="$2"; salida="$3"; fondo="${4:-}"

if [ -z "$fondo" ] || ! ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$video" | grep -q .; then
  ffmpeg -y -loglevel error -i "$video" -i "$voz" \
    -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest "$salida"
else
  ffmpeg -y -loglevel error -i "$video" -i "$voz" \
    -filter_complex "[0:a]volume=${fondo}[bg];[bg][1:a]amix=inputs=2:duration=first:normalize=0[a]" \
    -map 0:v:0 -map "[a]" -c:v copy -c:a aac -b:a 192k "$salida"
fi
echo "Listo: $salida"

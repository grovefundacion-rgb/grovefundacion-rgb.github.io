#!/usr/bin/env python3
"""Genera una locución con VoiceStudio (endpoint compatible con OpenAI).

Uso:
  python3 tts.py guion.txt salida.wav [--voice ID] [--model tts-1]
        [--url http://localhost:3900] [--format wav]

Si OMNIVOICE_API_KEY está definida, se envía como Bearer token.
Los guiones largos se dividen por párrafos y los WAV resultantes se unen con ffmpeg.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

MAX_CHARS = 1500


def trozos(texto):
    """Divide el texto por párrafos, agrupándolos hasta MAX_CHARS."""
    bloques, actual = [], ""
    for p in [p.strip() for p in texto.split("\n\n") if p.strip()]:
        if actual and len(actual) + len(p) + 2 > MAX_CHARS:
            bloques.append(actual)
            actual = p
        else:
            actual = f"{actual}\n\n{p}" if actual else p
    if actual:
        bloques.append(actual)
    return bloques


def sintetizar(url, texto, voz, modelo, formato):
    body = json.dumps({"model": modelo, "voice": voz, "input": texto,
                       "response_format": formato}).encode()
    req = urllib.request.Request(f"{url.rstrip('/')}/v1/audio/speech", data=body,
                                 headers={"Content-Type": "application/json"})
    clave = os.environ.get("OMNIVOICE_API_KEY")
    if clave:
        req.add_header("Authorization", f"Bearer {clave}")
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Error {e.code} de VoiceStudio: {e.read()[:500].decode(errors='replace')}")
    except urllib.error.URLError as e:
        sys.exit(f"No se pudo conectar con VoiceStudio en {url} ({e.reason}). ¿Está corriendo?")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("salida")
    ap.add_argument("--voice", default="alloy")
    ap.add_argument("--model", default="tts-1")
    ap.add_argument("--url", default=os.environ.get("VOICESTUDIO_URL", "http://localhost:3900"))
    ap.add_argument("--format", default="wav")
    a = ap.parse_args()

    with open(a.guion, encoding="utf-8") as f:
        partes = trozos(f.read())
    if not partes:
        sys.exit("El guion está vacío.")

    if len(partes) == 1:
        with open(a.salida, "wb") as f:
            f.write(sintetizar(a.url, partes[0], a.voice, a.model, a.format))
    else:
        with tempfile.TemporaryDirectory() as tmp:
            lista = os.path.join(tmp, "lista.txt")
            with open(lista, "w") as l:
                for i, p in enumerate(partes):
                    print(f"Generando parte {i + 1}/{len(partes)}…", file=sys.stderr)
                    ruta = os.path.join(tmp, f"{i:03d}.{a.format}")
                    with open(ruta, "wb") as f:
                        f.write(sintetizar(a.url, p, a.voice, a.model, a.format))
                    l.write(f"file '{ruta}'\n")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                            "-i", lista, a.salida], check=True)
    print(f"Listo: {a.salida}")


if __name__ == "__main__":
    main()

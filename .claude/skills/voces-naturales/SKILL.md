---
name: voces-naturales
description: Genera voces naturales (locución / voz en off) para videos de Fundación Grove con VoiceStudio (github.com/debpalash/VoiceStudio), un estudio de voz open-source y 100% local. Úsala cuando pidan "ponle voz a este video", "genera la narración", "voz en off", "doblaje", "clonar voz" o "texto a voz".
---

# Voces naturales para videos (VoiceStudio)

**Fuente:** https://github.com/debpalash/VoiceStudio (AGPL-3.0, gratis y local; motor por defecto: k2-fsa/OmniVoice).
Lo que hace: **clonar voz** a partir de unos segundos de audio, **diseñar voces** con controles, **generar** audio a partir de texto, y también doblar videos, transcribir y crear audiolibros.

> ⚠️ Regla de uso: solo se clona una voz **con permiso de su dueño**. Su licencia prohíbe expresamente la suplantación, el fraude y la clonación sin autorización.

## 1. Levantar VoiceStudio

### Opción A: app de escritorio (lo más fácil, para el equipo)
- **Mac (Apple Silicon, macOS 13.3+):** `brew tap debpalash/tap && brew install --cask debpalash/tap/voicestudio`
- **Windows 10/11 / Linux:** descarga el instalador desde la página de *Releases* del repo. Los binarios no están firmados, así que Windows mostrará un aviso de SmartScreen.
- Funciona sin GPU, aunque con CPU es más lento.

### Opción B: Docker (para scripts y automatización)
```bash
export OMNIVOICE_API_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
docker pull ghcr.io/debpalash/voicestudio:stable
docker run -d --name omnivoice \
  -p 127.0.0.1:3900:3900 \
  -e OMNIVOICE_API_KEY="$OMNIVOICE_API_KEY" \
  -e OMNIVOICE_DATA_DIR=/app/omnivoice_data \
  -v omnivoice-data:/app/omnivoice_data \
  ghcr.io/debpalash/voicestudio:stable
docker logs -f omnivoice   # la primera vez descarga ~2.4 GB de modelos
curl http://localhost:3900/health
```
- Con GPU NVIDIA: añade `--gpus all` (requiere NVIDIA Container Toolkit).
- La interfaz web queda en http://localhost:3900.
- Desde la misma máquina (loopback) la API no pide clave; desde otra máquina, envía `Authorization: Bearer $OMNIVOICE_API_KEY`.

## 2. Flujo para ponerle voz a un video

1. **Escribir el guion** en un `.txt`, en español natural: frases cortas, puntuación clara y los números escritos como se leen ("dos mil veintiséis").
2. **Elegir o crear la voz** en la interfaz de VoiceStudio:
   - *Voice Design*: crear una voz nueva con los controles.
   - *Voice Clone*: subir unos segundos de audio limpio de una persona que haya dado su autorización.
   - Para ver las voces disponibles: `curl http://localhost:3900/v1/audio/voices`
3. **Generar el audio:**
   ```bash
   python3 .claude/skills/voces-naturales/scripts/tts.py guion.txt voz.wav --voice "<id-de-voz>"
   ```
   El script usa el endpoint compatible con OpenAI, `POST /v1/audio/speech`, con un cuerpo como `{"model","voice","input","response_format"}`.
4. **Montar la voz sobre el video:**
   ```bash
   bash .claude/skills/voces-naturales/scripts/mezclar.sh video.mp4 voz.wav salida.mp4          # reemplaza el audio
   bash .claude/skills/voces-naturales/scripts/mezclar.sh video.mp4 voz.wav salida.mp4 0.15     # conserva la música original al 15 %
   ```
5. **Revisar** que no haya pronunciaciones raras (nombres propios, siglas). Si las hay, reescribe esa frase de forma fonética y vuelve a generar.

## Pendiente de confirmar en la documentación
- La sintaxis exacta del CLI `voicestudio`, que existe desde la v0.5.8, y la ruta de la API para clonar voces. Por ahora, clona desde la interfaz.
- Si `/v1/audio/speech` acepta un campo de idioma. Si el resultado sale con acento extraño, elige en el *Model Manager* un motor con buen español (por ejemplo, Ming-3.0-tts en GPU NVIDIA).

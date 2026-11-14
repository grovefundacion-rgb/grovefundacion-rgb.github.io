# Receta: video narrado con voz natural

Así se hizo el reel de seguridad social (noviembre 2026).

## Requisito de red
Abrir la sesión de Claude con el entorno **"Videos con voz natural"**, que permite
`speech.platform.bing.com` (voces de Microsoft) y Hugging Face.

## Voz
- `pip install edge-tts`
- Voces colombianas: `es-CO-SalomeNeural` (mujer) y `es-CO-GonzaloNeural` (hombre), con `--rate=-3%`.
- Voces más expresivas que también hablan español: `en-US-AvaMultilingualNeural`,
  `en-US-EmmaMultilingualNeural`, `en-US-AndrewMultilingualNeural`, `en-US-BrianMultilingualNeural`.
- En el proxy de Claude hay que pasar `--proxy "$HTTPS_PROXY"`.

## Pasos
1. `guion.txt`: una frase por escena, con el segundo en que empieza (`segundo|texto`).
   Guion descriptivo, no literal: no se lee el texto de la pantalla.
2. `ajustar_voz.sh`: genera cada frase, recorta silencios y sube la velocidad solo si no cabe en su escena.
3. `musica_y_efectos.py`: canción reflexiva en tono menor y efectos sincronizados con cada animación.
4. `final_arbol.py`: final con el logo (cae la semilla, crece el tronco con las ramas, salen las hojas verdes y luego las naranjas).
5. `mezclar_voz.py`: baja la música unos 8 dB mientras habla la voz; luego `ffmpeg` con `loudnorm=I=-14` para Instagram.

## Publicar en Instagram
En el texto del post, escribir los hashtags con `#` normal; la herramienta de Composio pide `%23`, pero lo publica literal.

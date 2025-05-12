# Telegram YouTube Downloader Bot

Este bot de Telegram te permite buscar y descargar videos o audios de YouTube.

## Características
- Busca por nombre o link
- Elige entre audio o video
- Recibe el archivo directamente en Telegram
- Reinicia el estado después de cada descarga

## Cómo usar en Render
1. Crea un nuevo Web Service
2. Start command: `gunicorn main:app`
3. Sube tu `.env` con tu token
4. Configura el webhook:

```
https://api.telegram.org/botTU_TOKEN/setWebhook?url=https://TU_SUBDOMINIO.onrender.com/TU_TOKEN
```
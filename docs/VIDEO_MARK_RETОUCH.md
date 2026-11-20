# Mask-guided video mark retouch

Endpoint: `POST /api/retouch/remove-mark`

Multipart fields:
- `video`: source MP4
- `mask`: MP4 mask matching source dimensions, duration, frame count and FPS. White marks pixels to inpaint; black leaves pixels unchanged.

The endpoint is authenticated by the existing API middleware. It uses OpenCV inpainting per frame and FFmpeg to restore the original audio. The mask must be created and tracked externally; this endpoint does not infer tattoo locations or distinguish people automatically.

Example:
```bash
curl -X POST 'https://YOUR-STUDIO/api/retouch/remove-mark' \
  -b 'studio_session=YOUR_SESSION_COOKIE' \
  -F 'video=@source.mp4' \
  -F 'mask=@tracked-mask.mp4'
```

The returned workspace path can be retrieved through the Studio media-serving flow.

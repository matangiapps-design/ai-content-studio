# MATANGI AI Android app

This is a separate Android application module in this repository. It does not replace the existing MATANGI Creator Studio app.

## Build
GitHub Actions builds a debug APK when files under `matangi-ai-app/` change, or when the workflow is manually run.

Open **Actions → Build MATANGI AI APK** and download the `MATANGI-AI-debug-APK` artifact after a successful run.

## AI server
The app expects an OpenAI-compatible chat completions endpoint:
- Base URL: HTTPS URL ending in `/v1` (for example, your server's `https://host/v1`)
- Chat route: `/chat/completions`
- Model: exact model identifier configured by the server
- Optional bearer token

The model runs on the cloud server, not on the Android device. Do not publish API tokens in source code or screenshots. This first build is a debug APK for private testing, not a Play Store-signed release.

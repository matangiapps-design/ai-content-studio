# ODIA HERO — Production Pack

This folder adds the first ODIA HERO production brief to MATANGI AI Content Studio.

## Film 01
**Title:** Biku — The Little Hero of Rath Yatra  
**Odia title:** ବିକୁ — ରଥଯାତ୍ରାର ଛୋଟ ବୀର  
**Exact target runtime:** 04:04 (244 seconds)  
**Format:** 16:9 landscape; final delivery target 3840×2160 (4K UHD), 24 fps  
**Animation:** 3D animated stickman characters only; no live-action actors  
**Video model target:** Wan 3.0, subject to an available provider endpoint/account

## Character bible
Biku is a small white stickman hero with a round white head, expressive black eyes, thin black arms and legs, and a bright red cape. Keep the same silhouette, face, cape, proportions and colours in every shot. Children are stylised animated characters. The story is family-friendly.

## Story
During Puri's Jagannath Rath Yatra, heavy rain begins and three children become separated from their family. Biku notices them, calmly reassures them, keeps them together in a safe place and alerts event volunteers. Volunteers follow the event's lost-child procedure and reunite the children with their mother. Biku watches the Rath from a safe viewing area. The message: a true hero helps others.

## Runtime / edit map
| Timecode | Duration | Beat |
|---|---:|---|
| 00:00–00:20 | 20s | Establish Puri Rath Yatra; chariots, flags, devotional atmosphere |
| 00:20–00:40 | 20s | Introduce Biku walking into the festival |
| 00:40–01:00 | 20s | Biku admires the Rath from a safe viewing area |
| 01:00–01:20 | 20s | Clouds gather; rain begins |
| 01:20–01:40 | 20s | Three children realise they are separated |
| 01:40–02:00 | 20s | Biku notices the frightened children |
| 02:00–02:20 | 20s | Biku comforts them and asks them to stay together |
| 02:20–02:40 | 20s | Biku signals nearby event volunteers |
| 02:40–03:00 | 20s | Volunteers take charge at the official help point |
| 03:00–03:20 | 20s | Volunteers locate and contact the family |
| 03:20–03:40 | 20s | Emotional family reunion |
| 03:40–04:04 | 24s | Biku's hero moment, moral and “Jai Jagannath” end card |

## Wan 3.0 scene-generation guidance
Generate short shots individually rather than asking the model for a continuous four-minute clip. Use the same approved Biku reference image and the same character description on every shot. Generate at the provider's supported resolution and duration; stitch shots in the editor. Do not label an upscaled file as native 4K.

**Base prompt**
> Cinematic 3D animated family film, Puri Odisha Jagannath Rath Yatra setting, authentic colourful decorated chariots and flags, respectful devotional atmosphere. Biku is the exact same small white stickman hero from the supplied reference: round white head, expressive black eyes, thin black arms and legs, bright red cape. Preserve his exact proportions, face, cape and colours. Fluid readable character animation, natural cape movement, expressive acting, detailed environment, cinematic lighting, smooth camera movement, 16:9 landscape, no captions, no logos, no watermark, no live-action people.

**Continuity / negative prompt**
> No character redesign, no missing or changed red cape, no extra limbs, no face deformation, no flicker, no inconsistent scale, no unreadable text, no watermark, no live-action actors, no dangerous crowd behaviour, no children running into a moving chariot, no one touching or attempting to move the Rath wheel. Respect Jagannath culture and symbols.

## Audio and post-production
- Odia narration: natural, clear, warm storyteller delivery; verify pronunciation with a native Odia speaker.
- Add licensed/original devotional instrumental music and subtle crowd, rain and bell ambience.
- Keep dialogue clearly above music; mix and loudness-check on phone speakers.
- Add accurate Odia subtitles and an optional English subtitle track.
- Edit to exactly 244 seconds; use short transitions and avoid stretching low-quality shots.
- Export 3840×2160 only after a quality-controlled upscale; retain the highest-quality master.
- Review all cultural details, spelling, character continuity, audio rights and child-safety depiction before release.

## Shorts cut-downs
1. **Biku notices the children** — 35s, vertical 9:16.
2. **The rain and the rescue** — 35s, vertical 9:16.
3. **The family reunion** — 40s, vertical 9:16.
4. **What makes a hero?** — 30s, vertical 9:16.

## Publishing metadata
**YouTube title:** BIKU — ରଥଯାତ୍ରାର ଛୋଟ ବୀର ❤️ | Odia Animated Story | Jagannath Rath Yatra

**Description:**  
ଏକ ଛୋଟ ଷ୍ଟିକମ୍ୟାନ୍, ଏକ ବଡ଼ ସାହସ ଏବଂ ଏକ ଅବିସ୍ମରଣୀୟ ରଥଯାତ୍ରା କାହାଣୀ। ବିକୁ କିପରି ଭୟଭୀତ ପିଲାମାନଙ୍କୁ ସାହାଯ୍ୟ କଲା, ଦେଖନ୍ତୁ ଏହି ହୃଦୟସ୍ପର୍ଶୀ ଓଡ଼ିଆ ଆନିମେସନ୍। ଜୟ ଜଗନ୍ନାଥ!

#OdiaHero #OdiaAnimation #JagannathRathYatra #OdiaStory #Biku #JaiJagannath

## Important implementation boundary
This is a production brief and prompt pack. It does not itself call Wan, create video files, or publish to social accounts. Add a provider adapter only after the Wan endpoint, authentication method, model identifier and account permissions are verified. Keep API keys in server-side environment variables; never commit secrets.

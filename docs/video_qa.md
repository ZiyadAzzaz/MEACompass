# Competition video QA

Status: **FINAL MEDIA PASS — HUMAN VIEWING APPROVAL REQUIRED BEFORE TAG**.

## Final deliverable

- File: `docs/media/MEACompass_Competition_Video.mp4`
- Public player: <https://ziyadazzaz.github.io/MEACompass/video/>
- Duration: 233.13 seconds (3:53.13), below the five-minute maximum
- Resolution: 1920×1080
- Frame rate: 30 fps
- Video: H.264 High, progressive, yuv420p
- Audio: AAC-LC, 48 kHz, mono, approximately 150 kb/s
- Audio loudness: −17.2 LUFS integrated; −1.4 dBTP true peak; 3.3 LU range
- Captions: 29 English cues and 29 Chinese cues
- Embedded tracks: English (default) and Chinese
- WebVTT tracks: `docs/video/captions-en.vtt` and `captions-zh.vtt`
- Source SRTs: `docs/video_script_en.srt` and `docs/video_script_zh.srt`
- File size: 7,908,838 bytes (7.54 MiB)

## Production record

Ziyad Azzaz recorded the English narration. The raw recording was preserved in
an ignored production directory and was never committed. Audio processing used
free local FFmpeg tools: high/low-pass filtering, loudness normalization, and
removal of one clearly repeated false start. No sentence was synthesized or
replaced. No paid service, music, synthetic voice, stock media, third-party
logo, or external footage was used.

Visuals are rendered project-authored competition slides plus the authentic
logged-out public-demo capture already documented in `docs/deck_qa.md`. Browser
control was unavailable during final assembly, so the video does not claim a
new live selector recording. The verified capture and registered failure-case
evidence are shown instead.

## Mechanical QA

- [x] Duration is below five minutes.
- [x] 1920×1080, 30 fps, H.264/AAC browser-compatible output.
- [x] Fast-start metadata permits progressive web playback.
- [x] No black interval of 0.5 seconds or longer was detected.
- [x] No unexpected silence of 2.5 seconds or longer was detected.
- [x] Final narration is normalized without clipping.
- [x] Full contact-sheet review shows the intended evidence sequence.
- [x] Demo evidence appears within the first minute.
- [x] Locked gains, interval coverage, and three-of-five limitation are visible.
- [x] Gate S stop, rat-MEA scope, non-human/non-OoC boundary, and
  non-autonomous-use language remain visible.
- [x] English and Chinese captions contain 29 non-overlapping cues within the
  video duration.
- [x] Chinese first mention uses “最强基线 BT+” and “平均绝对误差（MAE）”.
- [x] The final MP4 contains selectable English and Chinese subtitle streams.
- [ ] Ziyad Azzaz watches the public player from beginning to end and approves
  voice, timing, and both caption tracks before `v1.0.0-submission`.

## Rights and scientific boundary

All visuals, interface captures, model outputs, narration, and captions are
project-authored. This is research decision support using rat cortical neural
MEA data. It is not human or organ-on-chip validation and not an autonomous
assay-termination system.

# mcp research recheck for your pygame-ce setup

last rechecked: 2026-02-18

## scope and method
- goal: find mcp servers (installed + external) and skill packs that best support your workflow:
  - custom maps (tiled/ldtk)
  - custom sprites/animations (aseprite/pixel art)
  - custom sfx/audio
- method:
  - rediscovered currently available mcp tools in this session
  - validated external candidates with live github repo metadata (stars, update recency, archival state)
  - cross-checked official map editor docs for non-mcp fallback pipeline quality (tiled + ldtk)

## what is currently available in your environment

detected mcp servers in-session:
- `pycharm`
- `playwright`
- `context7`
- `svelte`
- `openaiDeveloperDocs`
- `codex_apps`

fit for your game pipeline:
- strong: `pycharm` (code/project ops)
- medium: `context7` (library docs lookup)
- low/none for sprites/maps/sfx directly: `playwright`, `svelte`, `openaiDeveloperDocs`, `codex_apps`

bottom line: your current installed mcp set does **not** include dedicated map/sprite/sfx servers yet.

## external mcp candidates (rechecked)

### 1) sprite + animation (aseprite/pixel art)

| mcp | stars | last push (utc) | fit | notes |
|---|---:|---|---|---|
| `diivi/aseprite-mcp` | 118 | 2025-09-02 | high | good baseline aseprite api bridge |
| `willibrandon/pixel-mcp` | 22 | 2025-10-18 | **very high** | pixel-art oriented, sprite/spritesheet workflow focus |
| `ext-sakamoro/AsepriteMCP` | 15 | 2025-06-21 | medium | smaller ecosystem |
| `mine3911/MCP-Aseprite` | 1 | 2025-04-01 | low | very early adoption |

verdict:
- best primary pick for your use case: `willibrandon/pixel-mcp`
- best fallback/general api option: `diivi/aseprite-mcp`

### 2) maps (tiled/ldtk/tilemaps)

| mcp | stars | last push (utc) | fit | notes |
|---|---:|---|---|---|
| `SubZeroX9/tiled-mcp-server` | 0 | 2026-02-15 | experimental | promising scope (tmx/tmj/tsx/tsj), but no adoption signal yet |
| `phaserjs/editor-mcp-server` | 25 | 2025-09-19 | low-medium | stronger activity, but phaser-editor-centric (not pygame-first) |
| `DjinnFoundry/godot-map-cli` | 0 | 2026-02-14 | low | godot tilemap specific |

ldtk status:
- no mature, widely adopted dedicated ldtk mcp stood out in current search.

verdict:
- for production stability today: use **native Tiled/LDtk export pipeline** + python importer in your game.
- treat `SubZeroX9/tiled-mcp-server` as optional experimental tooling only.

### 3) sfx/audio/voice

| mcp | stars | last push (utc) | fit | notes |
|---|---:|---|---|---|
| `egoist/ffmpeg-mcp` | 120 | 2025-03-29 | high | clean ffmpeg bridge, local deterministic processing |
| `video-creator/ffmpeg-mcp` | 118 | 2025-05-13 | high | broad ffmpeg operation support |
| `misbahsy/video-audio-mcp` | 61 | 2025-05-24 | medium-high | practical audio/video transforms |
| `am0y/mcp-fal` | 74 | 2026-02-15 | high (cloud gen) | active fal.ai integration |
| `raveenb/fal-mcp-server` | 31 | 2025-12-23 | medium-high (cloud gen) | broader media generation scope |
| `elevenlabs/elevenlabs-mcp` | 1217 | 2026-01-15 | very high (voice) | official server, strongest adoption |
| `mberg/kokoro-tts-mcp` | 73 | 2025-09-12 | medium-high (local-ish tts) | useful if you want non-elevenlabs voice path |

verdict:
- local sfx pipeline: `egoist/ffmpeg-mcp` (or `video-creator/ffmpeg-mcp`)
- ai-generated music/sfx: `am0y/mcp-fal` (currently stronger activity signal than `raveenb/fal-mcp-server`)
- voice/dialogue: `elevenlabs/elevenlabs-mcp`

## skills that can help (from your skill catalog)

already installed:
- `playwright`, `screenshot`, `doc`, `pdf`, `spreadsheet`, `openai-docs`, etc.

not installed but relevant:
- `imagegen` (sprite/concept generation workflows)
- `speech` (voice generation workflows)
- `transcribe` (audio-to-text pipeline for iteration/testing)
- `develop-web-game` (less relevant for pygame runtime, but can still help rapid prototyping ideas/assets)
- `sora` (video generation, mostly ancillary for trailers/promos)

## other discovered MCPs (not recommended for your stack)

- `keiver/image-tiler-mcp-server`: image tiling for llm vision, not game map authoring.
- `DjinnFoundry/godot-map-cli` and `Ekaitzsegurola/godot-tilemap-mcp`: godot-specific tilemap workflows, poor fit for pygame.
- `flynnsbit/PixelLab-MCP`: very early/low adoption signal.
- `video-editing` oriented MCPs (for example `burningion/video-editing-mcp`): useful for trailers/media workflows, not core 2d game asset pipeline.

## best stack for *your* setup (recommended)

1. sprite workflow:
   - primary: `pixel-mcp`
   - backup/control-heavy: `aseprite-mcp`
2. map workflow:
   - production: Tiled or LDtk native exports (`json/tmx`) + python loader in pygame
   - optional experiment: `tiled-mcp-server`
3. sfx workflow:
   - local deterministic editing/batching: `ffmpeg-mcp` (`egoist` or `video-creator`)
   - optional ai generation: `mcp-fal`
4. voice workflow (if needed):
   - `elevenlabs-mcp`
5. skill add-ons:
   - install `imagegen`, `speech`, `transcribe`

## risk notes
- map MCP ecosystem is still immature compared to sprite/audio MCP options.
- many MCP repos are very new; pin versions/commits before relying in production.
- cloud MCPs (fal/elevenlabs) add cost + key management overhead; keep a local ffmpeg path as fallback.

## sources

### local capability checks
- in-session mcp tool discovery (`search_tool_bm25`) and resource checks (`list_mcp_resources` / `list_mcp_resource_templates`) during this recheck session.
- local skill catalog:
  - `python C:/Users/ium/.codex/skills/.system/skill-installer/scripts/list-skills.py --format text`

### external references
- sprite MCPs:
  - https://github.com/diivi/aseprite-mcp
  - https://github.com/willibrandon/pixel-mcp
  - https://github.com/ext-sakamoro/AsepriteMCP
- map MCP/editor references:
  - https://github.com/SubZeroX9/tiled-mcp-server
  - https://github.com/phaserjs/editor-mcp-server
  - https://doc.mapeditor.org/en/stable/reference/json-map-format/
  - https://ldtk.io/docs/
- audio/voice/generation MCPs:
  - https://github.com/egoist/ffmpeg-mcp
  - https://github.com/video-creator/ffmpeg-mcp
  - https://github.com/misbahsy/video-audio-mcp
  - https://github.com/am0y/mcp-fal
  - https://github.com/raveenb/fal-mcp-server
  - https://github.com/elevenlabs/elevenlabs-mcp
  - https://github.com/mberg/kokoro-tts-mcp

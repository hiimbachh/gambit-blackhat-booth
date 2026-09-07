# V4.2 update

Current scene: Deliverables/v4.2/Gambit_BlackHat_v4.2.blend. Its ssets.json and screens.json remain authoritative. The roof bars have individual plan rotations and offsets; all materials and full-length playback settings are unchanged from v4.1. The v4.1 loop tests below remain valid, and v4.2 validates the unchanged media fingerprints.

---

# Materials, media and project folders

## Current scene

Open `Deliverables/v4.1/Gambit_BlackHat_v4.1.blend`. The user-edited v4 is preserved beside it in `Deliverables/v4/`.

- `Roof | Photo-based stacked blocks`: ten separate blocks, arranged in five alternating courses.
- `Roof | Replaceable display faces`: eight roof-only media faces, parented to their blocks.
- Existing booth collections, finishes, shared materials, static screens and playback settings are preserved.
- `Deliverables/v4.1/assets.json` lists each material and the objects using it.
- `Deliverables/v4.1/screens.json` lists actual object names, assigned media, and static/movie status. Legacy duplicate screen IDs are retained; use the full object name to identify a display.

Only zero-user materials and image datablocks were purged. Used materials were neither merged nor renamed, so intentional sharing stays intact. Some old `MEDIA_` numbers differ from their current object IDs because the user reassigned them; the inventory records the real assignments.

## Roof playback

The scene stays at the user's 60 fps and frames 1–720.

| Roof content | Source | Full clip length | Duration |
| --- | --- | --- | --- |
| Blue logo ends | A1.mov | 602 frames | 10.033 seconds |
| Red long face | D1.mov | 420 frames | 7 seconds |
| Red end | D2.mov | 420 frames | 7 seconds |
| Dotted ends | E1.mov | 420 frames | 7 seconds |
| Dotted long faces | E2.mov | 420 frames | 7 seconds |

Each roof movie starts at frame 1, has offset 0, and uses its full source length with cyclic playback and auto-refresh. Its native frame rate matches the scene. `loop_boundary_check.json` records rendered checks of the final frame and restart. Existing non-roof timing is intentionally untouched, including the user's 720-frame grid loops.

To change a roof clip, select its object and replace the image in the material's `REPLACE_MEDIA` node. Set Frames to the replacement clip's full length. The existing screen helper is also available, but it does not convert intentionally static materials into video materials. Some existing lower ribbon materials are shared, so editing those materials changes all objects listed against them in `assets.json`.

## Folder layout

- `Deliverables/`: current and historical editable scenes, previews and validation reports. Version folders stay in place to preserve relative media links.
- `Assets/Brand/`: derived flower artwork used by the scene. Other static textures are packed inside Blender.
- `Ref Material/`: original photos, supplied source scene, guides, movies and feedback. Original supplied files and old source movie variants are retained.
- `scripts/`: reproducible revision and validation tools.
- `working/`: historical reusable scripts and validation records only; temporary inspection output is archived.
- `docs/`: asset guidance and cleanup inventory.
- `.local/cleanup-archive-2026-09-08/`: recoverable local archive of unused PNG/GIF conversions, local FFmpeg tools, scratch previews and automatic Blender backups. Intentionally excluded from Git. Original MOV sources remain synchronized.

`cleanup-manifest.json` maps every archived item to its new path. Archiving reduces clutter, not disk usage. No original supplied reference or historical deliverable was deleted.

## Revision tools

Run `scripts/revise_v41.py` against the user-edited v4 to reproduce the roof addition. It replaces v4.1 outputs, so preserve any later manual v4.1 edits first. Run `scripts/validate_v41.py` and `scripts/check_roof_loop.py` against v4.1 for preservation, media and loop checks. Tests do not save their temporary scene changes.

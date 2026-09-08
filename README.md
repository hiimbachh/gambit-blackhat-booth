# Current deliverable: interactive booth viewer

Open web/START_VIEWER.bat (Python 3 required). See [web/README.md](web/README.md) and [technical guide](docs/3D_TO_HTML_TECHNICAL_GUIDE.md). The MKV in Deliverables/v4.2/Render is the retained video preview. Unwanted stills and old MP4 previews are archived locally; source models and reference assets remain intact. Read HANDOFF.md for current status.

---

# Current deliverable: v4.2

Open Deliverables/v4.2/Gambit_BlackHat_v4.2.blend. The roof now uses individual bar directions and offsets. Your accepted booth and verified media timing are preserved. Read [HANDOFF.md](HANDOFF.md) for current status.

---

# Current deliverable: v4.1

Open Deliverables/v4.1/Gambit_BlackHat_v4.1.blend. This preserves the user-edited v4 booth and adds the central roof. See [HANDOFF.md](HANDOFF.md) for current status and [docs/ASSETS.md](docs/ASSETS.md) for materials, clip timing and folder organization. Earlier version instructions below are historical.

---

# Gambit BlackHat Booth

Editable Blender reconstruction of the built Gambit booth, prepared for still renders, replaceable looping screens, optional subtle block motion, and later real-time interaction.

**Start with [HANDOFF.md](HANDOFF.md).** The active scene is `Deliverables/v4/Gambit_BlackHat_v4.blend`. The earlier v1 remains in Deliverables for comparison.

## Use on another machine

Install Git with Git LFS and Blender 5.2.1 (the version used to build and check this project).

```sh
git lfs install
git clone https://github.com/hiimbachh/gambit-blackhat-booth.git
cd gambit-blackhat-booth
git lfs pull
```

Authenticate with a GitHub account that has access to this private repository. Open the project folder in your agent app and ask it to read AGENTS.md and HANDOFF.md. The project's location can differ between machines; preserve the relative directory structure.

The reference folder contains around 1.8 GB of supplied media, including old versions. Binary assets use Git LFS. A normal download of pointer files without `git lfs pull` is not a complete working copy.

Before changing machines, save Blender, update the handoff and changelog, commit the intended changes, and push. On the receiving machine, pull before editing. Avoid simultaneous edits to the same binary Blender file.

## Change a screen

In Blender, open `scripts/screen_manager.py` in the Text Editor and press Run Script once. In the 3D view, open the N sidebar and select **Booth Screens**. Pick a named display, then **Choose image or looping video**. The script is also embedded in the Blender file. It does not run automatically when the file opens.

MP4/MOV video loops directly. GIF animation must first be converted to MP4 or a PNG sequence; selecting a GIF as a still image will not animate it. Each screen has its own `MEDIA_<ID>` material and `REPLACE_MEDIA` texture node for direct editing without the helper. Save replacement media inside this project before committing.

Use Material Preview or Rendered view and play the timeline to see screen playback. The block-motion control is independent and defaults to zero.

## Rebuild

From the repository root, use your Blender executable:

```sh
blender -b "Ref Material/Gambit BlackHat Booth/Gambit_Booth (1).blend" --disable-autoexec --python scripts/build_v2.py
```

The flower contour and optimized texture are checked in. Regenerating those two derived assets uses `scripts/prepare_flower.py` with Python, Pillow, and NumPy.

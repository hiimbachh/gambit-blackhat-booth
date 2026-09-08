# Gambit booth explorer

Double-click START_VIEWER.bat on Windows with Python 3 installed, or run `python serve.py`. Open http://127.0.0.1:8765. Keep the terminal open while viewing. If that port is already in use, stop the earlier server first. Opening index.html directly through file:// is not supported because the browser fetches the GLB and modules.

Drag to orbit, scroll to zoom, right-drag to pan. Choose one of four camera views. Wireframe switches off the original surface materials temporarily; switch it off to restore the realistic material view. Sliders control exposure, key-light strength/direction, additional roof tier spacing, and camera field of view. Reset restores defaults. Play screens pauses/resumes all nine video sources. Auto orbit is optional and off initially.

The original exported GLB is copied unchanged to booth.glb. Geometry edits are temporary browser state and do not modify the Blender or GLB file. Screen playback is restored separately from the latest Blender material mapping. No baked animation clips exist in this GLB. The browser is a real-time PBR approximation, not a Cycles render; shader nodes, exact shadows and transparent video do not transfer automatically. Current MP4 clips are opaque, muted, browser-compatible H.264 at 60 fps. No preview image exports are included.

To deploy later, upload only this folder to a static web host over HTTPS. It needs no database, build step or CDN: Three.js 0.180.0 is included locally under vendor with its MIT license. The web GLB and MP4 copies are stored directly in Git so Vercel can deploy them without enabling Git LFS. Original source assets elsewhere remain in LFS. This session prepares and tests the local viewer; no public site is published.

Read ../docs/3D_TO_HTML_TECHNICAL_GUIDE.md for the model pipeline and implementation details.

For Vercel: Root Directory = web, Framework Preset = Other, no build command, Output Directory = . (or the default static root). Deploy the latest main commit. This web folder requires no installation or build step.

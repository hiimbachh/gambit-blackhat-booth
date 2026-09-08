# From Blender to an interactive HTML model

This guide describes the Gambit booth viewer in `web/`, created on 2026-09-08. It is a working static website with a WebGL canvas, not a video embedded in a page.

## The pipeline

Blender is the authoring tool. The GLB is the delivery format. Three.js loads that format and draws it inside an HTML canvas. HTML supplies buttons and sliders; JavaScript connects those controls to scene properties; CSS arranges the interface. A small local HTTP server lets the browser fetch those files. The server does not render the model: the browser GPU does.

The supplied GLB is 11,488,884 bytes and contains 268 nodes, 261 meshes, 29 materials and three embedded images. It has no animation clips. `web/booth.glb` is a byte-for-byte copy of `Deliverables/Export/Gambit_BlackHat_v4.2.glb`; the original export is retained. The viewer uses the actual exported geometry rather than rebuilding the booth from boxes.

## What transfers from Blender

GLB packages mesh geometry, UV coordinates, transforms, hierarchy and supported material properties into one binary file. UVs tell each triangle where to sample its texture. Material names let the application find particular screens. Object names beginning with `ROOF_L` identify the eight exported roof block nodes that the spacing control can move. Their screen children move with them.

Blender shader graphs, drivers, Cycles lighting and movie-image playback do not automatically become browser behavior. This export contains no animation tracks, so an AnimationMixer would have nothing to play. The roof slider is an explicit JavaScript control, not an imported Blender driver. A future animated export would require baked transform clips and an AnimationMixer, or another deliberately implemented parameter system.

For future exports, preserve meaningful names and parent screen meshes to the structure they should follow. Apply appropriate transforms, confirm metre scale, export required objects, and test the result after each export. Merging the entire booth into one mesh would remove the independent roof controls. Blender is Z-up while glTF is Y-up; the exported data handles the conversion, and this viewer changes vertical position through `position.y`.

## The viewer files

| File | Purpose |
|---|---|
| `index.html` | Canvas container, labelled switches/sliders, camera buttons, import map |
| `style.css` | Desktop sidebar and stacked narrow-screen layout |
| `app.js` | Loading, lights, camera navigation, rendering and parameter connections |
| `booth.glb` | Unmodified model export |
| `media.json` | Exact exported material name → browser video file mapping |
| `media/` | Nine derived MP4 screen clips; these are runtime assets, not preview exports |
| `vendor/` | Pinned Three.js 0.180.0 modules and MIT license, with no CDN dependency |
| `serve.py`, `START_VIEWER.bat` | Start a loopback-only local HTTP server and open the page |

## How a parameter changes a model

An HTML range input emits an `input` event. The handler reads its value, converts it to a number, and updates a Three.js property. The next render displays the change. For example, the exposure slider sets `renderer.toneMappingExposure`. There is no need to export a fresh GLB for lighting or camera changes.

Roof spacing keeps a baseline position on each roof object and calculates:

```js
object.position.y = originalY + spacing * tier;
```

The slider runs from 0 to 0.5 metres of additional separation per tier. This is an exploratory exploded view, not a fabrication measurement. Values are computed from the original positions every time, so dragging back and forth does not accumulate errors. The original model files are never written by the browser. Reset restores the baseline.

For a new structural parameter, first identify the intended nodes, store their original transforms, define safe limits and units, then update only those nodes. If children must follow, use a parent group. If adjusting width, choose whether to scale geometry or reposition components: scaling a complete booth also stretches furniture, graphics and thicknesses. More complex changes usually need authored component groups or regenerated geometry.

## Controls in this version

| Control | Effect |
|---|---|
| Wireframe | Temporarily replaces mesh materials with a wireframe material; switching off restores the exact original material objects |
| Auto orbit | Enables OrbitControls' slow camera orbit; it starts off |
| Play screens | Pauses/resumes the nine shared video elements |
| Exposure | Changes tone-mapped image brightness, 0.3–2.0 |
| Studio light | Multiplies the directional key-light intensity, 0–3 |
| Light direction | Moves that light around the booth, −180°–180° |
| Roof spacing | Additional vertical separation per numbered roof tier, 0–0.5 m |
| Field of view | Changes perspective lens angle, 25°–65° |
| Four views | Repositions the camera and orbit target to overview, bar, service or roof |
| Reset | Restores defaults, original roof positions and overview camera |

OrbitControls also supports mouse/touch navigation. Camera framing excludes floor and suspension cables so their large bounds do not make the booth tiny. A ResizeObserver updates renderer size and camera aspect ratio when the canvas area changes. Device pixel ratio is capped at two to limit rendering cost.

## Restoring the screen videos

The latest Blender material mapping identifies 13 exported video materials. The source MOV files use production codecs, so nine unique clips were converted to H.264 MP4 with 4:2:0 pixels for browser playback. Matching materials share a VideoTexture and HTML video element rather than decoding the same file several times. The mapping uses existing material names, not every object that happens to contain “screen”; intentionally static surfaces stay unchanged.

Each VideoTexture uses sRGB color space and `flipY = false` to match glTF UV conventions. The material receives a color map and an emissive map so the display remains visible under different lighting. Clips are muted, looped and marked `playsInline`. If autoplay is blocked, the user can enable Play screens. Playback failure is surfaced in the sidebar.

Configured loop lengths are retained: 602 frames for A clips, 720 for B clips, 420 for D/E clips and 217 for the mesh-screen clip, at 60 fps. The grid clips deliberately follow the user's 720-frame setting rather than including extra source frames. These MP4 copies are opaque: transparent video requires a separate browser-compatible alpha or masking strategy. Browser video loops are not frame-locked to one master timeline, and web render frame rate depends on the device. This is distinct from the earlier 60 fps offline render request.

## “Realistic” versus wireframe

The realistic view uses glTF PBR materials, a generated room environment, a directional shadow-casting light, hemisphere fill, and ACES tone mapping. It is interactive raster rendering, not Cycles path tracing. Procedural Blender shaders, reflections, translucent screens and soft shadows may differ. More fidelity would require texture baking, deliberate material conversion, environment lighting calibration and potentially a different rendering approach.

Wireframe reveals exported triangles, including triangulated surfaces. It does not change topology. Saving original material references avoids destroying textures or video bindings when toggling modes.

## Running, replacing and publishing

Install Python 3 and double-click `web/START_VIEWER.bat`, or run `python web/serve.py`. Visit http://127.0.0.1:8765 and leave the terminal open. Opening index.html with file:// is insufficient for module and GLB fetches. If port 8765 is already occupied, stop the earlier server or change the port and URL together.

To replace the model, copy a new export to `web/booth.glb`, retain compatible names and hierarchy, and reload. Update `media.json` when material names or video assignments change. Test missing-file errors, every camera, reset, wireframe restoration, video pause/resume and all parameter limits. Keep a versioned Blender source separately.

For deployment, upload only `web/` to an HTTPS static host. No database or backend is required. The web GLB and MP4 copies now use ordinary Git storage via web/.gitattributes, so Vercel receives real binary files without LFS hydration. Source assets elsewhere still require Git LFS. Repository synchronization is not website publication. No public deployment or repository visibility change was performed in this session.

Possible next steps include URL-based saved presets, object selection, constrained component dimensions, compressed geometry/textures, lazy loading of clips, and a calibrated mobile quality mode. These are future extensions, not features claimed in this version.

## Primary references

- [Three.js GLTFLoader](https://threejs.org/docs/#examples/en/loaders/GLTFLoader)
- [Three.js OrbitControls](https://threejs.org/docs/#examples/en/controls/OrbitControls)
- [Three.js MeshStandardMaterial](https://threejs.org/docs/#api/en/materials/MeshStandardMaterial)
- [Three.js VideoTexture](https://threejs.org/docs/#api/en/textures/VideoTexture)
- [Khronos glTF overview](https://www.khronos.org/gltf/)

Implementation-specific details above come from inspecting the user's GLB and current Blender file and testing this viewer.

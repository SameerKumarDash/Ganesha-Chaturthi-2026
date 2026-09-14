# Divine Cosmic Ganesha — Brahmand manifestation

A separate Python/Blender experiment in which a devotional Ganesha drawing manifests stroke by stroke inside a procedural 3D universe. The camera, tubes, stars, planets, galaxies, clouds, drawing point and attracted dust are dynamically evaluated by Blender's Eevee Next engine. No background video, image sequence, image fade, paid API, downloaded artwork or runtime network access is used.

**Confirmed project location:** `D:\SaMMaaNs_InfoTech_Innovations_And_Products\Ganesha Chaturthi 2026`. This supersedes the earlier `tests\Ganesha Animation` location following the user's explicit clarification. Nothing here imports or modifies VAYUNA.

![Completed manifestation](output/sculptural_075.00s.png)

The image above is a validation render of the live scene, not a runtime asset.

## Default SCULPTURAL style (continued implementation)

`python launcher.py` builds the **SCULPTURAL** style by default (`--style VECTOR` keeps the original line-art scene described in the later sections). It is art-directed toward the supplied reference artwork: a translucent Ganesha of dark galactic matter, bright spiral galaxies in the ears, hands, belly and folded legs, glittering golden contours, a tiered gold mukut, a luminous vortex with a rising river of golden stars, large night-side planets at lower left and a ringed world at lower right.

| Module | Role in the sculptural style |
| --- | --- |
| `sculptural_scene.py` | Portrait camera, lighting, composition root; optional greeting (`show_greeting`, off by default because the reference has no text). |
| `ganesha/sculpture.py` | Fused anatomical meshes plus `contour_guides()`: 3D silhouette paths (crown tiers, head, ears, eyelids, tilak, trunk, arms, palms, chest, belly, thighs, shins, feet). |
| `animation/surface_manifestation.py` | Converts guides to `VectorPath` records ordered by phase, then runs the **same** progressive stroke engine as the vector style; attaches particle attraction and the trail to that exact tip. |
| `ganesha/manifestation.py` | `build_strokes()` — the single shared stroke/tip engine used by both styles. |
| `shaders/celestial_surface.py` | Broad photographic spiral arms with dust lanes, matte starry galactic skin, optional gilding (crown). |
| `cosmic/rich_universe.py` | Rich galaxies, larger-scale nebula, reference planet layout with night lights and rings, particle energy stream and vortex core. |

Manifestation order follows the timeline phases: crown → head/ears → eyelids/tilak → trunk → arms/hands/chest/belly → thighs/shins → feet. Each contour is hidden until its slot, reveals by arc length, and persists afterwards; the surface fills in behind the drawn outline. Sculptural validation (`--validate`) runs 28 Blender checks, including halfway reveal, exact tip tracking, hidden future contours and persistence.

## Quick start

Double-click **run_animation.bat**, or run these exact PowerShell commands:

```powershell
Set-Location 'D:\SaMMaaNs_InfoTech_Innovations_And_Products\Ganesha Chaturthi 2026'
python launcher.py
```

The launcher builds a fresh scene, enters rendered camera view, and starts playback. The first shader compilation can take several seconds. LOW is the default because this machine reports integrated Intel graphics.

```powershell
# Verify the executable without launching the scene
python launcher.py --check

# Choose quality / time scale
python launcher.py --quality MEDIUM
python launcher.py --quality LOW --speed 1.5

# Build and save a self-contained animated Blender file, with no window
python launcher.py --background --quality LOW --save

# Reproduce validation, diagnostics and selected stills
python launcher.py --background --quality LOW --validate --debug --save --render-seconds 0 18 31 66 75

# Pure Python tests: no Blender dependency
python -m unittest discover -s tests -v
```

The saved project is `output\divine_ganesha.blend`. It contains baked animation, Geometry Nodes and simple time drivers. Opening it directly requires no scene-building scripts. Custom F3 controls are registered by `launcher.py` / `main.py`; they are not installed globally. Native Blender controls still work when opening the `.blend` directly.

## Requirements and Blender installation

- Standard Python **3.10+** for the launcher and tests. Tested with Python 3.14 on this machine.
- **Blender 4.2–4.5**, Eevee Next. Actually tested with **Blender 4.5.9 LTS**. Other 4.x versions in that range are compatibility targets, not separately certified. Blender 4.0/4.1 and 5.x are rejected with a diagnostic.
- A graphics driver capable of running Eevee Next. More GPU memory improves higher quality modes.
- No pip packages, virtual environment, audio package, or network service required.

A portable Blender 4.5.9 distribution is included locally in `tools\blender-4.5.9-windows-x64`. It was downloaded from the [official Blender archive](https://download.blender.org/release/Blender4.5/) and checked against its published SHA-256. The ZIP checksum is `41da973b9bf95bb312cbeff4d1982feb13259b43c821686b9bafea4dfe5477cf`.

For another machine, obtain a Windows portable ZIP from the [Blender 4.5 LTS release page](https://www.blender.org/releases/4-5/) and extract it under this project's `tools` folder, or install Blender normally. [Official Windows installation instructions](https://docs.blender.org/manual/en/4.5/getting_started/installing/windows.html) describe both options.

Executable lookup order is explicit `--blender`, `BLENDER_EXE`, PATH, project-local portable Blender, then conventional Blender Foundation installation directories:

```powershell
python launcher.py --blender 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe'
# Or configure this shell only:
$env:BLENDER_EXE = 'C:\path\to\blender.exe'
.\run_animation.bat --quality LOW
```

The launcher directs Blender user resources and temporary files into the project. It does not alter global PATH, install packages, modify another application's environment, or save global Blender preferences. `--factory-startup` applies only to this new process.

## Modules and files

| Module | Responsibility |
| --- | --- |
| `main.py` | Argument parsing, isolated asset validation, scene orchestration, save/render/validation entry point. |
| `launcher.py`, `run_animation.bat` | Windows launch, Blender lookup/version checks, local resource and temp paths, propagated exit status. |
| `config.py` | Validated immutable settings, quality budgets, source normalization and anatomical depth constants. |
| `setup_scene.py` | Separate Eevee scene, camera, world, collections, mesh helpers, resolution and compositor. |
| `ganesha/path_loader.py` | JSON schema adapters, cubic sampling, diagnostics, metadata and stable ordering. |
| `ganesha/depth_mapper.py` | Aspect-preserving XY normalization, smooth anatomical Z depth, arc-length utilities. |
| `ganesha/curve_builder.py` | Shared Trim Curve → Curve to Mesh node group; one tube object per source path. |
| `ganesha/materials.py` | Four reusable gold variations, tip core, secondary blue and halo materials. |
| `ganesha/manifestation.py` | Build all strokes, active tip and its seven orbiting motes. |
| `ganesha/body_field.py` | Translucent cloud lobes behind the figure, interior star instances and two small galaxies. |
| `animation/timeline.py` | All ten phase windows and their category, light, particle, camera, halo and body metadata; source-aware scheduling. |
| `animation/stroke_animator.py` | Reveal keys, explicit future-stroke hiding, exact tip keyframes, smooth inter-stroke travel. |
| `animation/particle_flow.py` | Stateless, GPU-evaluated attraction, gentle spiral, arrival flash and merge envelope. |
| `animation/tip_trail.py` | Seven small, pre-baked trailing motes sampled from the active stroke. |
| `animation/camera_animator.py` | Slow approach/drift and approximately six-degree final orbit, with upright global Y. |
| `animation/light_animator.py` | Warm front and cool rim area lights, keyed from phase lighting levels. |
| `animation/controls.py` | F3 restart/speed/layer operators and clean rendered-camera view setup. |
| `animation/performance.py` | Opt-in scene evaluation timing, clearly separate from actual rendered playback FPS. |
| `cosmic/universe.py` | Assemble enabled environment layers. |
| `cosmic/particles.py` | Shared point-cloud Geometry Nodes instancing primitive and per-point radii. |
| `cosmic/stars.py` | Twelve independently phased groups over three distance classes; twinkle and drift. |
| `cosmic/nebula.py` | Soft procedural blue/violet cloud planes; optional faint volume on HIGH/ULTRA. |
| `cosmic/galaxies.py` | Three-arm point spirals, dense cores, distant clusters and slow rotation. |
| `cosmic/planets.py` | Two low-poly procedural spheres, atmospheres and slow axial rotation. |
| `cosmic/halo.py` | Faint concentric gold rings and slowly orbiting particles, visible after the eyes. |
| `shaders/divine_glow.py` | Shared emission builders, time expressions and version-aware Fog Glow compositor. |
| `shaders/nebula_shader.py` | Animated 4D noise, soft radial cloud opacity and optional low-density volume shader. |
| `shaders/cosmic_materials.py` | Procedural planet surfaces and translucent atmospheric rims. |
| `data/create_reference.py` | Reproducible authoring source for the original bundled devotional drawing. |
| `data/ganesha_vector_data.json` | 119 original cubic paths; no external runtime reference. |
| `tests/test_*.py` | Standard-library unit tests for data, depth, configuration and timing. |
| `tests/blender_validation.py` | Real Blender geometry, reveal, tip, motion and instance checks. |
| `tools/validate_shape.py` | Milestone 3 curve-only render used to check shape before building effects. |
| `tools/inspect_blender.py` | Small API diagnostic used to inspect Blender 4.5 compositor sockets. |
| `output/` | Generated `.blend`, preview images, validation logs, timing records and isolation status snapshots. |

Package `__init__.py` files keep imports explicit. `requirements.txt` documents the absence of pip dependencies. `.gitignore` excludes downloaded runtimes, generated output and Python caches. `IMPLEMENTATION_REPORT.md` records the completed work; `FILE_MANIFEST.txt` inventories files, including the portable runtime distribution.

## Vector source, import and 3D conversion

No `ganapati_python` project or `vector_data.json` was found in the available workspace. The supplied artwork is an **original hand-authored fallback**, not a copy or claimed reconstruction of the absent reference. It depicts a crowned, serene Ganesha with elephant ears, curved trunk, four arms, blessing and offering hands, a rounded torso, crossed legs and lotus seat. The initial geometry was visually checked before adding the universe.

Supported JSON forms are a root path array (default canvas 2700×3300) or:

```json
{
  "canvas": {"width": 1000, "height": 1200},
  "paths": [
    {
      "id": "example",
      "name": "Crown stroke",
      "category": "crown",
      "step_order": 0,
      "bezier_segments": [[[400,250],[420,190],[460,160],[500,120]]],
      "width": 2.5,
      "is_closed": false,
      "is_filled": false
    }
  ]
}
```

Each cubic segment is `[p0,p1,p2,p3]`, or an object with those four keys. Each point is `[x,y]` or `{"x":x,"y":y}`. A path may use a `points` array instead of cubics. This is not a general SVG command parser. Split disconnected cubic subpaths into separate entries. Polyline inputs are preserved; cubics are densely sampled without Blender auto-handle overshoot.

The loader skips individual bad paths with warnings: empty/micro geometry, invalid numbers, non-finite coordinates, invalid width, unsupported path types, repeated IDs or discontinuous cubic segments. Consecutive duplicate points are removed. Missing IDs/names/categories/width/order receive defaults. Invalid JSON, missing data, invalid canvas or zero usable paths stops with an actionable error. Source count and accepted count are printed. Closed paths explicitly repeat their first point while remaining non-cyclic for reliable trimming. Filled metadata is preserved; polygon-fill reconstruction is not implemented in this version.

Sort order is `step_order`, then original list order for ties. Anatomical windows are used when compatible with the source order. Otherwise all strokes receive length-weighted slots across seconds 8–58 without silently reordering the source drawing.

To use your own source, copy it into this project's `data` directory, then run:

```powershell
python launcher.py --vector data\my_ganapati.json
```

Runtime references outside the project are rejected. Compatibility with the absent Ganapati project's exact schema remains unverified; adapt its cubic keys to the documented schema if needed. The approximate body lobes in `body_field.py` match the bundled artwork and may need adjustment for another drawing.

Normalization uses one uniform scale, `min(world_width/canvas_width, world_height/canvas_height)`, preserving proportions. Coordinates center around the canvas midpoint; source Y is inverted. Ganesha lies in world **XY**, with **Z toward the camera**. Positive depth brings facial features forward. This deliberate coordinate convention is used by the camera, halo and particles.

Z depth is `DEPTHS[category] + depth_wave*sin(2*pi*u)`, where `u` is path arc-length fraction. Trunk paths add `0.16*sin(pi*u)^2`. The default wave is 0.065 world units; trunk baseline is 0.95, ears 0.1, crown 0.55, eyes 0.6, torso 0.2. Unknown categories use the silhouette baseline. Closed ends meet at the same depth. This is a shallow sculptural field of real 3D tubes, not a fully modeled anatomical statue.

## Reveal, tip and particle animation

Every path has a `reveal` custom property from 0 to 1. A shared Geometry Nodes group trims the source curve by **arc-length fraction**, then generates a round tube. Future objects are also explicitly hidden, preventing a zero-length cap from appearing. Completed strokes persist and their shared gold emission breathes gently. Original widths scale the tube radius within a safe visual range.

The active drawing point uses the **same sampled polyline and cumulative 3D length** as the trimmed stroke. Location keys are placed at vertex arrival times, with linear interpolation; this is exact along each polyline segment, including at subframes. Short dimmed arcs bridge the small gaps between strokes. The tip has a bright inner core, orbiting golden motes and a cached, diminishing trail.

Attraction dust is a point mesh and one shared icosphere instance. Geometry Nodes combines index-based phase, time and the active tip location. Position is `origin + (tip-origin)*phase^2.3` plus a small spiral that shrinks to zero at arrival. A birth/death envelope hides periodic reseeding. A small late-cycle size rise supplies the arrival flash, then the particle fades into the stroke. Activity decreases during the eyes. This is analytic directed motion, not a fluid solver or physical N-body simulation. No per-particle Python loop runs during playback.

## Timeline

| Seconds at speed 1 | Phase |
| --- | --- |
| 0–4 | Sparse cosmic void, slow approach, no Ganesha. |
| 4–8 | Awakening dust, faint central point, increasing depth. |
| 8–14 | Crown. |
| 14–22 | Head, ears and forehead. |
| 22–27 | Tilak and serene eyes, reduced particle activity. |
| 27–34 | Trunk and gradual halo appearance. |
| 34–48 | Arms, hands, torso, necklace and jewelry. |
| 48–58 | Waist, drapery, seated legs, feet and lotus details. |
| 58–65 | Cosmic body, internal stars and small galaxies fade in. |
| 65–665 by default | Living final form; continuing camera, cloud, star, planet and galaxy motion. |

Frames use `1 + seconds*FPS/ANIMATION_SPEED`. The final hold lasts ten minutes by default and is configurable via `final_hold_seconds`. Blender loops the whole timeline at its end. Drivers remain time-based if the end frame is extended. There is no frozen final pose.

## Cosmic scene and color

Twelve star groups use different twinkle frequencies/phases; camera movement produces parallax among their depths. Background galaxies include one large spiral, two medium spirals and at least three small clusters. Two distant planets have noise-based surface shading and faint atmospheric rims. Nebula planes use animated noise and soft spatial opacity, avoiding rectangular edges. The body uses very faint translucent blue-violet lobes behind the gold curves, with stars placed inside matching ellipses. Two small internal spirals activate with the body.

The palette emphasizes warm gold, soft white, midnight blue and restrained violet. Lights stay soft and the environment darker than the figure. Eevee Next glow is a lightweight **Fog Glow compositor**, not the removed legacy Eevee bloom switch. The rendered camera viewport enables the compositor. Blender 4.5 uses socket-based glare controls and GPU compositing when available.

## Quality and performance

| Preset | Background stars | Attraction particles | Background galaxies | Cubic resolution setting | Tube sides | Render samples | Resolution | Volume |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| LOW | 900 | 180 | 6 | 8 | 8 | 16 | 1280×720 | Off |
| MEDIUM | 2500 | 650 | 7 | 12 | 10 | 32 | 1920×1080 | Off |
| HIGH | 5000 | 1200 | 9 | 16 | 12 | 48 | 1920×1080 | On |
| ULTRA | 9000 | 2200 | 12 | 24 | 14 | 64 | 2560×1440 | On |

Each cubic is sampled at twice the resolution setting. Interior stars, halo motes and galaxy particles are additional shared instances; listed counts are not total luminous points. LOW has 182 scene objects, rather than an object per star. Geometry remains cached; no mesh rebuild handlers or simulation caches are needed. LOW galaxy arms use 360 samples plus core particles; other modes use 800 plus core. Ray tracing stays off.

**30–60 FPS is a hardware target, not a verified guarantee.** `--debug` writes median and p95 scene update cost to `output/performance.json`; it explicitly excludes viewport drawing/compositing. Selected offscreen PNG render times in the validation log also include compositor/readback/save costs and must not be interpreted as live FPS. Use Blender's live playback FPS display to assess your GPU. Frame dropping keeps cinematic timing if rendering is slower than the configured 60 FPS.

For slower hardware: use LOW, reduce the viewport size, disable volumetrics, lower star/particle counts, or disable nebula/galaxies through settings. For extra speed, set viewport compositor to Disabled in Blender's shading options; glow will be absent from that preview but still present in final renders. Adjust `Settings` and `PRESETS` in `config.py`; the feature toggles are `enable_stars`, `enable_particles`, `enable_nebula`, `enable_galaxies`, `enable_planets`, `enable_halo`, and `enable_volumetrics`.

## Controls

Native Blender playback is used to avoid installing global hotkeys or covering the cinematic view with panels:

| Requested action | Working equivalent |
| --- | --- |
| Restart | F3 → **Ganesha: Restart Manifestation**, or Shift+Left Arrow then Space. |
| Pause/resume | **Space** (native Blender). P is not overridden. |
| Increase/decrease speed | F3 → **Ganesha: Set Playback Speed**. For a rebuilt export use `--speed`. |
| Cinematic camera | **Numpad 0** toggles camera view. |
| Toggle G/S/N/H layers | F3 → **Ganesha: Toggle Cosmic Layer**, or collection visibility in Outliner. |
| Stop | Space pauses. Escape cancels an active Blender operation; close the Blender window to exit. |
| Clean full-area view | Move cursor over the viewport, **Ctrl+Space**. This hides the other editor areas. |

F3 speed changes playback rate via `fps_base`; it does not rewrite all keyframes. Custom F3 operators are available when launched through the Python entry point. No custom controls are embedded as auto-running text scripts in the saved file.

## Tests and validation

The unit suite exercises bundled JSON loading, malformed data, cubic extraction, duplicates, closed paths, sorting, missing/invalid files, coordinate normalization, category depths, deterministic depth, closed seams, arc-length sampling, phase overlap, speed conversion, preserved external order and all quality presets.

The Blender integration check evaluates actual tube meshes, hidden future strokes, halfway reveal, exact tip location at multiple anatomical stages, completed persistence, body invisibility before manifestation, final camera/galaxy motion, upright camera, valid drivers, file-texture independence and actual animated particle instances. Run it through `launcher.py --background --validate`; do not import `bpy` tests through ordinary Python.

Validation images at 0, 18, 31, 66 and 75 seconds are in `output`. `shape_validation.png` is the earlier curve-only milestone. Final motion is also tested by comparing evaluated transforms at different times. The completed file can be re-opened and scrubbed without running scene creation again.

## Troubleshooting

- **Blender not found:** run `python launcher.py --check`, set `BLENDER_EXE`, or pass `--blender`. Paths with spaces must be quoted.
- **No module named bpy:** run `launcher.py` using regular Python. `main.py` executes inside Blender.
- **Black first frames:** expected void. Seek to 66 seconds to inspect the completed form. Use camera view and Rendered shading.
- **Slow first display:** wait for shader compilation. Start with LOW; HIGH/ULTRA can exceed integrated GPU budgets.
- **No glow:** check Rendered shading and viewport compositor; final PNG renders use the scene compositor.
- **Malformed source:** read printed path diagnostics, confirm cubic p0/p1/p2/p3 controls and positive canvas dimensions. At least one usable path is required.
- **Different drawing has wrong body fill:** update `LOBES` in `ganesha/body_field.py` to its normalized anatomy. Curves themselves do not depend on this mask.
- **Transparent layers sort imperfectly during orbit:** the orbit is deliberately shallow. Full arbitrary camera movement is outside the current layered-body design.
- **GPU compositor problem:** change `scene.render.compositor_device` to `CPU` in `setup_scene.py`, or use a supported driver.
- **Saved file lacks F3 operators:** launch again through `launcher.py`; the controls are session registrations, not an installed add-on.
- **Interrupted render/build:** launch again. Outputs stay within this project; the original vector JSON is not overwritten by a launch.

## Honest limitations and next upgrades

This version uses original stylized devotional vector artwork because the requested reference was absent. It is a shallow 3D energy sculpture with an approximate translucent body, not a full volumetric anatomical model. Some line connections and artistic details can be refined further. Filled-path metadata is not tessellated. Background galaxies are efficient point spirals rather than physical galaxy simulations. Twinkling is phase-grouped, and particle attraction is analytic. The small trail is pre-baked at 20 Hz; the main tip remains exact at subframes. Broad keyboard shortcuts are supplied as Blender equivalents. No audio is included. Other Blender versions, every quality level's visual output and a sustained 30/60 FPS live viewport are not all certified.

Next steps: adapt the actual Ganapati reference when available; fit a continuous anatomical volume; refine depth per local feature; add physically richer cosmic flow; add temple-bell/mantra timing hooks and audio synchronization; refine camera choreography; package controls as a local add-on; and offer higher-quality offline cinematic rendering. These upgrades can remain entirely inside this experimental project.

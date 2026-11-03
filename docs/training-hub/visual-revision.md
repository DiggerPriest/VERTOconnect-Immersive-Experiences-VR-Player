# Visual revision: prove one finished plumbing bay first

Research status, 2 November 2026: primary catalogue/licence pages checked. No asset
binaries saved, unpacked, imported or visually validated in Godot during this
research. Candidate polygon counts below are publisher figures, not our mesh audit.
The .24 visual result has not met the user's quality expectation.

## Concrete asset candidates

| Candidate | Verified publisher information | Intended use and adaptation |
|---|---|---|
| [Poly Haven Metal Tool Chest](https://polyhaven.com/a/metal_tool_chest) | CC0; approximately 15K triangles; 0.7 m wide; rigged drawers/lid; Blend/glTF offered | Recognisable workshop storage with authored handles, seams and material wear. Keep closed; bake static transforms and remove hidden internal geometry after inspection. |
| [Poly Haven Bench Vice 01](https://polyhaven.com/a/bench_vice_01) | CC0; approximately 3K triangles; 0.4 m wide; rigged jaw; Blend/glTF offered | Foreground workbench anchor. Keep jaw fixed and place an actual workpiece in it. |
| [Poly Haven Modular Industrial Pipes 01](https://polyhaven.com/a/modular_industrial_pipes_01) | CC0; approximately 12K triangles for the published set; flanges, bends, junctions, valve/gauge; Blend/glTF offered | Select a compact training-board assembly. Retain flanges/fasteners and gauge silhouette; do not instantiate every piece. |
| [Poly Haven Painted Concrete 02](https://polyhaven.com/a/painted_concrete_02) | CC0; 4 m reference width; diffuse, normal and packed AO/roughness/metal maps offered | Subtle local surface variation at real scale. Reduce weathering; avoid turning a modern training centre into a derelict factory. |
| [MakeHuman system asset pack](https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html) | Individual catalogue entries mark `male_worksuit01`, system skin variants, eyes and hair CC0 | Replace the current simple jacket shape with fitted workwear geometry. Bake altered VERTO colours/tape into its materials; validate shoulder/elbow deformation and glove contact. Actual topology/UV quality still uninspected. |
| [MakeHuman Skins 02](https://static.makehumancommunity.org/assets/assetpacks/skins02.html) | Natural male skin pack, 72 MB, CC0; named Mindfront variants listed | Use an inspected natural face/hand material rather than a flat skin colour. Retain proper eye detail; crop/omit fully covered body textures in the shipped character. Not a claim that every third-party MakeHuman asset has this licence. |

Poly Haven explicitly permits commercial use and redistribution, including source
assets. That supports a public repository, subject to preserving our own provenance
and asset hashes. [Primary asset licence](https://polyhaven.com/license).
MakeHuman distinguishes CC0 and CC-BY packs; use only the reviewed CC0 entries for
this milestone. [Primary asset-pack index](https://static.makehumancommunity.org/assets/assetpacks.html).

## Download evidence and limits

These exact direct links were resolved from the primary pages:

- [MakeHuman system assets CC0 ZIP](https://files2.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip).
- [MakeHuman natural male skins CC0 ZIP](https://files2.makehumancommunity.org/asset_packs/skins02/skins02_cc0.zip).
- [Tool-chest 4K diffuse PNG](https://dl.polyhaven.org/file/ph-assets/Models/png/4k/metal_tool_chest/metal_tool_chest_diff_4k.png), an example of the page's direct material links, not the intended runtime resolution.

The browser research tool rejected ZIP rendering and the large PNG response; archive
contents/checksums are therefore **not verified**. Poly Haven model pages expose
Blend/glTF download choices, but exact model-archive URLs were not captured; use
the site's Download control when acquisition begins rather than inventing a URL.
The previously reported API 403 was not retried through another client or bypassed.

## One visual milestone

Build a single complete plumbing training bay, with the seated viewer about 3–4 m
from its worker/workbench. Keep the remainder of the room understated while this
bay is reviewed. The imported vice, tool chest and pipe fittings should immediately
read as manufactured objects, with material response, appropriate wear and small
functional details. Use a textured natural face, fitted workwear and a visible
head/torso/arm inspection routine, not only a tiny wrist rotation. Maintain planted
feet, continuous tool contact, varied pauses and a seamless 20–25 second cycle.

Lighting should provide broad skylight illumination, believable contact shading
and restrained highlights on pipes and tools. Bake static light/shadow detail and
retain authored normal/roughness maps; adding random surface noise is insufficient.
Review the worker's face and clothing at the actual seated distance before adding
more characters. This is a proposed approach, not a finished preview.

Engineering budgets for this one bay (targets, not headset measurements):

| Component | Target |
|---|---|
| Worker, workwear and held tool | 20–25K triangles; limited materials and one rig |
| Chest, vice, selected pipes, bench and surrounding structure | 35–45K triangles after measured simplification |
| Total visible bay geometry | 55–70K triangles; initially at most 35 scene draw calls, excluding UI/hands |
| Worker textures | 2K colour; 1K normal and packed masks |
| Props |Two shared 2K atlas sets, each colour/normal/packed masks; bake from reviewed source maps |
| Architecture |One tiled 2K material set plus selective 1K baked lighting |
| Texture memory target |At most 64 MiB for the bay's compressed mipmapped textures; verify actual formats/residency rather than PNG sizes |

Deliver an actual Godot seated-view screenshot, a close worker/bench screenshot,
and a 30 second Godot animation recording with no cinematic post-processing. The
user approves that visible quality before duplicating the bay approach across the
other trades. Only then assess a Quest build, frame rate and sustained performance.
Preserve the working panorama/default and player/Jess flows during this milestone.

## Updated user direction: environments without people

Ryan proposed removing people and making the trade areas themselves active:
underground mine entrance with lights running down the tunnel, occasional
sparks in the electrical station, and a burst/leaking pipe in plumbing.
This supersedes four animated workers as the required visual destination.
Retain the worker source assets for reference; do not let worker refinement delay
this new direction. The .24 room was explicitly rejected as too basic.

Build rich, readable scenes around the seated viewer: real tunnel depth with
rock/rails/services and practical lights; electrical switchgear/cable trays/tools;
plumbing valves/gauges/drainage with intermittent spray; carpentry framing and a
properly equipped bench. Prefer inspected, redistributable models and detailed
materials over primitive placeholders. Preview one finished bay in Godot first.

Environmental effects should be independent and intermittent, silent by default,
and suspended during videos, Jess, wearer absence and loss of app focus. Do not
add artificial camera motion. Keep the current panorama default until approved.
Headset-removal playback and persistent input rays remain separate open defects.

extends RefCounted
## Local repeated fine detail supplements low frequency baked illumination.
const SURFACE := preload("res://shaders/training_hub_surface.gdshader")
const DETAIL := preload("res://environments/training_hub/surface_detail.png")
static func apply(root: Node) -> int:
	var changed := 0
	if root is MeshInstance3D and root.mesh:
		for index in root.mesh.get_surface_count():
			var original = root.get_active_material(index)
			if not original is StandardMaterial3D:
				continue
			var label: String = original.resource_name
			var floor_surface := label == "Warm concrete"
			var steel_surface := label == "Powder coated graphite"
			var ceiling := label == "Skylight"
			if not floor_surface and not steel_surface and not ceiling:
				continue
			if not ceiling and original.albedo_texture == null:
				continue
			var material := ShaderMaterial.new()
			material.shader = SURFACE
			material.set_shader_parameter("baked_color", original.albedo_texture)
			material.set_shader_parameter("surface_detail", DETAIL)
			material.set_shader_parameter("detail_scale", 2.0 if floor_surface else 4.0)
			material.set_shader_parameter("detail_strength", 0.075 if floor_surface else 0.015)
			material.set_shader_parameter("daylight_ceiling", ceiling)
			material.set_shader_parameter("neutral_steel", steel_surface)
			root.set_surface_override_material(index, material)
			changed += 1
	for child in root.get_children():
		changed += apply(child)
	return changed

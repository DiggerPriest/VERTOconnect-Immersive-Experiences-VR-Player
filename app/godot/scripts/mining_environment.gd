extends Node3D
var ambience: AudioStreamPlayer

func set_environment_active(enabled: bool) -> void:
	if ambience:
		ambience.set_active(enabled)

## Imported mining scenery stays world-fixed beneath the existing hub loader.
## Never let Blender's review cameras replace the XR camera.
func _ready() -> void:
	ambience = preload("res://scripts/mining_ambience.gd").new()
	ambience.name = "MiningAmbience"
	add_child(ambience)
	for camera in find_children("*", "Camera3D", true, false):
		# Setting current=false can make Godot select another imported camera.
		# Preview cameras have no role in the runtime environment.
		camera.free()
	for light in find_children("*", "Light3D", true, false):
		light.light_energy *= 0.15
	# The imported floor keeps tiled detail UVs and a separate baked AO atlas.
	for mesh in find_children("*", "MeshInstance3D", true, false):
		for index in range(mesh.mesh.get_surface_count()):
			var material = mesh.get_active_material(index)
			if material is StandardMaterial3D and (str(material.resource_name).begins_with("PACKED_PBR_") or str(material.resource_name).begins_with("AO_")):
				# COLOR_0 contains either packed paint or the authored AO multiplier.
				# The glTF importer leaves both disabled; retain their shading.
				material.vertex_color_use_as_albedo = true
			if material is StandardMaterial3D and "concrete_floor" in material.resource_name:
				var adjusted = material.duplicate()
				adjusted.albedo_color = Color(0.64, 0.76, 0.92)
				adjusted.ao_light_affect = 1.0
				mesh.set_surface_override_material(index, adjusted)
	var motion = preload("res://scripts/mining_scene_motion.gd").new()
	motion.name = "MachineryMotion"
	add_child(motion)
	motion.configure(self)
	var instances = preload("res://scripts/mining_mesh_instances.gd").new()
	instances.name = "CoalInstances"
	add_child(instances)
	instances.configure(self)

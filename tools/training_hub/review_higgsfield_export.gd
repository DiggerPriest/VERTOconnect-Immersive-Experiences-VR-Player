extends SceneTree
## Isolated GLB intake. No changes to the live player or source Blender scene.
## Usage: Godot --path <review project containing concept.glb> --script <this file>
func _initialize():
	call_deferred("review")

func review():
	var packed = load("res://concept.glb") as PackedScene
	if packed == null:
		push_error("Concept GLB failed to import")
		quit(1)
		return
	var model = packed.instantiate()
	root.add_child(model)
	var report = {"meshes": 0, "lights": 0, "cameras": [], "animations": [], "moving_tracks": 0}
	for node in model.find_children("*", "", true, false):
		if node is MeshInstance3D: report.meshes += 1
		if node is Light3D: report.lights += 1
		if node is Camera3D: report.cameras.append(str(node.name))
		if node is AnimationPlayer:
			for name in node.get_animation_list():
				if name == "RESET": continue
				var animation = node.get_animation(name)
				var moving = 0
				for track in range(animation.get_track_count()):
					if animation.track_get_key_count(track) < 2: continue
					var initial = animation.track_get_key_value(track, 0)
					for key in range(1, animation.track_get_key_count(track)):
						if animation.track_get_key_value(track, key) != initial:
							moving += 1
							break
				report.animations.append({"name": name, "duration": animation.length, "tracks": animation.get_track_count(), "changing_tracks": moving})
				report.moving_tracks += moving
	var output = FileAccess.open("res://godot-intake.json", FileAccess.WRITE)
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print("HIGGSFIELD_GODOT_INTAKE ", JSON.stringify(report))
	if "--motion-test" in OS.get_cmdline_user_args():
		var controller = load("res://mining_scene_motion.gd").new()
		model.add_child(controller)
		controller.configure(model)
		var before = {}
		for node in model.find_children("*", "Node3D", true, false):
			before[node.get_path()] = node.transform
		for player in controller.players: player.advance(0.37)
		var changed = []
		for node in model.find_children("*", "Node3D", true, false):
			if not node.transform.is_equal_approx(before[node.get_path()]):
				changed.append(str(node.name))
		print("HIGGSFIELD_RUNTIME_CHANGED ", JSON.stringify(changed))
		var motion_report = FileAccess.open("res://godot-motion.json", FileAccess.WRITE)
		motion_report.store_string(JSON.stringify({"changed_nodes": changed, "players": controller.players.size()}, "\t"))
		motion_report.close()
		if changed.is_empty():
			push_error("No imported machinery moved")
			quit(1)
			return
	if "--render" in OS.get_cmdline_user_args():
		var light_scale = 1.0
		for argument in OS.get_cmdline_user_args():
			if argument.begins_with("--light-scale="):
				light_scale = argument.trim_prefix("--light-scale=").to_float()
		for light in model.find_children("*", "Light3D", true, false):
			light.light_energy *= light_scale
		if "--floor-lookdev" in OS.get_cmdline_user_args():
			for mesh in model.find_children("*", "MeshInstance3D", true, false):
				for index in range(mesh.mesh.get_surface_count()):
					var material = mesh.get_active_material(index)
					if material is StandardMaterial3D and "concrete_floor" in material.resource_name:
						var adjusted = material.duplicate()
						adjusted.albedo_color = Color(0.64, 0.76, 0.92)
						adjusted.ao_light_affect = 1.0
						mesh.set_surface_override_material(index, adjusted)
		var camera = model.find_child("CAM_main", true, false) as Camera3D
		if camera == null:
			push_error("Missing seated camera")
			quit(1)
			return
		root.size = Vector2i(1600, 900)
		root.msaa_3d = Viewport.MSAA_4X
		camera.current = true
		var world = WorldEnvironment.new()
		world.environment = Environment.new()
		world.environment.background_mode = Environment.BG_COLOR
		world.environment.background_color = Color(0.025, 0.03, 0.04)
		world.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
		world.environment.ambient_light_color = Color(0.6, 0.65, 0.72)
		world.environment.ambient_light_energy = 0.35
		root.add_child(world)
		for frame in range(12): await process_frame
		await RenderingServer.frame_post_draw
		var filename = "res://godot-seated-intake-%s.png" % str(light_scale)
		root.get_texture().get_image().save_png(filename)
		print("HIGGSFIELD_GODOT_PREVIEW ", ProjectSettings.globalize_path(filename))
	# This proves import and changing keyframes, not visual quality or device performance.
	quit(0 if report.meshes > 0 and report.moving_tracks > 0 else 1)

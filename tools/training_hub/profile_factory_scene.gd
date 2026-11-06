extends SceneTree
## Relative desktop rendering audit, never a claim about Quest frame time.
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var args := OS.get_cmdline_user_args()
	assert(args.size() >= 2)
	var folder := args[0]
	if DirAccess.make_dir_recursive_absolute(folder) != OK:
		push_error("Cannot create profile output directory: " + folder)
		quit(1)
		return
	var variant := args[1]
	root.size = Vector2i(1280, 720)
	root.msaa_3d = Viewport.MSAA_2X
	if variant == "lod_2": root.mesh_lod_threshold = 2.0
	if variant == "lod_4": root.mesh_lod_threshold = 4.0
	var world := WorldEnvironment.new()
	world.environment = Environment.new()
	world.environment.background_mode = Environment.BG_COLOR
	world.environment.background_color = Color(0.12, 0.15, 0.19)
	load("res://scripts/training_hub.gd").apply_preview_lighting(world.environment)
	root.add_child(world)
	var started := Time.get_ticks_usec()
	var scene_path := args[2] if args.size() > 2 else "res://environments/mining_facility/mining_facility.tscn"
	var model: Node3D
	if scene_path.ends_with(".glb"):
		# Standalone export comparisons use exactly the same wrapper and
		# coordinate conversion as the imported mining scene.
		var document := GLTFDocument.new()
		var state := GLTFState.new()
		assert(document.append_from_file(scene_path, state) == OK)
		model = Node3D.new()
		model.set_script(load("res://scripts/mining_environment.gd"))
		var geometry := document.generate_scene(state)
		geometry.rotation.y = PI
		model.add_child(geometry)
	else:
		model = load(scene_path).instantiate()
	root.add_child(model)
	if variant == "uninstanced_control":
		var batches = model.get_node("CoalInstances")
		# Restore exactly the sources hidden by this controller. Restoring only
		# CV_ORE would omit new coal/rollers/seams and invalidate the control.
		for group in batches.batches:
			for source in group.sources: source.show()
			group.batch.free()
		batches.free()
	var load_ms := (Time.get_ticks_usec() - started) / 1000.0
	var lights: Array = []
	for light: Light3D in model.find_children("*", "Light3D", true, false):
		lights.append({"name": str(light.name), "type": light.get_class(), "energy": light.light_energy, "shadows": light.shadow_enabled, "range": light.omni_range if light is OmniLight3D else (light.spot_range if light is SpotLight3D else 0.0)})
		if variant == "lights_off": light.visible = false
		if variant == "shadows_off": light.shadow_enabled = false
	var controller := model.get_node("MachineryMotion")
	if variant == "motion_off": controller.process_mode = Node.PROCESS_MODE_DISABLED
	var motions: Array = []
	for player: AnimationPlayer in controller.players:
		var clip := player.get_animation("loop")
		var keys := 0
		for t in clip.get_track_count(): keys += clip.track_get_key_count(t)
		motions.append({"length": clip.length, "tracks": clip.get_track_count(), "keys": keys})
	var mesh_groups := {}
	var surface_count := 0
	for node: MeshInstance3D in model.find_children("*", "MeshInstance3D", true, false):
		var key := str(node.mesh.get_instance_id())
		if not mesh_groups.has(key): mesh_groups[key] = []
		mesh_groups[key].append(str(node.name))
		surface_count += node.mesh.get_surface_count()
	var repeats: Array = []
	for key in mesh_groups:
		if mesh_groups[key].size() > 1: repeats.append({"count": mesh_groups[key].size(), "examples": mesh_groups[key].slice(0,4)})
	var camera := Camera3D.new()
	root.add_child(camera)
	var eye_height := float(args[3]) if args.size() > 3 else 1.6
	camera.position = Vector3(0, eye_height, 0)
	camera.fov = 85
	camera.current = true
	var views := {"portal": Vector3(0,1.25,-22), "fans": Vector3(16,2.4,-14), "conveyor": Vector3(-13,2,-4), "rear": Vector3(-1,2,22), "processing": Vector3(12,2.5,8), "plant": Vector3(-12,2.5,7), "left": Vector3(-22,1.25,0), "right": Vector3(22,1.25,0), "up": Vector3(0,23.25,-.01), "down": Vector3(0,-20.75,-.01)}
	var samples: Array = []
	for label in views:
		camera.look_at(views[label])
		for frame in range(30): await process_frame
		var times: Array[float] = []
		var begin := Time.get_ticks_usec()
		var last := begin
		var draw_calls := 0
		var primitives := 0
		while Time.get_ticks_usec() - begin < 2000000:
			await process_frame
			await RenderingServer.frame_post_draw
			var now := Time.get_ticks_usec()
			times.append(float(now-last)/1000.0)
			last = now
			draw_calls = int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
			primitives = int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME))
		times.sort()
		samples.append({"view": label, "draw_calls": draw_calls, "primitives": primitives, "frame_interval_ms_median": times[times.size()/2], "frame_interval_ms_p95": times[int(times.size()*.95)], "frames": times.size()})
		root.get_texture().get_image().save_png(folder.path_join(variant+"_"+label+".png"))
	var report := {"scope": "desktop Compatibility renderer, 1280x720, 2xMSAA; Quest unmeasured", "variant": variant, "eye_height": eye_height, "mesh_lod_threshold": root.mesh_lod_threshold, "load_and_motion_setup_ms": load_ms, "mesh_instances": model.find_children("*", "MeshInstance3D", true, false).size(), "surfaces": surface_count, "lights": lights, "motion_groups": motions, "repeated_meshes": repeats, "views": samples, "static_memory_bytes": Performance.get_monitor(Performance.MEMORY_STATIC), "video_memory_bytes": Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)}
	var file := FileAccess.open(folder.path_join(variant+".json"), FileAccess.WRITE)
	if file == null:
		push_error("Cannot write profile report")
		quit(1)
		return
	file.store_string(JSON.stringify(report,"  "))
	file.close()
	print("FACTORY_PROFILE ", variant, " ", JSON.stringify(samples))
	model.queue_free()
	await process_frame
	quit()

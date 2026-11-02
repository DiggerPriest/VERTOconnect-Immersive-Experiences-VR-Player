extends SceneTree
## Actual Godot Compatibility-renderer preview at seated eye height.
var actors: Array[Node] = []

func _collect_actors(node: Node) -> void:
	if node.has_method("seek_elapsed"):
		if not node.valid:
			push_error(node.diagnostic_error)
			quit(1)
		actors.append(node)
		node.set_process(false)
	for child in node.get_children():
		_collect_actors(child)

func _pose(seconds: float) -> void:
	for actor in actors:
		actor.seek_elapsed(seconds)

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var viewport := SubViewport.new()
	viewport.size = Vector2i(1600, 1000)
	viewport.own_world_3d = true
	viewport.msaa_3d = Viewport.MSAA_4X
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var world := WorldEnvironment.new()
	world.environment = Environment.new()
	world.environment.background_mode = Environment.BG_COLOR
	world.environment.background_color = Color(0.55, 0.67, 0.8)
	preload("res://scripts/training_hub.gd").apply_preview_lighting(world.environment)
	viewport.add_child(world)
	var packed := load("res://environments/training_hub/training_hub.tscn") as PackedScene
	if not packed:
		quit(1)
		return
	var hub := packed.instantiate()
	preload("res://scripts/training_hub_surfaces.gd").apply(hub)
	viewport.add_child(hub)
	_collect_actors(hub)
	if actors.size() != 4:
		push_error("Expected four valid trade actors")
		quit(1)
		return
	_pose(8.0)
	var camera := Camera3D.new()
	camera.position = Vector3(0, 1.25, 0)
	camera.fov = 85
	viewport.add_child(camera)
	var output := ProjectSettings.globalize_path("res://../../build/output/training-hub")
	DirAccess.make_dir_recursive_absolute(output)
	for view in [{"name": "front", "yaw": 0.0}, {"name": "overview", "yaw": -0.55}, {"name": "plumbing", "yaw": -PI/2}, {"name": "carpentry", "yaw": PI}, {"name": "mechanical", "yaw": PI/2}]:
		camera.rotation = Vector3(0.1, view.yaw, 0)
		await process_frame
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		viewport.get_texture().get_image().save_png(output.path_join(view.name + ".png"))
	# Inspect all stations at three runtime clock samples.
	camera.fov = 55
	for station in [{"name": "electrical", "yaw": 0.0}, {"name": "plumbing", "yaw": -PI/2}, {"name": "carpentry", "yaw": PI}, {"name": "mechanical", "yaw": PI/2}]:
		camera.position = Vector3(3.0, 1.5, -5.0).rotated(Vector3.UP, station.yaw)
		camera.look_at(Vector3(1.1, 1.0, -8.0).rotated(Vector3.UP, station.yaw))
		for second in [0.0, 8.0, 16.0]:
			_pose(second)
			await process_frame
			await RenderingServer.frame_post_draw
			await RenderingServer.frame_post_draw
			viewport.get_texture().get_image().save_png(output.path_join(station.name + "-worker-%02d.png" % int(second)))
	camera.position = Vector3(3.0, 1.5, -5.0)
	camera.look_at(Vector3(1.1, 1.0, -8.0))
	var record_all := OS.get_cmdline_user_args().has("--record-all")
	if record_all or OS.get_cmdline_user_args().has("--record-hub"):
		viewport.size = Vector2i(960, 600)
		var stations := [{"name": "electrical", "yaw": 0.0}]
		if record_all:
			stations.append_array([{"name": "plumbing", "yaw": -PI/2}, {"name": "carpentry", "yaw": PI}, {"name": "mechanical", "yaw": PI/2}])
		for station in stations:
			camera.position = Vector3(3.0, 1.5, -5.0).rotated(Vector3.UP, station.yaw)
			camera.look_at(Vector3(1.1, 1.0, -8.0).rotated(Vector3.UP, station.yaw))
			var frames := output.path_join("frames-" + station.name if record_all else "frames")
			DirAccess.make_dir_recursive_absolute(frames)
			# 32 seconds covers every routine plus its idle hold at least once.
			for frame in range(320 if record_all else 200):
				_pose(frame / 10.0)
				await process_frame
				await RenderingServer.frame_post_draw
				viewport.get_texture().get_image().save_png(frames.path_join("%04d.png" % frame))
	print("Training hub Godot previews: " + output)
	viewport.queue_free()
	quit()

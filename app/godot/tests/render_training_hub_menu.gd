extends SceneTree
## Real main.tscn and its menus, with training hub selected only in memory.
func _initialize() -> void:
	call_deferred("_run")

func _capture(viewport: SubViewport, output: String, name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	viewport.get_texture().get_image().save_png(output.path_join(name + ".png"))

func _run() -> void:
	var viewport := SubViewport.new()
	viewport.size = Vector2i(1600, 1000)
	viewport.own_world_3d = true
	viewport.msaa_3d = Viewport.MSAA_4X
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var app = load("res://scenes/main.tscn").instantiate()
	viewport.add_child(app)
	app.xr_camera.position = Vector3(0, 1.25, 0)
	app.xr_camera.fov = 85
	app.background.choice = "training_hub"
	app._update_background()
	app._show_recent_menu()
	var started := Time.get_ticks_msec()
	while not app.training_hub.content and Time.get_ticks_msec() - started < 30000:
		await process_frame
	if not app.training_hub.content:
		push_error("Training hub failed to load into actual main app")
		quit(1)
		return
	app._show_recent_menu()
	app.recent_menu.start_managed_files("/storage/emulated/0")
	app.recent_menu._local_entries = [
		{"id": "/preview/electrical.mp4", "title": "Electrical — a day in the workshop.mp4", "kind": "video", "uri": "file:///preview/electrical.mp4"},
		{"id": "/preview/plumbing.mp4", "title": "Plumbing — working with water systems.mp4", "kind": "video", "uri": "file:///preview/plumbing.mp4"},
		{"id": "/preview/carpentry.mp4", "title": "Carpentry — building your future.mp4", "kind": "video", "uri": "file:///preview/carpentry.mp4"}
	]
	app.recent_menu.refresh()
	app._place_menu(app.recent_menu)
	var output := ProjectSettings.globalize_path("res://../../build/output/training-hub")
	DirAccess.make_dir_recursive_absolute(output)
	await _capture(viewport, output, "main-menu")
	app.recent_menu.looking_around = true
	app.recent_menu.refresh()
	await _capture(viewport, output, "main-look-around")
	app.xr_camera.rotation.y = -PI / 2
	await _capture(viewport, output, "main-look-around-right")
	app.xr_camera.rotation.y = 0
	app.recent_menu.looking_around = false
	app.recent_menu.refresh()
	await _capture(viewport, output, "main-menu-returned")
	print("MAIN_APP_HUB_PREVIEW complete: ", output)
	viewport.queue_free()
	await process_frame
	quit()

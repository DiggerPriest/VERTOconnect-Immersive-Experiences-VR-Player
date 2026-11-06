extends SceneTree
## Real Main + runtime board, isolated history fixtures; never touches user history.
var failures: Array[String] = []
func _initialize():
	if not preload("res://tests/support/test_result.gd").prepare(self): return
	call_deferred("run")
func run():
	var args := OS.get_cmdline_user_args()
	assert(args.size() == 1)
	var folder := args[0]
	DirAccess.make_dir_recursive_absolute(folder)
	root.size = Vector2i(1280,720)
	root.msaa_3d = Viewport.MSAA_2X
	var main = preload("res://scripts/main.gd").new()
	main.settings_path = "user://review-settings.cfg"
	root.add_child(main)
	var deadline := Time.get_ticks_msec()+30000
	while main.training_hub.loading and Time.get_ticks_msec()<deadline: await process_frame
	assert(main.training_hub.ready_to_show())
	main.recent_menu.dismiss(); main.player_menu.dismiss()
	main.video.clear_history(); main._update_training_hub_activity()
	assert(main.mining_noticeboard.visible)
	var camera: Camera3D = main.xr_camera
	assert(camera.global_position.is_equal_approx(Vector3(0,1.6,0)))
	camera.fov=85
	for i in 20: await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(folder.path_join("forward_board_empty.png"))
	camera.look_at(main.mining_noticeboard.global_position)
	for i in 20: await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(folder.path_join("board_empty.png"))
	for i in 4:
		# Explicit fixtures exercise captions, layout and ray reachability only.
		main.video.recent_files.opened("file:///review-fixture-%d.mp4"%i,["Conveyor isolation","Decline access","Workshop inspection","Ventilation checks"][i],true)
	main.mining_noticeboard.refresh_history(true)
	main._update_training_hub_activity()
	for i in 20: await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(folder.path_join("board_fixture_titles.png"))
	var checks: Array=[]
	for button in main.mining_noticeboard._buttons:
		var point: Vector3=button.node.global_position
		var ray=[camera.global_position,point-camera.global_position]
		var reachable: bool=main._noticeboard_hit(ray)
		checks.append({"target":button.target,"reachable":reachable,"distance_m":ray[1].length()})
		if not reachable: failures.append("Poster not reachable: %s"%button.target)
	var output=FileAccess.open(folder.path_join("interaction-review.json"),FileAccess.WRITE)
	output.store_string(JSON.stringify({"scope":"Real Main, desktop camera, isolated fixture history; native decoding not tested","eye":camera.global_position,"posters":checks,"failures":failures},"  "))
	main.queue_free();await process_frame
	preload("res://tests/support/test_result.gd").finish(self,0 if failures.is_empty() else 1)

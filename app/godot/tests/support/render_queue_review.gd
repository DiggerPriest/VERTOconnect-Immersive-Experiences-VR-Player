extends SceneTree
## Visual review of the actual queue controls, without opening a video or changing user settings.
var menu: Node3D
var state := {"title": "Mining induction", "has_video": true, "source_uri": "file:///induction.mp4", "queue_items": [{"uri": "file:///induction.mp4", "title": "Mining induction"}, {"uri": "file:///workshop.mp4", "title": "Workshop orientation"}, {"uri": "file:///decline.mp4", "title": "Decline access"}], "queue_shuffle": false, "queue_loop": true}
func _initialize():
	call_deferred("run")
func run():
	root.size = Vector2i(1280, 960)
	var world := WorldEnvironment.new()
	world.environment = Environment.new()
	world.environment.background_mode = Environment.BG_COLOR
	world.environment.background_color = Color(0.045, 0.05, 0.06)
	root.add_child(world)
	menu = preload("res://scripts/player_menu.gd").new()
	menu.state_provider = func(): return state
	root.add_child(menu)
	menu._quick_open = "queue"
	menu.refresh()
	menu.visible = true
	var camera := Camera3D.new()
	root.add_child(camera)
	camera.position = Vector3(0, 0.30, 1.35)
	camera.fov = 20
	camera.current = true
	var destination := ProjectSettings.globalize_path("res://../../build/queue-review.png")
	for i in range(10): await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(destination)
	print("QUEUE_REVIEW ", destination)
	menu.queue_free()
	await process_frame
	quit()

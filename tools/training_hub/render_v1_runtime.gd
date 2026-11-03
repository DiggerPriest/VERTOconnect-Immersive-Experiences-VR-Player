extends SceneTree
## Run with the player project and --xr-mode off; uses its real scene wrapper.
func _initialize(): call_deferred("run")

func run():
	root.size = Vector2i(1280, 720)
	var world = WorldEnvironment.new()
	world.environment = Environment.new()
	world.environment.background_mode = Environment.BG_COLOR
	world.environment.background_color = Color(0.12, 0.15, 0.19)
	preload("res://scripts/training_hub.gd").apply_preview_lighting(world.environment)
	root.add_child(world)
	var model = load("res://environments/mining_facility/mining_facility.tscn").instantiate()
	root.add_child(model)
	var camera = Camera3D.new()
	root.add_child(camera)
	camera.position = Vector3(0, 1.25, 0)
	camera.fov = 85
	camera.current = true
	var views = {"portal": Vector3(1, 2, -22), "fans": Vector3(16, 2.4, -14), "conveyor": Vector3(-13, 2, -4), "door": Vector3(-1, 2, 22)}
	for label in views:
		camera.look_at(views[label])
		for frame in range(12): await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("/tmp/verto-runtime-%s.png" % label)
	model.queue_free()
	await create_timer(0.1).timeout
	quit()

extends SceneTree
## Actual Compatibility-renderer side/front/top contact inspection, no import.
func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var viewport := SubViewport.new()
	viewport.size = Vector2i(1400, 1000)
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
	var hub := preload("res://environments/training_hub/training_hub.tscn").instantiate()
	viewport.add_child(hub)
	var camera := Camera3D.new()
	camera.fov = 48
	viewport.add_child(camera)
	var output := ProjectSettings.globalize_path("res://../../build/output/training-hub/contacts")
	DirAccess.make_dir_recursive_absolute(output)
	for item in [{"name":"electrical", "node":"ElectricalWorker", "yaw":0.0,"time":9.0}, {"name":"plumbing","node":"PlumbingWorker","yaw":-PI/2,"time":10.0}, {"name":"carpentry","node":"CarpentryWorker","yaw":PI,"time":8.0}, {"name":"mechanical","node":"MechanicalWorker","yaw":PI/2,"time":3.64}]:
		var actor = hub.get_node(item.node)
		actor.set_process(false)
		actor.phase_offset = 0.0
		actor.idle_seconds = 0.0
		actor.seek_elapsed(item.time)
		for angle in [{"name":"side","position":Vector3(2.25,1.55,-8.05)}, {"name":"front","position":Vector3(1.1,1.6,-8.85)}, {"name":"upper","position":Vector3(1.45,2.25,-8.1)}]:
			camera.position = angle.position.rotated(Vector3.UP,item.yaw)
			camera.look_at(Vector3(1.1,1.22,-8.05).rotated(Vector3.UP,item.yaw))
			await process_frame
			await RenderingServer.frame_post_draw
			await RenderingServer.frame_post_draw
			viewport.get_texture().get_image().save_png(output.path_join(item.name+"-"+angle.name+".png"))
	print("CONTACT_PREVIEWS ",output)
	viewport.queue_free()
	quit()

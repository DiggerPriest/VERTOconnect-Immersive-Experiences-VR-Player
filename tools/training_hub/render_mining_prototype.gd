extends SceneTree
## Runs only in the isolated generated prototype project, not the player.
func _initialize():call_deferred("run")
func run():
	var viewport=SubViewport.new();viewport.size=Vector2i(1600,1000);viewport.own_world_3d=true;viewport.msaa_3d=Viewport.MSAA_4X;viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(viewport)
	var world=WorldEnvironment.new();var env=Environment.new();world.environment=env;env.background_mode=Environment.BG_COLOR;env.background_color=Color(.016,.021,.03);env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color(.45,.56,.68);env.ambient_light_energy=.45;env.tonemap_mode=Environment.TONE_MAPPER_FILMIC;viewport.add_child(world)
	var model=load("res://mining-prototype.glb").instantiate();viewport.add_child(model)
	var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-35,20,0);sun.light_color=Color(.64,.77,1);sun.light_energy=.16;sun.shadow_enabled=true;viewport.add_child(sun)
	for index in range(7):
		var y=1.0+index*4.0;var light=OmniLight3D.new();light.position=Vector3(.3,2.75,-y-15);light.omni_range=6.2;light.light_energy=.42;light.light_color=Color(1,.73,.39) if index%2==0 else Color(.58,.76,1);light.shadow_enabled=index<2;viewport.add_child(light)
	var front=OmniLight3D.new();front.position=Vector3(-2,7,3);front.light_color=Color(.69,.82,1);front.light_energy=1.2;front.omni_range=35;viewport.add_child(front)
	var camera=Camera3D.new();camera.position=Vector3(0,1.65,5);camera.fov=85;viewport.add_child(camera);camera.look_at(Vector3(1,3,-14));camera.current=true
	for index in range(24):await process_frame
	await RenderingServer.frame_post_draw
	var path=ProjectSettings.globalize_path("res://mining-seated-preview.png");viewport.get_texture().get_image().save_png(path);print("MINING_PREVIEW ",path)
	camera.position=Vector3(0,1.65,5);camera.look_at(Vector3(10,2.8,-1))
	for index in range(12):await process_frame
	await RenderingServer.frame_post_draw
	viewport.get_texture().get_image().save_png(ProjectSettings.globalize_path("res://mining-depth-preview.png"))
	viewport.queue_free();await process_frame;quit()

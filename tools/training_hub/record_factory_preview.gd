extends SceneTree
## Fixed-position 16-second development recording; no application camera changes.
## Run with Godot --fixed-fps 30 --write-movie OUTPUT.avi --script this.gd.
func _initialize():
 call_deferred("run")
func run():
 root.size=Vector2i(960,540)
 root.msaa_3d=Viewport.MSAA_2X
 var world=WorldEnvironment.new()
 world.environment=Environment.new()
 world.environment.background_mode=Environment.BG_COLOR
 world.environment.background_color=Color(.12,.15,.19)
 load("res://scripts/training_hub.gd").apply_preview_lighting(world.environment)
 root.add_child(world)
 var model=load("res://environments/mining_facility_density/mining_facility.tscn").instantiate()
 root.add_child(model)
 var camera=Camera3D.new()
 root.add_child(camera)
 camera.position=Vector3(0,1.6,0)
 camera.fov=85
 camera.look_at(Vector3(-13,2,-4))
 camera.current=true
 for i in 480:await process_frame
 quit(0)

extends SceneTree
func _initialize():
	call_deferred("verify")
func verify():
	var scene = load("res://factory.glb") as PackedScene
	assert(scene != null, "GLB did not import")
	var model = scene.instantiate()
	root.add_child(model)
	assert(model.find_child("Cube", true, false) == null, "Unrelated default cube leaked into export")
	assert(model.find_child("PROXY_fan*", true, false) == null, "Hidden fan proxy leaked into export")
	var player = model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	assert(player != null, "Missing exported AnimationPlayer")
	var rotors: Array[Node3D] = []
	for node in model.find_children("*rotor*", "Node3D", true, false):
		rotors.append(node)
	assert(rotors.size() == 2, "Expected two exported fan pivots")
	var moved = {}
	for animation in player.get_animation_list():
		if animation == "RESET": continue
		player.play(animation)
		player.seek(0.0, true)
		var before = rotors.map(func(n): return n.transform)
		player.seek(0.5, true)
		for i in range(rotors.size()):
			if not before[i].is_equal_approx(rotors[i].transform): moved[rotors[i].name] = true
	assert(moved.size() == 2, "Export lost one or both fan animations")
	print("FACTORY_GODOT_MOTION_PASS ", moved.keys())
	quit(0)

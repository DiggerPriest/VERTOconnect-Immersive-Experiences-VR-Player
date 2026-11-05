extends SceneTree
## Exercise the actual exported factory, including rigid meshes beneath moving rigs.
var failures: Array[String] = []
func check(ok: bool, message: String) -> void:
	if not ok: failures.append(message)
func _initialize() -> void:
	if not preload("res://tests/support/test_result.gd").prepare(self): return
	call_deferred("run")
func run() -> void:
	var model := load(preload("res://scripts/training_hub.gd").MINING_SCENE).instantiate() as Node3D
	root.add_child(model)
	var motion := model.get_node("MachineryMotion")
	check(not motion.players.is_empty(), "Exported factory has motion players")
	check(model.find_children("*", "Camera3D", true, false).is_empty(), "Review cameras cannot replace the headset camera")
	var names := ["EXP_Screen_0_Rotor", "EXP_Screen_1_Rotor", "FIT_Pump_0_ShaftMotion", "FIT_Pump_1_ShaftMotion", "FIT_TestBench_Rotor", "FIT_CraneBridgeMotion", "FIT_CraneTrolleyMotion", "FIT_DrumOre_0_00", "FIT_DrumOre_1_00", "FIT_Rear_RamMotion", "DENS_Compressor_FanMotion"]
	for player in motion.players:
		player.seek(0, true)
		player.advance(0)
	var before := {}
	for label in names:
		var node := model.find_child(label, true, false) as Node3D
		check(is_instance_valid(node), "Authored moving equipment survives export: " + label)
		if node: before[label] = node.global_transform
	var rigid := model.find_children("RIGID_EXP_Screen*", "MeshInstance3D", true, false)
	# Material packing merges the former two surfaces per drum into one mesh.
	# Check each independently animated parent retains the measured geometry.
	for label in ["EXP_Screen_0_Rotor", "EXP_Screen_1_Rotor"]:
		var vertex_count := 0
		for mesh in rigid:
			if str(mesh.get_parent().name) != label: continue
			for surface in mesh.mesh.get_surface_count():
				vertex_count += mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX].size()
		check(vertex_count >= 6464, "Complete drum panels and hoops remain under " + label)
	var initial_rigid: Array[Transform3D] = []
	for mesh in rigid: initial_rigid.append(mesh.global_transform)
	for player in motion.players: player.advance(14.3)
	for label in before:
		check(not (model.find_child(label, true, false) as Node3D).global_transform.is_equal_approx(before[label]), "Exported equipment actually moves: " + label)
	for i in rigid.size():
		check(not rigid[i].global_transform.is_equal_approx(initial_rigid[i]), "Batched drum mesh follows its rotor")
	model.process_mode = Node.PROCESS_MODE_DISABLED
	var hook := model.find_child("CRANE_hook_block", true, false) as Node3D
	var held := hook.global_transform
	await create_timer(.15).timeout
	check(hook.global_transform.is_equal_approx(held), "Suspended environment freezes the moving crane")
	model.queue_free()
	await process_frame
	for failure in failures: push_error(failure)
	print("FACTORY_EXPANSION ", "PASS" if failures.is_empty() else "FAIL", " issues=", failures.size())
	preload("res://tests/support/test_result.gd").finish(self, 0 if failures.is_empty() else 1)

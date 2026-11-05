extends SceneTree
func _initialize() -> void:
	if not preload("res://tests/support/test_result.gd").prepare(self): return
	call_deferred("run")
func run() -> void:
	var model := Node3D.new()
	model.position = Vector3(3,2,1)
	model.rotation.y = .7
	root.add_child(model)
	var mesh := BoxMesh.new()
	var material := StandardMaterial3D.new()
	mesh.material = material
	var sources: Array[MeshInstance3D] = []
	for index in range(8):
		var ore := MeshInstance3D.new()
		ore.name = "CV_ORE_%03d" % index
		ore.mesh = mesh
		ore.position = Vector3(index * .4, 1.4, -2)
		ore.rotation.z = index * .1
		model.add_child(ore)
		sources.append(ore)
	for zone in ["C1", "C2"]:
		for index in range(4):
			var ore := MeshInstance3D.new()
			ore.name = "DENS_ORE_%s_%02d" % [zone,index]
			ore.mesh = mesh
			ore.position = Vector3(index, 2, 20 if zone == "C1" else -20)
			model.add_child(ore)
	for prefix in ["CV_CarryIdler_", "CV_BeltSeam_", "CV2_COAL_"]:
		for index in range(4):
			var part := MeshInstance3D.new()
			part.name = prefix + str(index)
			part.mesh = mesh
			part.position = Vector3(index, 1, -10)
			model.add_child(part)
	var unrelated := MeshInstance3D.new()
	unrelated.name = "OrdinaryMachine"
	unrelated.mesh = mesh
	model.add_child(unrelated)
	var controller := preload("res://scripts/mining_mesh_instances.gd").new()
	model.add_child(controller)
	controller.configure(model)
	assert(controller.batches.size() == 6, "Shared geometry stays in separate conveyor culling zones")
	assert(unrelated.visible, "Unrelated geometry remains visible")
	var batch: MultiMeshInstance3D = controller.batches[0].batch
	assert(batch.multimesh.instance_count == 8 and batch.material_override == material)
	controller.configure(model)
	assert(controller.batches.size() == 6, "Repeated configure is idempotent")
	if DisplayServer.get_name() == "headless":
		# Dummy RenderingServer does not retain instance transforms: its getter
		# always returns identity. Rendered execution below proves buffer poses.
		for source in sources: assert(not source.visible)
		model.process_mode = Node.PROCESS_MODE_DISABLED
		assert(not controller.can_process())
		model.queue_free()
		await process_frame
		print("MINING_INSTANCES_CPU_PASS: grouping, materials, idempotency, suspension; GPU readback unavailable in Dummy renderer")
		preload("res://tests/support/test_result.gd").finish(self,0)
		return
	for index in sources.size():
		assert(not sources[index].visible)
		var actual := batch.global_transform * batch.multimesh.get_instance_transform(index)
		if not actual.is_equal_approx(sources[index].global_transform):
			print("INSTANCE_POSE_MISMATCH ", index, " source=", sources[index].global_transform, " batch=", batch.global_transform, " instance=", batch.multimesh.get_instance_transform(index))
			preload("res://tests/support/test_result.gd").finish(self,1)
			return
	controller.configure(model)
	assert(controller.batches.size() == 6, "Repeated configure is idempotent")
	sources[3].position.y += .6
	await process_frame
	await process_frame
	assert((batch.global_transform * batch.multimesh.get_instance_transform(3)).is_equal_approx(sources[3].global_transform), "Animation transform updates reach the instances")
	model.process_mode = Node.PROCESS_MODE_DISABLED
	var held := batch.multimesh.get_instance_transform(3)
	sources[3].position.y += .5
	await create_timer(.1).timeout
	assert(batch.multimesh.get_instance_transform(3).is_equal_approx(held), "Suspended environment freezes instance updates")
	model.process_mode = Node.PROCESS_MODE_INHERIT
	await process_frame
	await process_frame
	assert((batch.global_transform * batch.multimesh.get_instance_transform(3)).is_equal_approx(sources[3].global_transform), "Instance updates resume with the scene")
	model.queue_free()
	await process_frame
	print("MINING_INSTANCES_PASS: world poses, shared materials, idempotency, animation updates and suspension")
	preload("res://tests/support/test_result.gd").finish(self,0)

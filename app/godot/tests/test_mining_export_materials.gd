extends SceneTree
func _initialize():
	if not preload("res://tests/support/test_result.gd").prepare(self):return
	call_deferred("run")
func run():
	var model=load("res://environments/mining_facility_density/mining_facility.tscn").instantiate()
	root.add_child(model)
	var ao=0;var packed=0
	for node in model.find_children("*","MeshInstance3D",true,false):
		for i in node.mesh.get_surface_count():
			var material=node.get_active_material(i)
			if not material is StandardMaterial3D:continue
			var label=str(material.resource_name)
			if label.begins_with("AO_") or label.begins_with("PACKED_PBR_"):
				assert(material.vertex_color_use_as_albedo,"Authored tint/AO must reach runtime shading")
				assert(node.mesh.surface_get_arrays(i)[Mesh.ARRAY_COLOR].size()>0,"Material flag alone does not prove exported color data")
				if label.begins_with("AO_"):
					for color in node.mesh.surface_get_arrays(i)[Mesh.ARRAY_COLOR]:
						assert(color.r>=.61 and color.g>=.61 and color.b>=.61,"AO cannot be black: bake is bounded to 0.62–1; modifiers must precede baking")
					ao+=1
				else:packed+=1
	assert(ao>0 and packed>0,"Exercise both material families in the real exported scene")
	var controller=model.get_node("CoalInstances")
	var grouped={}
	var source_count=0
	for group in controller.batches:
		for source in group.sources:
			var zone=controller._instance_zone(str(source.name))
			grouped[zone]=grouped.get(zone,0)+1
			if zone == "original":
				# Native source-only export proves each original coal chunk has
				# 20 triangles. Joining a shared static mesh once inflated 12
				# animated chunks to 360 triangles and corrupted their shape.
				assert(source.mesh.get_faces().size() == 60, "Static batching contaminated an animated coal mesh: " + str(source.name))
			assert(not source.visible,"Instanced source must not draw twice")
			source_count+=1
	for zone in ["rollers","seams","stockpile","original"]:
		assert(grouped.get(zone,0)>=4,"Actual imported geometry must instance: "+zone)
	for i in range(1,14):
		assert(grouped.get("C"+str(i),0)==10,"All added conveyor coal must survive import and batch")
	if DisplayServer.get_name() != "headless":
		# Verify the real imported animations, not only synthetic fixture poses.
		for sample in range(3):
			await create_timer(.15).timeout
			await RenderingServer.frame_post_draw
			for group in controller.batches:
				for index in group.sources.size():
					var actual=group.batch.global_transform * group.batch.multimesh.get_instance_transform(index)
					assert(actual.is_equal_approx(group.sources[index].global_transform),"Imported animated instance diverged: "+str(group.sources[index].name))
		print("MINING_IMPORTED_INSTANCE_GPU_POSES_PASS samples=3 sources=",source_count)
	print("MINING_EXPORT_MATERIALS_PASS ao=",ao," packed=",packed," instanced_sources=",source_count," batches=",controller.batches.size()," zones=",grouped)
	model.queue_free();await process_frame
	preload("res://tests/support/test_result.gd").finish(self,0)

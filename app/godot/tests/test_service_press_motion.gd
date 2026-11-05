extends SceneTree
## Real imported press stroke, telescoping anchor and suspension regression.
func _initialize() -> void:
	if not preload("res://tests/support/test_result.gd").prepare(self):return
	call_deferred("run")
func bounds(node: MeshInstance3D) -> AABB:
	return node.global_transform * node.get_aabb()
func run() -> void:
	var model = load(preload("res://scripts/training_hub.gd").MINING_SCENE).instantiate()
	root.add_child(model)
	var piston = model.find_child("DENS_Press_Piston",true,false) as MeshInstance3D
	var plate = model.find_child("DENS_Press_ToolPlate",true,false) as MeshInstance3D
	if piston == null or plate == null:
		push_error("Animated press components missing from imported scene")
		model.queue_free();await process_frame
		preload("res://tests/support/test_result.gd").finish(self,1);return
	var motion = model.get_node("MachineryMotion")
	for player in motion.players:player.seek(0,true);player.advance(0)
	var anchor := bounds(piston).end.y
	var min_y := INF
	var max_y := -INF
	var clearance := INF
	var max_anchor_error := 0.0
	var failures := 0
	for step in range(3001):
		var pa := bounds(piston)
		var tool := bounds(plate)
		min_y = minf(min_y,tool.position.y);max_y = maxf(max_y,tool.position.y)
		clearance = minf(clearance,tool.position.y-1.4)
		max_anchor_error = maxf(max_anchor_error,absf(pa.end.y-anchor))
		if pa.position.y < tool.position.y or pa.position.y > tool.end.y:failures+=1
		for player in motion.players:player.advance(1.0/60.0)
	if absf(max_y-min_y-.65)>.002 or clearance<.20 or max_anchor_error>.0001:failures+=1
	model.process_mode=Node.PROCESS_MODE_DISABLED
	var held: Transform3D = plate.global_transform
	await create_timer(.1).timeout
	if not plate.global_transform.is_equal_approx(held):failures+=1
	print("SERVICE_PRESS ","PASS" if failures==0 else "FAIL"," stroke=",max_y-min_y," clearance=",clearance," anchor_error=",max_anchor_error," failures=",failures)
	model.queue_free();await process_frame
	preload("res://tests/support/test_result.gd").finish(self,0 if failures==0 else 1)

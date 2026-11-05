extends SceneTree
## Actual imported C11-C13 transforms, including export-resampled wrap intervals.
func _initialize() -> void:
	if not preload("res://tests/support/test_result.gd").prepare(self): return
	call_deferred("run")
func run() -> void:
	var model = load(preload("res://scripts/training_hub.gd").MINING_SCENE).instantiate()
	root.add_child(model)
	var motion = model.get_node("MachineryMotion")
	var routes = {
		"C11": [Vector3(-11.3,7.8,-22.3),Vector3(-11.3,7.8,12)],
		"C12": [Vector3(-11.3,7.4,12),Vector3(-30,10.2,12)],
		"C13": [Vector3(-11.3,.75,-25.8),Vector3(-11.3,.75,-23.2)]
	}
	var rocks: Array[Node3D] = []
	var zones: Array[String] = []
	for zone in routes:
		var found = model.find_children("DENS_ORE_"+zone+"_*", "Node3D", true, false)
		if found.size() != 10:
			push_error("Expected ten imported coal pieces for " + zone + "; got " + str(found.size()))
			model.queue_free();await process_frame
			preload("res://tests/support/test_result.gd").finish(self,1)
			return
		for node in found:
			rocks.append(node);zones.append(zone)
	for player in motion.players:
		player.seek(0,true);player.advance(0)
	var previous: Array[Vector3] = []
	var visible: Array[bool] = []
	var travelled: Array[float] = []
	for rock in rocks:
		previous.append(rock.global_position);visible.append(rock.scale.x>.1);travelled.append(0.0)
	var largest_step := 0.0
	var off_belt := 0
	for sample in range(2400):
		for player in motion.players:player.advance(1.0/60.0)
		for i in rocks.size():
			var rock: Node3D = rocks[i]
			var current: Vector3 = rock.global_position
			var shown: bool = rock.scale.x>.1
			if shown:
				var ends = routes[zones[i]]
				var closest := Geometry3D.get_closest_point_to_segment(current,ends[0],ends[1])
				if current.distance_to(closest)>.37:off_belt+=1
			if shown and visible[i]:
				var step: float = current.distance_to(previous[i])
				if step>.15:print("EAST_JUMP ",rock.name," sample=",sample," scale=",rock.scale.x," step=",step)
				largest_step=max(largest_step,step);travelled[i]+=step
			previous[i]=current;visible[i]=shown
	var stagnant := 0
	for distance in travelled:
		if distance<1.0:stagnant+=1
	var failed := largest_step>=.15 or off_belt>0 or stagnant>0
	print("EAST_CONVEYOR_MOTION ","FAIL" if failed else "PASS"," rocks=",rocks.size()," seconds=40 max_visible_step=",largest_step," off_belt=",off_belt," stagnant=",stagnant)
	model.queue_free();await process_frame
	preload("res://tests/support/test_result.gd").finish(self,1 if failed else 0)

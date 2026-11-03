extends SceneTree

func _initialize(): call_deferred("run")

func run():
	var model = Node3D.new()
	root.add_child(model)
	var fan = Node3D.new()
	fan.name = "Fan"
	model.add_child(fan)
	var ore = Node3D.new()
	ore.name = "Ore"
	model.add_child(ore)
	var source = AnimationPlayer.new()
	model.add_child(source)
	var library = AnimationLibrary.new()
	for label in ["fan", "ore"]:
		var animation = Animation.new()
		animation.length = 2.0 if label == "fan" else 4.0
		var track = animation.add_track(Animation.TYPE_VALUE)
		animation.track_set_path(track, NodePath("Fan:rotation:y" if label == "fan" else "Ore:position:x"))
		animation.track_insert_key(track, 0.0, 0.0)
		animation.track_insert_key(track, animation.length, 2.0)
		# glTF import adds constant rest tracks for other animated objects.
		# These must not overwrite a concurrently running independent action.
		var rest = animation.add_track(Animation.TYPE_VALUE)
		animation.track_set_path(rest, NodePath("Ore:position:x" if label == "fan" else "Fan:rotation:y"))
		animation.track_insert_key(rest, 0.0, 0.0)
		library.add_animation(label, animation)
	source.add_animation_library("", library)
	var controller = preload("res://scripts/mining_scene_motion.gd").new()
	model.add_child(controller)
	controller.configure(model)
	assert(controller.players.size() == 2)
	assert(not source.active)
	for player in controller.players: player.advance(1.0)
	assert(is_equal_approx(fan.rotation.y, 1.0), "Fan clip did not run")
	assert(is_equal_approx(ore.position.x, 0.5), "Ore clip did not run alongside fan")
	assert(source.get_animation("fan").loop_mode == Animation.LOOP_NONE, "Source animation was mutated")
	controller.configure(model)
	assert(controller.players.size() == 2, "Repeated configure duplicated players")
	model.process_mode = Node.PROCESS_MODE_DISABLED
	var held = fan.rotation.y
	await create_timer(0.1).timeout
	assert(is_equal_approx(fan.rotation.y, held), "Hidden scenery kept animating")
	for player in controller.players: assert(not player.can_process())
	model.process_mode = Node.PROCESS_MODE_INHERIT
	await create_timer(0.1).timeout
	assert(not is_equal_approx(fan.rotation.y, held), "Scenery did not resume")
	model.queue_free()
	await process_frame
	print("MINING_MOTION_PASS: concurrent clips, source preservation, idempotency, pause and resume")
	quit()

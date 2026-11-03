extends SceneTree
var failures: Array[String] = []

func check(condition: bool, message: String):
	if not condition: failures.append(message)

func _initialize(): call_deferred("run")

func run():
	var hub = preload("res://scripts/training_hub.gd").new()
	hub.scene_path = "res://environments/mining_facility/mining_facility.tscn"
	root.add_child(hub)
	# Loading while Jess/video is active must not briefly animate the scene.
	hub.set_context(true, false)
	var deadline = Time.get_ticks_msec() + 15000
	while hub.loading and Time.get_ticks_msec() < deadline:
		await process_frame
	check(hub.ready_to_show(), "Mining asset did not load")
	if hub.content:
		var ambience = hub.content.find_child("MiningAmbience", true, false)
		check(ambience != null and not ambience.playing, "Ambience autoplayed during suspended load")
		check(not hub.content.visible and not hub.content.can_process(), "Suspended load became active")
		var motion = hub.content.find_child("MachineryMotion", true, false)
		check(motion != null and motion.players.size() == 6, "Expected six independent machinery loop groups")
		var stockpile_coal = hub.content.find_child("CV2_COAL_000", true, false) as Node3D
		check(stockpile_coal != null, "Missing stockpile conveyor coal")
		var coal_initial = stockpile_coal.transform if stockpile_coal else Transform3D.IDENTITY
		for camera in hub.content.find_children("*", "Camera3D", true, false):
			check(not camera.current, "Imported camera took over XR view")
		var ore = hub.content.find_child("CV_ORE_000", true, false) as Node3D
		check(ore != null, "Missing ore geometry")
		if ore:
			var initial = ore.transform
			await create_timer(0.1).timeout
			check(ore.transform.is_equal_approx(initial), "Ore moved before scenery activation")
			hub.set_context(true, true)
			await create_timer(0.15).timeout
			check(not ore.transform.is_equal_approx(initial), "Ore did not move after activation")
			check(stockpile_coal != null and not stockpile_coal.transform.is_equal_approx(coal_initial), "Stockpile conveyor did not animate")
			check(ambience != null and ambience.playing, "Ambience did not start with scenery")
			for reason in ["video", "Jess", "wearer absent", "focus loss", "background deselected"]:
				hub.set_context(reason != "background deselected", false)
				var held = ore.transform
				await create_timer(0.08).timeout
				check(ore.transform.is_equal_approx(held), "Ore kept moving during " + reason)
				check(not hub.content.visible and not motion.can_process(), "Scenery stayed active during " + reason)
				check(ambience != null and not ambience.playing, "Ambience leaked during " + reason)
				hub.set_context(true, true)
				await create_timer(0.08).timeout
				check(not ore.transform.is_equal_approx(held), "Ore did not resume after " + reason)
		# Switch while another scene is still requested. Only the latest choice
		# may instantiate, and old actor/player references must be discarded.
		hub.set_scene_path(hub.SCENE)
		hub.set_scene_path(hub.MINING_SCENE)
		deadline = Time.get_ticks_msec() + 15000
		while hub.loading and Time.get_ticks_msec() < deadline:
			await process_frame
		check(hub.ready_to_show() and hub.content.name == "MiningFacility", "Rapid switching installed a stale world")
		check(hub.actors.is_empty(), "Old worker actor references survived scene switch")
		check(hub.content.find_child("MachineryMotion", true, false) != null, "Mining motion missing after switch")
	hub.queue_free()
	await process_frame
	# AudioServer releases stopped MP3 playback on its mixing thread.
	await create_timer(0.15).timeout
	for failure in failures: push_error(failure)
	print("MINING_ENVIRONMENT_", "PASS" if failures.is_empty() else "FAIL", ": ", failures)
	quit(0 if failures.is_empty() else 1)

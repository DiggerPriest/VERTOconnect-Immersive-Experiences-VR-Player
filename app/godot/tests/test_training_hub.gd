extends SceneTree
const Hub := preload("res://scripts/training_hub.gd")
const RayMenu := preload("res://scripts/ray_menu.gd")
const Main := preload("res://scripts/main.gd")
const Menu := preload("res://scripts/library_menu.gd")
var failures: Array[String] = []

func check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)

func _initialize() -> void:
	if not preload("res://tests/support/test_result.gd").prepare(self):
		return
	call_deferred("_run")

func _run() -> void:
	RayMenu.FONT = preload("res://branding/fonts/Inter.ttf")
	check(Hub.can_run(false, false, true, false, true, true), "Visible library can animate")
	for flags in [[true, false, true, false, true, true], [false, true, true, false, true, true], [false, false, false, false, true, true], [false, false, true, true, true, true], [false, false, true, false, false, true], [false, false, true, false, true, false]]:
		check(not Hub.can_run(flags[0], flags[1], flags[2], flags[3], flags[4], flags[5]), "Media, Jess, absence, passthrough, application pause or XR focus loss suspends scenery")
	var hub := Hub.new()
	hub.scene_path = "res://does-not-exist-training-hub.tscn"
	root.add_child(hub)
	hub.set_context(true, true)
	check(hub.failed and not hub.ready_to_show(), "Missing asset must report unavailable scenery")
	check(hub.status_text().contains("unavailable"), "Failure must explain fallback")
	hub.set_context(false, true)
	check(hub.status_text().is_empty(), "Unselected hub must not show failure text")
	hub.queue_free()
	await process_frame

	var prototype := Node3D.new()
	for index in range(4):
		var actor := preload("res://scripts/training_hub_actor.gd").new()
		actor.name = "Worker%d" % index
		actor.animation_clip = "Trade%d" % index
		actor.phase_offset = float(index * 3)
		actor.idle_seconds = 3.0 + index
		actor.contact_shadow = false
		prototype.add_child(actor)
		actor.owner = prototype
		var player := AnimationPlayer.new()
		actor.add_child(player)
		player.owner = prototype
		var library := AnimationLibrary.new()
		library.add_animation("RESET", Animation.new())
		var clip := Animation.new()
		clip.length = 18.0 + index * 2
		library.add_animation(actor.animation_clip, clip)
		player.add_animation_library("", library)
	var packed := PackedScene.new()
	packed.pack(prototype)
	var path := "user://training_hub_fixture.tscn"
	check(ResourceSaver.save(packed, path) == OK, "Test scene saved")
	prototype.free()
	hub = Hub.new()
	hub.scene_path = path
	root.add_child(hub)
	var environment := Environment.new()
	environment.ambient_light_color = Color.RED
	environment.ambient_light_energy = 0.27
	var original_source := environment.ambient_light_source
	hub.configure_environment(environment)
	hub.set_context(true, false)
	hub.set_context(false, false)
	var deadline := Time.get_ticks_msec() + 5000
	while hub.loading and Time.get_ticks_msec() < deadline:
		await process_frame
	check(hub.ready_to_show(), "Asynchronous scene loads even after selection changes")
	check(not hub.selected and not hub.active, "Late completion does not reselect the hub")
	if hub.content:
		check(not hub.content.visible and hub.content.process_mode == Node.PROCESS_MODE_DISABLED, "Scene completing during Jess stays suspended")
		hub.set_context(true, true)
		check(environment.ambient_light_color == Color(0.72, 0.78, 0.83) and is_equal_approx(environment.ambient_light_energy, 0.65), "Runtime matches preview ambient lighting")
		check(hub.content.visible and hub.content.process_mode == Node.PROCESS_MODE_INHERIT, "Returning to library restores scenery")
		await process_frame
		check(hub.actors.size() == 4, "All four named routines are loaded")
		for index in range(hub.actors.size()):
			check(hub.actors[index].valid and hub.actors[index].player.current_animation == "Trade%d" % index, "Explicit routine selected instead of RESET")
			check(is_equal_approx(hub.actors[index].clip_duration, 18.0 + index * 2), "Independent authored duration preserved")
		hub.actors[0].seek_elapsed(19.0)
		check(is_equal_approx(hub.actors[0].player.current_animation_position, 18.0), "End pose held through idle pause")
		hub.actors[0].seek_elapsed(21.5)
		check(is_equal_approx(hub.actors[0].player.current_animation_position, .5), "Routine resumes after its own idle period")
		var before := hub.actors.map(func(actor): return actor.elapsed)
		check(not hub.diagnostics_enabled and not hub._diagnostics.visible, "Diagnostics opt-in and hidden by default")
		hub.diagnostics_enabled = true
		hub._update_diagnostics(.6)
		check(hub._diagnostics.visible and hub._diagnostics.text.contains("GPU timing not measured"), "On-device counters labelled with measurement limitation")
		hub.set_context(true, false)
		check(environment.ambient_light_color == Color.RED and is_equal_approx(environment.ambient_light_energy, 0.27) and environment.ambient_light_source == original_source, "Video/Jess suspension restores previous lighting exactly")
		await create_timer(.1).timeout
		check(not hub._diagnostics.visible, "Diagnostics hidden during video/Jess")
		for index in range(hub.actors.size()):
			check(is_equal_approx(before[index], hub.actors[index].elapsed), "Each worker clock stops during suspension")
		hub.set_context(true, true)
		await create_timer(.1).timeout
		for index in range(hub.actors.size()):
			check(hub.actors[index].elapsed > before[index], "Each worker resumes from its paused clock")
		hub.set_context(false, true)
		check(not hub.content.visible, "Selecting panorama hides geometry")
	hub.queue_free()
	var invalid_actor := preload("res://scripts/training_hub_actor.gd").new()
	invalid_actor.animation_clip = "MissingTrade"
	invalid_actor.add_child(AnimationPlayer.new())
	root.add_child(invalid_actor)
	check(not invalid_actor.valid and invalid_actor.diagnostic_error.contains("Missing"), "Missing requested clip is rejected instead of silently playing another routine")
	invalid_actor.queue_free()
	var main := Main.new()
	main.settings_path = "user://hub-settings.cfg"
	root.add_child(main)
	main.set_process(false)
	check(main.background.choice == "mining_facility", "Fresh launches default to animated mining scenery")
	check(main.training_hub.scene_path == main.training_hub.MINING_SCENE, "Launch default requests the mining scene")
	main._update_training_hub_activity()
	deadline = Time.get_ticks_msec() + 5000
	while main.training_hub.loading and Time.get_ticks_msec() < deadline:
		await process_frame
	check(main.training_hub.ready_to_show() and main.training_hub.active, "Main app activates optional hub")
	main._on_setting_changed("training_hub_diagnostics", true)
	check(main.training_hub.diagnostics_enabled and main._library_settings().training_hub_diagnostics, "Settings control reaches diagnostics and reflects current state")
	main._jess_opened = true
	main._update_training_hub_activity()
	check(not main.training_hub.content.visible, "Opening Jess suspends the real main-app scenery")
	main._jess_opened = false
	main._hub_wearer_present = false
	main._update_training_hub_activity()
	check(not main.training_hub.content.visible, "Removing headset keeps scenery suspended")
	main._hub_wearer_present = true
	main.photo_active = true
	main._update_training_hub_activity()
	check(not main.training_hub.content.visible, "Active media suspends scene")
	main.photo_active = false
	main._update_training_hub_activity()
	check(main.training_hub.content.visible, "Return to idle library resumes scene")
	check(not main.background.select("verto"), "Retired panoramas cannot be selected")
	check(main.background.choice == "mining_facility", "Mining stays selected after a retired choice")
	main.queue_free()
	await process_frame
	DirAccess.remove_absolute(path)
	var menu := Menu.new()
	root.add_child(menu)
	menu.visible = true
	menu.refresh()
	menu._activate(Menu.LOOK_AROUND)
	check(menu.looking_around and not menu._backdrop.visible, "Look around removes opaque menu backdrop")
	check(menu._buttons.size() == 1 and menu._buttons[0].target == Menu.LOOK_AROUND, "Only return control remains")
	menu.refresh_session_controls(true)
	check(menu.device_status == null or not menu.device_status.visible, "Periodic controls refresh does not restore hidden status bar")
	var button: Node3D = menu._buttons[0].node
	var origin := button.global_position + button.global_basis.z
	var direction := -button.global_basis.z
	check(menu.press_pointer("left_hand", origin, direction, true), "Hand ray can press Return to menu")
	menu.release_pointer("left_hand", origin, direction, true)
	check(not menu.looking_around and menu._backdrop.visible, "Return restores menu")
	menu.playback_browser = true
	menu._activate(Menu.LOOK_AROUND)
	check(not menu.looking_around, "Look-around cannot hide controls while browsing during playback")
	menu.queue_free()
	await process_frame
	for failure in failures:
		push_error(failure)
	print("Training hub lifecycle: %s" % ("PASS" if failures.is_empty() else "FAIL"))
	preload("res://tests/support/test_result.gd").finish(self, 0 if failures.is_empty() else 1)

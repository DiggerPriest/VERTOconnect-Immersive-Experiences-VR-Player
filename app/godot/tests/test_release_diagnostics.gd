extends SceneTree
const Main := preload("res://scripts/main.gd")
var failures: Array[String] = []

func check(ok: bool, message: String) -> void:
	if not ok: failures.append(message)

func _initialize() -> void:
	if not preload("res://tests/support/test_result.gd").prepare(self): return
	_run.call_deferred()

func _run() -> void:
	var config := ConfigFile.new()
	config.set_value("ui", "show_fps", true)
	config.save("user://release-diagnostics.cfg")
	var main := Main.new()
	main.settings_path = "user://release-diagnostics.cfg"
	root.add_child(main)
	main.set_process(false)
	check(main.fps_overlay == null, "A saved FPS preference cannot create an overlay")
	check(not main.settings.has_section_key("ui", "show_fps"), "Saved diagnostic preference is retired")
	main._on_setting_changed("show_fps", true)
	main._on_setting_changed("training_hub_diagnostics", true)
	check(main.fps_overlay == null and not main.training_hub.diagnostics_enabled, "Legacy actions cannot enable diagnostic overlays")
	main._on_native_presence_changed(false, "screen_off")
	main._on_native_presence_changed(true, "screen_on")
	check(main._hub_wearer_present, "Removing diagnostics preserves wearer handling")
	main._jess_opened = true
	main._jess_xr_lost_focus = true
	main._on_android_lifecycle("resume")
	check(not main._jess_opened and not main._jess_xr_lost_focus, "Jess return still releases the workshop activity gate")
	main._update_status()
	check(not main.status_label.visible, "Production status HUD remains hidden")
	for label in main.find_children("*", "Label3D", true, false):
		if label.is_visible_in_tree():
			check(not label.text.contains("Return diagnostic") and not label.text.contains("Wearer:") and not label.text.contains("Training hub test"), "Lifecycle events cannot expose diagnostic text")
	for tab in [main.recent_menu.DISPLAY_TAB, main.recent_menu.BACKGROUND_TAB]:
		main.recent_menu.section = main.recent_menu.Section.SETTINGS
		main.recent_menu.tab = tab
		main.recent_menu.refresh()
		check(not main.recent_menu.rows.any(func(row): return row.get("key", "") in ["show_fps", "training_hub_diagnostics"]), "Test overlay controls are absent")
	main.queue_free()
	await process_frame
	for failure in failures: push_error(failure)
	print("Release diagnostics: ", failures.size(), " failures")
	preload("res://tests/support/test_result.gd").finish(self, 0 if failures.is_empty() else 1)

extends SceneTree
const Background := preload("res://scripts/app_background.gd")
const Main := preload("res://scripts/main.gd")

class SupportedDisplay:
	extends XrDisplay
	func supports_passthrough() -> bool:
		return true

var failures: Array[String] = []
func check(ok: bool, message: String) -> void:
	if not ok: failures.append(message)

func _initialize() -> void:
	if not preload("res://tests/support/test_result.gd").prepare(self): return
	_run.call_deferred()

func _run() -> void:
	var settings := ConfigFile.new()
	settings.set_value("appearance", "background", "verto")
	settings.save("user://old-background.cfg")
	var main := Main.new()
	main.settings_path = "user://old-background.cfg"
	root.add_child(main)
	main.set_process(false)
	check(main.background.choice == "mining_facility", "Retired saved backgrounds migrate to mining on launch")
	check(Background.CHOICES == ["mining_facility"], "Only mining remains selectable")
	for retired in ["verto", "belfast", "training_hub", "dark", "custom", "passthrough", "auto_service"]:
		check(not main.background.select(retired), "Retired background is rejected: " + retired)
	check(main.background.ready_sky() == null and not main.background.has_custom(), "No panorama texture or custom background is retained")
	check(not main.background.import_photo({}, "test"), "Photos cannot replace the mining backdrop")
	var deadline := Time.get_ticks_msec() + 20000
	while main.training_hub.loading and Time.get_ticks_msec() < deadline:
		await process_frame
	check(main.training_hub.ready_to_show() and main.training_hub.active, "Mining loads as the actual launch background")
	var menu := main.recent_menu
	menu.section = menu.Section.SETTINGS
	menu.tab = menu.BACKGROUND_TAB
	menu.refresh()
	var rows: Array = menu.rows.filter(func(row): return row.get("key", "") == "background")
	check(rows.size() == 1 and rows[0].choices.size() == 1 and rows[0].choices[0].value == "mining_facility", "Background menu exposes only mining")
	check(not main.photo_menu._buttons.any(func(button): return button.target == main.photo_menu.PHOTO_BACKGROUND), "Photo controls no longer offer alternate backgrounds")
	var supported := SupportedDisplay.new()
	supported.configure(root, main.display.environment, null, true)
	main.display = supported
	main.video.local_uri = "smb://test/share/clip.mp4"
	main.video.media.begin(7)
	main.video.geometry = 1
	main.video.alpha_requested = true
	main._update_background()
	check(supported.applied_passthrough, "Alpha video still enables passthrough")
	check(main.background.choice == "mining_facility" and not main.training_hub.active, "Alpha suspends mining without replacing the launch choice")
	main.video.alpha_requested = false
	main.video.alpha_enabled = false
	main.video.media.state = "ended"
	main._update_background()
	check(not supported.applied_passthrough and main.training_hub.active, "Video end restores the mining background")
	main.video.close_video()
	main._toggle_display()
	check(main.temporary_passthrough and supported.applied_passthrough, "Idle passthrough shortcut remains temporary")
	main._toggle_display()
	check(not main.temporary_passthrough and main.training_hub.active, "Leaving temporary passthrough restores mining")
	main.queue_free()
	await process_frame
	for failure in failures: push_error(failure)
	print("Mining background: ", failures.size(), " failures")
	preload("res://tests/support/test_result.gd").finish(self, 0 if failures.is_empty() else 1)

extends SceneTree

const Splash := preload("res://scripts/verto_splash.gd")
var finished := false
var failures := 0


func check(condition: bool, message: String) -> void:
	if not condition:
		failures += 1
		push_error(message)


func _initialize() -> void:
	if not preload("res://tests/support/test_result.gd").prepare(self):
		return
	call_deferred("_run")


func _run() -> void:
	var splash := Splash.new()
	check(splash.hold_seconds == 5.0, "Opening holds for five seconds")
	check(splash.fade_seconds > 0.0, "Opening fades in and out")
	splash.hold_seconds = 0.1
	splash.fade_seconds = 0.02
	splash.finished.connect(func(): finished = true)
	root.add_child(splash)
	check(splash._materials.size() == 13 and splash._labels.size() == 4, "Opening contains title, backdrop and loading dots")
	await create_timer(0.06).timeout
	check(not finished, "App does not open before the hold completes")
	await create_timer(0.25).timeout
	check(finished, "App opens after the fade-out")
	preload("res://tests/support/test_result.gd").finish(self, 1 if failures else 0)

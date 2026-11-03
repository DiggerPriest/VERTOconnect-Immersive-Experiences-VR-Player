extends SceneTree
## Uses the shipped scene and rigs, not the empty-clip scheduling fixture.
const Hub := preload("res://scripts/training_hub.gd")
var failures: Array[String] = []
func check(ok: bool, message: String) -> void:
	if not ok:
		failures.append(message)
func _initialize() -> void:
	if not preload("res://tests/support/test_result.gd").prepare(self):return
	call_deferred("run")
func run() -> void:
	var hub := Hub.new()
	root.add_child(hub)
	hub.set_context(true, true)
	var deadline := Time.get_ticks_msec() + 15000
	while hub.loading and Time.get_ticks_msec() < deadline:await process_frame
	check(hub.ready_to_show() and hub.actors.size() == 4, "All four real scene actors must load")
	if hub.actors.size() == 4:
		# Disable only manager sampling so the baseline isn't replaced underneath
		# the test; actor clocks remain automatic and no seek/advance is called.
		hub.set_process(false)
		var before := hub.sample_actor_motion()
		await create_timer(3.0).timeout
		var after := hub.sample_actor_motion()
		for index in range(4):
			check(after[index].elapsed > before[index].elapsed + 2.0, "Real actor clock must advance automatically: " + after[index].name)
			check(after[index].changed_bones > 0, "Real authored rig must change actual bone poses: " + after[index].name)
		var gates := {"menu": true, "media": false, "jess": false, "wearer": true, "application": true, "passthrough": false, "focus": false}
		hub.diagnostics_enabled = true
		hub.set_context(true, false, gates)
		hub._update_diagnostics(.6)
		check(hub._diagnostics.visible and hub._diagnostics.text.contains("no focus"), "Visible menu reports focus-blocked state instead of hiding diagnostics")
		var paused := hub.sample_actor_motion()
		await create_timer(.2).timeout
		var frozen := hub.sample_actor_motion()
		for index in range(4):
			check(is_equal_approx(paused[index].elapsed, frozen[index].elapsed) and frozen[index].changed_bones == 0, "Diagnostics must not force actor clocks/bones to move")
		for unsafe in ["jess", "media"]:
			gates[unsafe] = true
			hub.set_context(true, false, gates)
			hub._update_diagnostics(.6)
			check(not hub._diagnostics.visible, "No diagnostic overlay during " + unsafe)
			gates[unsafe] = false
		gates.wearer = false
		hub.set_context(true, false, gates)
		hub._update_diagnostics(.6)
		check(not hub._diagnostics.visible, "No diagnostic overlay when headset removed")
	hub.queue_free()
	await process_frame
	# Allow queued texture cleanup to run before headless shutdown.
	await create_timer(0.5).timeout
	await process_frame
	for failure in failures:push_error(failure)
	preload("res://tests/support/test_result.gd").finish(self, 0 if failures.is_empty() else 1)

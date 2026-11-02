extends Node3D
## Optional, world-fixed environment. Loading continues while content is suspended.
signal state_changed
const SCENE := "res://environments/training_hub/training_hub.tscn"
var scene_path := SCENE
var selected := false
var active := false
var loading := false
var failed := false
var content: Node3D
var animation_players: Array[AnimationPlayer] = []
var actors: Array[Node3D] = []
var diagnostics_enabled := false
var _diagnostics: Label3D
var _sample_seconds := 0.0
var _sample_frames := 0
var _sample_max_delta := 0.0
var _status: Label3D
var _environment: Environment
var _saved_lighting := {}


static func apply_preview_lighting(environment: Environment) -> void:
	# Identical prototype fill for the desktop preview and optional Quest scene.
	# Shadows/material bakes belong in the scene asset, not the media renderer.
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.72, 0.78, 0.83)
	environment.ambient_light_energy = 0.65


static func can_run(media_active: bool, jess_open: bool, wearer_present: bool, passthrough: bool, application_active: bool, input_focused: bool) -> bool:
	return not media_active and not jess_open and wearer_present and not passthrough and application_active and input_focused


func configure_environment(environment: Environment) -> void:
	_restore_lighting()
	_environment = environment
	_apply_activity()


func _restore_lighting() -> void:
	if _environment and not _saved_lighting.is_empty():
		for property in _saved_lighting:
			_environment.set(property, _saved_lighting[property])
	_saved_lighting.clear()


func _exit_tree() -> void:
	_restore_lighting()


func _ready() -> void:
	_status = Label3D.new()
	_status.position = Vector3(0, 2.0, -2.5)
	_status.font_size = 30
	_status.pixel_size = 0.001
	_status.no_depth_test = true
	add_child(_status)
	_diagnostics = Label3D.new()
	_diagnostics.position = Vector3(0, 1.9, -2.5)
	_diagnostics.font = preload("res://branding/fonts/Inter.ttf")
	_diagnostics.font_size = 24
	_diagnostics.pixel_size = 0.001
	_diagnostics.outline_size = 5
	_diagnostics.no_depth_test = true
	_diagnostics.visible = false
	add_child(_diagnostics)


func set_context(wanted: bool, can_animate: bool) -> void:
	selected = wanted
	active = wanted and can_animate
	if selected and not content and not loading and not failed:
		if not ResourceLoader.exists(scene_path):
			failed = true
			state_changed.emit()
		elif ResourceLoader.load_threaded_request(scene_path, "PackedScene") == OK:
			loading = true
			state_changed.emit()
		else:
			failed = true
			state_changed.emit()
	_apply_activity()


func _process(delta: float) -> void:
	_update_diagnostics(delta)
	if _status:
		_status.text = status_text()
		_status.visible = active and not _status.text.is_empty()
	if not loading:
		return
	var status := ResourceLoader.load_threaded_get_status(scene_path)
	if status == ResourceLoader.THREAD_LOAD_LOADED:
		var packed := ResourceLoader.load_threaded_get(scene_path) as PackedScene
		loading = false
		if packed:
			var instance := packed.instantiate()
			content = instance as Node3D
			if not content:
				instance.free()
		if content:
			# Never briefly run an autoplay animation when a request finishes
			# while Jess/video is active or the headset is off.
			content.visible = false
			content.process_mode = Node.PROCESS_MODE_DISABLED
			preload("res://scripts/training_hub_surfaces.gd").apply(content)
			add_child(content)
			_find_animations(content)
		else:
			failed = true
		_apply_activity()
		state_changed.emit()
	elif status in [ResourceLoader.THREAD_LOAD_FAILED, ResourceLoader.THREAD_LOAD_INVALID_RESOURCE]:
		loading = false
		failed = true
		state_changed.emit()


func _find_animations(node: Node) -> void:
	if node is AnimationPlayer:
		animation_players.append(node)
	if node.has_method("seek_elapsed"):
		actors.append(node)
		if not node.valid:
			failed = true
	for child in node.get_children():
		_find_animations(child)


func _update_diagnostics(delta: float) -> void:
	if not _diagnostics:
		return
	_diagnostics.visible = diagnostics_enabled and active and ready_to_show()
	if not _diagnostics.visible:
		_sample_seconds = 0.0
		_sample_frames = 0
		_sample_max_delta = 0.0
		return
	_sample_seconds += delta
	_sample_frames += 1
	_sample_max_delta = maxf(_sample_max_delta, delta)
	if _sample_seconds < 0.5:
		return
	var frame_ms := _sample_seconds * 1000.0 / _sample_frames
	var memory := Performance.get_monitor(Performance.MEMORY_STATIC) / 1048576.0
	var video_memory := Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0
	_diagnostics.text = "Training hub test | %.0f FPS\nFrame interval %.1f ms avg / %.1f ms max\nDraw calls %d | Primitives %d\nEngine memory %.1f MiB | Render memory %s\nApp counters only; GPU timing not measured" % [
		Performance.get_monitor(Performance.TIME_FPS), frame_ms, _sample_max_delta * 1000.0,
		int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),
		int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)),
		memory, "%.1f MiB" % video_memory if video_memory > 0.0 else "unavailable"
	]
	_sample_seconds = 0.0
	_sample_frames = 0
	_sample_max_delta = 0.0


func _apply_activity() -> void:
	if content:
		content.visible = active and not failed
		content.process_mode = Node.PROCESS_MODE_INHERIT if active and not failed else Node.PROCESS_MODE_DISABLED
	if active and ready_to_show() and _environment:
		if _saved_lighting.is_empty():
			for property in ["ambient_light_source", "ambient_light_color", "ambient_light_energy"]:
				_saved_lighting[property] = _environment.get(property)
			apply_preview_lighting(_environment)
	else:
		_restore_lighting()


func ready_to_show() -> bool:
	return content != null and not failed


func status_text() -> String:
	if not selected:
		return ""
	if failed:
		return "Training hub unavailable — showing the workshop panorama"
	if loading:
		return "Loading training hub…"
	return ""

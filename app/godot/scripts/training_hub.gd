extends Node3D
## Optional, world-fixed environment. Loading continues while content is suspended.
signal state_changed
const SCENE := "res://environments/training_hub/training_hub.tscn"
const MINING_SCENE := "res://environments/mining_facility/mining_facility.tscn"
var scene_path := SCENE
var _loading_path := ""
var selected := false
var active := false
var loading := false
var failed := false
var content: Node3D
var animation_players: Array[AnimationPlayer] = []
var actors: Array[Node3D] = []
var diagnostics_enabled := false
var diagnostic_context := {}
var last_motion_samples: Array[Dictionary] = []
var _motion_previous := {}
var _diagnostics: Label3D
var _sample_seconds := 0.0
var _sample_frames := 0
var _sample_max_delta := 0.0
var _status: Label3D
var _environment: Environment
var _saved_lighting := {}
var _exiting := false


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
	_exiting = true
	_restore_lighting()
	drain_pending_load()


func drain_pending_load() -> void:
	# A launch can be closed while the background is still loading. Drain its
	# request before Godot releases resources during application/test shutdown.
	if loading and not _loading_path.is_empty():
		ResourceLoader.load_threaded_get(_loading_path)
		loading = false


func _ready() -> void:
	_exiting = false
	add_to_group("training_hub_loaders")
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


func set_scene_path(path: String) -> void:
	if path == scene_path: return
	scene_path = path
	_restore_lighting()
	if content:
		remove_child(content)
		content.queue_free()
		content = null
	animation_players.clear()
	actors.clear()
	_motion_previous.clear()
	last_motion_samples.clear()
	failed = false
	# A threaded request cannot be cancelled; drain it before requesting the
	# latest choice. Its result must never briefly replace the requested world.
	set_context(selected, active, diagnostic_context)
	state_changed.emit()


func set_context(wanted: bool, can_animate: bool, gates: Dictionary = {}) -> void:
	if _exiting or is_queued_for_deletion():
		return
	diagnostic_context = gates
	selected = wanted
	active = wanted and can_animate
	if selected and not content and not loading and not failed:
		if not ResourceLoader.exists(scene_path):
			failed = true
			state_changed.emit()
		elif ResourceLoader.load_threaded_request(scene_path, "PackedScene") == OK:
			loading = true
			_loading_path = scene_path
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
	var status := ResourceLoader.load_threaded_get_status(_loading_path)
	if status == ResourceLoader.THREAD_LOAD_LOADED:
		var packed := ResourceLoader.load_threaded_get(_loading_path) as PackedScene
		loading = false
		if _loading_path != scene_path:
			_loading_path = ""
			set_context(selected, active, diagnostic_context)
			return
		_loading_path = ""
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
		if _loading_path != scene_path:
			_loading_path = ""
			set_context(selected, active, diagnostic_context)
			return
		_loading_path = ""
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
	var safe_to_show := active
	if not diagnostic_context.is_empty():
		safe_to_show = bool(diagnostic_context.get("menu", false)) and not diagnostic_context.get("media", false) and not diagnostic_context.get("jess", false) and diagnostic_context.get("wearer", false) and diagnostic_context.get("application", false) and not diagnostic_context.get("passthrough", false)
	_diagnostics.visible = diagnostics_enabled and selected and safe_to_show
	if not _diagnostics.visible:
		_sample_seconds = 0.0
		_sample_frames = 0
		_sample_max_delta = 0.0
		_motion_previous.clear()
		last_motion_samples.clear()
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
	_diagnostics.text += "\nActive: %s | Loaded: %s | Gates: %s" % [active, ready_to_show(), diagnostic_gate_text()]
	_diagnostics.text += "\nScene visible: %s | Process mode: %s" % [content.is_visible_in_tree() if content else false, content.process_mode if content else -1]
	last_motion_samples = sample_actor_motion()
	for sample in last_motion_samples:
		_diagnostics.text += "\n%s t %.1f clip %.1f | show %s proc %s phy %s | boneΔ %s" % [sample.name, sample.elapsed, sample.clip_time, sample.visible, sample.processing, sample.physics_processing, sample.motion]
	_diagnostics.text += "\nBoneΔ is CPU pose change; GPU motion not verified. Physics off is normal."
	_sample_seconds = 0.0
	_sample_frames = 0
	_sample_max_delta = 0.0


func diagnostic_gate_text() -> String:
	if diagnostic_context.is_empty():
		return "caller active" if active else "caller suspended"
	var blocked: Array[String] = []
	for flag in ["media", "jess", "passthrough"]:
		if diagnostic_context.get(flag, false):
			blocked.append(flag)
	for flag in ["wearer", "application", "focus"]:
		if not diagnostic_context.get(flag, false):
			blocked.append("no " + flag)
	return "open" if blocked.is_empty() else ", ".join(blocked)


static func find_skeleton(node: Node) -> Skeleton3D:
	if node is Skeleton3D:
		return node
	for child in node.get_children():
		var found := find_skeleton(child)
		if found:
			return found
	return null


func sample_actor_motion() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for actor in actors:
		var skeleton := find_skeleton(actor)
		var current: Array[Transform3D] = []
		var changed := 0
		var representative := ""
		var maximum_degrees := 0.0
		var previous: Array = _motion_previous.get(actor.get_instance_id(), [])
		if skeleton:
			for index in skeleton.get_bone_count():
				var pose := skeleton.get_bone_pose(index)
				current.append(pose)
				if index < previous.size() and not pose.is_equal_approx(previous[index]):
					changed += 1
					var angle := rad_to_deg(pose.basis.get_rotation_quaternion().angle_to(previous[index].basis.get_rotation_quaternion()))
					if angle > maximum_degrees:
						maximum_degrees = angle
						representative = skeleton.get_bone_name(index)
		var motion := "first sample" if previous.is_empty() else "%d (%s %.2f°)" % [changed, representative if not representative.is_empty() else "none", maximum_degrees]
		if not skeleton:
			motion = "no skeleton"
		_motion_previous[actor.get_instance_id()] = current
		result.append({"name": str(actor.name).replace("Worker", ""), "elapsed": actor.elapsed, "clip_time": actor.player.current_animation_position if actor.player else -1.0, "visible": actor.is_visible_in_tree(), "processing": actor.is_processing() and actor.can_process(), "physics_processing": actor.is_physics_processing() and actor.can_process(), "changed_bones": changed, "motion": motion})
	return result


func _apply_activity() -> void:
	if content:
		content.visible = active and not failed
		content.process_mode = Node.PROCESS_MODE_INHERIT if active and not failed else Node.PROCESS_MODE_DISABLED
		if content.has_method("set_environment_active"):
			content.set_environment_active(active and not failed)
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
		return "Mining facility unavailable"
	if loading:
		return "Loading training hub…"
	return ""

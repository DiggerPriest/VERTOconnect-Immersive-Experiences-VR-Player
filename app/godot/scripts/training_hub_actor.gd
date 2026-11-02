extends Node3D
## One authored trade routine, with an independent clock and a quiet end-pose pause.
## No AnimationPlayer is allowed to select an arbitrary first animation.
@export var animation_clip := ""
@export var phase_offset := 0.0
@export var idle_seconds := 3.0
@export var contact_shadow := true
var player: AnimationPlayer
var valid := false
var diagnostic_error := ""
var elapsed := 0.0
var clip_duration := 0.0
var _resolved_clip := ""
var _last_sample := -1.0


func _ready() -> void:
	player = _find_player(self)
	if not player or animation_clip.is_empty():
		diagnostic_error = "Missing animation for " + str(name)
		return
	for candidate in player.get_animation_list():
		if candidate == animation_clip or str(candidate).get_file() == animation_clip:
			_resolved_clip = candidate
			break
	if _resolved_clip.is_empty():
		diagnostic_error = "Missing clip " + animation_clip
		return
	var animation := player.get_animation(_resolved_clip)
	clip_duration = animation.length
	if not is_finite(clip_duration) or clip_duration <= 0.0:
		diagnostic_error = "Invalid duration for " + animation_clip
		return
	# The actor's cycle includes a separate idle period, so imported loop flags
	# must not drive a second clock underneath it.
	animation.loop_mode = Animation.LOOP_NONE
	player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	player.play(_resolved_clip)
	valid = true
	seek_elapsed(0.0)
	if contact_shadow:
		_add_contact_shadow()


func _find_player(node: Node) -> AnimationPlayer:
	if node is AnimationPlayer:
		return node
	for child in node.get_children():
		var found := _find_player(child)
		if found:
			return found
	return null


func _process(delta: float) -> void:
	if valid:
		seek_elapsed(elapsed + delta)


func seek_elapsed(seconds: float) -> void:
	if not valid or not is_finite(seconds):
		return
	elapsed = maxf(0.0, seconds)
	var cycle := clip_duration + maxf(0.0, idle_seconds)
	var phase := fposmod(elapsed + phase_offset, cycle)
	var sample := minf(phase, clip_duration)
	if not is_equal_approx(sample, _last_sample):
		player.seek(sample, true)
		_last_sample = sample


func _add_contact_shadow() -> void:
	# Two soft ellipses in one draw call. Parent is placed on the local mat/floor.
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	for foot_x in [-0.183, 0.183]:
		for uv in [Vector2(0, 0), Vector2(0, 1), Vector2(1, 1), Vector2(0, 0), Vector2(1, 1), Vector2(1, 0)]:
			surface.set_uv(uv)
			surface.add_vertex(Vector3(foot_x + (uv.x - 0.5) * 0.25, 0.003, 0.09 + (uv.y - 0.5) * 0.36))
	var mesh := MeshInstance3D.new()
	mesh.name = "FootContactShadow"
	mesh.mesh = surface.commit()
	mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var shader := Shader.new()
	shader.code = """shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled;
void fragment() {
    ALBEDO = vec3(0.035, 0.045, 0.05);
    ALPHA = (1.0 - smoothstep(0.12, 0.5, length(UV - vec2(0.5)))) * 0.38;
}"""
	var material := ShaderMaterial.new()
	material.shader = shader
	mesh.material_override = material
	add_child(mesh)

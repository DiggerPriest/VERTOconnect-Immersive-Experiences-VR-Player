extends Node3D
## Head-locked opening screen; the animation is decorative, not a progress meter.
signal finished

var fade_seconds := 0.65
var hold_seconds := 5.0
var _materials: Array[Material] = []
var _colors: Array[Color] = []
var _labels: Array[Label3D] = []
var _label_colors: Array[Color] = []
var _spinner: Node3D


func _ready() -> void:
	position = Vector3(0, 0, -1.6)
	_quad(Vector2(8.0, 8.0), Vector3.ZERO, Color.BLACK)
	_quad(Vector2(5.4, 3.6), Vector3(0, 0, 0.006), Color.WHITE, preload("res://branding/vertoconnect-hero.png"))
	_quad(Vector2(8.0, 8.0), Vector3(0, 0, 0.018), Color(0.0, 0.0, 0.0, 0.82))
	_quad(Vector2(0.24, 0.21), Vector3(-0.56, 0.13, 0.025), Color.WHITE, preload("res://branding/vertoconnect-v.svg"))
	_label("VERTO", Vector3(-0.14, 0.13, 0.02), 83, 0.0018, Color(1.0, 0.7686, 0.1608))
	_label("connect", Vector3(0.39, 0.13, 0.02), 83, 0.0018, Color.WHITE)
	_label("I M M E R S I V E   E X P E R I E N C E S", Vector3(0, -0.065, 0.02), 22, 0.0018, Color(0.86, 0.86, 0.88))
	_label("V R   P L A Y E R", Vector3(0, -0.145, 0.02), 20, 0.0018, Color(0.74, 0.74, 0.76))
	_quad(Vector2(0.88, 0.002), Vector3(0, -0.235, 0.025), Color(0.6, 0.6, 0.6, 0.5))
	_spinner = Node3D.new()
	_spinner.position = Vector3(0, -0.36, 0.02)
	add_child(_spinner)
	for i in 8:
		var dot := MeshInstance3D.new()
		var sphere := SphereMesh.new()
		sphere.radius = 0.008
		sphere.height = 0.016
		dot.mesh = sphere
		var angle := TAU * float(i) / 8.0
		dot.position = Vector3(cos(angle) * 0.055, sin(angle) * 0.055, 0)
		var mat := _material(Color(1.0, 1.0, 1.0, 0.22 + 0.52 * float(i) / 7.0), 104)
		dot.material_override = mat
		_spinner.add_child(dot)
	_set_opacity(0.0)
	var tween := create_tween()
	tween.tween_method(_set_opacity, 0.0, 1.0, fade_seconds)
	tween.tween_interval(hold_seconds)
	tween.tween_method(_set_opacity, 1.0, 0.0, fade_seconds)
	tween.tween_callback(_finish)


func _process(delta: float) -> void:
	if _spinner:
		_spinner.rotation.z -= delta * 2.0


func _quad(size: Vector2, at: Vector3, color: Color, texture: Texture2D = null) -> void:
	var item := MeshInstance3D.new()
	var mesh := QuadMesh.new()
	mesh.size = size
	item.mesh = mesh
	item.position = at
	var mat := _material(color, 100 + roundi(at.z * 100.0))
	mat.albedo_texture = texture
	item.material_override = mat
	add_child(item)


func _label(text: String, at: Vector3, size: int, pixels: float, color: Color) -> void:
	var label := Label3D.new()
	label.text = text
	label.position = at
	label.font = preload("res://branding/fonts/Inter.ttf")
	label.font_size = size
	label.pixel_size = pixels
	label.shaded = false
	label.no_depth_test = true
	label.render_priority = 110
	label.outline_size = 0
	add_child(label)
	_labels.append(label)
	_label_colors.append(color)


func _material(color: Color, priority: int) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.no_depth_test = true
	mat.render_priority = priority
	_materials.append(mat)
	_colors.append(color)
	return mat


func _set_opacity(value: float) -> void:
	for i in _materials.size():
		var color := _colors[i]
		color.a *= clampf(value, 0.0, 1.0)
		_materials[i].albedo_color = color
	for i in _labels.size():
		var label_color := _label_colors[i]
		label_color.a *= clampf(value, 0.0, 1.0)
		_labels[i].modulate = label_color


func _finish() -> void:
	finished.emit()
	queue_free()

extends Node3D
## A small illuminated brand sign in the menu environment.


func _ready() -> void:
	position = Vector3(0, 5.8, -7.0)
	var backing := MeshInstance3D.new()
	var backing_mesh := QuadMesh.new()
	backing_mesh.size = Vector2(4.2, 0.70)
	backing.mesh = backing_mesh
	backing.position.z = -0.02
	var backing_material := StandardMaterial3D.new()
	backing_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	backing_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	backing_material.albedo_color = Color(0.06, 0.055, 0.04, 0.78)
	backing_material.render_priority = -10
	backing.material_override = backing_material
	add_child(backing)
	var mark := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2(0.56, 0.49)
	mark.mesh = quad
	mark.position = Vector3(-1.73, 0.0, 0)
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.albedo_texture = preload("res://branding/vertoconnect-v.svg")
	material.render_priority = 10
	mark.material_override = material
	add_child(mark)
	var title := Label3D.new()
	title.text = "VERTO"
	title.position = Vector3(-1.32, 0.0, 0)
	title.font = preload("res://branding/fonts/Inter.ttf")
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	title.font_size = 100
	title.pixel_size = 0.0045
	title.shaded = false
	title.modulate = Color(1.0, 0.7686, 0.1608)
	title.outline_size = 4
	title.outline_modulate = Color(0.62, 0.31, 0.02, 0.55)
	add_child(title)
	var connect := Label3D.new()
	connect.text = "connect"
	connect.font = title.font
	connect.font_size = title.font_size
	connect.pixel_size = title.pixel_size
	connect.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	connect.position = title.position + Vector3(title.font.get_string_size(title.text, HORIZONTAL_ALIGNMENT_LEFT, -1, title.font_size).x * title.pixel_size, 0, 0)
	connect.shaded = false
	connect.modulate = Color.WHITE
	connect.outline_size = 4
	connect.outline_modulate = Color(0.08, 0.08, 0.08, 0.55)
	add_child(connect)

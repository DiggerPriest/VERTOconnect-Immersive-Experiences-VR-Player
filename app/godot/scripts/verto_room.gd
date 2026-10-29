extends Node3D
## Lightweight physical scenery for the menu, hidden during immersive playback.

func _ready() -> void:
	_box(Vector3(18.0, 0.12, 18.0), Vector3(0, -0.12, 0), Color(0.12, 0.12, 0.11))
	_box(Vector3(18.0, 0.12, 18.0), Vector3(0, 4.4, 0), Color(0.10, 0.10, 0.095))
	for i in range(16):
		var angle := TAU * float(i) / 16.0
		var radial := Vector3(sin(angle), 0, cos(angle))
		var wall := _box(Vector3(3.15, 4.5, 0.12), radial * 8.0 + Vector3(0, 2.15, 0), Color(0.16, 0.16, 0.15))
		wall.rotation.y = angle
		var column := _box(Vector3(0.06, 3.5, 0.06), radial * 7.85 + Vector3(0, 1.8, 0), Color(0.78, 0.57, 0.10))
		column.rotation.y = angle
	for radius in [3.0, 6.0]:
		var ring := MeshInstance3D.new()
		var mesh := TorusMesh.new()
		mesh.inner_radius = radius
		mesh.outer_radius = radius + 0.025
		ring.mesh = mesh
		ring.position.y = -0.045
		ring.material_override = _material(Color(0.76, 0.55, 0.10))
		add_child(ring)


func _box(size: Vector3, position: Vector3, color: Color) -> MeshInstance3D:
	var item := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	item.mesh = mesh
	item.position = position
	item.material_override = _material(color)
	add_child(item)
	return item


func _material(color: Color) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = color
	return material

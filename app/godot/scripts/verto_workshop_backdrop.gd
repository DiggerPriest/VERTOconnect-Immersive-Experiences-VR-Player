extends Node3D
## A world-fixed curved backdrop for a wide photograph, not a 360 panorama or 3D reconstruction.

const IMAGE := preload("res://backgrounds/verto-workshop-4k.jpg")
const RADIUS := 8.0
const ANGLE := deg_to_rad(140.0)
const SEGMENTS := 64
const HEIGHT := RADIUS * ANGLE * 1760.0 / 4096.0
var material: StandardMaterial3D

func _ready() -> void:
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in SEGMENTS:
		var u0 := float(i) / SEGMENTS
		var u1 := float(i + 1) / SEGMENTS
		for uv in [Vector2(u0, 0), Vector2(u0, 1), Vector2(u1, 1), Vector2(u0, 0), Vector2(u1, 1), Vector2(u1, 0)]:
			var theta: float = (uv.x - 0.5) * ANGLE
			surface.set_uv(uv)
			surface.add_vertex(Vector3(sin(theta) * RADIUS, 2.0 + (0.5 - uv.y) * HEIGHT, -cos(theta) * RADIUS))
	var instance := MeshInstance3D.new()
	instance.mesh = surface.commit()
	material = StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.albedo_texture = IMAGE
	instance.material_override = material
	add_child(instance)

func set_brightness(value: float) -> void:
	if material:
		material.albedo_color = Color(value, value, value, 1.0)

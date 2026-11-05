extends Node
## Compatibility does not automatically instance repeated mesh nodes.
## Keep authored ore transform nodes/animations and submit their shared geometry
## in local conveyor batches instead of one draw for each repeated part.
var batches: Array[Dictionary] = []
var _model: Node3D
var _configured := false

func configure(model: Node3D) -> void:
	if _configured: return
	_configured = true
	_model = model
	process_priority = 100
	var groups := {}
	for source: MeshInstance3D in model.find_children("*", "MeshInstance3D", true, false):
		var zone := _instance_zone(str(source.name))
		if zone.is_empty():continue
		if not source.visible or not source.mesh or source.mesh.get_surface_count() != 1: continue
		var material := source.get_active_material(0)
		var key := "%s:%s:%s:%s:%s" % [zone,source.mesh.get_instance_id(), material.get_instance_id() if material else 0, source.layers, source.cast_shadow]
		if not groups.has(key): groups[key] = []
		groups[key].append(source)
	for sources: Array in groups.values():
		if sources.size() < 4: continue
		var first: MeshInstance3D = sources[0]
		var batch := MultiMeshInstance3D.new()
		batch.name = "InstancedCoal_%02d" % batches.size()
		batch.multimesh = MultiMesh.new()
		batch.multimesh.transform_format = MultiMesh.TRANSFORM_3D
		batch.multimesh.mesh = first.mesh
		batch.multimesh.instance_count = sources.size()
		batch.material_override = first.get_active_material(0)
		batch.layers = first.layers
		batch.cast_shadow = first.cast_shadow
		model.add_child(batch)
		batches.append({"batch": batch, "sources": sources})
		for source: MeshInstance3D in sources: source.visible = false
	_update_instances()

func _process(_delta: float) -> void:
	_update_instances()

func _update_instances() -> void:
	if not is_instance_valid(_model): return
	var inverse := _model.global_transform.affine_inverse()
	for group in batches:
		var multimesh: MultiMesh = group.batch.multimesh
		for index in group.sources.size():
			var source: Node3D = group.sources[index]
			multimesh.set_instance_transform(index, inverse * source.global_transform)

static func _instance_zone(label: String) -> String:
	if label.begins_with("DENS_ORE_"):return label.get_slice("_",2)
	if label.begins_with("CV_ORE_"):return "original"
	if label.begins_with("CV2_COAL_"):return "stockpile"
	if label.begins_with("CV_CarryIdler_") or label.begins_with("CV_ReturnIdler_"):return "rollers"
	if label.begins_with("CV_BeltSeam_"):return "seams"
	return ""

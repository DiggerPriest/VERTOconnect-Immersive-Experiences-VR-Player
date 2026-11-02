extends SceneTree
func _initialize() -> void:
	if not preload("res://tests/support/test_result.gd").prepare(self):
		return
	call_deferred("_run")
func _run() -> void:
	var scene = load("res://environments/training_hub/training_hub.tscn").instantiate()
	var changed = preload("res://scripts/training_hub_surfaces.gd").apply(scene)
	if changed != 3:
		push_error("Expected concrete, graphite and ceiling surfaces; got %s" % changed)
		scene.free()
		preload("res://tests/support/test_result.gd").finish(self, 1)
		return
	# Re-application must be harmless and never remap worker materials.
	assert(preload("res://scripts/training_hub_surfaces.gd").apply(scene) == 0)
	scene.free()
	print("Training hub surface mappings passed: 3 scoped material overrides")
	preload("res://tests/support/test_result.gd").finish(self, 0)

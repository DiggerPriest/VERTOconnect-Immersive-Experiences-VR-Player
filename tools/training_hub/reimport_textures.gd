extends SceneTree
## Editor-only, scoped rebuild of GLB-extracted hub textures.
func _initialize() -> void:
	call_deferred("_reimport")

func _reimport() -> void:
	var filesystem := EditorInterface.get_resource_filesystem()
	while filesystem.is_scanning():
		await process_frame
	var paths := PackedStringArray()
	var folder := "res://environments/training_hub/"
	for filename in DirAccess.get_files_at(folder):
		if filename.ends_with(".png"):
			paths.append(folder + filename)
	if paths.is_empty():
		push_error("No extracted training hub textures")
		quit(1)
		return
	filesystem.reimport_files(paths)
	print("TRAINING_HUB_TEXTURES_IMPORTED ", paths.size())
	quit(0)

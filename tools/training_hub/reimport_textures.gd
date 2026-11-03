extends SceneTree
## Editor-only, scoped rebuild of GLB-extracted hub textures.
func _initialize() -> void:
	call_deferred("_reimport")

func _reimport() -> void:
	var filesystem := EditorInterface.get_resource_filesystem()
	while filesystem.is_scanning():
		await process_frame
	var paths := PackedStringArray()
	var requested = JSON.parse_string(OS.get_environment("VERTO_HUB_TEXTURE_PATHS"))
	if requested is Array:
		for path in requested:
			if path is String and (path.begins_with("res://environments/training_hub/") or path.begins_with("res://environments/mining_facility/")):
				paths.append(path)
	if paths.is_empty():
		push_error("No extracted training hub textures")
		quit(1)
		return
	filesystem.reimport_files(paths)
	print("TRAINING_HUB_TEXTURES_IMPORTED ", paths.size())
	quit(0)

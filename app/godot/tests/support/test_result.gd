extends RefCounted
## Only explicit completion may authorize a successful headless test run.


static func prepare(tree: SceneTree) -> bool:
	var case_name: String = tree.get_script().resource_path.get_file().get_basename()
	ProjectSettings.set_setting("application/config/use_custom_user_dir", true)
	ProjectSettings.set_setting(
		"application/config/custom_user_dir_name",
		"ImmivioTests/%s/%d-%d" % [case_name, OS.get_process_id(), Time.get_ticks_usec()]
	)
	if DirAccess.make_dir_recursive_absolute(OS.get_user_data_dir()) != OK:
		push_error("Cannot create isolated test user data")
		finish(tree, 1)
		return false
	print("Test user data: ", OS.get_user_data_dir())
	# The headless dummy renderer races RID allocation when a large imported
	# mesh loads on a worker while UI fixtures create meshes on the main thread.
	# Warm this shared fixture before UI construction; retain a separate cold
	# asynchronous scene-loader test, including suspension during load.
	if DisplayServer.get_name() == "headless" and case_name != "test_mining_environment":
		tree.set_meta("mining_fixture", load(preload("res://scripts/training_hub.gd").MINING_SCENE))
	return true


static func finish(tree: SceneTree, exit_code: int) -> void:
	# Launch scenery now loads asynchronously in every real Main fixture.
	# Finish pending requests while script/resources are still alive, rather
	# than racing ResourceLoader shutdown after the test calls quit().
	for loader in tree.get_nodes_in_group("training_hub_loaders"):
		loader.drain_pending_load()
	print(
		(
			"IMMIVIO_TEST_RESULT "
			+ (
				JSON
				. stringify(
					{
						"script": tree.get_script().resource_path,
						"exit_code": exit_code,
					}
				)
			)
		)
	)
	tree.quit(exit_code)

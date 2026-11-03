extends SceneTree
func _initialize():
	if not preload("res://tests/support/test_result.gd").prepare(self): return
	call_deferred("run")
func run():
	var audio = preload("res://scripts/mining_ambience.gd").new()
	root.add_child(audio)
	assert(audio.stream.get_length() > 29.0)
	assert(audio.stream.loop)
	assert(not audio.playing, "Must not autoplay during load")
	audio.set_active(true)
	await create_timer(0.15).timeout
	assert(audio.playing)
	for reason in ["video", "Jess", "absence", "focus", "deselected"]:
		audio.set_active(false)
		assert(not audio.playing, "Audio leaked during " + reason)
		audio.set_active(false)
		audio.set_active(true)
		assert(audio.playing)
	audio.queue_free()
	await process_frame
	print("MINING_AMBIENCE_PASS")
	preload("res://tests/support/test_result.gd").finish(self, 0)

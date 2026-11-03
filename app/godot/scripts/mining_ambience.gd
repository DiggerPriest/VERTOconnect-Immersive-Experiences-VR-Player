extends AudioStreamPlayer

func _exit_tree() -> void:
	stop()
	stream = null
## Explicit lifecycle gate; never autoplay during asynchronous scene loading.
var resume_position := 0.0

func _ready() -> void:
	var audio = preload("res://audio/mining_background.mp3").duplicate() as AudioStreamMP3
	audio.loop = true
	stream = audio
	volume_db = -22.0

func set_active(enabled: bool) -> void:
	if enabled:
		if not playing:
			play(resume_position)
	elif playing:
		resume_position = get_playback_position()
		stop()

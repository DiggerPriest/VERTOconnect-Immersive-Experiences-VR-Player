extends RefCounted
## Restart the same active video only after an actual absence/presence transition.

var _absent := false
var _session_id := 0
var _uri := ""


func presence_changed(present: bool, video: Variant) -> void:
	if not present:
		if _absent:
			return
		_absent = true
		_session_id = 0
		_uri = ""
		if not is_instance_valid(video) or not video.media.accepts(video.media.session_id):
			return
		_session_id = video.media.session_id
		_uri = video.local_uri
		if video.requested_play and video.media.state != "ended":
			video.toggle_play()
		return

	if not _absent:
		return
	_absent = false
	var session_id := _session_id
	var uri := _uri
	_session_id = 0
	_uri = ""
	if (
		not is_instance_valid(video)
		or session_id <= 0
		or video.media.session_id != session_id
		or video.local_uri != uri
		or not video.media.accepts(session_id)
	):
		return
	# The normal seek pipeline retains projection, stereo and the playback queue.
	video.requested_play = true
	video.seek_absolute(0)

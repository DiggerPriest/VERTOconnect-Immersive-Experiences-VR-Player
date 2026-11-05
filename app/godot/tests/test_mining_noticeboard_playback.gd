extends SceneTree
const Main = preload("res://scripts/main.gd")
const NativeHost = preload("res://tests/test_recent_files.gd")
var failures: Array[String] = []
func check(ok: bool, message: String):
	if not ok:failures.append(message)
func _initialize():
	if not preload("res://tests/support/test_result.gd").prepare(self):return
	call_deferred("run")
func run():
	var main=Main.new()
	main.settings_path="user://noticeboard-settings.cfg"
	root.add_child(main)
	main.set_process(false);main.video.set_process(false);main.photo.set_process(false)
	main.mining_noticeboard.set_process(false)
	var deadline=Time.get_ticks_msec()+15000
	while main.training_hub.loading and Time.get_ticks_msec()<deadline:
		await process_frame
	check(main.training_hub.ready_to_show(),"Main loads the selected factory asynchronously")
	check(main.training_hub.scene_path==main.training_hub.MINING_SCENE,"Main selects the current density scene")
	var platform=NativeHost.Host.new();main.video.platform=platform
	var uri="content://noticeboard/real-player-source.mp4"
	main.video.recent_files.opened(uri,"Actual player source",true)
	main.video.recent_files.progress(uri,23000,60000)
	main.video.recent_files.save()
	main.mining_noticeboard.refresh_history()
	main._update_training_hub_activity()
	check(main.mining_noticeboard.visible,"Real factory activity enables the recent-video board")
	var ambience=main.training_hub.content.get_node("MiningAmbience")
	check(ambience.playing,"Factory audio starts with the loaded world")
	for gate in ["_jess_opened","_hub_wearer_present","temporary_passthrough","_hub_application_active"]:
		var original=main.get(gate)
		main.set(gate,not original)
		main._update_training_hub_activity()
		check(not main.mining_noticeboard.visible,"Board hides during "+gate)
		check(not main.training_hub.content.visible and not ambience.playing,"World and audio suspend during "+gate)
		main.set(gate,original)
		main._update_training_hub_activity()
		check(main.mining_noticeboard.visible and ambience.playing,"World/board/audio resume after "+gate)
	check(main.mining_noticeboard.entries[0].uri==uri,"Board reads the player's own history instance")
	main._queue_add_mode=true
	main.recent_menu.dismiss();main.player_menu.dismiss()
	var paper: Node3D=main.mining_noticeboard._buttons[0].node
	var eye=Vector3(0,1.25,0)
	check(main.mining_noticeboard.press_pointer("right_hand",eye,paper.global_position-eye,true),"Actual poster ray activates")
	check(not main._queue_add_mode,"Poster playback overrides stale add-to-queue mode")
	check(platform.calls.back()[0]=="check" and platform.calls.back()[1]==uri,"Stored Android URI receives access preflight")
	var request:int=main.video._access_request
	main.video._on_local_access(request,JSON.stringify({"uri":uri,"state":"readable","persisted_permission":true}))
	var opens=platform.calls.filter(func(call):return call[0]=="open")
	check(opens.size()==1 and opens[0]==["open",uri,0],"The same real source reaches the native player at 0ms, not saved 23s")
	check(main.video.local_uri==uri and main.video.requested_play,"Playback source and play intent match poster")
	# Selecting/opening alone must not fabricate a recent play. A validated
	# frame from the active native session is the existing history boundary.
	var new_uri="file:///noticeboard/new-source.mp4"
	main.video.open_local(new_uri,"New video",0,true)
	main.video.checkpoint_playback()
	check(not main.mining_noticeboard.entries.any(func(e):return e.uri==new_uri),"No poster for an unpresented video")
	main.video.media.generation=2;main.video.media.state="playing"
	main.video.media.last_pair={"session_id":main.video.media.session_id,"generation":2,"pts_us":1000000,"source_pts_verified":false,"source_ticket_origin":"standard_libmpv_render","source_ticket_valid":true}
	main.video.panel.visible=true
	main.video.checkpoint_playback()
	check(main.mining_noticeboard.entries[0].uri==new_uri,"First validated frame updates the actual board via history_changed")
	main.video.clear_history()
	check(main.mining_noticeboard.entries.is_empty(),"Clear history immediately removes all posters")
	main.video.close_video();main.queue_free();await process_frame
	for failure in failures:push_error(failure)
	print("NOTICEBOARD_PLAYBACK ",failures.size()," failures; real Main/board/video path, fake native decoder/access boundary")
	preload("res://tests/support/test_result.gd").finish(self,0 if failures.is_empty() else 1)

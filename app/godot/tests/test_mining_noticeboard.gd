extends SceneTree
const Board = preload("res://scripts/mining_noticeboard.gd")
const Catalog = preload("res://scripts/recent_files.gd")
var selected: Array = []
func _initialize() -> void:
	if not preload("res://tests/support/test_result.gd").prepare(self):return
	call_deferred("run")
func run() -> void:
	var catalog = Catalog.new()
	for i in 6:
		assert(catalog.opened("file:///noticeboard/video%d.mp4" % i,"Workshop training %d" % i,true))
		assert(catalog.save())
	assert(catalog.opened("file:///noticeboard/photo.jpg","Photo",true,"image"))
	assert(catalog.save())
	assert(catalog.opened("file:///noticeboard/video2.mp4","Isolation and lockout",true))
	assert(catalog.save())
	var restored = Catalog.new();restored.load_saved()
	var videos = Board.recent_videos(restored)
	assert(videos.size()==4)
	assert(videos[0].uri.ends_with("video2.mp4"))
	assert(videos[1].uri.ends_with("video5.mp4"))
	assert(videos[3].uri.ends_with("video3.mp4"))
	var board = Board.new();board.catalog=restored;root.add_child(board);board.set_active(true)
	board.chosen.connect(func(uri,title):selected.append([uri,title]))
	var camera = Camera3D.new();root.add_child(camera);camera.position=Vector3(0,1.25,0)
	camera.keep_aspect=Camera3D.KEEP_WIDTH;camera.fov=85;camera.current=true
	var origin = camera.position
	for i in 4:
		var paper: Node3D=board._buttons[i].node
		# Include corners in each tilted plane, not only an easy centre hit.
		for offset in [Vector3.ZERO,Vector3(-.32,.24,0),Vector3(.32,-.24,0)]:
			var point: Vector3=paper.to_global(offset)
			assert(abs(rad_to_deg(atan2(point.x,-point.z)))<42.5,"Every poster fits the default 85 degree horizontal view")
			assert(origin.distance_to(point)<board.max_ray_metres)
			var hit: Dictionary=board.ray_hit(origin,point-origin)
			assert(hit.get("target",-1)==i,"Tilted poster target follows its visible paper")
		assert(board.press_pointer("right_hand",origin,paper.global_position-origin,true))
		assert(selected.back()[0]==videos[i].uri)
		var rear: Vector3=paper.global_position-paper.global_basis.z
		assert(board.ray_hit(rear,paper.global_basis.z).is_empty(),"Back faces cannot activate")
	board.set_active(false)
	assert(board.ray_hit(origin,Vector3(1,0,-1)).is_empty())
	board.set_active(true)
	restored.clear_all();restored.save();board.refresh_history()
	assert(board.entries.is_empty() and board._buttons.is_empty())
	board.queue_free();camera.queue_free();await process_frame
	print("NOTICEBOARD_PASS: saved four distinct videos, photo exclusion, tilted corner rays, default-view bounds, selection, disabled and empty history")
	preload("res://tests/support/test_result.gd").finish(self,0)

extends Node
## Attach only to the imported mining scene, never the existing worker scene.
## Compatible actions share a player per duration/root. Parent process
## suspension pauses every group together without synchronising different loops.
var players: Array[AnimationPlayer] = []

func configure(model: Node) -> void:
	if not players.is_empty(): return
	var sources = model.find_children("*", "AnimationPlayer", true, false)
	for source: AnimationPlayer in sources:
		var animation_root = source.get_node(source.root_node)
		source.stop()
		source.active = false
		var groups: Array[Animation] = []
		for clip in source.get_animation_list():
			if clip == "RESET": continue
			var animation = source.get_animation(clip).duplicate() as Animation
			if animation.length <= 0.0: continue
			# Godot's glTF importer adds constant rest tracks for neighbouring
			# objects. Keeping those would cancel their independent animations.
			for track in range(animation.get_track_count() - 1, -1, -1):
				var changes = false
				if animation.track_get_key_count(track) > 1:
					var first = animation.track_get_key_value(track, 0)
					for key in range(1, animation.track_get_key_count(track)):
						if animation.track_get_key_value(track, key) != first:
							changes = true
							break
				if not changes: animation.remove_track(track)
			if animation.get_track_count() == 0: continue
			animation.loop_mode = Animation.LOOP_LINEAR
			var group: Animation = null
			for candidate in groups:
				if candidate.length != animation.length: continue
				var overlaps = false
				for track in range(animation.get_track_count()):
					if candidate.find_track(animation.track_get_path(track), animation.track_get_type(track)) >= 0:
						overlaps = true
						break
				if not overlaps:
					group = candidate
					break
			if group:
				for track in range(animation.get_track_count()):
					animation.copy_track(track, group)
			else:
				groups.append(animation)
		for animation in groups:
			var library = AnimationLibrary.new()
			library.add_animation("loop", animation)
			var player = AnimationPlayer.new()
			player.name = "MiningMotion_%d" % players.size()
			add_child(player)
			player.root_node = player.get_path_to(animation_root)
			player.add_animation_library("", library)
			player.play("loop")
			players.append(player)

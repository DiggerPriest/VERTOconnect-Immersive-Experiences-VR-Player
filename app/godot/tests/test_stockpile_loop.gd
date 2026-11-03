extends SceneTree
## Checks the exported stockpile conveyor for visible reset jumps over a full loop.
func _initialize(): call_deferred("run")
func run():
 var model = load("res://environments/mining_facility/mining_facility.tscn").instantiate()
 root.add_child(model)
 var rocks: Array[Node3D] = []
 for node in model.find_children("CV2_COAL_*", "Node3D", true, false): rocks.append(node)
 var motion = model.find_child("MachineryMotion", true, false)
 if rocks.size() != 42 or motion == null:
  push_error("Expected 42 coal pieces and a motion controller")
  quit(1)
  return
 var previous = []
 var visible = []
 for rock in rocks:
  previous.append(rock.global_position)
  visible.append(rock.scale.length() > 0.1)
 var largest_step := 0.0
 for sample in range(1200):
  for player in motion.players: player.advance(1.0 / 60.0)
  for i in range(rocks.size()):
   var current: Vector3 = rocks[i].global_position
   var is_visible := rocks[i].scale.length() > 0.1
   if is_visible and visible[i]:
    var distance = current.distance_to(previous[i])
    if distance > 0.15: print("JUMP ", rocks[i].name, " sample=", sample, " scale=", rocks[i].scale, " distance=", distance)
    largest_step = max(largest_step, distance)
   previous[i] = current
   visible[i] = is_visible
 print("STOCKPILE_LOOP max_visible_step_m=", largest_step)
 model.queue_free()
 await create_timer(0.2).timeout
 if largest_step >= 0.15:
  push_error("Visible coal teleport detected")
  quit(1)
 else: quit(0)

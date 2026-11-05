extends "res://scripts/ray_menu.gd"
## World-fixed recent-video noticeboard. Native poster planes are also the ray
## targets, so their rotation never diverges from the clickable area.
signal chosen(uri: String, title: String)
const Thumbnails := preload("res://scripts/thumbnail_cache.gd")
const POSTER_SIZE := Vector2(.72,.58)
const ANGLES := [-2.0,7.0,1.5,-3.5]
var catalog: RefCounted
var entries: Array[Dictionary] = []
var _signature := ""
var _poll := 0.0
var enabled := false

func _ready() -> void:
	position = Vector3(1.8,1.75,-3.6)
	rotation.y = atan2(-position.x,-position.z)
	allow_user_dismiss = false
	_backdrop = _quad(Vector2(1.95,1.65),Vector3(0,0,-.025),Color(.31,.24,.14),10)
	add_child(_backdrop)
	# Industrial freestanding frame; the four paper surfaces remain separate.
	for x in [-1.0,1.0]:
		_box(Vector3(x,-.465,-.06),Vector3(.07,2.57,.09),Color(.075,.085,.09))
		_box(Vector3(x,-1.71,0),Vector3(.4,.08,.55),Color(.075,.085,.09))
	for y in [-.85,.85]: _box(Vector3(0,y,-.04),Vector3(2.07,.065,.09),Color(.075,.085,.09))
	visible = false
	refresh_history(true)

func _box(at: Vector3,size: Vector3,color: Color) -> void:
	var node := MeshInstance3D.new()
	var mesh := BoxMesh.new(); mesh.size=size;node.mesh=mesh;node.position=at
	var mat := StandardMaterial3D.new();mat.albedo_color=color;mat.roughness=.75
	node.material_override=mat;add_child(node)

func set_active(value: bool) -> void:
	if enabled == value:return
	if not value:
		for hand in _pointers: cancel_pointer(hand)
	enabled=value;visible=value
	if value:refresh_history()

func _process(delta: float) -> void:
	if not enabled:return
	_poll+=delta
	if _poll >= .75:
		_poll=0;refresh_history()

static func recent_videos(source: RefCounted) -> Array[Dictionary]:
	var result: Array[Dictionary]=[]
	if not source:return result
	var seen := {}
	for entry in source.list_recent():
		var uri := str(entry.get("uri",""))
		if entry.get("kind","video") != "video" or uri.is_empty() or seen.has(uri):continue
		seen[uri]=true;result.append(entry.duplicate(true))
		if result.size()==4:break
	return result

func refresh_history(force: bool=false) -> void:
	var next := recent_videos(catalog)
	var key: Array=[]
	for entry in next:key.append([entry.uri,entry.title,entry.opened,entry.get("cover","")])
	var signature := JSON.stringify(key)
	if not force and signature==_signature:return
	_signature=signature;entries=next
	if _backdrop:refresh()

func thumbnail_updated(uri: String) -> void:
	if entries.any(func(entry):return entry.uri==uri):refresh_history(true)

func _draw() -> void:
	_clear_layout()
	var title := _label("SAFETY & TRAINING",Vector3(0,.70,.015),54)
	title.modulate=Color(1,.82,.24)
	_label("RECENTLY PLAYED  •  POINT AND SELECT TO REPLAY",Vector3(0,.60,.015),22)
	if entries.is_empty():
		_label("Your recently played videos\nwill appear here",Vector3(0,0,.015),32)
		return
	for i in entries.size():
		var centre := Vector2(-.46 if i%2==0 else .45,.25 if i<2 else -.39)
		_button(i,"",centre,POSTER_SIZE,true)
		var button: Dictionary=_buttons.back()
		button.base_color=Color(.94,.91,.80)
		var paper: Node3D=button.node
		paper.rotation.z=deg_to_rad(ANGLES[i]);paper.position.z=.025+i*.002
		# The skewed poster hangs from its remaining top-left pin.
		if i==1:
			var pin:=Vector3(-.29,.24,0)
			paper.position+=pin-paper.basis*pin
		var thumbnail := Thumbnails.texture(str(entries[i].uri))
		if thumbnail:
			var picture:=MeshInstance3D.new();var quad:=QuadMesh.new();quad.size=Vector2(.64,.30)
			picture.mesh=quad;picture.position=Vector3(0,.085,.006)
			var material:=_material(Color.WHITE,12)
			material.albedo_texture=thumbnail;material.texture_filter=BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
			picture.material_override=material;paper.add_child(picture)
		else:
			var placeholder:=_quad(Vector2(.64,.30),Vector3(0,.085,.006),Color(.055,.15,.16),12)
			paper.add_child(placeholder)
			_label("▶  VIDEO",Vector3(0,.085,.012),34,paper)
		var caption:=_label(str(entries[i].title),Vector3(0,-.16,.012),36,paper)
		caption.modulate=Color(.08,.09,.09);caption.width=490;caption.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
		caption.text=str(entries[i].title).left(50)
		for child in paper.get_children():
			if child is Label3D:child.render_priority=13
		var marker:=_label("▶ REPLAY",Vector3(.22,-.255,.012),15,paper);marker.modulate=Color(.10,.28,.22)
		for px in ([-.29] if i==1 else [-.29,.29]):
			var pin:=MeshInstance3D.new();var sphere:=SphereMesh.new();sphere.radius=.018;sphere.height=.036
			pin.mesh=sphere;pin.position=Vector3(px,.245,.026)
			var material:=StandardMaterial3D.new();material.albedo_color=Color(.65,.06,.035);material.roughness=.4
			pin.material_override=material;paper.add_child(pin)

func _activate(target: int) -> void:
	if enabled and target>=0 and target<entries.size():
		var entry: Dictionary=entries[target]
		chosen.emit(str(entry.uri),str(entry.title))

func has_pointer_capture() -> bool:return false

func _update_highlights() -> void:
	super._update_highlights()
	# Keep black titles readable when selected; highlight the whole paper.
	for button in _buttons:
		if _hover.values().has(button.target):
			button.node.material_override.set_shader_parameter("surface_color", Color(1.0,.86,.50))

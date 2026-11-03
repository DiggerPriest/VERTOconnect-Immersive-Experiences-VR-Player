extends Node
## The animated mining facility is the only application background.
signal changed
signal custom_saved(path: String, title: String, orientation: int)
const DEFAULT := "mining_facility"
const CHOICES := [DEFAULT]
const INDUSTRIAL := {}
var choice := DEFAULT
# Retained preference fields let older settings load without touching user media.
var directory := "user://backgrounds"
var custom_path := ""
var custom_title := ""
var custom_orientation := 1
var yaw := 0.0
var brightness := 1.0
var loading := false
var error := ""

func _ready() -> void:
	if not select(choice):
		select(DEFAULT)

func select(value: String) -> bool:
	if value not in CHOICES:
		return false
	choice = value
	changed.emit()
	return true

func has_custom() -> bool:
	return false

func import_photo(_source: Dictionary, _title: String) -> bool:
	return false

func ready_sky() -> Sky:
	return null

func set_ambient_active(_active: bool) -> void:
	pass

func rotate_sky() -> void:
	pass

func cycle_brightness() -> void:
	pass

func set_yaw(_value: float) -> void:
	pass

func set_brightness(_value: float) -> void:
	pass

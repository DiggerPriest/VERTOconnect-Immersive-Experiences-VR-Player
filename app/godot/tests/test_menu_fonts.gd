extends SceneTree
const Menu := preload("res://scripts/ray_menu.gd")
const I18n := preload("res://scripts/i18n.gd")
func _initialize() -> void:
	if not preload("res://tests/support/test_result.gd").prepare(self):
		return
	var failures := 0
	var previous := I18n.language
	for language in ["en", "zh", "zh_Hant", "ja"]:
		I18n.language = language
		var font := Menu.ui_font()
		var width := font.get_string_size("A long video filename", HORIZONTAL_ALIGNMENT_LEFT, -1, 22).x
		if width < 100.0 or not is_finite(width):
			push_error("Invalid Latin font metrics for " + language)
			failures += 1
		if language == "en" and not font is FontFile:
			push_error("English must use bundled font as its primary face")
			failures += 1
		if OS.get_name() == "macOS" and not font.has_char("字".unicode_at(0)):
			push_error("macOS CJK fallback must retain actual glyph coverage")
			failures += 1
		# Exercise shaping against system CJK fallbacks, including mixed titles.
		var mixed := font.get_string_size("Video 字幕 日本語", HORIZONTAL_ALIGNMENT_LEFT, -1, 22)
		if not mixed.is_finite() or mixed.x <= 0.0:
			push_error("Invalid mixed-language title metrics")
			failures += 1
	I18n.language = previous
	Menu.ui_font()
	preload("res://tests/support/test_result.gd").finish(self, 0 if failures == 0 else 1)

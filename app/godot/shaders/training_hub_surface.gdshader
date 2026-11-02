shader_type spatial;
render_mode unshaded, cull_back;
uniform sampler2D baked_color : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
uniform sampler2D surface_detail : filter_linear_mipmap_anisotropic, repeat_enable;
uniform float detail_scale = 2.0;
uniform float detail_strength = 0.055;
uniform bool daylight_ceiling = false;
uniform bool neutral_steel = false;
varying vec3 world_position;
void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}
void fragment() {
	if (daylight_ceiling) {
		float centre = exp(-dot(world_position.xz,world_position.xz) / 180.0);
		ALBEDO = mix(vec3(0.29,0.42,0.53),vec3(0.73,0.80,0.82),centre);
	} else {
		vec3 lighting = texture(baked_color, UV).rgb;
		float detail = texture(surface_detail, world_position.xz * detail_scale).r - 0.5;
		if (neutral_steel) {
			float grey = dot(lighting,vec3(0.2126,0.7152,0.0722));
			lighting = mix(vec3(0.035,0.042,0.048), vec3(grey) * vec3(0.93,0.98,1.0),0.55);
		}
		ALBEDO = lighting * (1.0 + detail * detail_strength);
	}
}

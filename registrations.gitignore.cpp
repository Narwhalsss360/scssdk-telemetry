void register_all(scs_telemetry_register_for_channel_t register_for_channel) {
	register_for_channel(SCS_TELEMETRY_CHANNEL_local_scale, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.channel_local_scale);
	register_for_channel(SCS_TELEMETRY_CHANNEL_game_time, SCS_U32_NIL, SCS_VALUE_TYPE_u32, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_u32_t>, &game_data.channel_game_time);
	register_for_channel(SCS_TELEMETRY_CHANNEL_multiplayer_time_offset, SCS_U32_NIL, SCS_VALUE_TYPE_s32, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_s32_t>, &game_data.channel_multiplayer_time_offset);
	register_for_channel(SCS_TELEMETRY_CHANNEL_next_rest_stop, SCS_U32_NIL, SCS_VALUE_TYPE_s32, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_s32_t>, &game_data.channel_next_rest_stop);
	register_for_channel(SCS_TELEMETRY_JOB_CHANNEL_cargo_damage, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.job_channel_cargo_damage);
	char SCS_TELEMETRY_TRAILER_CHANNEL_connected_expansion[] = "trailer.0.connected";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_connected_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_connected_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_connected_trailer_index_char = '0' + t;
		register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_connected_expansion, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.trailers[t].trailer_channel_connected);
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_cargo_damage_expansion[] = "trailer.0.cargo.damage";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_cargo_damage_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_cargo_damage_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_cargo_damage_trailer_index_char = '0' + t;
		register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_cargo_damage_expansion, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.trailers[t].trailer_channel_cargo_damage);
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_world_placement_expansion[] = "trailer.0.world.placement";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_world_placement_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_world_placement_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_world_placement_trailer_index_char = '0' + t;
		register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_world_placement_expansion, SCS_U32_NIL, SCS_VALUE_TYPE_dplacement, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_dplacement_t>, &game_data.trailers[t].trailer_channel_world_placement);
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_local_linear_velocity_expansion[] = "trailer.0.velocity.linear";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_local_linear_velocity_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_local_linear_velocity_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_local_linear_velocity_trailer_index_char = '0' + t;
		register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_local_linear_velocity_expansion, SCS_U32_NIL, SCS_VALUE_TYPE_fvector, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_fvector_t>, &game_data.trailers[t].trailer_channel_local_linear_velocity);
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_local_angular_velocity_expansion[] = "trailer.0.velocity.angular";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_local_angular_velocity_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_local_angular_velocity_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_local_angular_velocity_trailer_index_char = '0' + t;
		register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_local_angular_velocity_expansion, SCS_U32_NIL, SCS_VALUE_TYPE_fvector, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_fvector_t>, &game_data.trailers[t].trailer_channel_local_angular_velocity);
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_local_linear_acceleration_expansion[] = "trailer.0.acceleration.linear";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_local_linear_acceleration_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_local_linear_acceleration_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_local_linear_acceleration_trailer_index_char = '0' + t;
		register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_local_linear_acceleration_expansion, SCS_U32_NIL, SCS_VALUE_TYPE_fvector, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_fvector_t>, &game_data.trailers[t].trailer_channel_local_linear_acceleration);
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_local_angular_acceleration_expansion[] = "trailer.0.acceleration.angular";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_local_angular_acceleration_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_local_angular_acceleration_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_local_angular_acceleration_trailer_index_char = '0' + t;
		register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_local_angular_acceleration_expansion, SCS_U32_NIL, SCS_VALUE_TYPE_fvector, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_fvector_t>, &game_data.trailers[t].trailer_channel_local_angular_acceleration);
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_wear_body_expansion[] = "trailer.0.wear.body";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_wear_body_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_wear_body_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_wear_body_trailer_index_char = '0' + t;
		register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_wear_body_expansion, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.trailers[t].trailer_channel_wear_body);
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_wear_chassis_expansion[] = "trailer.0.wear.chassis";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_wear_chassis_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_wear_chassis_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_wear_chassis_trailer_index_char = '0' + t;
		register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_wear_chassis_expansion, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.trailers[t].trailer_channel_wear_chassis);
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_wear_wheels_expansion[] = "trailer.0.wear.wheels";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_wear_wheels_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_wear_wheels_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_wear_wheels_trailer_index_char = '0' + t;
		register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_wear_wheels_expansion, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.trailers[t].trailer_channel_wear_wheels);
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_wheel_susp_deflection_expansion[] = "trailer.0.wheel.suspension.deflection";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_wheel_susp_deflection_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_wheel_susp_deflection_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_wheel_susp_deflection_trailer_index_char = '0' + t;
		for(scs_u32_t i = 0; i < 19; i++) {
			register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_wheel_susp_deflection_expansion, i, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t, 19>, &game_data.trailers[t].trailer_channel_wheel_susp_deflection);
		}
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_wheel_on_ground_expansion[] = "trailer.0.wheel.on_ground";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_wheel_on_ground_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_wheel_on_ground_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_wheel_on_ground_trailer_index_char = '0' + t;
		for(scs_u32_t i = 0; i < 19; i++) {
			register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_wheel_on_ground_expansion, i, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t, 19>, &game_data.trailers[t].trailer_channel_wheel_on_ground);
		}
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_wheel_substance_expansion[] = "trailer.0.wheel.substance";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_wheel_substance_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_wheel_substance_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_wheel_substance_trailer_index_char = '0' + t;
		for(scs_u32_t i = 0; i < 19; i++) {
			register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_wheel_substance_expansion, i, SCS_VALUE_TYPE_u32, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_u32_t, 19>, &game_data.trailers[t].trailer_channel_wheel_substance);
		}
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_wheel_velocity_expansion[] = "trailer.0.wheel.angular_velocity";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_wheel_velocity_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_wheel_velocity_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_wheel_velocity_trailer_index_char = '0' + t;
		for(scs_u32_t i = 0; i < 19; i++) {
			register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_wheel_velocity_expansion, i, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t, 19>, &game_data.trailers[t].trailer_channel_wheel_velocity);
		}
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_wheel_steering_expansion[] = "trailer.0.wheel.steering";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_wheel_steering_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_wheel_steering_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_wheel_steering_trailer_index_char = '0' + t;
		for(scs_u32_t i = 0; i < 19; i++) {
			register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_wheel_steering_expansion, i, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t, 19>, &game_data.trailers[t].trailer_channel_wheel_steering);
		}
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_wheel_rotation_expansion[] = "trailer.0.wheel.rotation";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_wheel_rotation_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_wheel_rotation_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_wheel_rotation_trailer_index_char = '0' + t;
		for(scs_u32_t i = 0; i < 19; i++) {
			register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_wheel_rotation_expansion, i, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t, 19>, &game_data.trailers[t].trailer_channel_wheel_rotation);
		}
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_wheel_lift_expansion[] = "trailer.0.wheel.lift";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_wheel_lift_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_wheel_lift_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_wheel_lift_trailer_index_char = '0' + t;
		for(scs_u32_t i = 0; i < 19; i++) {
			register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_wheel_lift_expansion, i, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t, 19>, &game_data.trailers[t].trailer_channel_wheel_lift);
		}
	}
	char SCS_TELEMETRY_TRAILER_CHANNEL_wheel_lift_offset_expansion[] = "trailer.0.wheel.lift.offset";
	char& SCS_TELEMETRY_TRAILER_CHANNEL_wheel_lift_offset_trailer_index_char = SCS_TELEMETRY_TRAILER_CHANNEL_wheel_lift_offset_expansion[8];
	for (scs_u32_t t = 0; t < 10; t++) {
		SCS_TELEMETRY_TRAILER_CHANNEL_wheel_lift_offset_trailer_index_char = '0' + t;
		for(scs_u32_t i = 0; i < 19; i++) {
			register_for_channel(SCS_TELEMETRY_TRAILER_CHANNEL_wheel_lift_offset_expansion, i, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t, 19>, &game_data.trailers[t].trailer_channel_wheel_lift_offset);
		}
	}
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_world_placement, SCS_U32_NIL, SCS_VALUE_TYPE_dplacement, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_dplacement_t>, &game_data.truck_channel_world_placement);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_local_linear_velocity, SCS_U32_NIL, SCS_VALUE_TYPE_fvector, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_fvector_t>, &game_data.truck_channel_local_linear_velocity);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_local_angular_velocity, SCS_U32_NIL, SCS_VALUE_TYPE_fvector, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_fvector_t>, &game_data.truck_channel_local_angular_velocity);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_local_linear_acceleration, SCS_U32_NIL, SCS_VALUE_TYPE_fvector, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_fvector_t>, &game_data.truck_channel_local_linear_acceleration);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_local_angular_acceleration, SCS_U32_NIL, SCS_VALUE_TYPE_fvector, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_fvector_t>, &game_data.truck_channel_local_angular_acceleration);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_cabin_offset, SCS_U32_NIL, SCS_VALUE_TYPE_fplacement, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_fplacement_t>, &game_data.truck_channel_cabin_offset);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_cabin_angular_velocity, SCS_U32_NIL, SCS_VALUE_TYPE_fvector, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_fvector_t>, &game_data.truck_channel_cabin_angular_velocity);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_cabin_angular_acceleration, SCS_U32_NIL, SCS_VALUE_TYPE_fvector, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_fvector_t>, &game_data.truck_channel_cabin_angular_acceleration);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_head_offset, SCS_U32_NIL, SCS_VALUE_TYPE_fplacement, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_fplacement_t>, &game_data.truck_channel_head_offset);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_speed, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_speed);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_engine_rpm, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_engine_rpm);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_engine_gear, SCS_U32_NIL, SCS_VALUE_TYPE_s32, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_s32_t>, &game_data.truck_channel_engine_gear);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_displayed_gear, SCS_U32_NIL, SCS_VALUE_TYPE_s32, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_s32_t>, &game_data.truck_channel_displayed_gear);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_input_steering, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_input_steering);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_input_throttle, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_input_throttle);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_input_brake, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_input_brake);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_input_clutch, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_input_clutch);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_effective_steering, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_effective_steering);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_effective_throttle, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_effective_throttle);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_effective_brake, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_effective_brake);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_effective_clutch, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_effective_clutch);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_cruise_control, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_cruise_control);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_hshifter_slot, SCS_U32_NIL, SCS_VALUE_TYPE_u32, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_u32_t>, &game_data.truck_channel_hshifter_slot);
	for (scs_u32_t i = 0; i < 2; i++) {
		register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_hshifter_selector, i, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t, 2>, &game_data.truck_channel_hshifter_selector);
	}
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_parking_brake, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_parking_brake);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_motor_brake, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_motor_brake);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_retarder_level, SCS_U32_NIL, SCS_VALUE_TYPE_u32, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_u32_t>, &game_data.truck_channel_retarder_level);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_brake_air_pressure, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_brake_air_pressure);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_brake_air_pressure_warning, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_brake_air_pressure_warning);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_brake_air_pressure_emergency, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_brake_air_pressure_emergency);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_brake_temperature, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_brake_temperature);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_fuel, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_fuel);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_fuel_warning, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_fuel_warning);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_fuel_average_consumption, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_fuel_average_consumption);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_fuel_range, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_fuel_range);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_adblue, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_adblue);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_adblue_warning, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_adblue_warning);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_adblue_average_consumption, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_adblue_average_consumption);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_oil_pressure, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_oil_pressure);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_oil_pressure_warning, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_oil_pressure_warning);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_oil_temperature, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_oil_temperature);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_water_temperature, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_water_temperature);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_water_temperature_warning, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_water_temperature_warning);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_battery_voltage, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_battery_voltage);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_battery_voltage_warning, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_battery_voltage_warning);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_electric_enabled, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_electric_enabled);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_engine_enabled, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_engine_enabled);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_lblinker, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_lblinker);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_rblinker, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_rblinker);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_hazard_warning, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_hazard_warning);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_light_lblinker, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_light_lblinker);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_light_rblinker, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_light_rblinker);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_light_parking, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_light_parking);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_light_low_beam, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_light_low_beam);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_light_high_beam, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_light_high_beam);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_light_aux_front, SCS_U32_NIL, SCS_VALUE_TYPE_u32, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_u32_t>, &game_data.truck_channel_light_aux_front);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_light_aux_roof, SCS_U32_NIL, SCS_VALUE_TYPE_u32, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_u32_t>, &game_data.truck_channel_light_aux_roof);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_light_beacon, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_light_beacon);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_light_brake, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_light_brake);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_light_reverse, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_light_reverse);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wipers, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_wipers);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_dashboard_backlight, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_dashboard_backlight);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_differential_lock, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_differential_lock);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_lift_axle, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_lift_axle);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_lift_axle_indicator, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_lift_axle_indicator);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_trailer_lift_axle, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_trailer_lift_axle);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_trailer_lift_axle_indicator, SCS_U32_NIL, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t>, &game_data.truck_channel_trailer_lift_axle_indicator);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wear_engine, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_wear_engine);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wear_transmission, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_wear_transmission);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wear_cabin, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_wear_cabin);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wear_chassis, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_wear_chassis);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wear_wheels, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_wear_wheels);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_odometer, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_odometer);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_navigation_distance, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_navigation_distance);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_navigation_time, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_navigation_time);
	register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_navigation_speed_limit, SCS_U32_NIL, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t>, &game_data.truck_channel_navigation_speed_limit);
	for (scs_u32_t i = 0; i < 14; i++) {
		register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wheel_susp_deflection, i, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t, 14>, &game_data.truck_channel_wheel_susp_deflection);
	}
	for (scs_u32_t i = 0; i < 14; i++) {
		register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wheel_on_ground, i, SCS_VALUE_TYPE_bool, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_bool_t, 14>, &game_data.truck_channel_wheel_on_ground);
	}
	for (scs_u32_t i = 0; i < 14; i++) {
		register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wheel_substance, i, SCS_VALUE_TYPE_u32, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_u32_t, 14>, &game_data.truck_channel_wheel_substance);
	}
	for (scs_u32_t i = 0; i < 14; i++) {
		register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wheel_velocity, i, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t, 14>, &game_data.truck_channel_wheel_velocity);
	}
	for (scs_u32_t i = 0; i < 14; i++) {
		register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wheel_steering, i, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t, 14>, &game_data.truck_channel_wheel_steering);
	}
	for (scs_u32_t i = 0; i < 14; i++) {
		register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wheel_rotation, i, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t, 14>, &game_data.truck_channel_wheel_rotation);
	}
	for (scs_u32_t i = 0; i < 14; i++) {
		register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wheel_lift, i, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t, 14>, &game_data.truck_channel_wheel_lift);
	}
	for (scs_u32_t i = 0; i < 14; i++) {
		register_for_channel(SCS_TELEMETRY_TRUCK_CHANNEL_wheel_lift_offset, i, SCS_VALUE_TYPE_float, SCS_TELEMETRY_CHANNEL_FLAG_none, store<scs_value_float_t, 14>, &game_data.truck_channel_wheel_lift_offset);
	}
}

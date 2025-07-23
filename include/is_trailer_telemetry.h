constexpr const bool is_trailer_telemetry(const telemetry_id& id) {
    return id == telemetry_id::trailer || id == telemtry_id::configuraion_trailer_info ? true : is_trailer_channel(id);
}

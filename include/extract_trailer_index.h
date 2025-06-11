constexpr const uint32_t extract_trailer_index(const char* const cstr, const bool reversing = true, size_t count = 0) {
	return (
		reversing ?
			extract_trailer_index(cstr + 1, *(cstr + 1) != '\0', count + 1) :
			count == 0 ?
				INVALID_OFFSET :
				'0' <= *cstr && *cstr <= '9' ?
					*cstr - '0' :
					extract_trailer_index(cstr - 1, false, count - 1)
		);
}
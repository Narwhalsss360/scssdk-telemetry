struct scs_invalid_t;

template <typename T>
struct value_storage {
    bool initialized = false;
    T value {};
};

template <typename T, size_t max_count>
struct value_array_storage {
    bool initialized = false;
    std::array<T, max_count> values {};
    size_t count = 0;
};

template <typename T>
struct value_vector_storage {
    std::vector<T> values {};
};

//Avoid template specialization for bool to avoid potentially non-contiguous values.
//(Does not necessarily store its elements as a contiguous array.)
template <>
struct value_vector_storage<bool> {
    std::vector<uint8_t> values {};
};

template <typename T>
static void append_bytes(const value_storage<T>& storage, std::vector<uint8_t>& out) {
    const uint8_t* const& start = reinterpret_cast<const uint8_t*>(&storage);
    constexpr const size_t initialized_size = sizeof(storage.initialized);
    constexpr const size_t initialized_offset = offsetof(value_storage<T>, initialized);
    constexpr const size_t data_size = sizeof(storage.value);
    constexpr const size_t data_offset = offsetof(value_storage<T>, value);

    out.resize(out.size() + initialized_size + data_size);
    std::copy(start + initialized_offset, start + initialized_offset + initialized_size, out.end() - data_size - initialized_size);
    std::copy(start + data_offset, start + data_offset + data_size, out.end() - data_size);
}

template <>
static void append_bytes(const value_storage<std::string>& storage, std::vector<uint8_t>& out) {
    const uint8_t* const& start = reinterpret_cast<const uint8_t*>(&storage);
    constexpr const size_t initialized_size = sizeof(storage.initialized);
    constexpr const size_t initialized_offset = offsetof(value_storage<std::string>, initialized);
    const size_t data_size = storage.value.size() + 1;

    out.resize(out.size() + initialized_size + data_size);
    std::copy(start + initialized_offset, start + initialized_offset + initialized_size, out.end() - data_size - initialized_size);
    std::copy(storage.value.c_str(), storage.value.c_str() + data_size, out.end() - data_size);
}

template <typename T, size_t max_count>
static void append_bytes(const value_array_storage<T, max_count>& storage, std::vector<uint8_t>& out) {
    using storage_type = value_array_storage<T, max_count>;
    const uint8_t* const& start = reinterpret_cast<const uint8_t*>(&storage);
    constexpr const size_t count_size = sizeof(storage.count);
    constexpr const size_t count_offset = offsetof(storage_type, count);
    constexpr const size_t initialized_size = sizeof(storage.initialized);
    constexpr const size_t initialized_offset = offsetof(storage_type, initialized);
    constexpr const size_t data_size = sizeof(storage.values);
    constexpr const size_t data_offset = offsetof(storage_type, values);

    out.resize(out.size() + initialized_size + count_size + data_size);
    std::copy(start + initialized_offset, start + initialized_offset + initialized_size, out.end() - data_size - count_size - initialized_size);
    std::copy(start + count_offset, start + count_offset + count_size, out.end() - data_size - count_size);
    std::copy(start + data_offset, start + data_offset + data_size, out.end() - data_size);
}

template <size_t max_count>
static void append_bytes(const value_array_storage<std::string, max_count>& storage, std::vector<uint8_t>& out) {
    using storage_type = value_array_storage<std::string, max_count>;
    const uint8_t* const& start = reinterpret_cast<const uint8_t*>(&storage);
    constexpr const size_t initialized_size = sizeof(storage.initialized);
    constexpr const size_t initialized_offset = offsetof(storage_type, initialized);
    constexpr const size_t count_size = sizeof(storage.count);
    constexpr const size_t count_offset = offsetof(storage_type, count);

    out.resize(out.size() + initialized_size + count_size);
    std::copy(start + initialized_offset, start + initialized_offset + initialized_size, out.end() - count_size - initialized_size);
    std::copy(start + count_offset, start + count_offset + count_size, out.end() - count_size);

    for (int i = 0; i < max_count; i++) {
        const std::string& data = storage.values[i];
        const size_t& data_size = data.size() + 1;
        out.resize(out.size() + data_size);
        std::copy(data.c_str(), data.c_str() + data_size, out.end() - data_size);
    }
}

template <typename T>
static void append_bytes(const value_vector_storage<T>& storage, std::vector<uint8_t>& out) {
    const size_t count = storage.values.size();
    const uint8_t* const& count_start = reinterpret_cast<const uint8_t*>(&count);
    const size_t count_size = sizeof(size_t);
    const uint8_t* const& data_start = reinterpret_cast<const uint8_t*>(&storage.values.front()); // reinterpret_cast<const uint8_t*>(&storage.values.front());
    const size_t data_size = sizeof(T) * count;

    out.resize(out.size() + count_size + data_size);
    std::copy(count_start, count_start + count_size, out.end() - count_size - data_size);
    std::copy(data_start, data_start + data_size, out.end() - data_size);
}

template <>
static void append_bytes(const value_vector_storage<std::string>& storage, std::vector<uint8_t>& out) {
    const size_t count = storage.values.size();
    const uint8_t* const& count_start = reinterpret_cast<const uint8_t*>(&count);
    const size_t count_size = sizeof(size_t);
    out.resize(out.size() + count_size);
    std::copy(count_start, count_start + count_size, out.end() - count_size);

    for (const std::string& string : storage.values) {
        const size_t data_size = string.size() + 1;
        out.resize(out.size() + data_size);
        std::copy(string.c_str(), string.c_str() + data_size, out.end() - data_size);
    }
}
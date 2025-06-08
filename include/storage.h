template <typename T>
struct value_storage {
    T value {};
    bool initialized = false;
};

template <typename T, size_t max_count>
struct value_array_storage {
    std::array<T, max_count> values {};
    bool initialized;
    size_t count;
};

template <typename T>
struct value_vector_storage {
    std::vector<T> values {};
};

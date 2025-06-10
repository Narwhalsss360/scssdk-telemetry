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

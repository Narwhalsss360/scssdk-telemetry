#pragma once
#include <stdint.h>
#include <array>
#include <vector>
#include <algorithm>
#include <string>

#ifndef __cpp_if_constexpr
#define __cpp_if_constexpr 201606L
#endif

#if __cplusplus >= __cpp_if_constexpr
#define ifconstexpr constexpr
#else
#define ifconstexpr
#endif

#pragma region constant expression utility
template <typename T, uint32_t count>
constexpr const T sum(const T(&array)[count], const uint32_t& end = count, const uint32_t& start = 0) {
    return start >= end || start >= count ? 0 : array[start] + sum(array, end, start + 1);
}

template <typename T, uint32_t count>
constexpr const uint32_t countof(const T(&array)[count]) {
    return count;
}

constexpr const uint32_t bit_count(const uint32_t& byte_count) {
    return byte_count == 0 ? 2 : 2 * bit_count(byte_count - 1);
}

template <typename TR = int, typename T1 = TR, typename T2>
constexpr const TR cieldiv(const T1& numerator, const T2& denominator) {
    return (numerator + denominator - 1) / denominator;
}
#pragma endregion

#pragma region storage types
struct scs_invalid_t;

template <typename T>
struct value_storage {
    bool initialized = false;
    T value{};

    struct serialization_info {
        using type = value_storage<T>;

        static constexpr const bool constant_size = true;

        static constexpr const uint32_t ordered_sizes[] = {
            sizeof(initialized),
            sizeof(value)
        };

        static constexpr const uint32_t ordered_offsets[] = {
            offsetof(type, initialized),
            offsetof(type, value)
        };

        static constexpr const uint32_t packed_size = sum(ordered_sizes);

        static constexpr const uint32_t count = countof(ordered_sizes);

        static_assert(countof(ordered_sizes) == countof(ordered_offsets), "sizes and offsets must be equal count");
    };

    constexpr const size_t ordered_size(const uint32_t& i) const {
        return serialization_info::ordered_sizes[i];
    }

    constexpr const uint8_t* const ordered_offset(const uint32_t& i) const {
        return reinterpret_cast<const uint8_t* const>(this) + serialization_info::ordered_offsets[i];
    }

    constexpr uint8_t* const ordered_offset(const uint32_t& i) {
        return reinterpret_cast<uint8_t* const>(this) + serialization_info::ordered_offsets[i];
    }

    constexpr const uint32_t packed_size() const {
        return serialization_info::packed_size;
    }

    void append_bytes(std::vector<uint8_t>& out, const uint32_t& i = 0) const {
        if ifconstexpr (i >= serialization_info::count) {
            return;
        } else if ifconstexpr (i == 0) {
            if (out.capacity() - out.size() < packed_size()) {
                out.reserve(out.size() + packed_size());
            }
        }

        out.resize(out.size() + ordered_size(i));
        std::copy(ordered_offset(i), ordered_offset(i) + ordered_size(i), out.end() - ordered_size(i));
        append_bytes(out, i + 1);
    }

    bool from_bytes(const std::vector<uint8_t>& bytes, const uint32_t& offset, uint32_t& read, const uint32_t& i = 0) {
        constexpr const uint32_t (&ordered_sizes)[serialization_info::count] = serialization_info::ordered_sizes;
        if ifconstexpr (i >= serialization_info::count) {
            read = packed_size();
            return true;
        } else if ifconstexpr (i == 0) {
            if (bytes.size() - offset < packed_size()) {
                return false;
            }
        }

        std::copy(
            bytes.cbegin() + offset + sum(ordered_sizes, i),
            bytes.cbegin() + offset + sum(ordered_sizes, i + 1),
            ordered_offset(i)
        );

        return from_bytes(bytes, offset, read, i + 1);
    }
};

template <>
struct value_storage<std::string> {
    bool initialized = false;
    std::string value = "";

    struct serialization_info {
        using type = value_storage<std::string>;

        static constexpr bool constant_size = false;

        static constexpr uint32_t packed_size = sizeof(initialized);
    };

    constexpr const uint32_t packed_size() const {
        return serialization_info::packed_size;
    }

    void append_bytes(std::vector<uint8_t>& out) const {
        const uint32_t count = static_cast<uint32_t>(value.size() + 1);
        out.resize(out.size() + sizeof(initialized) + count);

        const uint8_t* const& initialized_start = reinterpret_cast<const uint8_t* const>(&initialized);
        std::copy(initialized_start, initialized_start + sizeof(initialized), out.end() - count - sizeof(initialized));
        std::copy(value.c_str(), value.c_str() + count, out.end() - count);
    }

    bool from_bytes(const std::vector<uint8_t>& bytes, const uint32_t& offset, uint32_t& read) {
        if (bytes.size() - offset < packed_size()) {
            return false;
        }

        uint32_t end = offset;
        for (int i = offset + sizeof(bool); i < bytes.size(); i++) {
            if (bytes[i] == 0) {
                end = i;
                break;
            }
        }
        if (end == offset) {
            return false;
        }

        const uint8_t* const& bytes_start = &bytes[0];
        initialized = *reinterpret_cast<const bool*>(bytes_start);
        value.resize(end - sizeof(initialized) - offset + 1);
        std::copy(bytes.cbegin() + offset + sizeof(initialized), bytes.cbegin() + offset + sizeof(initialized) + value.size(), value.begin());
        read = sizeof(initialized) + end - offset;
        return true;
    }
};

template <typename T, uint32_t max_count>
struct value_array_storage {
    bool initialized = false;
    std::array<T, max_count> values{};
    uint32_t count;

    struct serialization_info {
        using type = value_array_storage<T, max_count>;

        static constexpr const bool constant_size = true;

        static constexpr const uint32_t ordered_sizes[] = {
            sizeof(initialized),
            sizeof(count),
            sizeof(values)
        };

        static constexpr const uint32_t ordered_offsets[] = {
            offsetof(type, initialized),
            offsetof(type, count),
            offsetof(type, values)
        };

        static constexpr const uint32_t packed_size = sum(ordered_sizes);

        static constexpr const uint32_t count = countof(ordered_sizes);

        static_assert(countof(ordered_sizes) == countof(ordered_offsets), "sizes and offsets must be equal count");
    };

    constexpr const size_t ordered_size(const uint32_t& i) const {
        return serialization_info::ordered_sizes[i];
    }

    constexpr const uint8_t* const ordered_offset(const uint32_t& i) const {
        return reinterpret_cast<const uint8_t* const>(this) + serialization_info::ordered_offsets[i];
    }

    constexpr uint8_t* const ordered_offset(const uint32_t& i) {
        return reinterpret_cast<uint8_t* const>(this) + serialization_info::ordered_offsets[i];
    }

    constexpr const uint32_t packed_size() const {
        return serialization_info::packed_size;
    }

    void append_bytes(std::vector<uint8_t>& out, const uint32_t& i = 0) const {
        if ifconstexpr (i >= serialization_info::count) {
            return;
        } else if ifconstexpr (i == 0) {
            if (out.capacity() - out.size() < packed_size()) {
                out.reserve(out.size() + packed_size());
            }
        }

        out.resize(out.size() + ordered_size(i));
        std::copy(ordered_offset(i), ordered_offset(i) + ordered_size(i), out.end() - ordered_size(i));
        append_bytes(out, i + 1);
    }

    bool from_bytes(const std::vector<uint8_t>& bytes, const uint32_t& offset, uint32_t& read, const uint32_t& i = 0) {
        constexpr const uint32_t (&ordered_sizes)[serialization_info::count] = serialization_info::ordered_sizes;
        if ifconstexpr (i >= serialization_info::count) {
            read = packed_size();
            return true;
        } else if ifconstexpr (i == 0) {
            if (bytes.size() - offset < packed_size()) {
                return false;
            }
        }

        std::copy(
            bytes.cbegin() + offset + sum(ordered_sizes, i),
            bytes.cbegin() + offset + sum(ordered_sizes, i + 1),
            ordered_offset(i)
        );

        return from_bytes(bytes, offset, read, i + 1);
    }
};

template <uint32_t max_count>
struct value_array_storage<std::string, max_count> {
    bool initialized = false;
    std::array<std::string, max_count> values{};
    uint32_t count;

    struct serialization_info {
        using type = value_array_storage<std::string, max_count>;

        static constexpr const bool constant_size = false;

        static constexpr const uint32_t packed_size = sizeof(initialized) + sizeof(count);
    };

    constexpr const uint32_t packed_size() const {
        return serialization_info::packed_size;
    }

    void append_bytes(std::vector<uint8_t>& out) const {
        out.resize(out.size() + sizeof(initialized) + sizeof(count));
        const uint8_t* const initialized_start = reinterpret_cast<const uint8_t* const>(&initialized);
        const uint8_t* const count_start = reinterpret_cast<const uint8_t* const>(&count);

        std::copy(initialized_start, initialized_start + sizeof(initialized), out.end() - sizeof(count) - sizeof(initialized));
        std::copy(count_start, count_start + sizeof(initialized), out.end() - sizeof(count));

        for (uint32_t i = 0; i < count; i++) {
            const uint32_t size = static_cast<uint32_t>(values[i].size() + 1);
            out.resize(out.size() + size);
            std::copy(values[i].c_str(), values[i].c_str() + size, out.end() - size);
        }
    }

    bool from_bytes(const std::vector<uint8_t>& bytes, const uint32_t& offset, uint32_t& read) {
        if (bytes.size() - offset < packed_size()) {
            return false;
        }

        const uint8_t* const& bytes_start = &bytes[0];

        const bool& initialized = *reinterpret_cast<const bool*>(bytes_start);
        const uint32_t& count = *reinterpret_cast<const uint32_t*>(bytes_start + sizeof(initialized));

        if (count > max_count) {
            return false;
        }

        read = 0;
        const uint8_t* const& back = &bytes.back();
        const uint8_t* str_start = bytes_start + sizeof(initialized) + sizeof(count);
        for (uint32_t i = 0; i < count; i++) {
            if (str_start > back) {
                return false;
            }
            values[i] = std::string(reinterpret_cast<const char* const>(str_start));
            const uint32_t szlength = static_cast<uint32_t>(values[i].size() + 1);
            str_start += szlength;
            read += szlength;
        }
        
        read += sizeof(initialized) + sizeof(count);
        this->initialized = initialized;
        this->count = count;
        return true;
    }
};

template <typename T>
struct value_vector_storage {
    std::vector<T> values{};

    const inline uint32_t count() const { return static_cast<uint32_t>(values.size()); };

    struct serialization_info {
        using type = value_vector_storage<T>;

        static constexpr const bool constant_size = false;

        static constexpr const uint32_t packed_size = sizeof(uint32_t);
    };

    constexpr const uint32_t packed_size() const {
        return serialization_info::packed_size;
    }

    void append_bytes(std::vector<uint8_t>& out) const {
        const uint32_t lcount = count();
        const uint8_t* const& count_start = reinterpret_cast<const uint8_t* const>(&lcount);
        
        const uint32_t size = lcount * sizeof(T);
        out.resize(out.size() + sizeof(lcount) + size);
        
        std::copy(count_start, count_start + sizeof(lcount), out.end() - size - sizeof(lcount));

        if (size != 0) {
            const uint8_t* const& data_start = reinterpret_cast<const uint8_t* const>(&*values.cbegin());
            std::copy(data_start, data_start + size, out.end() - size);
        }
    }

    bool from_bytes(const std::vector<uint8_t>& bytes, const uint32_t& offset, uint32_t& read) {
        if (bytes.size() - offset < packed_size()) {
            return false;
        }

        const uint8_t* const bytes_start = &bytes[offset];
        const uint32_t& count = *reinterpret_cast<const uint32_t* const>(bytes_start);

        if (bytes.size() - offset - count < sizeof(T) * count) {
            return false;
        }

        const T* const& data_start = reinterpret_cast<const T* const>(&bytes[offset + sizeof(count)]);

        values.resize(count);
        std::copy(data_start, data_start + count, values.begin());
        read = sizeof(count) + count * sizeof(T);
        return true;
    }
};

template <>
struct value_vector_storage<std::string> {
    std::vector<std::string> values{};

    const inline uint32_t count() const { return static_cast<uint32_t>(values.size()); };

    struct serialization_info {
        static constexpr const bool constant_size = false;

        static constexpr const uint32_t packed_size = sizeof(uint32_t);
    };

    constexpr const uint32_t packed_size() const {
        return serialization_info::packed_size;
    }

    void append_bytes(std::vector<uint8_t>& out) const {
        const uint32_t lcount = count();
        const uint8_t* const& count_start = reinterpret_cast<const uint8_t* const>(&lcount);

        out.resize(out.size() + sizeof(lcount));
        std::copy(count_start, count_start + sizeof(lcount), out.end() - sizeof(lcount));
        for (const std::string& value : values) {
            const uint32_t size = static_cast<uint32_t>(value.size() + 1);
            out.resize(out.size() + size);
            std::copy(value.c_str(), value.c_str() + size, out.end() - size);
        }
    }

    bool from_bytes(const std::vector<uint8_t>& bytes, const uint32_t& offset, uint32_t& read) {
        if (bytes.size() - offset < packed_size()) {
            return false;
        }

        const uint8_t* const bytes_start = &bytes[offset];
        const uint32_t& count = *reinterpret_cast<const uint32_t* const>(bytes_start);

        const uint8_t* const& back = &bytes.back();
        const uint8_t* str_start = bytes_start + sizeof(count);
        values.clear();
        values.reserve(count);
        read = 0;
        for (uint32_t i = 0; i < count; i++) {
            if (str_start > back) {
                return false;
            }
            values.resize(values.size() + 1);
            values.back() = std::string(reinterpret_cast<const char* const>(str_start));
            const uint32_t szlength = static_cast<uint32_t>(values[i].size() + 1);
            str_start += szlength;
            read += szlength;
        }
        read += sizeof(count);

        return true;
    }
};

//Avoid template specialization for bool to avoid potentially non-contiguous values.
//(Does not necessarily store its elements as a contiguous array.)
template <>
struct value_vector_storage<bool> {
    using bool_int = uint32_t;

    static constexpr const uint32_t bool_int_bit_count = bit_count(sizeof(bool_int));

    std::vector<bool> values{};
    
    const inline uint32_t count() const { return static_cast<uint32_t>(values.size()); };

    struct serialization_info {
        static constexpr const bool constant_size = false;

        static constexpr const uint32_t packed_size = sizeof(uint32_t);
    };

    constexpr const uint32_t packed_size() const {
        return serialization_info::packed_size;
    }

    void append_bytes(std::vector<uint8_t>& out) const {
        const uint32_t lcount = count();
        const uint8_t* const& count_start = reinterpret_cast<const uint8_t* const>(&lcount);
        const uint32_t bool_int_count = cieldiv(lcount, bool_int_bit_count);

        out.resize(out.size() + sizeof(lcount) + bool_int_count);
        std::copy(count_start, count_start + sizeof(lcount), out.end() - bool_int_count - sizeof(lcount));

        for (
            uint32_t i = 0, bit = 0, iint = static_cast<uint32_t>(out.size() - bool_int_count);
            i < lcount; i++,
            iint = bit == bool_int_bit_count - 1 ? iint + 1 : iint, bit = bit == bool_int_bit_count - 1 ? 0 : bit + 1
        ) {
            if (values[i]) {
                out[iint] |= 1 << bit;
            } else {
                out[iint] &= ~(1 << bit);
            }
        }
    }

    bool from_bytes(const std::vector<uint8_t>& bytes, const uint32_t& offset, uint32_t& read) {
        if (bytes.size() - offset < packed_size()) {
            return false;
        }

        const uint8_t* const bytes_start = &bytes[offset];
        const uint32_t& count = *reinterpret_cast<const uint32_t* const>(bytes_start);
        const uint32_t bool_int_count = cieldiv(count, bool_int_bit_count);
        if (bytes.size() - offset - sizeof(count) < bool_int_count) {
            return false;
        }

        read = sizeof(count) + bool_int_count;
        values.clear();
        values.resize(count);

        for (
            uint32_t i = 0, bit = 0, iint = offset + sizeof(count);
            i < count; i++,
            iint = bit == bool_int_bit_count - 1 ? iint + 1 : iint, bit = bit == bool_int_bit_count - 1 ? 0 : bit + 1
        ) {
            values[i] = bytes[iint] & (1 << bit);
        }

        return true;
    }
};
#pragma endregion

#pragma region append/from bytes overloads
template <typename T>
void append_bytes(const value_storage<T>& value, std::vector<uint8_t>& out) {
    value.append_bytes(out);
}

template <typename T, uint32_t max_count>
void append_bytes(const value_array_storage<T, max_count>& value, std::vector<uint8_t>& out) {
    value.append_bytes(out);
}

template <typename T>
void append_bytes(const value_vector_storage<T>& value, std::vector<uint8_t>& out) {
    value.append_bytes(out);
}

template <typename T, uint32_t max_count>
void append_bytes(const std::array<T, max_count>& array, std::vector<uint8_t>& out) {
    for (uint32_t i = 0; i < max_count; i++) {
        append_bytes(array[i], out);
    }
}

template <typename T>
bool from_bytes(const std::vector<uint8_t>& bytes, value_storage<T>& out, uint32_t offset, uint32_t& read) {
    return out.from_bytes(bytes, offset, read);
}

template <typename T>
bool from_bytes(const std::vector<uint8_t>& bytes, value_storage<T>& out, uint32_t offset = 0) {
    uint32_t read;
    return out.from_bytes(bytes, offset, read);
}

template <typename T, uint32_t max_count>
bool from_bytes(const std::vector<uint8_t>& bytes, value_array_storage<T, max_count>& out, uint32_t offset, uint32_t& read) {
    return out.from_bytes(bytes, offset, read);
}

template <typename T, uint32_t max_count>
bool from_bytes(const std::vector<uint8_t>& bytes, value_array_storage<T, max_count>& out, uint32_t offset = 0) {
    uint32_t read;
    return out.from_bytes(bytes, offset, read);
}

template <typename T>
bool from_bytes(const std::vector<uint8_t>& bytes, value_vector_storage<T>& out, uint32_t offset, uint32_t& read) {
    return out.from_bytes(bytes, offset, read);
}

template <typename T>
bool from_bytes(const std::vector<uint8_t>& bytes, value_vector_storage<T>& out, uint32_t offset = 0) {
    uint32_t read;
    return out.from_bytes(bytes, offset, read);
}

template <typename T, uint32_t max_count>
bool from_bytes(const std::vector<uint8_t>& bytes, std::array<T, max_count>& out, uint32_t offset, uint32_t& read, uint32_t& count) {
    for (uint32_t i = 0; i < max_count; i++) {
        uint32_t iread;
        if (!from_bytes(bytes, out[i], offset + read, iread)) {
            return false;
        }
        count++;
        read += iread;
    }
    return true;
}

template <typename T, uint32_t max_count>
bool from_bytes(const std::vector<uint8_t>& bytes, std::array<T, max_count>& out, uint32_t offset) {
    uint32_t read, count;
    return from_bytes(bytes, out, offset, read, count);
}
template <typename T, uint32_t max_count>
bool from_bytes(const std::vector<uint8_t>& bytes, std::array<T, max_count>& out) {
    uint32_t read, count;
    return from_bytes(bytes, out, 0, read, count);
}
#pragma endregion

from __future__ import annotations
from dataclasses import dataclass, asdict
from os.path import isfile
import json


try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


REWRITE_JSON = False


SCS_TELEMETRY_trailers_count: int = 10

TYPE_MACROS_BY_ID: list[str] = [
    "SCS_VALUE_TYPE_INVALID",
    "SCS_VALUE_TYPE_bool",
    "SCS_VALUE_TYPE_s32",
    "SCS_VALUE_TYPE_u32",
    "SCS_VALUE_TYPE_u64",
    "SCS_VALUE_TYPE_float",
    "SCS_VALUE_TYPE_double",
    "SCS_VALUE_TYPE_fvector",
    "SCS_VALUE_TYPE_dvector",
    "SCS_VALUE_TYPE_euler",
    "SCS_VALUE_TYPE_fplacement",
    "SCS_VALUE_TYPE_dplacement",
    "SCS_VALUE_TYPE_string",
    "SCS_VALUE_TYPE_s64",
]

# This type should be an incomplete type, that cannot be instantiated. a simple forward declaration should be fine
CPP_INVALID_TYPE = "scs_invalid_t"

TYPES_BY_ID: list[str] = [
    CPP_INVALID_TYPE,
    "scs_value_bool_t",
    "scs_value_s32_t",
    "scs_value_u32_t",
    "scs_value_u64_t",
    "scs_value_float_t",
    "scs_value_double_t",
    "scs_value_fvector_t",
    "scs_value_dvector_t",
    "scs_value_euler_t",
    "scs_value_fplacement_t",
    "scs_value_dplacement_t",
    "scs_value_string_t",
    "scs_value_s64_t",
]

SHORT_TYPENAME_TO_TYPE: dict[str, str] = {
    None: CPP_INVALID_TYPE,
    "bool": "scs_value_bool_t",
    "s32": "scs_value_s32_t",
    "u32": "scs_value_u32_t",
    "u64": "scs_value_u64_t",
    "float": "scs_value_float_t",
    "double": "scs_value_double_t",
    "fvector": "scs_value_fvector_t",
    "dvector": "scs_value_dvector_t",
    "euler": "scs_value_euler_t",
    "fplacement": "scs_value_fplacement_t",
    "dplacement": "scs_value_dplacement_t",
    "string": "scs_value_string_t",
    "s64": "scs_value_s64_t",
}


PRIMITIVE_TYPE_BY_ID: list[str] = [
    CPP_INVALID_TYPE,
    "bool",
    "int32_t",
    "uint32_t",
    "uint64_t",
    "float",
    "double",
    "scs_value_fvector_t",
    "scs_value_dvector_t",
    "scs_value_euler_t",
    "scs_value_fplacement_t",
    "scs_value_dplacement_t",
    "scs_value_string_t",
    "int64_t",
]

TYPE_SIZE_BY_ID: list[int] = [0, 1, 4, 4, 8, 4, 8, 12, 24, 12, 24, 40, 0, 8]

PADDING_BY_TYPE: dict[str, dict[str, int]] = (
    {"scs_value_dplacement_t": {"offset": 36, "size": 4}},
)


def id_of_type(type: str) -> int:
    try:
        return TYPE_MACROS_BY_ID.index(type)
    except ValueError:
        try:
            return TYPES_BY_ID.index(type)
        except ValueError:
            try:
                return TYPES_BY_ID.index(SHORT_TYPENAME_TO_TYPE.get(type))
            except ValueError:
                try:
                    return PRIMITIVE_TYPE_BY_ID.index(type)
                except ValueError:
                    return -1


@dataclass
class Channel:
    macro: str
    expansion: str
    type: str
    indexed: bool
    simple_name: str
    is_trailer_channel: bool
    max_count: int

    @property
    def scs_type(self) -> str:
        return SHORT_TYPENAME_TO_TYPE[self.type]

    @property
    def scs_type_id(self) -> int:
        return id_of_type(self.type)

    @property
    def primitive_type(self) -> str:
        return PRIMITIVE_TYPE_BY_ID[self.scs_type_id]

    def trailer_index_expansion(self, trailer_index: int = -1) -> str:
        if trailer_index != -1 and not self.is_trailer_channel:
            raise RuntimeError(
                "`trailer_index` can only be specified for trailer channels"
            )
        if 0 <= trailer_index < SCS_TELEMETRY_trailers_count:
            return self.expansion.replace("trailer", f"trailer.{trailer_index}", 1)
        raise IndexError(f"Trailer index max is {SCS_TELEMETRY_trailers_count}")

    def __hash__(self) -> int:
        return hash(self.macro)


@dataclass
class EventAttribute:
    macro: str
    expansion: str
    simple_name: str
    type: str
    indexed: bool

    def __post_init__(self) -> None:
        self._event_info: EventInfo | None = None

    @property
    def event_info(self) -> EventInfo | None:
        return self._event_info

    @property
    def scs_type(self) -> str:
        return SHORT_TYPENAME_TO_TYPE[self.type]

    @property
    def scs_type_id(self) -> int:
        return id_of_type(self.type)

    @property
    def primitive_type(self) -> str:
        return PRIMITIVE_TYPE_BY_ID[self.scs_type_id]
    
    def __hash__(self) -> int:
        return hash(f"{self.event_info.macro if self.event_info else None}.{self.macro}")


@dataclass
class EventInfo:
    macro: str
    expansion: str
    simple_name: str
    attributes: list[EventAttribute]

    def __post_init__(self) -> None:
        self._event: Event | None = None
        for i in range(len(self.attributes)):
            if isinstance(self.attributes[i], dict):
                self.attributes[i] = EventAttribute(**self.attributes[i])

        for attribute in self.attributes:
            attribute._event_info = self

    @property
    def event(self) -> Event | None:
        return self._event

    def __hash__(self) -> int:
        return hash(f"{self.event.macro if self.event else None}.{self.macro}")


@dataclass
class Event:
    macro: str
    expansion: str
    simple_name: str
    event_infos: list[EventInfo]

    def __post_init__(self) -> None:
        for i in range(len(self.event_infos)):
            if isinstance(self.event_infos[i], dict):
                self.event_infos[i] = EventInfo(**self.event_infos[i])
        for event_info in self.event_infos:
            event_info._event = self


SCSSDK_TELEMETRY_FILE: str = "scssdk_telemetry.json"


def load() -> tuple[
    list[Channel],
    list[Event],
]:
    if not isfile(SCSSDK_TELEMETRY_FILE):
        raise FileNotFoundError(f"File {SCSSDK_TELEMETRY_FILE} doesn't exist")
    with open(SCSSDK_TELEMETRY_FILE, encoding="utf-8") as file:
        scssdk: dict = json.loads(file.read())
    return (
        [Channel(**channel) for channel in scssdk["channels"]],
        [Event(**event) for event in scssdk["events"]],
    )


def scssdk_dict(
    channels: list[Channel],
    events: list[Event],
) -> None:
    return {
        "SCS_TELEMETRY_trailers_count": SCS_TELEMETRY_trailers_count,
        "TYPE_MACROS_BY_ID": TYPE_MACROS_BY_ID,
        "CPP_INVALID_TYPE": CPP_INVALID_TYPE,
        "TYPES_BY_ID": TYPES_BY_ID,
        "SHORT_TYPENAME_TO_TYPE": SHORT_TYPENAME_TO_TYPE,
        "PRIMITIVE_TYPE_BY_ID": PRIMITIVE_TYPE_BY_ID,
        "TYPE_SIZE_BY_ID": TYPE_SIZE_BY_ID,
        "PADDING_BY_TYPE": PADDING_BY_TYPE,
        "channels": [asdict(dc) for dc in channels],
        "events": [asdict(dc) for dc in events],
    }


def yamlfy() -> None:
    if not HAS_YAML:
        return
    with open(SCSSDK_TELEMETRY_FILE, encoding="utf-8") as file:
        scssdk: dict = json.loads(file.read())
    with open(
        SCSSDK_TELEMETRY_FILE.replace(".json", ".yaml"), "w", encoding="utf-8"
    ) as file:
        file.write(yaml.dump(scssdk, sort_keys=False))
    print("Yamlfied!")


def main() -> None:
    channels, events = load()
    print(f"Loaded {len(channels)} channels, and {len(events)} events.")
    yamlfy()

    if REWRITE_JSON:
        with open(SCSSDK_TELEMETRY_FILE, "w", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    scssdk_dict(channels, events),
                    indent=4,
                )
            )


if __name__ == "__main__":
    main()

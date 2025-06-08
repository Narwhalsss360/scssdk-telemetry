from dataclasses import dataclass, field, asdict
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
class Telemetry:
    id: int
    macro: str
    expansion: str
    type: str
    is_event: bool
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


@dataclass
class TelemetryEventAttribute:
    macro: str
    expansion: str
    simple_name: str
    type: str
    indexed: bool


@dataclass
class Configuration:
    macro: str
    expansion: str
    simple_name: str
    attributes: list[TelemetryEventAttribute]

    def __post_init__(self) -> None:
        for i in range(len(self.attributes)):
            if isinstance(self.attributes[i], dict):
                self.attributes[i] = TelemetryEventAttribute(**self.attributes[i])


@dataclass
class GameplayEvent:
    macro: str
    expansion: str
    simple_name: str
    attributes: list[TelemetryEventAttribute]

    def __post_init__(self) -> None:
        for i in range(len(self.attributes)):
            if isinstance(self.attributes[i], dict):
                self.attributes[i] = TelemetryEventAttribute(**self.attributes[i])


SCSSDK_TELEMETRY_FILE: str = "scssdk_telemetry.json"


def load() -> tuple[
    list[Telemetry],
    list[TelemetryEventAttribute],
    list[Configuration],
    list[GameplayEvent],
]:
    if not isfile(SCSSDK_TELEMETRY_FILE):
        raise FileNotFoundError(f"File {SCSSDK_TELEMETRY_FILE} doesn't exist")
    with open(SCSSDK_TELEMETRY_FILE, encoding="utf-8") as file:
        scssdk: dict = json.loads(file.read())
    return (
        [Telemetry(**telemetry) for telemetry in scssdk["telemetries"]],
        [TelemetryEventAttribute(**attribute) for attribute in scssdk["attributes"]],
        [Configuration(**configuration) for configuration in scssdk["configurations"]],
        [
            GameplayEvent(**gameplay_event)
            for gameplay_event in scssdk["gameplay_events"]
        ],
    )


def scssdk_dict(
    telemetries: list[Telemetry],
    attributes: list[TelemetryEventAttribute],
    configurations: list[Configuration],
    gameplay_events: list[GameplayEvent],
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
        "telemetries": [asdict(dc) for dc in telemetries],
        "attributes": [asdict(dc) for dc in attributes],
        "configurations": [asdict(dc) for dc in configurations],
        "gameplay_events": [asdict(dc) for dc in gameplay_events],
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
    telemetries, attributes, configurations, gameplay_events = load()
    print(
        f"Loaded {len(telemetries)} telemetries, {len(attributes)} attributes, {len(configurations)} configurations and {len(gameplay_events)} gameplay events."
    )
    yamlfy()

    if REWRITE_JSON:
        with open(SCSSDK_TELEMETRY_FILE, "w", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    scssdk_dict(
                        telemetries, attributes, configurations, gameplay_events
                    ),
                    indent=4,
                )
            )


if __name__ == "__main__":
    main()

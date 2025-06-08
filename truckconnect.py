from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from scssdk_dataclasses import Channel, Event, EventInfo, load


TELEMETRY_EVENTS: str = [
    "SCS_TELEMETRY_EVENT_configuration",
    "SCS_TELEMETRY_EVENT_gameplay",
]
INVALID_TELEMETRY_ID: int = -1


class ChannelCategory(Enum):
    General = (0,)
    Truck = (1,)
    Trailer = 2

    @staticmethod
    def of(channel: Channel) -> ChannelCategory:
        if channel.macro.startswith("SCS_TELEMETRY_TRUCK_CHANNEL"):
            return ChannelCategory.Truck
        if channel.macro.startswith("SCS_TELEMETRY_TRAILER_CHANNEL"):
            return ChannelCategory.Trailer
        elif channel.macro.startswith(
            "SCS_TELEMETRY_CHANNEL"
        ) or channel.macro.startswith("SCS_TELEMETRY_JOB_CHANNEL"):
            return ChannelCategory.General
        assert False, "A channel was not supplied"


@dataclass
class Structure:
    data: Event | str
    children: list[Telemetry]


@dataclass
class Telemetry:
    telemetry: Channel | EventInfo | Structure
    id: int = field(default=INVALID_TELEMETRY_ID)

    @property
    def is_channel(self) -> bool:
        return isinstance(self.telemetry, Channel)

    @property
    def as_channel(self) -> Channel:
        assert self.is_channel, "Requested Channel, but telemetry was not"
        return self.telemetry

    @property
    def is_event_info(self) -> bool:
        return isinstance(self.telemetry, EventInfo)

    @property
    def as_event_info(self) -> EventInfo:
        assert self.is_event_info, "Requested EventInfo, but telemetry was not"
        return self.telemetry

    @property
    def is_structure(self) -> bool:
        return isinstance(self.telemetry, Structure)

    @property
    def as_structure(self) -> Structure:
        assert self.is_structure, "Requested Structure, but telemetry was not"
        return self.telemetry

    @property
    def rank(self) -> int:
        if self.is_structure:
            return 0
        elif self.is_event_info:
            return 1
        elif self.is_channel:
            return 2

    @staticmethod
    def build(channels: list[Channel], events: list[Event]) -> list[Telemetry]:
        telemetries: list[Telemetry] = Telemetry._load_event_telemetries(events)
        general_structure: Telemetry = Telemetry(Structure("general", []))
        truck_structure: Telemetry = Telemetry(Structure("truck", []))
        trailer_structure: Telemetry = Telemetry(Structure("trailer", []))

        for channel_telemetry in Telemetry._load_channel_telemetries(channels):
            match ChannelCategory.of(channel_telemetry.telemetry):
                case ChannelCategory.General:
                    general_structure.telemetry.children.append(channel_telemetry)
                case ChannelCategory.Truck:
                    truck_structure.telemetry.children.append(channel_telemetry)
                case ChannelCategory.Trailer:
                    trailer_structure.telemetry.children.append(channel_telemetry)
                case _:
                    assert False, "'of' must always return a ChannelCategory"
            telemetries.append(channel_telemetry)

        telemetries.extend(
            (
                Telemetry(
                    Structure(
                        "channels",
                        [general_structure, truck_structure, trailer_structure],
                    )
                ),
                general_structure,
                truck_structure,
                trailer_structure,
            )
        )

        telemetries.sort(key=lambda t: t.rank)

        telemetries.insert(
            0,
            Telemetry(
                Structure("master", [filter(lambda t: t.is_structure, telemetries)])
            ),
        )

        return telemetries

    @staticmethod
    def _load_event_telemetries(events: list[Event]) -> list[Telemetry]:
        event_telemetries: list[Telemetry] = []
        for event in events:
            if event.macro not in TELEMETRY_EVENTS:
                continue
            event_telemetries.append(
                Telemetry(
                    Structure(
                        event,
                        [Telemetry(event_info) for event_info in event.event_infos],
                    )
                )
            )
            event_telemetries.extend(event_telemetries[-1].telemetry.children)
        return event_telemetries

    @staticmethod
    def _load_channel_telemetries(channels: list[Channel]) -> list[Telemetry]:
        channel_telemetries: list[Telemetry] = []
        for channel in channels:
            channel_telemetries.append(Telemetry(channel))
        return channel_telemetries


def main() -> None:
    telemetries: list[Telemetry] = Telemetry.build(*load())
    print(f"Loaded {len(telemetries)} telemetries.")


if __name__ == "__main__":
    if retval := main():
        print(retval)

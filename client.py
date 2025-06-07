from socket import socket, AddressFamily, SocketKind, IPPROTO_TCP, SHUT_RDWR
from struct import unpack
from scssdk_dataclasses import load, Telemetry, TYPE_SIZE_BY_ID
from prototc import store_size, offsets_of

try:
    from nstreamcom import Collector, CollectorStates, encode_with_size
except ImportError:
    print("Ensure nstreamcom is installed. extern/NStreamCom")
    exit()

HOST: str = "127.0.0.1"
PORT: int = 52878
ENDPOINT: tuple[str, str] = (HOST, PORT)

telemetries, attributes, configurations, gameplay_events = load()
STORE_SIZE: int = store_size(telemetries)

speed_telemetry: Telemetry = next(
    filter(lambda t: t.macro == "SCS_TELEMETRY_TRUCK_CHANNEL_speed", telemetries)
)
speed_offset, speed_initialized_offset, _ = offsets_of(telemetries, speed_telemetry)
speed_size, speed_initialized_size = TYPE_SIZE_BY_ID[speed_telemetry.scs_type_id], 1
rpm_telemetry: Telemetry = next(
    filter(lambda t: t.macro == "SCS_TELEMETRY_TRUCK_CHANNEL_engine_rpm", telemetries)
)
rpm_offset, rpm_initialized_offset, _ = offsets_of(telemetries, rpm_telemetry)
rpm_size, rpm_initialized_size = TYPE_SIZE_BY_ID[rpm_telemetry.scs_type_id], 1


def get_data(game: socket) -> None:
    game.sendall(encode_with_size(b"\x01"))

    collector: Collector = Collector()
    while collector.state in (CollectorStates.WaitingSize, CollectorStates.WaitingData):
        if not (recv := game.recv(1)):
            break
        collector.collect(recv[0])

    if not collector.state == CollectorStates.Collected:
        print(f"Collector error: {collector.state}")
        return

    request: int = int(collector.bytearray[0])

    if request != 1:
        print("Received reply for other request")
        return

    speed: float = unpack(
        "f", collector.bytearray[1 + speed_offset : 1 + speed_offset + speed_size]
    )[0]
    speed_initialized: bool = unpack(
        "?",
        collector.bytearray[
            1 + speed_initialized_offset : 1
            + speed_initialized_offset
            + speed_initialized_size
        ],
    )[0]
    rpm: float = unpack(
        "f", collector.bytearray[1 + rpm_offset : 1 + rpm_offset + rpm_size]
    )[0]
    rpm_initialized: bool = unpack(
        "?",
        collector.bytearray[
            1 + rpm_initialized_offset : 1
            + rpm_initialized_offset
            + rpm_initialized_size
        ],
    )[0]

    print(f"{speed :02.03f}" if speed_initialized else "---", end="")
    print(" m/s | ", end="")
    print(f"{rpm :04.0f}" if rpm_initialized else "---", end="")
    print(" rpm \r")


def main(game: socket) -> None:
    while True:
        try:
            get_data(game)
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    game = socket(AddressFamily.AF_INET, SocketKind.SOCK_STREAM, IPPROTO_TCP)
    game.connect(ENDPOINT)
    main(game)
    game.shutdown(SHUT_RDWR)
    game.close()

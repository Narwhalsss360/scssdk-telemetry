from socket import socket, AddressFamily, SocketKind, IPPROTO_TCP, SHUT_RDWR
from struct import unpack
from prototc import Telemetry, load, offsets_of, store_size, TYPE_SIZE_BY_ID

HOST: str = '127.0.0.1'
PORT: int = 10203
ENDPOINT: tuple[str, str] = (HOST, PORT)


telemetries, attributes, configurations, gameplay_events = load()
STORE_SIZE: int = store_size(telemetries)

speed: Telemetry = next(filter(lambda t: t.id == 38, telemetries))
speed_size: int = TYPE_SIZE_BY_ID[speed.scs_type_id]

rpm: Telemetry = next(filter(lambda t: t.id == 39, telemetries))
rpm_size: int = TYPE_SIZE_BY_ID[rpm.scs_type_id]

light_lblinker: Telemetry = next(filter(lambda t: t.id == 79, telemetries))
light_lblinker_size: int = TYPE_SIZE_BY_ID[light_lblinker.scs_type_id]

light_rblinker: Telemetry = next(filter(lambda t: t.id == 80, telemetries))
light_rblinker_size: int = TYPE_SIZE_BY_ID[light_rblinker.scs_type_id]

speed_offset, speed_initialized_offset, _ = offsets_of(telemetries, speed)
rpm_offset, rpm_initialized_offset, _ = offsets_of(telemetries, rpm)
light_lblinker_offset, light_lblinker_initialized_offset, _ = offsets_of(telemetries, light_lblinker)
light_rblinker_offset, light_rblinker_initialized_offset, _ = offsets_of(telemetries, light_rblinker)

game = socket(AddressFamily.AF_INET, SocketKind.SOCK_STREAM, IPPROTO_TCP)
game.connect(ENDPOINT)
while True:
    try:
        recv: bytes = game.recv(STORE_SIZE)
        if not recv:
            break
        data_speed, speed_initialized = unpack('f', recv[speed_offset:speed_offset + speed_size])[0], recv[speed_initialized_offset] > 0
        data_rpm, rpm_initialized = unpack('f', recv[rpm_offset:rpm_offset + rpm_size])[0], recv[rpm_initialized_offset] > 0
        data_light_lblinker, light_lblinker_initialized = recv[light_lblinker_offset] > 0, recv[light_lblinker_initialized_offset] > 0
        data_light_rblinker, light_rblinker_initialized = recv[light_rblinker_offset] > 0, recv[light_rblinker_initialized_offset] > 0

        speed_str: str = f'{data_speed:02.02f} m/s' if speed_initialized else '?'
        rpm_str: str = f'{data_rpm:04.0f} rpm' if rpm_initialized else '?'
        lblinker_str: str = f'{'<' if data_light_lblinker else '-'}' if light_lblinker_initialized else '?'
        rblinker_str: str = f'{'>' if data_light_rblinker else '-'}' if light_rblinker_initialized else '?'

        print(f'{speed_str} | {rpm_str} | {lblinker_str}{rblinker_str}')

    except KeyboardInterrupt:
        break

game.shutdown(SHUT_RDWR)
game.close()
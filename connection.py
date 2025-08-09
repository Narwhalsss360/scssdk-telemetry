from __future__ import annotations
from enum import Enum
from socket import socket, AddressFamily, SocketKind, IPPROTO_TCP
from dataclasses import dataclass
from nstreamcom import Collector, encode_with_size
from scssdk_dataclasses import id_of_type
from truckconnect import Version, VERSION
from telemetry_id import TelemetryID
from time import sleep, time
from value_storage import value_storage_from_bytes


@dataclass
class TrailerIndexOrCount:
    is_count: bool
    index_or_count: int

    @staticmethod
    def from_int(as_int: int) -> TrailerIndexOrCount:
        if not (0 <= as_int <= 255):
            raise ValueError("TrailerIndexOrCount integer must fit within unsigned 8-bit width")
        return TrailerIndexOrCount(as_int & 1 > 0, as_int >> 1)

    def __int__(self) -> int:
        return int(self.is_count) | (self.index_or_count << 1)


class RequestType(Enum):
    NoRequest = 0
    TelemetryID = 1
    RegisterDataDefinition = 2
    DefinedData = 3
    UnregisterDataDefinition = 4
    Version = 5
    ErrorResponse = 6


class CommunicationResult(Enum):
    Success = 0
    GenericSocketError = 1
    AlreadyConnected = 2
    NotConnected = 3
    Disconnected = 4
    Incomplete = 5
    CollectorError = 6
    NoPendingRequest = 7
    InvalidTelemetry = 8
    InvalidTrailerIndex = 9
    OtherRequestPending = 10
    OtherTelemetryIDPending = 11
    OtherTrailerIndexRequestPending = 12
    ReceivedOtherResponse = 13
    ReceivedOtherTelemetry = 14
    ReceivedOtherTrailerIndex = 15
    DeserializationFailure = 16
    TrailerIndexOutOfBounds = 17
    TrailerCountOutOfBounds = 18
    TrailerIndexOrCountWasCount = 19
    NullArgument = 20
    Empty = 21
    AlreadyRegistered = 22
    OtherDefinedDataPending = 23
    NotRegistered = 24
    ArrangeError = 25
    BadlyFormed = 26
    UnknownData = 27


class CommunicationError(Exception):
    def __init__(self, communication_result: CommunicationResult, *args: object) -> None:
        super().__init__(f"CommunicationResult:{communication_result}", *args)
        self.communication_result = communication_result


class Connection:
    PORT: int = 52878
    TELEMETRY_DATA_START: int = 1 + 2
    DATA_DEFINITION_DATA_START: int = 1 + 1
    DEFINED_DATA_DATA_START: int = 1 + 1

    def __init__(self, ip: str = "127.0.0.1") -> None:
        self.addr: tuple[str, int] = ip, Connection.PORT
        self._socket: socket = socket(AddressFamily.AF_INET, SocketKind.SOCK_STREAM, IPPROTO_TCP)
        self._connected: bool = False
        self.pending_request: RequestType = RequestType.NoRequest
        self.pending_telemetry_id: TelemetryID = TelemetryID.Invalid
        self.pending_trailer_index_or_count: TrailerIndexOrCount = TrailerIndexOrCount(False, 0)
        self.collector: Collector = Collector()

    def connect(self) -> None:
        if self._connected:
            raise CommunicationError(CommunicationResult.AlreadyConnected)
        self._socket.connect(self.addr)
        self._connected = True

    @property
    def connected(self):
        return self._connected

    def receive_one(self) -> None:
        self._ensure_connected()
        if self.pending_request == RequestType.NoRequest:
            raise CommunicationError(CommunicationResult.NoPendingRequest)
        if not (recv := self._socket.recv(1)):
            raise CommunicationError(CommunicationResult.Disconnected)
        self.collector.collect(recv[0])

    def receive_all(self) -> None:
        self._ensure_connected()
        if self.pending_request == RequestType.NoRequest:
            raise CommunicationError(CommunicationResult.NoPendingRequest)

        if self.collector.data_ready:
            self.collector.reset()
        while not self.collector.error_state and not self.collector.data_ready:
            if not (recv := self._socket.recv(1)):
                raise CommunicationError(CommunicationResult.Disconnected)
            self.collector.collect(recv[0])

    def get_version(self) -> Version:
        self._ensure_connected()
        self._ensure_pending_request(RequestType.NoRequest)

        self.pending_request = RequestType.Version
        self._socket.send(encode_with_size([RequestType.Version.value]))
        self.receive_all()
        self.pending_request = RequestType.NoRequest

        if self.collector.next_size == 0:
            raise CommunicationError(CommunicationResult.UnknownData)

        if self.collector.bytearray[0] == RequestType.ErrorResponse.value:
            raise CommunicationError(CommunicationResult(self.collector.bytearray[1]))

        if self.collector.bytearray[0] != RequestType.Version.value:
            raise CommunicationError(CommunicationResult.ReceivedOtherResponse)

        if self.collector.next_size != 1 + 4:
            raise CommunicationError(CommunicationResult.UnknownData)

        return Version.from_int(int.from_bytes(self.collector.bytearray[1:4], "little"))

    def send_request_for(self, telemetry_id: TelemetryID, trailer_index_or_count: TrailerIndexOrCount | None = None) -> None:
        self._ensure_connected()
        self._ensure_pending_request(RequestType.NoRequest)
        trailer_index_or_count = trailer_index_or_count or TrailerIndexOrCount(False, 0)
        self._socket.send(encode_with_size([
            RequestType.TelemetryID.value,
            telemetry_id.value,
            int(trailer_index_or_count)
        ]))
        self.pending_request = RequestType.TelemetryID
        self.pending_telemetry_id = telemetry_id
        self.pending_trailer_index_or_count = trailer_index_or_count

    def receive_for_request(self, telemetry_id: TelemetryID, trailer_index_or_count: TrailerIndexOrCount | None = None) -> None:
        self._ensure_connected()
        self._ensure_pending_request(RequestType.TelemetryID)
        trailer_index_or_count = trailer_index_or_count or TrailerIndexOrCount(False, 0)

        if self.pending_telemetry_id != telemetry_id:
            raise CommunicationError(CommunicationResult.OtherTelemetryIDPending)
        if self.pending_trailer_index_or_count != trailer_index_or_count:
            raise CommunicationError(CommunicationResult.OtherTrailerIndexRequestPending)

        self.receive_all()
        self.pending_request = RequestType.NoRequest
        if self.collector.next_size < 2:
            raise CommunicationError(CommunicationResult.UnknownData)

        if self.collector.bytearray[0] == RequestType.ErrorResponse.value:
            raise CommunicationError(CommunicationResult(self.collector.bytearray[1]))

        if self.collector.bytearray[0] != RequestType.TelemetryID.value:
            raise CommunicationError(CommunicationResult.ReceivedOtherResponse)

        if self.collector.bytearray[1] != telemetry_id.value:
            raise CommunicationError(CommunicationResult.ReceivedOtherTelemetry)

        if TrailerIndexOrCount.from_int(self.collector.bytearray[2]) != trailer_index_or_count:
            raise CommunicationError(CommunicationResult.ReceivedOtherTrailerIndex)

    def disconnect(self) -> None:
        if not self._connected:
            raise CommunicationError(CommunicationResult.NotConnected)
        self._socket.close()
        self._connected = False

    def _ensure_connected(self) -> None:
        if not self.connected:
            raise CommunicationError(CommunicationResult.NotConnected)

    def _ensure_pending_request(self, request_type: RequestType) -> None:
        if self.pending_request != request_type:
            raise CommunicationError(CommunicationResult.OtherRequestPending)


def main() -> None:
    connection: Connection = Connection()
    connection.connect()
    print(f"Version: {VERSION}, Server Version: {connection.get_version()}")

    start_time: float = time()
    duration: float = 5 * 60
    while time() - start_time < duration:
        connection.send_request_for(TelemetryID.ChannelPaused)
        connection.receive_for_request(TelemetryID.ChannelPaused)
        (_, paused), _ = value_storage_from_bytes(
            id_of_type("bool"),
            connection.collector.bytearray,
            Connection.TELEMETRY_DATA_START
        )
        if paused:
            print("<paused>")
        else:
            connection.send_request_for(TelemetryID.ChannelGameTime)
            connection.receive_for_request(TelemetryID.ChannelGameTime)
            (initialized, game_time), _ = value_storage_from_bytes(
                id_of_type("u32"),
                connection.collector.bytearray,
                Connection.TELEMETRY_DATA_START
            )
            print(game_time if initialized else ".")
        sleep(0.1)

    connection.disconnect()


if __name__ == "__main__":
    main()

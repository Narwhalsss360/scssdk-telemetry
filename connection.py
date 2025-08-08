from __future__ import annotations
from enum import Enum
from socket import socket, AddressFamily, SocketKind, IPPROTO_TCP
from dataclasses import dataclass
from nstreamcom import Collector, encode_with_size
from truckconnect import INVALID_TELEMETRY_ID, Version, VERSION


@dataclass
class TrailerIndexOrCount:
    is_count: bool
    index_or_count: int


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
    PORT = 52878

    def __init__(self, ip: str = "127.0.0.1") -> None:
        self.addr: tuple[str, int] = ip, Connection.PORT
        self._socket: socket = socket(AddressFamily.AF_INET, SocketKind.SOCK_STREAM, IPPROTO_TCP)
        self._connected: bool = False
        self.pending_request: RequestType = RequestType.NoRequest
        self.pending_telemetry_id: int = INVALID_TELEMETRY_ID
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
        while not self.collector.error_state and not self.collector.data_ready:
            if not (recv := self._socket.recv(1)):
                raise CommunicationError(CommunicationResult.Disconnected)
            self.collector.collect(recv[0])

    def get_version(self) -> Version:
        self._ensure_connected()
        self._ensure_pendinng_request(RequestType.NoRequest)

        self.pending_request = RequestType.Version
        self._socket.send(encode_with_size([RequestType.Version.value]))
        self.receive_all()
        self.pending_request = RequestType.NoRequest

        if self.collector.next_size == 0:
            raise CommunicationError(CommunicationResult.UnknownData)

        if self.collector.bytearray[0] == RequestType.ErrorResponse:
            raise CommunicationError(CommunicationResult(self.collector.bytearray[1]))

        if self.collector.bytearray[0] == RequestType.Version:
            raise CommunicationError(CommunicationResult.ReceivedOtherResponse)

        if self.collector.next_size != 1 + 4:
            raise CommunicationError(CommunicationResult.UnknownData)

        return Version.from_int(int.from_bytes(self.collector.bytearray[1:4], "little"))

    def disconnect(self) -> None:
        if not self._connected:
            raise CommunicationError(CommunicationResult.NotConnected)
        self._socket.close()
        self._connected = False

    def _ensure_connected(self) -> None:
        if not self.connected:
            raise CommunicationError(CommunicationResult.NotConnected)

    def _ensure_pendinng_request(self, request_type: RequestType) -> None:
        if self.pending_request != request_type:
            raise CommunicationError(CommunicationResult.OtherRequestPending)


def main() -> None:
    connection: Connection = Connection()
    connection.connect()
    print(VERSION)
    print(str(connection.get_version()))
    connection.disconnect()


if __name__ == "__main__":
    main()

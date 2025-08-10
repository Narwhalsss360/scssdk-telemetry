from __future__ import annotations
from dataclasses import dataclass, field
from scssdk_dataclasses import SCS_TELEMETRY_trailers_count
from value_storage import (
    SCSValueFVector,
    SCSValueFPlacement,
    SCSValueDPlacement,
    value_storage_from_bytes,
    SCSValueType,
    value_storage_guard,
    value_array_storage_guard,
    value_vector_storage_guard
)


@dataclass
class GameplayPlayerUseTrainInfo:
    latest: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    pay_amount: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    source_name: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    target_name: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    source_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    target_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[GameplayPlayerUseTrainInfo, int]:
        gameplay_player_use_train_info: GameplayPlayerUseTrainInfo = GameplayPlayerUseTrainInfo()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_player_use_train_info.latest = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_s64, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_player_use_train_info.pay_amount = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        gameplay_player_use_train_info.source_name = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        gameplay_player_use_train_info.target_name = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        gameplay_player_use_train_info.source_id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        gameplay_player_use_train_info.target_id = storage
        total_read += read

        return gameplay_player_use_train_info, total_read


@dataclass
class GameplayPlayerUseFerryInfo:
    latest: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    pay_amount: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    source_name: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    target_name: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    source_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    target_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[GameplayPlayerUseFerryInfo, int]:
        gameplay_player_use_ferry_info: GameplayPlayerUseFerryInfo = GameplayPlayerUseFerryInfo()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_player_use_ferry_info.latest = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_s64, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_player_use_ferry_info.pay_amount = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        gameplay_player_use_ferry_info.source_name = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        gameplay_player_use_ferry_info.target_name = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        gameplay_player_use_ferry_info.source_id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        gameplay_player_use_ferry_info.target_id = storage
        total_read += read

        return gameplay_player_use_ferry_info, total_read


@dataclass
class GameplayPlayerTollgatePaidInfo:
    latest: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    pay_amount: tuple[bool, int] = field(default_factory=lambda: (False, int()))

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[GameplayPlayerTollgatePaidInfo, int]:
        gameplay_player_tollgate_paid_info: GameplayPlayerTollgatePaidInfo = GameplayPlayerTollgatePaidInfo()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_player_tollgate_paid_info.latest = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_s64, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_player_tollgate_paid_info.pay_amount = storage
        total_read += read

        return gameplay_player_tollgate_paid_info, total_read


@dataclass
class GameplayPlayerFinedInfo:
    latest: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    fine_offence: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    fine_amount: tuple[bool, int] = field(default_factory=lambda: (False, int()))

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[GameplayPlayerFinedInfo, int]:
        gameplay_player_fined_info: GameplayPlayerFinedInfo = GameplayPlayerFinedInfo()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_player_fined_info.latest = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        gameplay_player_fined_info.fine_offence = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_s64, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_player_fined_info.fine_amount = storage
        total_read += read

        return gameplay_player_fined_info, total_read


@dataclass
class GameplayJobDeliveredInfo:
    latest: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    revenue: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    earned_xp: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    cargo_damage: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    distance_km: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    delivery_time: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    auto_park_used: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    auto_load_used: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[GameplayJobDeliveredInfo, int]:
        gameplay_job_delivered_info: GameplayJobDeliveredInfo = GameplayJobDeliveredInfo()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_job_delivered_info.latest = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_s64, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_job_delivered_info.revenue = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_s32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_job_delivered_info.earned_xp = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        gameplay_job_delivered_info.cargo_damage = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        gameplay_job_delivered_info.distance_km = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_job_delivered_info.delivery_time = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        gameplay_job_delivered_info.auto_park_used = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        gameplay_job_delivered_info.auto_load_used = storage
        total_read += read

        return gameplay_job_delivered_info, total_read


@dataclass
class GameplayJobCancelledInfo:
    latest: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    cancel_penalty: tuple[bool, int] = field(default_factory=lambda: (False, int()))

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[GameplayJobCancelledInfo, int]:
        gameplay_job_cancelled_info: GameplayJobCancelledInfo = GameplayJobCancelledInfo()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_job_cancelled_info.latest = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_s64, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        gameplay_job_cancelled_info.cancel_penalty = storage
        total_read += read

        return gameplay_job_cancelled_info, total_read


@dataclass
class ConfigurationJobInfo:
    latest: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    cargo_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    cargo: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    cargo_mass: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    destination_city_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    cargo_unit_mass: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    cargo_unit_count: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    destination_city: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    source_city_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    source_city: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    destination_company_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    destination_company: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    source_company_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    source_company: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    income: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    delivery_time: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    is_cargo_loaded: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    job_market: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    special_job: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    planned_distance_km: tuple[bool, int] = field(default_factory=lambda: (False, int()))

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[ConfigurationJobInfo, int]:
        configuration_job_info: ConfigurationJobInfo = ConfigurationJobInfo()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_job_info.latest = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_job_info.cargo_id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_job_info.cargo = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        configuration_job_info.cargo_mass = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_job_info.destination_city_id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        configuration_job_info.cargo_unit_mass = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_job_info.cargo_unit_count = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_job_info.destination_city = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_job_info.source_city_id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_job_info.source_city = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_job_info.destination_company_id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_job_info.destination_company = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_job_info.source_company_id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_job_info.source_company = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u64, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_job_info.income = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_job_info.delivery_time = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        configuration_job_info.is_cargo_loaded = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_job_info.job_market = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        configuration_job_info.special_job = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_job_info.planned_distance_km = storage
        total_read += read

        return configuration_job_info, total_read


@dataclass
class ConfigurationTrailerInfo:
    latest: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    cargo_accessory_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    hook_position: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    brand_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    brand: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    name: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    chain_type: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    body_type: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    license_plate: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    license_plate_country: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    license_plate_country_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    wheel_count: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    wheel_position: list[SCSValueFVector] = field(default_factory=lambda: [])
    wheel_steerable: list[bool] = field(default_factory=lambda: [])
    wheel_simulated: list[bool] = field(default_factory=lambda: [])
    wheel_radius: list[float] = field(default_factory=lambda: [])
    wheel_powered: list[bool] = field(default_factory=lambda: [])
    wheel_liftable: list[bool] = field(default_factory=lambda: [])

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[ConfigurationTrailerInfo, int]:
        configuration_trailer_info: ConfigurationTrailerInfo = ConfigurationTrailerInfo()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_trailer_info.latest = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_trailer_info.id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_trailer_info.cargo_accessory_id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        configuration_trailer_info.hook_position = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_trailer_info.brand_id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_trailer_info.brand = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_trailer_info.name = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_trailer_info.chain_type = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_trailer_info.body_type = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_trailer_info.license_plate = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_trailer_info.license_plate_country = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_trailer_info.license_plate_country_id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_trailer_info.wheel_count = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, SCSValueFVector())
        configuration_trailer_info.wheel_position = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, bool())
        configuration_trailer_info.wheel_steerable = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, bool())
        configuration_trailer_info.wheel_simulated = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, float())
        configuration_trailer_info.wheel_radius = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, bool())
        configuration_trailer_info.wheel_powered = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, bool())
        configuration_trailer_info.wheel_liftable = storage
        total_read += read

        return configuration_trailer_info, total_read


@dataclass
class ConfigurationTruckInfo:
    latest: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    brand_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    brand: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    name: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    fuel_capacity: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    fuel_warning_factor: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    adblue_capacity: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    adblue_warning_factor: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    air_pressure_warning: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    air_pressure_emergency: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    oil_pressure_warning: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    water_temperature_warning: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    battery_voltage_warning: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    rpm_limit: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    forward_gear_count: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    reverse_gear_count: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    differential_ratio: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    retarder_step_count: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    cabin_position: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    forward_ratio: list[float] = field(default_factory=lambda: [])
    reverse_ratio: list[float] = field(default_factory=lambda: [])
    head_position: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    hook_position: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    license_plate: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    license_plate_country: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    license_plate_country_id: tuple[bool, str] = field(default_factory=lambda: (False, str()))
    wheel_count: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    wheel_position: list[SCSValueFVector] = field(default_factory=lambda: [])
    wheel_steerable: list[bool] = field(default_factory=lambda: [])
    wheel_simulated: list[bool] = field(default_factory=lambda: [])
    wheel_radius: list[float] = field(default_factory=lambda: [])
    wheel_powered: list[bool] = field(default_factory=lambda: [])
    wheel_liftable: list[bool] = field(default_factory=lambda: [])

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[ConfigurationTruckInfo, int]:
        configuration_truck_info: ConfigurationTruckInfo = ConfigurationTruckInfo()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_truck_info.latest = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_truck_info.brand_id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_truck_info.brand = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_truck_info.id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_truck_info.name = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        configuration_truck_info.fuel_capacity = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        configuration_truck_info.fuel_warning_factor = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        configuration_truck_info.adblue_capacity = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        configuration_truck_info.adblue_warning_factor = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        configuration_truck_info.air_pressure_warning = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        configuration_truck_info.air_pressure_emergency = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        configuration_truck_info.oil_pressure_warning = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        configuration_truck_info.water_temperature_warning = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        configuration_truck_info.battery_voltage_warning = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        configuration_truck_info.rpm_limit = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_truck_info.forward_gear_count = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_truck_info.reverse_gear_count = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        configuration_truck_info.differential_ratio = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_truck_info.retarder_step_count = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        configuration_truck_info.cabin_position = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, float())
        configuration_truck_info.forward_ratio = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, float())
        configuration_truck_info.reverse_ratio = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        configuration_truck_info.head_position = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        configuration_truck_info.hook_position = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_truck_info.license_plate = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_truck_info.license_plate_country = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_truck_info.license_plate_country_id = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_truck_info.wheel_count = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, SCSValueFVector())
        configuration_truck_info.wheel_position = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, bool())
        configuration_truck_info.wheel_steerable = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, bool())
        configuration_truck_info.wheel_simulated = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, float())
        configuration_truck_info.wheel_radius = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, bool())
        configuration_truck_info.wheel_powered = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, bool())
        configuration_truck_info.wheel_liftable = storage
        total_read += read

        return configuration_truck_info, total_read


@dataclass
class ConfigurationHshifterInfo:
    latest: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    selector_count: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    slot_gear: list[int] = field(default_factory=lambda: [])
    slot_handle_position: list[int] = field(default_factory=lambda: [])
    slot_selectors: list[int] = field(default_factory=lambda: [])

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[ConfigurationHshifterInfo, int]:
        configuration_hshifter_info: ConfigurationHshifterInfo = ConfigurationHshifterInfo()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_hshifter_info.latest = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_hshifter_info.selector_count = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_s32, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, int())
        configuration_hshifter_info.slot_gear = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, int())
        configuration_hshifter_info.slot_handle_position = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, int())
        configuration_hshifter_info.slot_selectors = storage
        total_read += read

        return configuration_hshifter_info, total_read


@dataclass
class ConfigurationControlsInfo:
    latest: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    shifter_type: tuple[bool, str] = field(default_factory=lambda: (False, str()))

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[ConfigurationControlsInfo, int]:
        configuration_controls_info: ConfigurationControlsInfo = ConfigurationControlsInfo()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_controls_info.latest = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read)
        assert value_storage_guard(storage, str())
        configuration_controls_info.shifter_type = storage
        total_read += read

        return configuration_controls_info, total_read


@dataclass
class ConfigurationSubstancesInfo:
    latest: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    id: list[str] = field(default_factory=lambda: [])

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[ConfigurationSubstancesInfo, int]:
        configuration_substances_info: ConfigurationSubstancesInfo = ConfigurationSubstancesInfo()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        configuration_substances_info.latest = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_string, buffer, offset + total_read, dynamic_size=True)
        assert value_vector_storage_guard(storage, str())
        configuration_substances_info.id = storage
        total_read += read

        return configuration_substances_info, total_read


@dataclass
class Trailer:
    trailer_channel_connected: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    trailer_channel_cargo_damage: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    trailer_channel_world_placement: tuple[bool, SCSValueDPlacement] = field(default_factory=lambda: (False, SCSValueDPlacement()))
    trailer_channel_local_linear_velocity: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    trailer_channel_local_angular_velocity: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    trailer_channel_local_linear_acceleration: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    trailer_channel_local_angular_acceleration: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    trailer_channel_wear_body: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    trailer_channel_wear_chassis: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    trailer_channel_wear_wheels: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    trailer_channel_wheel_susp_deflection: tuple[bool, list[float], int] = field(default_factory=lambda: (False, [float() for _ in range(19)], 0))
    trailer_channel_wheel_on_ground: tuple[bool, list[bool], int] = field(default_factory=lambda: (False, [bool() for _ in range(19)], 0))
    trailer_channel_wheel_substance: tuple[bool, list[int], int] = field(default_factory=lambda: (False, [int() for _ in range(19)], 0))
    trailer_channel_wheel_velocity: tuple[bool, list[float], int] = field(default_factory=lambda: (False, [float() for _ in range(19)], 0))
    trailer_channel_wheel_steering: tuple[bool, list[float], int] = field(default_factory=lambda: (False, [float() for _ in range(19)], 0))
    trailer_channel_wheel_rotation: tuple[bool, list[float], int] = field(default_factory=lambda: (False, [float() for _ in range(19)], 0))
    trailer_channel_wheel_lift: tuple[bool, list[float], int] = field(default_factory=lambda: (False, [float() for _ in range(19)], 0))
    trailer_channel_wheel_lift_offset: tuple[bool, list[float], int] = field(default_factory=lambda: (False, [float() for _ in range(19)], 0))

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[Trailer, int]:
        trailer: Trailer = Trailer()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        trailer.trailer_channel_connected = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        trailer.trailer_channel_cargo_damage = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_dplacement, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueDPlacement())
        trailer.trailer_channel_world_placement = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        trailer.trailer_channel_local_linear_velocity = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        trailer.trailer_channel_local_angular_velocity = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        trailer.trailer_channel_local_linear_acceleration = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        trailer.trailer_channel_local_angular_acceleration = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        trailer.trailer_channel_wear_body = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        trailer.trailer_channel_wear_chassis = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        trailer.trailer_channel_wear_wheels = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, array_size=19)
        assert value_array_storage_guard(storage, float())
        trailer.trailer_channel_wheel_susp_deflection = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read, array_size=19)
        assert value_array_storage_guard(storage, bool())
        trailer.trailer_channel_wheel_on_ground = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read, array_size=19)
        assert value_array_storage_guard(storage, int())
        trailer.trailer_channel_wheel_substance = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, array_size=19)
        assert value_array_storage_guard(storage, float())
        trailer.trailer_channel_wheel_velocity = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, array_size=19)
        assert value_array_storage_guard(storage, float())
        trailer.trailer_channel_wheel_steering = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, array_size=19)
        assert value_array_storage_guard(storage, float())
        trailer.trailer_channel_wheel_rotation = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, array_size=19)
        assert value_array_storage_guard(storage, float())
        trailer.trailer_channel_wheel_lift = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, array_size=19)
        assert value_array_storage_guard(storage, float())
        trailer.trailer_channel_wheel_lift_offset = storage
        total_read += read

        return trailer, total_read


@dataclass
class Truck:
    truck_channel_world_placement: tuple[bool, SCSValueDPlacement] = field(default_factory=lambda: (False, SCSValueDPlacement()))
    truck_channel_local_linear_velocity: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    truck_channel_local_angular_velocity: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    truck_channel_local_linear_acceleration: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    truck_channel_local_angular_acceleration: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    truck_channel_cabin_offset: tuple[bool, SCSValueFPlacement] = field(default_factory=lambda: (False, SCSValueFPlacement()))
    truck_channel_cabin_angular_velocity: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    truck_channel_cabin_angular_acceleration: tuple[bool, SCSValueFVector] = field(default_factory=lambda: (False, SCSValueFVector()))
    truck_channel_head_offset: tuple[bool, SCSValueFPlacement] = field(default_factory=lambda: (False, SCSValueFPlacement()))
    truck_channel_speed: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_engine_rpm: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_engine_gear: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    truck_channel_displayed_gear: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    truck_channel_input_steering: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_input_throttle: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_input_brake: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_input_clutch: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_effective_steering: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_effective_throttle: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_effective_brake: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_effective_clutch: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_cruise_control: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_hshifter_slot: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    truck_channel_hshifter_selector: tuple[bool, list[bool], int] = field(default_factory=lambda: (False, [bool() for _ in range(2)], 0))
    truck_channel_parking_brake: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_motor_brake: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_retarder_level: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    truck_channel_brake_air_pressure: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_brake_air_pressure_warning: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_brake_air_pressure_emergency: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_brake_temperature: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_fuel: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_fuel_warning: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_fuel_average_consumption: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_fuel_range: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_adblue: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_adblue_warning: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_oil_pressure: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_oil_pressure_warning: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_oil_temperature: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_water_temperature: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_water_temperature_warning: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_battery_voltage: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_battery_voltage_warning: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_electric_enabled: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_engine_enabled: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_lblinker: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_rblinker: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_hazard_warning: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_light_lblinker: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_light_rblinker: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_light_parking: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_light_low_beam: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_light_high_beam: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_light_aux_front: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    truck_channel_light_aux_roof: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    truck_channel_light_beacon: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_light_brake: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_light_reverse: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_wipers: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_dashboard_backlight: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_differential_lock: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_lift_axle: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_lift_axle_indicator: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_trailer_lift_axle: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_trailer_lift_axle_indicator: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    truck_channel_wear_engine: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_wear_transmission: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_wear_cabin: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_wear_chassis: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_wear_wheels: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_odometer: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_navigation_distance: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_navigation_time: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_navigation_speed_limit: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    truck_channel_wheel_susp_deflection: tuple[bool, list[float], int] = field(default_factory=lambda: (False, [float() for _ in range(14)], 0))
    truck_channel_wheel_on_ground: tuple[bool, list[bool], int] = field(default_factory=lambda: (False, [bool() for _ in range(14)], 0))
    truck_channel_wheel_substance: tuple[bool, list[int], int] = field(default_factory=lambda: (False, [int() for _ in range(14)], 0))
    truck_channel_wheel_velocity: tuple[bool, list[float], int] = field(default_factory=lambda: (False, [float() for _ in range(14)], 0))
    truck_channel_wheel_steering: tuple[bool, list[float], int] = field(default_factory=lambda: (False, [float() for _ in range(14)], 0))
    truck_channel_wheel_rotation: tuple[bool, list[float], int] = field(default_factory=lambda: (False, [float() for _ in range(14)], 0))
    truck_channel_wheel_lift: tuple[bool, list[float], int] = field(default_factory=lambda: (False, [float() for _ in range(14)], 0))
    truck_channel_wheel_lift_offset: tuple[bool, list[float], int] = field(default_factory=lambda: (False, [float() for _ in range(14)], 0))

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[Truck, int]:
        truck: Truck = Truck()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_dplacement, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueDPlacement())
        truck.truck_channel_world_placement = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        truck.truck_channel_local_linear_velocity = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        truck.truck_channel_local_angular_velocity = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        truck.truck_channel_local_linear_acceleration = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        truck.truck_channel_local_angular_acceleration = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fplacement, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFPlacement())
        truck.truck_channel_cabin_offset = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        truck.truck_channel_cabin_angular_velocity = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fvector, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFVector())
        truck.truck_channel_cabin_angular_acceleration = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_fplacement, buffer, offset + total_read)
        assert value_storage_guard(storage, SCSValueFPlacement())
        truck.truck_channel_head_offset = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_speed = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_engine_rpm = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_s32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        truck.truck_channel_engine_gear = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_s32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        truck.truck_channel_displayed_gear = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_input_steering = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_input_throttle = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_input_brake = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_input_clutch = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_effective_steering = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_effective_throttle = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_effective_brake = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_effective_clutch = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_cruise_control = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        truck.truck_channel_hshifter_slot = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read, array_size=2)
        assert value_array_storage_guard(storage, bool())
        truck.truck_channel_hshifter_selector = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_parking_brake = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_motor_brake = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        truck.truck_channel_retarder_level = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_brake_air_pressure = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_brake_air_pressure_warning = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_brake_air_pressure_emergency = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_brake_temperature = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_fuel = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_fuel_warning = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_fuel_average_consumption = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_fuel_range = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_adblue = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_adblue_warning = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_oil_pressure = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_oil_pressure_warning = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_oil_temperature = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_water_temperature = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_water_temperature_warning = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_battery_voltage = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_battery_voltage_warning = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_electric_enabled = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_engine_enabled = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_lblinker = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_rblinker = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_hazard_warning = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_light_lblinker = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_light_rblinker = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_light_parking = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_light_low_beam = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_light_high_beam = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        truck.truck_channel_light_aux_front = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        truck.truck_channel_light_aux_roof = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_light_beacon = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_light_brake = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_light_reverse = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_wipers = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_dashboard_backlight = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_differential_lock = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_lift_axle = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_lift_axle_indicator = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_trailer_lift_axle = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        truck.truck_channel_trailer_lift_axle_indicator = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_wear_engine = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_wear_transmission = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_wear_cabin = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_wear_chassis = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_wear_wheels = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_odometer = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_navigation_distance = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_navigation_time = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        truck.truck_channel_navigation_speed_limit = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, array_size=14)
        assert value_array_storage_guard(storage, float())
        truck.truck_channel_wheel_susp_deflection = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read, array_size=14)
        assert value_array_storage_guard(storage, bool())
        truck.truck_channel_wheel_on_ground = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read, array_size=14)
        assert value_array_storage_guard(storage, int())
        truck.truck_channel_wheel_substance = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, array_size=14)
        assert value_array_storage_guard(storage, float())
        truck.truck_channel_wheel_velocity = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, array_size=14)
        assert value_array_storage_guard(storage, float())
        truck.truck_channel_wheel_steering = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, array_size=14)
        assert value_array_storage_guard(storage, float())
        truck.truck_channel_wheel_rotation = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, array_size=14)
        assert value_array_storage_guard(storage, float())
        truck.truck_channel_wheel_lift = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read, array_size=14)
        assert value_array_storage_guard(storage, float())
        truck.truck_channel_wheel_lift_offset = storage
        total_read += read

        return truck, total_read


@dataclass
class General:
    channel_paused: tuple[bool, bool] = field(default_factory=lambda: (False, bool()))
    channel_local_scale: tuple[bool, float] = field(default_factory=lambda: (False, float()))
    channel_game_time: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    channel_multiplayer_time_offset: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    channel_next_rest_stop: tuple[bool, int] = field(default_factory=lambda: (False, int()))
    job_channel_cargo_damage: tuple[bool, float] = field(default_factory=lambda: (False, float()))

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[General, int]:
        general: General = General()
        total_read: int = 0
        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_bool, buffer, offset + total_read)
        assert value_storage_guard(storage, bool())
        general.channel_paused = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        general.channel_local_scale = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_u32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        general.channel_game_time = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_s32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        general.channel_multiplayer_time_offset = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_s32, buffer, offset + total_read)
        assert value_storage_guard(storage, int())
        general.channel_next_rest_stop = storage
        total_read += read

        storage, read = value_storage_from_bytes(SCSValueType.SCS_VALUE_TYPE_float, buffer, offset + total_read)
        assert value_storage_guard(storage, float())
        general.job_channel_cargo_damage = storage
        total_read += read

        return general, total_read


@dataclass
class Channels:
    general: General = field(default_factory=General)
    truck: Truck = field(default_factory=Truck)
    trailer: list[Trailer] = field(default_factory=lambda: [])

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[Channels, int]:
        channels: Channels = Channels()
        total_read: int = 0
        deserialized, read = General.from_bytes(buffer, offset + total_read)
        channels.general = deserialized
        total_read += read

        deserialized, read = Truck.from_bytes(buffer, offset + total_read)
        channels.truck = deserialized
        total_read += read

        for _ in range(SCS_TELEMETRY_trailers_count):
            deserialized, read = Trailer.from_bytes(buffer, offset + total_read)
            channels.trailer.append(deserialized)
            total_read += read

        return channels, total_read


@dataclass
class Gameplay:
    gameplay_job_cancelled_info: GameplayJobCancelledInfo = field(default_factory=GameplayJobCancelledInfo)
    gameplay_job_delivered_info: GameplayJobDeliveredInfo = field(default_factory=GameplayJobDeliveredInfo)
    gameplay_player_fined_info: GameplayPlayerFinedInfo = field(default_factory=GameplayPlayerFinedInfo)
    gameplay_player_tollgate_paid_info: GameplayPlayerTollgatePaidInfo = field(default_factory=GameplayPlayerTollgatePaidInfo)
    gameplay_player_use_ferry_info: GameplayPlayerUseFerryInfo = field(default_factory=GameplayPlayerUseFerryInfo)
    gameplay_player_use_train_info: GameplayPlayerUseTrainInfo = field(default_factory=GameplayPlayerUseTrainInfo)

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[Gameplay, int]:
        gameplay: Gameplay = Gameplay()
        total_read: int = 0
        deserialized, read = GameplayJobCancelledInfo.from_bytes(buffer, offset + total_read)
        gameplay.gameplay_job_cancelled_info = deserialized
        total_read += read

        deserialized, read = GameplayJobDeliveredInfo.from_bytes(buffer, offset + total_read)
        gameplay.gameplay_job_delivered_info = deserialized
        total_read += read

        deserialized, read = GameplayPlayerFinedInfo.from_bytes(buffer, offset + total_read)
        gameplay.gameplay_player_fined_info = deserialized
        total_read += read

        deserialized, read = GameplayPlayerTollgatePaidInfo.from_bytes(buffer, offset + total_read)
        gameplay.gameplay_player_tollgate_paid_info = deserialized
        total_read += read

        deserialized, read = GameplayPlayerUseFerryInfo.from_bytes(buffer, offset + total_read)
        gameplay.gameplay_player_use_ferry_info = deserialized
        total_read += read

        deserialized, read = GameplayPlayerUseTrainInfo.from_bytes(buffer, offset + total_read)
        gameplay.gameplay_player_use_train_info = deserialized
        total_read += read

        return gameplay, total_read


@dataclass
class Configuration:
    configuration_substances_info: ConfigurationSubstancesInfo = field(default_factory=ConfigurationSubstancesInfo)
    configuration_controls_info: ConfigurationControlsInfo = field(default_factory=ConfigurationControlsInfo)
    configuration_hshifter_info: ConfigurationHshifterInfo = field(default_factory=ConfigurationHshifterInfo)
    configuration_truck_info: ConfigurationTruckInfo = field(default_factory=ConfigurationTruckInfo)
    configuration_trailer_info: list[ConfigurationTrailerInfo] = field(default_factory=lambda: [])
    configuration_job_info: ConfigurationJobInfo = field(default_factory=ConfigurationJobInfo)

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[Configuration, int]:
        configuration: Configuration = Configuration()
        total_read: int = 0
        deserialized, read = ConfigurationSubstancesInfo.from_bytes(buffer, offset + total_read)
        configuration.configuration_substances_info = deserialized
        total_read += read

        deserialized, read = ConfigurationControlsInfo.from_bytes(buffer, offset + total_read)
        configuration.configuration_controls_info = deserialized
        total_read += read

        deserialized, read = ConfigurationHshifterInfo.from_bytes(buffer, offset + total_read)
        configuration.configuration_hshifter_info = deserialized
        total_read += read

        deserialized, read = ConfigurationTruckInfo.from_bytes(buffer, offset + total_read)
        configuration.configuration_truck_info = deserialized
        total_read += read

        for _ in range(SCS_TELEMETRY_trailers_count):
            deserialized, read = ConfigurationTrailerInfo.from_bytes(buffer, offset + total_read)
            configuration.configuration_trailer_info.append(deserialized)
            total_read += read

        deserialized, read = ConfigurationJobInfo.from_bytes(buffer, offset + total_read)
        configuration.configuration_job_info = deserialized
        total_read += read

        return configuration, total_read


@dataclass
class Master:
    configuration: Configuration = field(default_factory=Configuration)
    gameplay: Gameplay = field(default_factory=Gameplay)
    channels: Channels = field(default_factory=Channels)

    @staticmethod
    def from_bytes(buffer, offset: int) -> tuple[Master, int]:
        master: Master = Master()
        total_read: int = 0
        deserialized, read = Configuration.from_bytes(buffer, offset + total_read)
        master.configuration = deserialized
        total_read += read

        deserialized, read = Gameplay.from_bytes(buffer, offset + total_read)
        master.gameplay = deserialized
        total_read += read

        deserialized, read = Channels.from_bytes(buffer, offset + total_read)
        master.channels = deserialized
        total_read += read

        return master, total_read

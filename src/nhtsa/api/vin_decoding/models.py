from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime


class BaseNHTSAResponse(BaseModel):
    """Base model for NHTSA API responses."""
    count: Optional[int] = Field(alias="Count")
    message: Optional[str] = Field(alias="Message")
    search_criteria: Optional[str] = Field(alias="SearchCriteria")


class VinDecodeEntry(BaseModel):
    """Represents a single decoded VIN variable in key-value format."""
    value: Optional[str] = Field(alias="Value")
    value_id: Optional[str] = Field(alias="ValueId")
    variable: str = Field(alias="Variable")
    variable_id: int = Field(alias="VariableId")


class VinDecodeResult(BaseNHTSAResponse):
    """Represents the response structure for Decode VIN (key-value)."""
    results: List[VinDecodeEntry] = Field(alias="Results")


class VinDecodeFlatEntry(BaseModel):
    """Represents a single decoded VIN entry in flat format."""
    abs: Optional[str] = Field(alias="ABS", default=None)
    active_safety_sys_note: Optional[str] = Field(alias="ActiveSafetySysNote", default=None)
    adaptive_cruise_control: Optional[str] = Field(alias="AdaptiveCruiseControl", default=None)
    adaptive_driving_beam: Optional[str] = Field(alias="AdaptiveDrivingBeam", default=None)
    adaptive_headlights: Optional[str] = Field(alias="AdaptiveHeadlights", default=None)
    additional_error_text: Optional[str] = Field(alias="AdditionalErrorText", default=None)
    air_bag_loc_curtain: Optional[str] = Field(alias="AirBagLocCurtain", default=None)
    air_bag_loc_front: Optional[str] = Field(alias="AirBagLocFront", default=None)
    air_bag_loc_knee: Optional[str] = Field(alias="AirBagLocKnee", default=None)
    air_bag_loc_seat_cushion: Optional[str] = Field(alias="AirBagLocSeatCushion", default=None)
    air_bag_loc_side: Optional[str] = Field(alias="AirBagLocSide", default=None)
    auto_reverse_system: Optional[str] = Field(alias="AutoReverseSystem", default=None)
    automatic_pedestrian_alerting_sound: Optional[str] = Field(alias="AutomaticPedestrianAlertingSound", default=None)
    axle_configuration: Optional[str] = Field(alias="AxleConfiguration", default=None)
    axles: Optional[str] = Field(alias="Axles", default=None)
    base_price: Optional[str] = Field(alias="BasePrice", default=None)
    battery_a: Optional[str] = Field(alias="BatteryA", default=None)
    battery_a_to: Optional[str] = Field(alias="BatteryA_to", default=None)
    battery_cells: Optional[str] = Field(alias="BatteryCells", default=None)
    battery_info: Optional[str] = Field(alias="BatteryInfo", default=None)
    battery_k_wh: Optional[str] = Field(alias="BatteryKWh", default=None)
    battery_k_wh_to: Optional[str] = Field(alias="BatteryKWh_to", default=None)
    battery_modules: Optional[str] = Field(alias="BatteryModules", default=None)
    battery_packs: Optional[str] = Field(alias="BatteryPacks", default=None)
    battery_type: Optional[str] = Field(alias="BatteryType", default=None)
    battery_v: Optional[str] = Field(alias="BatteryV", default=None)
    battery_v_to: Optional[str] = Field(alias="BatteryV_to", default=None)
    bed_length_in: Optional[str] = Field(alias="BedLengthIN", default=None)
    bed_type: Optional[str] = Field(alias="BedType", default=None)
    blind_spot_intervention: Optional[str] = Field(alias="BlindSpotIntervention", default=None)
    blind_spot_mon: Optional[str] = Field(alias="BlindSpotMon", default=None)
    body_cab_type: Optional[str] = Field(alias="BodyCabType", default=None)
    body_class: Optional[str] = Field(alias="BodyClass", default=None)
    brake_system_desc: Optional[str] = Field(alias="BrakeSystemDesc", default=None)
    brake_system_type: Optional[str] = Field(alias="BrakeSystemType", default=None)
    bus_floor_config_type: Optional[str] = Field(alias="BusFloorConfigType", default=None)
    bus_length: Optional[str] = Field(alias="BusLength", default=None)
    bus_type: Optional[str] = Field(alias="BusType", default=None)
    can_aacn: Optional[str] = Field(alias="CAN_AACN", default=None)
    cib: Optional[str] = Field(alias="CIB", default=None)
    cash_for_clunkers: Optional[str] = Field(alias="CashForClunkers", default=None)
    charger_level: Optional[str] = Field(alias="ChargerLevel", default=None)
    charger_power_kw: Optional[str] = Field(alias="ChargerPowerKW", default=None)
    combined_braking_system: Optional[str] = Field(alias="CombinedBrakingSystem", default=None)
    cooling_type: Optional[str] = Field(alias="CoolingType", default=None)
    curb_weight_lb: Optional[str] = Field(alias="CurbWeightLB", default=None)
    custom_motorcycle_type: Optional[str] = Field(alias="CustomMotorcycleType", default=None)
    daytime_running_light: Optional[str] = Field(alias="DaytimeRunningLight", default=None)
    destination_market: Optional[str] = Field(alias="DestinationMarket", default=None)
    displacement_cc: Optional[str] = Field(alias="DisplacementCC", default=None)
    displacement_ci: Optional[str] = Field(alias="DisplacementCI", default=None)
    displacement_l: Optional[str] = Field(alias="DisplacementL", default=None)
    doors: Optional[str] = Field(alias="Doors", default=None)
    drive_type: Optional[str] = Field(alias="DriveType", default=None)
    driver_assist: Optional[str] = Field(alias="DriverAssist", default=None)
    dynamic_brake_support: Optional[str] = Field(alias="DynamicBrakeSupport", default=None)
    edr: Optional[str] = Field(alias="EDR", default=None)
    esc: Optional[str] = Field(alias="ESC", default=None)
    ev_drive_unit: Optional[str] = Field(alias="EVDriveUnit", default=None)
    electrification_level: Optional[str] = Field(alias="ElectrificationLevel", default=None)
    engine_configuration: Optional[str] = Field(alias="EngineConfiguration", default=None)
    engine_cycles: Optional[str] = Field(alias="EngineCycles", default=None)
    engine_cylinders: Optional[str] = Field(alias="EngineCylinders", default=None)
    engine_hp: Optional[str] = Field(alias="EngineHP", default=None)
    engine_hp_to: Optional[str] = Field(alias="EngineHP_to", default=None)
    engine_kw: Optional[str] = Field(alias="EngineKW", default=None)
    engine_manufacturer: Optional[str] = Field(alias="EngineManufacturer", default=None)
    engine_model: Optional[str] = Field(alias="EngineModel", default=None)
    entertainment_system: Optional[str] = Field(alias="EntertainmentSystem", default=None)
    error_code: Optional[str] = Field(alias="ErrorCode", default=None)
    error_text: Optional[str] = Field(alias="ErrorText", default=None)
    forward_collision_warning: Optional[str] = Field(alias="ForwardCollisionWarning", default=None)
    fuel_injection_type: Optional[str] = Field(alias="FuelInjectionType", default=None)
    fuel_tank_material: Optional[str] = Field(alias="FuelTankMaterial", default=None)
    fuel_tank_type: Optional[str] = Field(alias="FuelTankType", default=None)
    fuel_type_primary: Optional[str] = Field(alias="FuelTypePrimary", default=None)
    fuel_type_secondary: Optional[str] = Field(alias="FuelTypeSecondary", default=None)
    gcwr: Optional[str] = Field(alias="GCWR", default=None)
    gcwr_to: Optional[str] = Field(alias="GCWR_to", default=None)
    gvwr: Optional[str] = Field(alias="GVWR", default=None)
    gvwr_to: Optional[str] = Field(alias="GVWR_to", default=None)
    keyless_ignition: Optional[str] = Field(alias="KeylessIgnition", default=None)
    lane_centering_assistance: Optional[str] = Field(alias="LaneCenteringAssistance", default=None)
    lane_departure_warning: Optional[str] = Field(alias="LaneDepartureWarning", default=None)
    lane_keep_system: Optional[str] = Field(alias="LaneKeepSystem", default=None)
    lower_beam_headlamp_light_source: Optional[str] = Field(alias="LowerBeamHeadlampLightSource", default=None)
    make: Optional[str] = Field(alias="Make", default=None)
    make_id: Optional[str] = Field(alias="MakeID", default=None)
    manufacturer: Optional[str] = Field(alias="Manufacturer", default=None)
    manufacturer_id: Optional[str] = Field(alias="ManufacturerId", default=None)
    model: Optional[str] = Field(alias="Model", default=None)
    model_id: Optional[str] = Field(alias="ModelID", default=None)
    model_year: Optional[str] = Field(alias="ModelYear", default=None)
    motorcycle_chassis_type: Optional[str] = Field(alias="MotorcycleChassisType", default=None)
    motorcycle_suspension_type: Optional[str] = Field(alias="MotorcycleSuspensionType", default=None)
    ncsa_body_type: Optional[str] = Field(alias="NCSABodyType", default=None)
    ncsa_make: Optional[str] = Field(alias="NCSAMake", default=None)
    ncsa_map_exc_approved_by: Optional[str] = Field(alias="NCSAMapExcApprovedBy", default=None)
    ncsa_map_exc_approved_on: Optional[str] = Field(alias="NCSAMapExcApprovedOn", default=None)
    ncsa_mapping_exception: Optional[str] = Field(alias="NCSAMappingException", default=None)
    ncsa_model: Optional[str] = Field(alias="NCSAModel", default=None)
    ncsa_note: Optional[str] = Field(alias="NCSANote", default=None)
    non_land_use: Optional[str] = Field(alias="NonLandUse", default=None)
    note: Optional[str] = Field(alias="Note", default=None)
    other_bus_info: Optional[str] = Field(alias="OtherBusInfo", default=None)
    other_engine_info: Optional[str] = Field(alias="OtherEngineInfo", default=None)
    other_motorcycle_info: Optional[str] = Field(alias="OtherMotorcycleInfo", default=None)
    other_restraint_system_info: Optional[str] = Field(alias="OtherRestraintSystemInfo", default=None)
    other_trailer_info: Optional[str] = Field(alias="OtherTrailerInfo", default=None)
    park_assist: Optional[str] = Field(alias="ParkAssist", default=None)
    pedestrian_automatic_emergency_braking: Optional[str] = Field(alias="PedestrianAutomaticEmergencyBraking", default=None)
    plant_city: Optional[str] = Field(alias="PlantCity", default=None)
    plant_company_name: Optional[str] = Field(alias="PlantCompanyName", default=None)
    plant_country: Optional[str] = Field(alias="PlantCountry", default=None)
    plant_state: Optional[str] = Field(alias="PlantState", default=None)
    possible_values: Optional[str] = Field(alias="PossibleValues", default=None)
    pretensioner: Optional[str] = Field(alias="Pretensioner", default=None)
    rear_automatic_emergency_braking: Optional[str] = Field(alias="RearAutomaticEmergencyBraking", default=None)
    rear_cross_traffic_alert: Optional[str] = Field(alias="RearCrossTrafficAlert", default=None)
    rear_visibility_system: Optional[str] = Field(alias="RearVisibilitySystem", default=None)
    sae_automation_level: Optional[str] = Field(alias="SAEAutomationLevel", default=None)
    sae_automation_level_to: Optional[str] = Field(alias="SAEAutomationLevel_to", default=None)
    seat_belts_all: Optional[str] = Field(alias="SeatBeltsAll", default=None)
    seat_rows: Optional[str] = Field(alias="SeatRows", default=None)
    seats: Optional[str] = Field(alias="Seats", default=None)
    semiautomatic_headlamp_beam_switching: Optional[str] = Field(alias="SemiautomaticHeadlampBeamSwitching", default=None)
    series: Optional[str] = Field(alias="Series", default=None)
    series2: Optional[str] = Field(alias="Series2", default=None)
    steering_location: Optional[str] = Field(alias="SteeringLocation", default=None)
    suggested_vin: Optional[str] = Field(alias="SuggestedVIN", default=None)
    tpms: Optional[str] = Field(alias="TPMS", default=None)
    top_speed_mph: Optional[str] = Field(alias="TopSpeedMPH", default=None)
    track_width: Optional[str] = Field(alias="TrackWidth", default=None)
    traction_control: Optional[str] = Field(alias="TractionControl", default=None)
    trailer_body_type: Optional[str] = Field(alias="TrailerBodyType", default=None)
    trailer_length: Optional[str] = Field(alias="TrailerLength", default=None)
    trailer_type: Optional[str] = Field(alias="TrailerType", default=None)
    transmission_speeds: Optional[str] = Field(alias="TransmissionSpeeds", default=None)
    transmission_style: Optional[str] = Field(alias="TransmissionStyle", default=None)
    trim: Optional[str] = Field(alias="Trim", default=None)
    trim2: Optional[str] = Field(alias="Trim2", default=None)
    turbo: Optional[str] = Field(alias="Turbo", default=None)
    vin: Optional[str] = Field(alias="VIN", default=None)
    valve_train_design: Optional[str] = Field(alias="ValveTrainDesign", default=None)
    vehicle_descriptor: Optional[str] = Field(alias="VehicleDescriptor", default=None)
    vehicle_type: Optional[str] = Field(alias="VehicleType", default=None)
    wheel_base_long: Optional[str] = Field(alias="WheelBaseLong", default=None)
    wheel_base_short: Optional[str] = Field(alias="WheelBaseShort", default=None)
    wheel_base_type: Optional[str] = Field(alias="WheelBaseType", default=None)
    wheel_size_front: Optional[str] = Field(alias="WheelSizeFront", default=None)
    wheel_size_rear: Optional[str] = Field(alias="WheelSizeRear", default=None)
    wheelie_mitigation: Optional[str] = Field(alias="WheelieMitigation", default=None)
    wheels: Optional[str] = Field(alias="Wheels", default=None)
    windows: Optional[str] = Field(alias="Windows", default=None)


class VinDecodeFlatResult(BaseNHTSAResponse):
    """Represents the response structure for Decode VIN (flat format)."""
    results: List[VinDecodeFlatEntry] = Field(alias="Results")


class VinDecodeExtendedResult(BaseNHTSAResponse):
    """Represents the response structure for Decode VIN Extended (key-value)."""
    results: List[VinDecodeEntry] = Field(alias="Results")


class VinDecodeExtendedFlatResult(BaseNHTSAResponse):
    """Represents the response structure for Decode VIN Extended (flat format)."""
    results: List[VinDecodeFlatEntry] = Field(alias="Results")


class WmiDecodeEntry(BaseModel):
    """Represents a single decoded WMI entry."""
    common_name: Optional[str] = Field(alias="CommonName", default=None)
    created_on: Optional[datetime] = Field(alias="CreatedOn")
    date_available_to_public: Optional[datetime] = Field(alias="DateAvailableToPublic")
    make: Optional[str] = Field(alias="Make")
    manufacturer_name: Optional[str] = Field(alias="ManufacturerName")
    parent_company_name: Optional[str] = Field(alias="ParentCompanyName", default=None)
    url: Optional[str] = Field(alias="URL")
    updated_on: Optional[datetime] = Field(alias="UpdatedOn", default=None)
    vehicle_type: Optional[str] = Field(alias="VehicleType")


class WmiDecodeResult(BaseNHTSAResponse):
    """Represents the response structure for Decode WMI."""
    results: List[WmiDecodeEntry] = Field(alias="Results")


class WmiForManufacturerEntry(BaseModel):
    """Represents a single WMI for a manufacturer."""
    country: Optional[str] = Field(alias="Country")
    created_on: Optional[datetime] = Field(alias="CreatedOn")
    date_available_to_public: Optional[datetime] = Field(alias="DateAvailableToPublic")
    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    updated_on: Optional[datetime] = Field(alias="UpdatedOn")
    vehicle_type: str = Field(alias="VehicleType")
    wmi: str = Field(alias="WMI")


class WmiForManufacturerResult(BaseNHTSAResponse):
    """Represents the response structure for Get WMIs for Manufacturer."""
    results: List[WmiForManufacturerEntry] = Field(alias="Results")


class AllMakesEntry(BaseModel):
    """Represents a single make from the Get All Makes endpoint."""
    make_id: int = Field(alias="Make_ID")
    make_name: str = Field(alias="Make_Name")


class AllMakesResult(BaseNHTSAResponse):
    """Represents the response structure for Get All Makes."""
    results: List[AllMakesEntry] = Field(alias="Results")


class PartsEntry(BaseModel):
    """Represents a single part entry from the Get Parts endpoint."""
    cover_letter_url: Optional[str] = Field(alias="CoverLetterURL")
    letter_date: datetime = Field(alias="LetterDate", json_schema_extra={'format': '%m/%d/%Y'})
    manufacturer_id: int = Field(alias="ManufacturerId")
    manufacturer_name: str = Field(alias="ManufacturerName")
    model_year_from: Optional[int] = Field(alias="ModelYearFrom")
    model_year_to: Optional[int] = Field(alias="ModelYearTo")
    name: str = Field(alias="Name")
    type: str = Field(alias="Type")
    url: str = Field(alias="URL")


class PartsResult(BaseNHTSAResponse):
    """Represents the response structure for Get Parts."""
    results: List[PartsEntry] = Field(alias="Results")


class ManufacturerVehicleType(BaseModel):
    """Represents a vehicle type associated with a manufacturer."""
    is_primary: bool = Field(alias="IsPrimary")
    name: str = Field(alias="Name")


class AllManufacturersEntry(BaseModel):
    """Represents a single manufacturer from the Get All Manufacturers endpoint."""
    country: Optional[str] = Field(alias="Country")
    mfr_common_name: Optional[str] = Field(alias="Mfr_CommonName")
    mfr_id: int = Field(alias="Mfr_ID")
    mfr_name: str = Field(alias="Mfr_Name")
    vehicle_types: List[ManufacturerVehicleType] = Field(alias="VehicleTypes")


class AllManufacturersResult(BaseNHTSAResponse):
    """Represents the response structure for Get All Manufacturers."""
    results: List[AllManufacturersEntry] = Field(alias="Results")


class ManufacturerDetailsVehicleType(BaseModel):
    """Represents a detailed vehicle type for a manufacturer."""
    gvwr_from: Optional[str] = Field(alias="GVWRFrom")
    gvwr_to: Optional[str] = Field(alias="GVWRTo")
    is_primary: bool = Field(alias="IsPrimary")
    name: str = Field(alias="Name")


class ManufacturerDetailsEntry(BaseModel):
    """Represents detailed information for a single manufacturer."""
    address: Optional[str] = Field(alias="Address")
    address2: Optional[str] = Field(alias="Address2")
    city: Optional[str] = Field(alias="City")
    contact_email: Optional[str] = Field(alias="ContactEmail")
    contact_fax: Optional[str] = Field(alias="ContactFax")
    contact_phone: Optional[str] = Field(alias="ContactPhone")
    country: Optional[str] = Field(alias="Country")
    db_as: Optional[str] = Field(alias="DBAs")
    equipment_items: List[Dict[str, Any]] = Field(alias="EquipmentItems")  # Could be more specific if schema provided
    last_updated: Optional[datetime] = Field(alias="LastUpdated")
    manufacturer_types: List[Dict[str, str]] = Field(alias="ManufacturerTypes") # Could be more specific
    mfr_common_name: Optional[str] = Field(alias="Mfr_CommonName")
    mfr_id: int = Field(alias="Mfr_ID")
    mfr_name: str = Field(alias="Mfr_Name")
    other_manufacturer_details: Optional[str] = Field(alias="OtherManufacturerDetails")
    postal_code: Optional[str] = Field(alias="PostalCode")
    primary_product: Optional[str] = Field(alias="PrimaryProduct")
    principal_first_name: Optional[str] = Field(alias="PrincipalFirstName")
    principal_last_name: Optional[str] = Field(alias="PrincipalLastName")
    principal_position: Optional[str] = Field(alias="PrincipalPosition")
    state_province: Optional[str] = Field(alias="StateProvince")
    submitted_name: Optional[str] = Field(alias="SubmittedName")
    submitted_on: Optional[datetime] = Field(alias="SubmittedOn")
    submitted_position: Optional[str] = Field(alias="SubmittedPosition")
    vehicle_types: List[ManufacturerDetailsVehicleType] = Field(alias="VehicleTypes")


class ManufacturerDetailsResult(BaseNHTSAResponse):
    """Represents the response structure for Get Manufacturer Details."""
    results: List[ManufacturerDetailsEntry] = Field(alias="Results")


class MakeForManufacturerEntry(BaseModel):
    """Represents a single make for a manufacturer."""
    make_id: int = Field(alias="Make_ID")
    make_name: str = Field(alias="Make_Name")
    mfr_name: str = Field(alias="Mfr_Name")


class MakeForManufacturerResult(BaseNHTSAResponse):
    """Represents the response structure for Get Makes for Manufacturer."""
    results: List[MakeForManufacturerEntry] = Field(alias="Results")


class MakesForManufacturerAndYearEntry(BaseModel):
    """Represents a single make for a manufacturer and year."""
    make_id: int = Field(alias="MakeId")
    make_name: str = Field(alias="MakeName")
    mfr_id: int = Field(alias="MfrId")
    mfr_name: str = Field(alias="MfrName")


class MakesForManufacturerAndYearResult(BaseNHTSAResponse):
    """Represents the response structure for Get Makes for Manufacturer by Manufacturer Name and Year."""
    results: List[MakesForManufacturerAndYearEntry] = Field(alias="Results")


class MakesForVehicleTypeEntry(BaseModel):
    """Represents a single make for a vehicle type."""
    make_id: int = Field(alias="MakeId")
    make_name: str = Field(alias="MakeName")
    vehicle_type_id: int = Field(alias="VehicleTypeId")
    vehicle_type_name: str = Field(alias="VehicleTypeName")


class MakesForVehicleTypeResult(BaseNHTSAResponse):
    """Represents the response structure for Get Makes for Vehicle Type by Vehicle Type Name."""
    results: List[MakesForVehicleTypeEntry] = Field(alias="Results")


class VehicleTypesForMakeEntry(BaseModel):
    """Represents a single vehicle type for a make."""
    make_id: int = Field(alias="MakeId")
    make_name: str = Field(alias="MakeName")
    vehicle_type_id: int = Field(alias="VehicleTypeId")
    vehicle_type_name: str = Field(alias="VehicleTypeName")


class VehicleTypesForMakeResult(BaseNHTSAResponse):
    """Represents the response structure for Get Vehicle Types for Make by Name."""
    results: List[VehicleTypesForMakeEntry] = Field(alias="Results")


class VehicleTypesForMakeIdEntry(BaseModel):
    """Represents a single vehicle type for a make ID."""
    vehicle_type_id: int = Field(alias="VehicleTypeId")
    vehicle_type_name: str = Field(alias="VehicleTypeName")


class VehicleTypesForMakeIdResult(BaseNHTSAResponse):
    """Represents the response structure for Get Vehicle Types for Make by Id."""
    results: List[VehicleTypesForMakeIdEntry] = Field(alias="Results")


class EquipmentPlantCodeEntry(BaseModel):
    """Represents a single equipment plant code."""
    address: Optional[str] = Field(alias="Address", default=None)
    city: Optional[str] = Field(alias="City", default=None)
    country: str = Field(alias="Country")
    dot_code: str = Field(alias="DOTCode")
    name: str = Field(alias="Name")
    old_dot_code: Optional[str] = Field(alias="OldDotCode")
    postal_code: Optional[str] = Field(alias="PostalCode", default=None)
    state_province: Optional[str] = Field(alias="StateProvince", default=None)
    status: Optional[str] = Field(alias="Status", default=None)


class EquipmentPlantCodeResult(BaseNHTSAResponse):
    """Represents the response structure for Get Equipment Plant Codes."""
    results: List[EquipmentPlantCodeEntry] = Field(alias="Results")


class ModelsForMakeEntry(BaseModel):
    """Represents a single model for a make."""
    make_id: int = Field(alias="Make_ID")
    make_name: str = Field(alias="Make_Name")
    model_id: int = Field(alias="Model_ID")
    model_name: str = Field(alias="Model_Name")


class ModelsForMakeResult(BaseNHTSAResponse):
    """Represents the response structure for Get Models for Make."""
    results: List[ModelsForMakeEntry] = Field(alias="Results")


class ModelsForMakeIdEntry(BaseModel):
    """Represents a single model for a make ID."""
    make_id: int = Field(alias="Make_ID")
    make_name: str = Field(alias="Make_Name")
    model_id: int = Field(alias="Model_ID")
    model_name: str = Field(alias="Model_Name")


class ModelsForMakeIdResult(BaseNHTSAResponse):
    """Represents the response structure for Get Models for MakeId."""
    results: List[ModelsForMakeIdEntry] = Field(alias="Results")


class ModelsForMakeYearEntry(BaseModel):
    """Represents a single model for a make, year, and/or vehicle type."""
    make_id: int = Field(alias="Make_ID")
    make_name: str = Field(alias="Make_Name")
    model_id: int = Field(alias="Model_ID")
    model_name: str = Field(alias="Model_Name")
    vehicle_type_id: Optional[int] = Field(alias="VehicleTypeId", default=None)
    vehicle_type_name: Optional[str] = Field(alias="VehicleTypeName", default=None)


class ModelsForMakeYearResult(BaseNHTSAResponse):
    """Represents the response structure for Get Models for Make and a combination of Year and Vehicle Type."""
    results: List[ModelsForMakeYearEntry] = Field(alias="Results")


class VehicleVariableListEntry(BaseModel):
    """Represents a single vehicle variable."""
    data_type: str = Field(alias="DataType")
    description: str = Field(alias="Description")
    group_name: str = Field(alias="GroupName")
    id: int = Field(alias="ID")
    name: str = Field(alias="Name")


class VehicleVariableListResult(BaseNHTSAResponse):
    """Represents the response structure for Get Vehicle Variables List."""
    results: List[VehicleVariableListEntry] = Field(alias="Results")


class VehicleVariableValuesListEntry(BaseModel):
    """Represents a single value for a vehicle variable."""
    element_name: str = Field(alias="ElementName")
    id: int = Field(alias="Id")
    name: str = Field(alias="Name")


class VehicleVariableValuesListResult(BaseNHTSAResponse):
    """Represents the response structure for Get Vehicle Variable Values List."""
    results: List[VehicleVariableValuesListEntry] = Field(alias="Results")


class DecodeVinBatchEntry(VinDecodeFlatEntry):
    """Represents a single VIN decode result from a batch request."""
    # Inherits all fields from VinDecodeFlatEntry


class DecodeVinBatchResult(BaseNHTSAResponse):
    """Represents the response structure for Decode VIN (flat format) in a Batch."""
    results: List[DecodeVinBatchEntry] = Field(alias="Results")


class CanadianVehicleSpecification(BaseModel):
    """Represents a single Canadian vehicle specification."""
    name: str = Field(alias="Name")
    value: str = Field(alias="Value")


class CanadianVehicleSpecificationsEntry(BaseModel):
    """Represents a collection of Canadian vehicle specifications for a model."""
    specs: List[CanadianVehicleSpecification] = Field(alias="Specs")


class CanadianVehicleSpecificationsResult(BaseNHTSAResponse):
    """Represents the response structure for Get Canadian vehicle specifications."""
    results: List[CanadianVehicleSpecificationsEntry] = Field(alias="Results")

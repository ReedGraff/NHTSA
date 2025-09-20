from typing import List, Optional, Any
from pydantic import BaseModel, Field


class SafetyRatingMessage(BaseModel):
    """Base model for NHTSA API responses."""
    count: int = Field(alias="Count")
    message: str = Field(alias="Message")


class VehicleVariantResult(BaseModel):
    """Represents a single vehicle variant."""
    vehicle_description: str = Field(alias="VehicleDescription")
    vehicle_id: int = Field(alias="VehicleId")


class VehicleVariant(SafetyRatingMessage):
    """Represents the response for available vehicle variants."""
    results: List[VehicleVariantResult] = Field(alias="Results")


class SafetyRatingDetail(BaseModel):
    """Represents detailed safety rating information for a vehicle."""
    vehicle_picture: Optional[str] = Field(alias="VehiclePicture", default=None)
    overall_rating: Optional[str] = Field(alias="OverallRating", default=None)
    overall_front_crash_rating: Optional[str] = Field(alias="OverallFrontCrashRating", default=None)
    front_crash_driverside_rating: Optional[str] = Field(alias="FrontCrashDriversideRating", default=None)
    front_crash_passengerside_rating: Optional[str] = Field(alias="FrontCrashPassengersideRating", default=None)
    overall_side_crash_rating: Optional[str] = Field(alias="OverallSideCrashRating", default=None)
    side_crash_driverside_rating: Optional[str] = Field(alias="SideCrashDriversideRating", default=None)
    side_crash_passengerside_rating: Optional[str] = Field(alias="SideCrashPassengersideRating", default=None)
    combined_side_barrier_and_pole_rating_front: Optional[str] = Field(alias="combinedSideBarrierAndPoleRating-Front", default=None)
    combined_side_barrier_and_pole_rating_rear: Optional[str] = Field(alias="combinedSideBarrierAndPoleRating-Rear", default=None)
    side_barrier_rating_overall: Optional[str] = Field(alias="sideBarrierRating-Overall", default=None)
    rollover_rating: Optional[str] = Field(alias="RolloverRating", default=None)
    rollover_rating2: Optional[str] = Field(alias="RolloverRating2", default=None)
    rollover_possibility: Optional[float] = Field(alias="RolloverPossibility", default=None)
    rollover_possibility2: Optional[float] = Field(alias="RolloverPossibility2", default=None)
    dynamic_tip_result: Optional[str] = Field(alias="dynamicTipResult", default=None)
    side_pole_crash_rating: Optional[str] = Field(alias="SidePoleCrashRating", default=None)
    nhtsa_electronic_stability_control: Optional[str] = Field(alias="NHTSAElectronicStabilityControl", default=None)
    nhtsa_forward_collision_warning: Optional[str] = Field(alias="NHTSAForwardCollisionWarning", default=None)
    nhtsa_lane_departure_warning: Optional[str] = Field(alias="NHTSALaneDepartureWarning", default=None)
    complaints_count: Optional[int] = Field(alias="ComplaintsCount", default=None)
    recalls_count: Optional[int] = Field(alias="RecallsCount", default=None)
    investigation_count: Optional[int] = Field(alias="InvestigationCount", default=None)
    model_year: Optional[int] = Field(alias="ModelYear", default=None)
    make: Optional[str] = Field(alias="Make", default=None)
    model: Optional[str] = Field(alias="Model", default=None)
    vehicle_description: Optional[str] = Field(alias="VehicleDescription", default=None)
    vehicle_id: Optional[int] = Field(alias="VehicleId", default=None)


class SafetyRatingResult(SafetyRatingMessage):
    """Represents the response for safety ratings for a specific vehicle ID."""
    results: List[SafetyRatingDetail] = Field(alias="Results")


class ModelYearResult(BaseModel):
    """Represents a single model year."""
    model_year: int = Field(alias="ModelYear")
    vehicle_id: int = Field(alias="VehicleId")


class SafetyRatingModelYear(SafetyRatingMessage):
    """Represents the response for all available model years."""
    results: List[ModelYearResult] = Field(alias="Results")


class MakeResult(BaseModel):
    """Represents a single make for a model year."""
    model_year: int = Field(alias="ModelYear")
    make: str = Field(alias="Make")
    vehicle_id: int = Field(alias="VehicleId")


class SafetyRatingMake(SafetyRatingMessage):
    """Represents the response for all makes for a specific model year."""
    results: List[MakeResult] = Field(alias="Results")


class ModelResult(BaseModel):
    """Represents a single model for a make and model year."""
    model_year: int = Field(alias="ModelYear")
    make: str = Field(alias="Make")
    model: str = Field(alias="Model")
    vehicle_id: int = Field(alias="VehicleId")


class SafetyRatingModel(SafetyRatingMessage):
    """Represents the response for all models for a specific make and model year."""
    results: List[ModelResult] = Field(alias="Results")

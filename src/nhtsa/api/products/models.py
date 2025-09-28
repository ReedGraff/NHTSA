from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field
from datetime import datetime

from ...lib.models import Meta, Pagination, Error # Reusing common meta/pagination
from ..safety_issues.models import ( # Reusing common safety issue models
    SafetyIssuesDetail, SafetyIssueComponent, SafetyIssueAssociatedDocument,
    SafetyIssueAssociatedProduct, SafetyIssueComplaint, SafetyIssueRecall,
    SafetyIssueInvestigation, SafetyIssueManufacturerCommunication, SafetyIssueRecallInvestigationInfo
)
# Reusing SafetyRating models if applicable, but some fields are subtly different or nested
# For now, redefining for clarity within the 'products' domain if needed, or explicitly importing.
# From safety_service.models, the crashTestRatings are different.

# --- Common nested models for Vehicle safety details (Crash Tests, Safety Features, Recommended Features) ---

class CrashTestSubRating(BaseModel):
    position: Optional[str] = Field(alias="position", default=None)
    display: Optional[str] = Field(alias="display", default=None)
    rating: Optional[Union[str, int, float]] = Field(alias="rating", default=None)
    notes: Optional[str] = Field(alias="notes", default=None)
    safety_concerns: Optional[str] = Field(alias="safetyConcerns", default=None)

class CrashTestRatingEntry(BaseModel):
    position: Optional[str] = Field(alias="position", default=None)
    display: Optional[str] = Field(alias="display", default=None)
    rating: Optional[Union[str, int, float]] = Field(alias="rating", default=None)
    notes: Optional[str] = Field(alias="notes", default=None)
    safety_concerns: Optional[str] = Field(alias="safetyConcerns", default=None)
    ratings: Optional[List[CrashTestSubRating]] = Field(alias="ratings", default_factory=list) # Nested ratings
    tip: Optional[str] = Field(alias="tip", default=None)
    possibility: Optional[Union[str, float]] = Field(alias="possibility", default=None)

class CrashTestMedia(BaseModel):
    type: Optional[str] = Field(alias="type", default=None)
    url: Optional[str] = Field(alias="url", default=None)

class CrashTestReport(BaseModel):
    type: Optional[str] = Field(alias="type", default=None)
    number: Optional[str] = Field(alias="number", default=None)
    file_name: Optional[str] = Field(alias="fileName", default=None)
    url: Optional[str] = Field(alias="url", default=None)
    file_size: Optional[str] = Field(alias="fileSize", default=None)


class CrashTestRating(BaseModel):
    type: Optional[str] = Field(alias="type", default=None)
    display: Optional[str] = Field(alias="display", default=None)
    mmy: Optional[str] = Field(alias="mmy", default=None)
    ncap_vehicle_id: Optional[int] = Field(alias="ncapVehicleId", default=None)
    curb_weight: Optional[str] = Field(alias="curbWeight", default=None)
    ratings: List[CrashTestRatingEntry] = Field(alias="ratings", default_factory=list)
    tested_with: Optional[str] = Field(alias="testedWith", default=None)
    test_no: Optional[str] = Field(alias="testNo", default=None)
    media: Optional[List[CrashTestMedia]] = Field(alias="media", default_factory=list)
    reports: Optional[List[CrashTestReport]] = Field(alias="reports", default_factory=list)

class SafetyFeatureItem(BaseModel):
    label: Optional[str] = Field(alias="label", default=None)
    value: Optional[str] = Field(alias="value", default=None)
    notes: Optional[str] = Field(alias="notes", default=None)

class SafetyFeatureCategory(BaseModel):
    category: Optional[str] = Field(alias="category", default=None)
    notes: Optional[str] = Field(alias="notes", default=None)
    features: List[SafetyFeatureItem] = Field(alias="features", default_factory=list)

class RecommendedFeature(BaseModel):
    key: Optional[str] = Field(alias="key", default=None)
    label: Optional[str] = Field(alias="label", default=None)
    video: Optional[str] = Field(alias="video", default=None)
    icon: Optional[str] = Field(alias="icon", default=None)
    type: Optional[str] = Field(alias="type", default=None)
    nhtsa_evaluation: Optional[str] = Field(alias="nhtsaEvaluation", default=None)
    nhtsa_comments: Optional[str] = Field(alias="nhtsaComments", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    note: Optional[str] = Field(alias="note", default=None) # Specific to some recommended features

class VehicleSafetyRatings(BaseModel):
    crash_test_ratings: Optional[List[CrashTestRating]] = Field(alias="crashTestRatings", default_factory=list)
    safety_features: Optional[List[SafetyFeatureCategory]] = Field(alias="safetyFeatures", default_factory=list)
    recommended_features: Optional[List[RecommendedFeature]] = Field(alias="recommendedFeatures", default_factory=list)

# --- Base Product Info (common across Vehicles, Tires, Equipment, Child Seats) ---
class BaseProductInfo(BaseModel):
    id: Optional[int] = Field(alias="id", default=None) # Used by Tires, Equipment, ChildSeats, and general SafetyIssues
    artemis_id: Optional[int] = Field(alias="artemisId", default=None)
    active: Optional[bool] = Field(alias="active", default=None)
    complaints_count: Optional[int] = Field(alias="complaintsCount", default=None)
    recalls_count: Optional[int] = Field(alias="recallsCount", default=None)
    investigations_count: Optional[int] = Field(alias="investigationsCount", default=None)
    manufacturer_communications_count: Optional[int] = Field(alias="manufacturerCommunicationsCount", default=None)
    park_it: Optional[bool] = Field(alias="parkIt", default=None)
    park_outside: Optional[bool] = Field(alias="parkOutSide", default=None)
    over_the_air_update: Optional[bool] = Field(alias="overTheAirUpdate", default=None)
    ncap_id: Optional[int] = Field(alias="ncapId", default=None)
    ncap_rated: Optional[bool] = Field(alias="ncapRated", default=None)

# --- Vehicle Models ---
class VehicleBaseInfo(BaseProductInfo):
    vehicle_id: Optional[int] = Field(alias="vehicleId", default=None)
    model_year: Optional[int] = Field(alias="modelYear", default=None)
    make: Optional[str] = Field(alias="make", default=None)
    vehicle_model: Optional[str] = Field(alias="vehicleModel", default=None)
    trim: Optional[str] = Field(alias="trim", default=None)
    series: Optional[str] = Field(alias="series", default=None)
    class_type: Optional[str] = Field(alias="class", default=None) # Renamed 'class' to 'class_type' to avoid Python keyword conflict
    manufacturer: Optional[str] = Field(alias="manufacturer", default=None)
    vehicle_picture: Optional[str] = Field(alias="vehiclePicture", default=None)

class VehicleByYmmtResultItem(VehicleBaseInfo, VehicleSafetyRatings):
    """Combines base vehicle info with safety ratings for byYmmt endpoint."""
    pass

class VehicleByYmmtResult(BaseModel):
    meta: Meta = Field(alias="meta")
    results: List[VehicleByYmmtResultItem] = Field(alias="results")

class VehicleDetailsResultItem(VehicleBaseInfo):
    safety_issues: Optional[SafetyIssuesDetail] = Field(alias="safetyIssues", default=None)

class VehicleDetailsResult(BaseModel):
    meta: Meta = Field(alias="meta")
    results: List[VehicleDetailsResultItem] = Field(alias="results")

class VehicleByVinProxyDecoder(BaseModel):
    model_year: Optional[str] = Field(alias="modelYear", default=None)
    make: Optional[str] = Field(alias="make", default=None)
    errors: Optional[List[str]] = Field(alias="errors", default_factory=list)
    source_url: Optional[str] = Field(alias="sourceUrl", default=None)
    vehicle_model: Optional[str] = Field(alias="vehicleModel", default=None)
    vehicle_type: Optional[str] = Field(alias="vehicleType", default=None)
    source: Optional[str] = Field(alias="source", default=None)

class VehicleByVinProxyResult(BaseModel):
    meta: Meta = Field(alias="meta")
    results: List[VehicleBaseInfo] = Field(alias="results")
    decoder: Optional[List[VehicleByVinProxyDecoder]] = Field(alias="decoder", default_factory=list)

class Filter(BaseModel):
    value: Optional[str] = Field(alias="value", default=None)
    type: Optional[str] = Field(alias="type", default=None)
    count: Optional[int] = Field(alias="count", default=None)

class VehicleSearchResultItem(VehicleBaseInfo, VehicleSafetyRatings):
    """Combines base vehicle info with safety ratings for bySearch endpoint."""
    pass

class VehicleSearchResult(BaseModel):
    meta: Meta = Field(alias="meta")
    results: List[VehicleSearchResultItem] = Field(alias="results")
    filters: Optional[List[Filter]] = Field(alias="filters", default_factory=list)
    decoder: Optional[List[Any]] = Field(alias="decoder", default_factory=list) # decoder can be empty list

# --- Tire Models ---
class TireSafetyIssues(BaseModel):
    complaints: List[SafetyIssueComplaint] = Field(alias="complaints", default_factory=list)
    recalls: List[SafetyIssueRecall] = Field(alias="recalls", default_factory=list)
    investigations: List[SafetyIssueInvestigation] = Field(alias="investigations", default_factory=list)
    manufacturer_communications: List[SafetyIssueManufacturerCommunication] = Field(alias="manufacturerCommunications", default_factory=list)

class TireSearchItem(BaseProductInfo):
    brand: Optional[str] = Field(alias="brand", default=None)
    const: Optional[Any] = Field(alias="const", default=None) # Unknown type
    tireline: Optional[str] = Field(alias="tireline", default=None)
    size: Optional[str] = Field(alias="size", default=None)
    trac: Optional[Any] = Field(alias="trac", default=None) # Unknown type
    temp: Optional[Any] = Field(alias="temp", default=None) # Unknown type
    wear: Optional[Any] = Field(alias="wear", default=None) # Unknown type
    product_name: Optional[str] = Field(alias="productName", default=None)
    safety_issues: Optional[TireSafetyIssues] = Field(alias="safetyIssues", default=None)


class TireSearchResult(BaseModel):
    meta: Meta = Field(alias="meta")
    results: List[TireSearchItem] = Field(alias="results")

# --- Equipment Models ---
class EquipmentSafetyIssues(BaseModel):
    complaints: List[SafetyIssueComplaint] = Field(alias="complaints", default_factory=list)
    recalls: List[SafetyIssueRecall] = Field(alias="recalls", default_factory=list)
    investigations: List[SafetyIssueInvestigation] = Field(alias="investigations", default_factory=list)
    manufacturer_communications: List[SafetyIssueManufacturerCommunication] = Field(alias="manufacturerCommunications", default_factory=list)

class EquipmentSearchItem(BaseProductInfo):
    brand: Optional[str] = Field(alias="brand", default=None)
    model: Optional[str] = Field(alias="model", default=None)
    product_name: Optional[str] = Field(alias="productName", default=None)
    safety_issues: Optional[EquipmentSafetyIssues] = Field(alias="safetyIssues", default=None)

class EquipmentSearchResult(BaseModel):
    meta: Meta = Field(alias="meta")
    results: List[EquipmentSearchItem] = Field(alias="results")

# --- Child Seat Models ---
class ChildSeatModeRating(BaseModel):
    type: Optional[str] = Field(alias="type", default=None)
    label: Optional[str] = Field(alias="label", default=None)
    rating: Optional[Union[int, str]] = Field(alias="rating", default=None)
    notes: Optional[str] = Field(alias="notes", default=None)

class ChildSeatMode(BaseModel):
    mode: Optional[str] = Field(alias="mode", default=None)
    recommended_age: Optional[bool] = Field(alias="recommendedAge", default=None)
    harness_type: Optional[str] = Field(alias="harnessType", default=None)
    mode_weight: Optional[float] = Field(alias="modeWeight", default=None)
    weight_height_range: Optional[str] = Field(alias="weightHeightRange", default=None)
    min_using_seat_belts: Optional[float] = Field(alias="minUsingSeatBelts", default=None)
    max_using_seat_belts: Optional[float] = Field(alias="maxUsingSeatBelts", default=None)
    min_using_lower_anchors: Optional[float] = Field(alias="minUsingLowerAnchors", default=None)
    max_using_lower_anchors: Optional[float] = Field(alias="maxUsingLowerAnchors", default=None)
    max_using_lower_anchors_final: Optional[float] = Field(alias="maxUsingLowerAnchorsFinal", default=None)
    min_child_height: Optional[float] = Field(alias="minChildHeight", default=None)
    max_child_height: Optional[float] = Field(alias="maxChildHeight", default=None)
    max_child_height_final: Optional[float] = Field(alias="maxChildHeightFinal", default=None)
    max_child_weight_final: Optional[float] = Field(alias="maxChildWeightFinal", default=None)
    ratings: Optional[List[ChildSeatModeRating]] = Field(alias="ratings", default_factory=list)

class ChildSeatItem(BaseProductInfo):
    make: Optional[str] = Field(alias="make", default=None)
    manufacturer_date: Optional[datetime] = Field(alias="manufacturerDate", default=None)
    product_model: Optional[str] = Field(alias="productModel", default=None)
    model_number: Optional[str] = Field(alias="modelNumber", default=None)
    seat_type: Optional[str] = Field(alias="seatType", default=None)
    height_range: Optional[str] = Field(alias="heightRange", default=None)
    weight_range: Optional[str] = Field(alias="weightRange", default=None)
    min_height: Optional[int] = Field(alias="minHeight", default=None)
    max_height: Optional[int] = Field(alias="maxHeight", default=None)
    min_weight: Optional[int] = Field(alias="minWeight", default=None)
    max_weight: Optional[int] = Field(alias="maxWeight", default=None)
    picture: Optional[str] = Field(alias="picture", default=None)
    modes: Optional[List[ChildSeatMode]] = Field(alias="modes", default_factory=list)

class ChildSeatsResult(BaseModel):
    meta: Meta = Field(alias="meta")
    results: List[ChildSeatItem] = Field(alias="results")
    filters: Optional[List[Filter]] = Field(alias="filters", default_factory=list)

class ChildSeatModeEntry(BaseModel):
    type: Optional[str] = Field(alias="type", default=None)
    min_age: Optional[int] = Field(alias="minAge", default=None)
    max_age: Optional[int] = Field(alias="maxAge", default=None)

class ChildSeatModesResult(BaseModel):
    meta: Meta = Field(alias="meta")
    results: List[ChildSeatModeEntry] = Field(alias="results")
    filters: Optional[List[Filter]] = Field(alias="filters", default_factory=list)

class ChildSeatBySearchResult(BaseModel):
    meta: Meta = Field(alias="meta")
    results: List[ChildSeatItem] = Field(alias="results")
    filters: Optional[List[Filter]] = Field(alias="filters", default_factory=list)
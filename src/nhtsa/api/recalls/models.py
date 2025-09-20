from typing import List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class RecallBaseResponse(BaseModel):
    """Base model for NHTSA API responses."""
    count: int = Field(alias="Count")
    message: str = Field(alias="Message")


class ProductInfo(BaseModel):
    """Represents product information within a complaint."""
    type: str = Field(alias="type")
    product_year: Optional[str] = Field(alias="productYear")
    product_make: Optional[str] = Field(alias="productMake")
    product_model: Optional[str] = Field(alias="productModel")
    manufacturer: Optional[str] = Field(alias="manufacturer")


class RecallResult(BaseModel):
    """Represents a single recall entry."""
    manufacturer: str = Field(alias="Manufacturer")
    nhtsa_campaign_number: str = Field(alias="NHTSACampaignNumber")
    park_it: bool = Field(alias="parkIt")
    park_outside: bool = Field(alias="parkOutSide")
    over_the_air_update: bool = Field(alias="overTheAirUpdate")
    nhtsa_action_number: Optional[str] = Field(alias="NHTSAActionNumber")
    report_received_date: datetime = Field(alias="ReportReceivedDate",
                                          json_schema_extra={'format': '%m/%d/%Y'}) # Handle string date format
    component: str = Field(alias="Component")
    summary: str = Field(alias="Summary")
    consequence: str = Field(alias="Consequence")
    remedy: str = Field(alias="Remedy")
    notes: Optional[str] = Field(alias="Notes")
    model_year: Optional[str] = Field(alias="ModelYear")
    make: Optional[str] = Field(alias="Make")
    model: Optional[str] = Field(alias="Model")
    # This field is dynamic in the API response, sometimes it's just a string like "2012", sometimes it's a list.
    # We'll use Any to handle this, but for structured processing, it might need a custom validator or converter.
    products: Optional[List[ProductInfo]] = None


class RecallByVehicle(RecallBaseResponse):
    """Represents the response structure for recalls by vehicle."""
    results: List[RecallResult] = Field(alias="results")


class ModelYearResult(BaseModel):
    """Represents a single model year."""
    model_year: str = Field(alias="modelYear")


class ModelYear(RecallBaseResponse):
    """Represents the response structure for all model years."""
    results: List[ModelYearResult] = Field(alias="results")


class MakeResult(BaseModel):
    """Represents a single make."""
    model_year: str = Field(alias="modelYear")
    make: str = Field(alias="make")


class Make(RecallBaseResponse):
    """Represents the response structure for all makes for a model year."""
    results: List[MakeResult] = Field(alias="results")


class ModelResult(BaseModel):
    """Represents a single model."""
    model_year: str = Field(alias="modelYear")
    make: str = Field(alias="make")
    model: str = Field(alias="model")


class Model(RecallBaseResponse):
    """Represents the response structure for all models for a make and model year."""
    results: List[ModelResult] = Field(alias="results")


class RecallCampaign(RecallBaseResponse):
    """Represents the response structure for recalls by campaign number."""
    results: List[RecallResult] = Field(alias="results")
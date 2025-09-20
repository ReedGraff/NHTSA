from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ComplaintBaseResponse(BaseModel):
    """Base model for NHTSA API responses."""
    count: int = Field(alias="count")
    message: str = Field(alias="message")


class ProductInfo(BaseModel):
    """Represents product information within a complaint."""
    type: str = Field(alias="type")
    product_year: Optional[str] = Field(alias="productYear")
    product_make: Optional[str] = Field(alias="productMake")
    product_model: Optional[str] = Field(alias="productModel")
    manufacturer: Optional[str] = Field(alias="manufacturer")


class ComplaintResult(BaseModel):
    """Represents a single complaint entry."""
    odi_number: int = Field(alias="odiNumber")
    manufacturer: Optional[str] = Field(alias="manufacturer")
    crash: bool = Field(alias="crash")
    fire: bool = Field(alias="fire")
    number_of_injuries: int = Field(alias="numberOfInjuries")
    number_of_deaths: int = Field(alias="numberOfDeaths")
    date_of_incident: Optional[datetime] = Field(alias="dateOfIncident",
                                               json_schema_extra={'format': '%m/%d/%Y'})
    date_complaint_filed: Optional[datetime] = Field(alias="dateComplaintFiled",
                                                    json_schema_extra={'format': '%m/%d/%Y'})
    vin: Optional[str] = Field(alias="vin")
    components: Optional[str] = Field(alias="components")
    summary: Optional[str] = Field(alias="summary")
    products: List[ProductInfo] = Field(alias="products")


class ComplaintByVehicle(ComplaintBaseResponse):
    """Represents the response structure for complaints by vehicle."""
    results: List[ComplaintResult] = Field(alias="results")


class ModelYearResult(BaseModel):
    """Represents a single model year."""
    model_year: str = Field(alias="modelYear")


class ModelYear(ComplaintBaseResponse):
    """Represents the response structure for all model years for complaints."""
    results: List[ModelYearResult] = Field(alias="results")


class MakeResult(BaseModel):
    """Represents a single make."""
    model_year: str = Field(alias="modelYear")
    make: str = Field(alias="make")


class Make(ComplaintBaseResponse):
    """Represents the response structure for all makes for a model year for complaints."""
    results: List[MakeResult] = Field(alias="results")


class ModelResult(BaseModel):
    """Represents a single model."""
    model_year: str = Field(alias="modelYear")
    make: str = Field(alias="make")
    model: str = Field(alias="model")


class Model(ComplaintBaseResponse):
    """Represents the response structure for all models for a make and model year for complaints."""
    results: List[ModelResult] = Field(alias="results")


class ComplaintByOdiNumber(ComplaintBaseResponse):
    """Represents the response structure for complaints by ODI number."""
    results: List[ComplaintResult] = Field(alias="results")


class ComplaintFlatFile(BaseModel):
    """
    Represents information about an available complaint flat file for download.
    """
    path: str = Field(..., description="The URL path to the complaint flat file.")
    size: str = Field(..., description="The size of the flat file.")
    updated: str = Field(..., description="The last updated date of the flat file.")

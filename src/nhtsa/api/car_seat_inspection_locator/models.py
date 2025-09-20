from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CarSeatInspectionBaseResponse(BaseModel):
    """Base model for NHTSA Car Seat Inspection Locator API responses."""
    start_latitude: Optional[float] = Field(alias="StartLatitude", default=None)
    start_longitude: Optional[float] = Field(alias="StartLongitude", default=None)
    count: int = Field(alias="Count")
    message: str = Field(alias="Message")


class CarSeatInspectionStation(BaseModel):
    """Represents a single car seat inspection station."""
    contact_first_name: Optional[str] = Field(alias="ContactFirstName", default=None)
    contact_last_name: Optional[str] = Field(alias="ContactLastName", default=None)
    organization: Optional[str] = Field(alias="Organization", default=None)
    address_line_1: Optional[str] = Field(alias="AddressLine1", default=None)
    city: Optional[str] = Field(alias="City", default=None)
    state: Optional[str] = Field(alias="State", default=None)
    zip: Optional[str] = Field(alias="Zip", default=None)
    email: Optional[str] = Field(alias="Email", default=None)
    fax: Optional[str] = Field(alias="Fax", default=None)
    phone1: Optional[str] = Field(alias="Phone1", default=None)
    cps_week_event_flag: Optional[str] = Field(alias="CPSWeekEventFlag", default=None)
    last_updated_date: Optional[datetime] = Field(alias="LastUpdatedDate")
    mobile_station_flag: Optional[str] = Field(alias="MobileStationFlag", default=None)
    counties_served: Optional[str] = Field(alias="CountiesServed", default=None)
    location_latitude: Optional[float] = Field(alias="LocationLatitude", default=None)
    location_longitude: Optional[float] = Field(alias="LocationLongitude", default=None)


class CarSeatInspectionStationList(CarSeatInspectionBaseResponse):
    """Represents a list of car seat inspection stations."""
    results: List[CarSeatInspectionStation] = Field(alias="Results")

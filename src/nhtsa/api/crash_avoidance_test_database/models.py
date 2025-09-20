
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from ...lib.models import APIResponse, Error, Meta, Pagination


class NhtsaCaDbTestData(BaseModel):
    """Represents a single crash avoidance test data entry."""
    test_id: Optional[int] = Field(alias="testID", default=None)
    test_submission_test_id: Optional[int] = Field(alias="testSubmissionTestID", default=None)
    modified_date: Optional[str] = Field(alias="modifiedDate", default=None) # Consider datetime if format is consistent
    json_data: Optional[str] = Field(alias="jsonData", default=None) # JSON string, might need further parsing
    comments: Optional[str] = Field(alias="comments", default=None)
    status: Optional[str] = Field(alias="status", default=None)
    modified_by_user_id: Optional[int] = Field(alias="modifiedbyuserid", default=None)
    test_type: Optional[str] = Field(alias="testType", default=None)
    lab_id: Optional[str] = Field(alias="labId", default=None)


class CurveData(BaseModel):
    """Represents curve data for a crash avoidance test."""
    test_id: Optional[int] = Field(alias="testid", default=None)
    curve_no: Optional[int] = Field(alias="curveno", default=None)
    curve_data: Optional[str] = Field(alias="curveData", default=None) # Might be stringified data or a direct curve data string

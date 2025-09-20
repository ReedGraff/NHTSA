from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class InvestigationFlatFile(BaseModel):
    """
    Represents information about an available defect investigation flat file for download.
    """
    path: str = Field(..., description="The URL path to the investigation flat file.")
    size: str = Field(..., description="The size of the flat file.")
    updated: str = Field(..., description="The last updated date of the flat file.")

# Since the Investigations API primarily deals with downloading flat files as per the provided context,
# there are no direct JSON API responses to model beyond the metadata of the files themselves.
# If there were direct API endpoints for querying investigations (like for recalls or complaints),
# additional Pydantic models would be defined here to represent those response structures.
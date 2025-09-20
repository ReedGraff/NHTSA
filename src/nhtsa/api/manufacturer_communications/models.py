from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ManufacturerCommunicationFlatFile(BaseModel):
    """
    Represents information about an available manufacturer communication flat file for download.
    """
    path: str = Field(..., description="The URL path to the manufacturer communication flat file.")
    size: str = Field(..., description="The size of the flat file.")
    updated: str = Field(..., description="The last updated date of the flat file.")


class TSBInfo(BaseModel):
    """
    Represents key information extracted from a TSB flat file to construct PDF URLs.
    """
    nhtsa_id_number: int = Field(..., description="NHTSA identifier for this communication (Field#1 in TSBS.txt).")
    tsb_document_id: str = Field(..., description="Identifier the manufacturer uses (Field#4 in TSBS.txt).")
    mfr_communication_date: Optional[datetime] = Field(None, description="Date the communication was disseminated by the manufacturer (Field#5 in TSBS.txt).")


# As with Investigations, this module primarily handles static file downloads.
# If there were direct API query endpoints for manufacturer communications,
# additional Pydantic models would be defined here.
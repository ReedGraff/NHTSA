from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field
from datetime import datetime

from ...lib.models import Meta, Pagination, Error # Reusing common meta/pagination

# --- Common nested models for safety issues (Complaints, Recalls, Investigations, Mfr Comms) ---
class SafetyIssueComponent(BaseModel):
    id: int = Field(alias="id")
    name: str = Field(alias="name")
    description: str = Field(alias="description")

class SafetyIssueAssociatedDocument(BaseModel):
    id: Optional[int] = Field(alias="id", default=None)
    file_name: Optional[str] = Field(alias="fileName", default=None)
    file_size: Optional[int] = Field(alias="fileSize", default=None)
    load_date: Optional[datetime] = Field(alias="loadDate", default=None)
    meta_data: Optional[List[Dict[str, Any]]] = Field(alias="metaData", default_factory=list)
    mime_type: Optional[str] = Field(alias="mimeType", default=None)
    summary: Optional[str] = Field(alias="summary", default=None)
    url: Optional[str] = Field(alias="url", default=None)

class SafetyIssueAssociatedProduct(BaseModel):
    type: Optional[str] = Field(alias="type", default=None)
    product_year: Optional[str] = Field(alias="productYear", default=None)
    product_make: Optional[str] = Field(alias="productMake", default=None)
    product_model: Optional[str] = Field(alias="productModel", default=None)
    manufacturer: Optional[str] = Field(alias="manufacturer", default=None)
    size: Optional[str] = Field(alias="size", default=None) # Specific to Tires, but optional

class SafetyIssueComplaint(BaseModel):
    date_filed: Optional[datetime] = Field(alias="dateFiled", default=None)
    date_of_incident: Optional[datetime] = Field(alias="dateOfIncident", default=None)
    nhtsa_id_number: int = Field(alias="nhtsaIdNumber")
    id: int = Field(alias="id")
    number_of_injuries: int = Field(alias="numberOfInjuries")
    number_of_deaths: int = Field(alias="numberOfDeaths")
    fire: bool = Field(alias="fire")
    crash: bool = Field(alias="crash")
    vin: Optional[str] = Field(alias="vin", default=None)
    consumer_location: Optional[str] = Field(alias="consumerLocation", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    components: List[SafetyIssueComponent] = Field(alias="components", default_factory=list)
    associated_documents_count: int = Field(alias="associatedDocumentsCount")
    associated_documents: Union[List[SafetyIssueAssociatedDocument], str] = Field(alias="associatedDocuments", default_factory=list) # Can be list or string "N/A"
    associated_products_count: int = Field(alias="associatedProductsCount")
    associated_products: Union[List[SafetyIssueAssociatedProduct], str] = Field(alias="associatedProducts", default_factory=list) # Can be list or string "N/A"

class SafetyIssueRecallInvestigationInfo(BaseModel):
    nhtsa_campaign_number: Optional[str] = Field(alias="nhtsaCampaignNumber", default=None)
    subject: Optional[str] = Field(alias="subject", default=None)
    report_received_date: Optional[datetime] = Field(alias="reportReceivedDate", default=None)
    summary: Optional[str] = Field(alias="summary", default=None)

class SafetyIssueRecall(BaseModel):
    id: int = Field(alias="id")
    park_it: bool = Field(alias="parkIt")
    park_outside: bool = Field(alias="parkOutSide")
    over_the_air_update: bool = Field(alias="overTheAirUpdate")
    manufacturer: Optional[str] = Field(alias="manufacturer", default=None)
    mfr_campaign_number: Optional[str] = Field(alias="mfrCampaignNumber", default=None)
    nhtsa_campaign_number: Optional[str] = Field(alias="nhtsaCampaignNumber", default=None)
    report_received_date: Optional[datetime] = Field(alias="reportReceivedDate", default=None)
    subject: Optional[str] = Field(alias="subject", default=None)
    summary: Optional[str] = Field(alias="summary", default=None)
    consequence: Optional[str] = Field(alias="consequence", default=None)
    corrective_action: Optional[str] = Field(alias="correctiveAction", default=None)
    potential_number_of_units_affected: Optional[int] = Field(alias="potentialNumberOfUnitsAffected", default=None)
    notes: Optional[str] = Field(alias="notes", default=None)
    components: List[SafetyIssueComponent] = Field(alias="components", default_factory=list)
    investigations: List[Any] = Field(alias="investigations", default_factory=list) # List of basic investigation info
    associated_documents_count: int = Field(alias="associatedDocumentsCount")
    associated_documents: Union[List[SafetyIssueAssociatedDocument], str] = Field(alias="associatedDocuments", default_factory=list)
    associated_products_count: int = Field(alias="associatedProductsCount")
    associated_products: Union[List[SafetyIssueAssociatedProduct], str] = Field(alias="associatedProducts", default_factory=list)

class SafetyIssueInvestigation(BaseModel):
    nhtsa_action_number: Optional[str] = Field(alias="nhtsaActionNumber", default=None)
    subject: Optional[str] = Field(alias="subject", default=None)
    summary: Optional[str] = Field(alias="summary", default=None)
    date_opened: Optional[datetime] = Field(alias="dateOpened", default=None)
    date_closed: Optional[datetime] = Field(alias="dateClosed", default=None)
    type: Optional[str] = Field(alias="type", default=None)
    components: List[SafetyIssueComponent] = Field(alias="components", default_factory=list)
    associated_documents_count: int = Field(alias="associatedDocumentsCount")
    associated_documents: Union[List[SafetyIssueAssociatedDocument], str] = Field(alias="associatedDocuments", default_factory=list)
    associated_products_count: int = Field(alias="associatedProductsCount")
    associated_products: Union[List[SafetyIssueAssociatedProduct], str] = Field(alias="associatedProducts", default_factory=list)
    recalls: List[SafetyIssueRecallInvestigationInfo] = Field(alias="recalls", default_factory=list) # List of basic recall info

class SafetyIssueManufacturerCommunication(BaseModel):
    manufacturer_communication_number: Optional[str] = Field(alias="manufacturerCommunicationNumber", default=None)
    nhtsa_id_number: int = Field(alias="nhtsaIdNumber")
    subject: Optional[str] = Field(alias="subject", default=None)
    summary: Optional[str] = Field(alias="summary", default=None)
    communication_date: Optional[datetime] = Field(alias="communicationDate", default=None)
    components: List[SafetyIssueComponent] = Field(alias="components", default_factory=list)
    associated_documents_count: int = Field(alias="associatedDocumentsCount")
    associated_documents: Union[List[SafetyIssueAssociatedDocument], str] = Field(alias="associatedDocuments", default_factory=list)
    associated_products_count: int = Field(alias="associatedProductsCount")
    associated_products: Union[List[SafetyIssueAssociatedProduct], str] = Field(alias="associatedProducts", default_factory=list)


class SafetyIssuesDetail(BaseModel):
    complaints: List[SafetyIssueComplaint] = Field(alias="complaints", default_factory=list)
    recalls: List[SafetyIssueRecall] = Field(alias="recalls", default_factory=list)
    investigations: List[SafetyIssueInvestigation] = Field(alias="investigations", default_factory=list)
    manufacturer_communications: List[SafetyIssueManufacturerCommunication] = Field(alias="manufacturerCommunications", default_factory=list)

class SafetyIssueByNhtsaIdResult(BaseModel):
    meta: Meta = Field(alias="meta")
    results: List[SafetyIssuesDetail] = Field(alias="results")

class SafetyIssueGeneralEntry(BaseModel):
    id: int = Field(alias="id")
    artemis_id: Optional[int] = Field(alias="artemisId", default=None)
    campaign_id: Optional[str] = Field(alias="campaignId", default=None)
    consequence: Optional[str] = Field(alias="consequence", default=None)
    corrective_action: Optional[str] = Field(alias="correctiveAction", default=None)
    create_date: Optional[datetime] = Field(alias="createDate", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    issue_year: Optional[str] = Field(alias="issueYear", default=None)
    major: Optional[str] = Field(alias="major", default=None)
    manufacturer_name: Optional[str] = Field(alias="manufacturerName", default=None)
    mfr_recall_number: Optional[str] = Field(alias="mfrRecallNumber", default=None)
    mfr_toll_free_number: Optional[str] = Field(alias="mfrTollFreeNumber", default=None)
    nhtsa_campaign_number: Optional[str] = Field(alias="nhtsaCampaignNumber", default=None)
    notes: Optional[str] = Field(alias="notes", default=None)
    over_the_air_update_yn: Optional[bool] = Field(alias="overTheAirUpdateYn", default=None)
    owner_notification_date: Optional[datetime] = Field(alias="ownerNotificationDate", default=None)
    park_outside_yn: Optional[bool] = Field(alias="parkOutsideYn", default=None)
    park_vehicle_yn: Optional[bool] = Field(alias="parkVehicleYn", default=None)
    potaff: Optional[int] = Field(default=None) # Potential affected
    potdef: Optional[int] = Field(default=None) # Potential defective
    recall_573_date: Optional[datetime] = Field(alias="recall573Date", default=None)
    recall_573_received_date: Optional[datetime] = Field(alias="recall573ReceivedDate", default=None)
    recall_type: Optional[str] = Field(alias="recallType", default=None)
    status_update_date: Optional[datetime] = Field(alias="statusUpdateDate", default=None)
    sub: Optional[str] = Field(default=None)
    subject: Optional[str] = Field(alias="subject", default=None)
    synopsis: Optional[str] = Field(alias="synopsis", default=None)
    type_code: Optional[str] = Field(alias="typeCode", default=None)
    update_date: Optional[datetime] = Field(alias="updateDate", default=None)

class SafetyIssuesListResult(BaseModel):
    meta: Meta = Field(alias="meta")
    results: List[SafetyIssueGeneralEntry] = Field(alias="results")
from typing import TYPE_CHECKING, List
from pydantic import parse_obj_as
import logging
import re

from .models import ManufacturerCommunicationFlatFile, TSBInfo

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class ManufacturerCommunicationsAPI:
    """
    API for accessing NHTSA Manufacturer Communications data.
    Note: As per the provided HTML, this API primarily offers data downloads, not direct API calls for filtering.
    The primary interaction is through downloading flat files.
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the ManufacturerCommunicationsAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client

    async def download_flat_file(self, file_url: str) -> bytes:
        """
        Downloads a manufacturer communication flat file.

        Args:
            file_url (str): The URL of the flat file to download.

        Returns:
            bytes: The content of the downloaded file.
        """
        logger.info(f"Downloading manufacturer communication data from: {file_url}")
        # Use the new static_client for downloading files
        response = await self.client._request("GET", file_url, follow_redirects=True, use_static_client=True)
        return response.content

    async def get_flat_file_metadata(self) -> List[ManufacturerCommunicationFlatFile]:
        """
        Returns metadata about available manufacturer communication flat files.
        Note: This information is scraped from the HTML documentation and is static.

        Returns:
            List[ManufacturerCommunicationFlatFile]: A list of Pydantic models describing the available flat files.
        """
        # This data is hardcoded based on the provided HTML snippet.
        metadata = [
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/TSBS.txt", size="6 KB", updated="06/26/2024 11:44:33 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/MFR_COMMS_RECEIVED_1995-1999.zip", size="633 KB", updated="09/19/2025 06:05:02 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/MFR_COMMS_RECEIVED_2000-2004.zip", size="2 MB", updated="09/19/2025 06:05:03 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/MFR_COMMS_RECEIVED_2005-2009.zip", size="885 KB", updated="09/19/2025 06:05:02 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/MFR_COMMS_RECEIVED_2010-2014.zip", size="2 MB", updated="09/19/2025 06:05:03 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/MFR_COMMS_RECEIVED_2015-2019.zip", size="12 MB", updated="09/19/2025 06:05:52 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/MFR_COMMS_RECEIVED_2020-2024.zip", size="11 MB", updated="09/19/2025 06:05:43 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/MFR_COMMS_RECEIVED_2025-2025.zip", size="2 MB", updated="09/19/2025 06:05:06 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/TSBS_RECEIVED_1995-1999.zip", size="1 MB", updated="09/19/2025 06:05:05 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/TSBS_RECEIVED_2000-2004.zip", size="3 MB", updated="09/19/2025 06:05:08 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/TSBS_RECEIVED_2005-2009.zip", size="2 MB", updated="09/19/2025 06:05:07 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/TSBS_RECEIVED_2010-2014.zip", size="4 MB", updated="09/19/2025 06:05:29 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/TSBS_RECEIVED_2015-2019.zip", size="31 MB", updated="09/19/2025 06:12:40 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/TSBS_RECEIVED_2020-2024.zip", size="30 MB", updated="09/19/2025 06:14:17 AM ET"),
            ManufacturerCommunicationFlatFile(path="https://static.nhtsa.gov/odi/ffdd/tsbs/TSBS_RECEIVED_2025-2025.zip", size="5 MB", updated="09/19/2025 06:05:41 AM ET"),
        ]
        return metadata

    async def get_tsb_information_from_flat_file(self, file_url: str) -> List[TSBInfo]:
        """
        Downloads a TSBS flat file (e.g., TSBS_RECEIVED_2025-2025.txt) and parses its content
        to extract TSB information including NHTSA ID and TSB/Document ID.

        Args:
            file_url (str): The URL of the TSBS .txt flat file to download.

        Returns:
            List[TSBInfo]: A list of Pydantic models, each representing a TSB entry.
        """
        logger.info(f"Fetching TSB information from flat file: {file_url}")
        file_content = await self.download_flat_file(file_url)

        decoded_content = file_content.decode('utf-8', errors='ignore')
        lines = decoded_content.strip().split('\n')

        tsb_data: List[TSBInfo] = []
        # Assuming the first few lines are headers/metadata and actual data starts later.
        # Based on RCL.txt, there's a FIELDS section. We need to skip this.
        # A more robust solution would dynamically find the start of data.
        # For now, we'll assume a fixed skip or look for the first line that looks like data.

        # Skip lines until we find something that looks like data or a specific header pattern
        data_started = False
        for line in lines:
            if not data_started and re.match(r'^\d+\t', line): # heuristic: starts with digits then tab
                data_started = True
            if not data_started:
                continue

            # Assuming tab-delimited as per RCL.txt, TSBS.txt should be similar
            parts = line.strip().split('\t')
            if len(parts) >= 10: # Based on the TSBS.txt structure, minimum required fields for NHTSA ID and TSB ID
                try:
                    nhtsa_id = int(parts[0]) # Field#1 "NHTSA ID Number"
                    tsb_document_id = parts[3] # Field#4 "TSB/Document ID"
                    mfr_comm_date_str = parts[4] # Field#5 "Mfr Communication Date"
                    # Attempt to parse the date, handling potential errors
                    mfr_communication_date = None
                    if mfr_comm_date_str and mfr_comm_date_str != "null":
                        try:
                            # Dates in TSBS.txt are YYYYMMDD
                            mfr_communication_date = datetime.strptime(mfr_comm_date_str, '%Y%m%d')
                        except ValueError:
                            logger.warning(f"Could not parse Mfr Communication Date: {mfr_comm_date_str} for NHTSA ID: {nhtsa_id}")

                    tsb_data.append(TSBInfo(
                        nhtsa_id_number=nhtsa_id,
                        tsb_document_id=tsb_document_id,
                        mfr_communication_date=mfr_communication_date
                    ))
                except ValueError as ve:
                    logger.warning(f"Could not parse line as TSBInfo, skipping: {line}. Error: {ve}", exc_info=True)
                except IndexError as ie:
                    logger.warning(f"Line had fewer parts than expected, skipping: {line}. Error: {ie}", exc_info=True)
        return tsb_data
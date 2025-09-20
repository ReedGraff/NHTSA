from typing import TYPE_CHECKING, List, Optional
from pydantic import parse_obj_as
import logging

from .models import InvestigationFlatFile

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class InvestigationsAPI:
    """
    API for accessing NHTSA Defect Investigations data.
    Note: As per the provided HTML, this API only offers data downloads, not direct API calls for filtering.
    The primary interaction is through downloading flat files.
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the InvestigationsAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client

    async def download_flat_file(self, file_url: str) -> bytes:
        """
        Downloads a defect investigation flat file.

        Args:
            file_url (str): The URL of the flat file to download.

        Returns:
            bytes: The content of the downloaded file.
        """
        logger.info(f"Downloading investigation data from: {file_url}")
        response = await self.client._request("GET", file_url, follow_redirects=True, base_url="")
        return response.content

    async def get_flat_file_metadata(self) -> List[InvestigationFlatFile]:
        """
        Returns metadata about available investigation flat files.
        Note: This information is scraped from the HTML documentation and is static.
        In a real-world scenario, you might want to consider dynamically parsing the HTML
        or maintaining this metadata externally if it changes frequently.

        Returns:
            List[InvestigationFlatFile]: A list of Pydantic models describing the available flat files.
        """
        # This data is hardcoded based on the provided HTML snippet.
        # If this data changes, this method needs to be updated.
        metadata = [
            InvestigationFlatFile(
                path="https://static.nhtsa.gov/odi/ffdd/inv/FLAT_INV.zip",
                size="43 MB",
                updated="09/19/2025 05:14:22 AM ET"
            ),
            InvestigationFlatFile(
                path="https://static.nhtsa.gov/odi/ffdd/inv/INV.txt",
                size="2 KB",
                updated="09/19/2025 05:14:23 AM ET"
            ),
        ]
        return metadata

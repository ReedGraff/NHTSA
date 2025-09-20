from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class StaticFilesAPI:
    """
    API for downloading static files directly from static.nhtsa.gov.
    These are not JSON API endpoints but direct links to documents/archives.
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the StaticFilesAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client

    async def download_file(self, file_url: str) -> bytes:
        """
        Downloads a generic static file given its full URL.

        Args:
            file_url (str): The full URL of the static file to download.

        Returns:
            bytes: The content of the downloaded file.

        Raises:
            httpx.RequestError: If the download fails.
        """
        logger.info(f"Downloading static file from: {file_url}")
        # Use a generic client base_url="" or explicitly provide the static_base_url if different
        response = await self.client._request("GET", file_url, follow_redirects=True, base_url="")
        return response.content

    async def get_manufacturer_communication_pdf(self, year: int, nhtsa_id_number: int, sequential_number: int = 1) -> bytes:
        """
        Constructs the URL for a specific Manufacturer Communication PDF and downloads it.

        The URL format is: https://static.nhtsa.gov/odi/tsbs/{year}/MC-{nhtsa_id_number}-{sequential_number}.pdf

        Args:
            year (int): The year the communication was received (from the file path, e.g., 2025).
            nhtsa_id_number (int): The NHTSA ID Number (from Field#1 in TSBS.txt, e.g., 11022868).
            sequential_number (int): A sequential number for the PDF (e.g., 1 for '0001').

        Returns:
            bytes: The content of the downloaded PDF file.

        Raises:
            httpx.RequestError: If the download fails.
        """
        # Format sequential_number to be 4 digits, e.g., 1 -> 0001
        formatted_sequential_number = f"{sequential_number:04d}"
        file_url = f"https://static.nhtsa.gov/odi/tsbs/{year}/MC-{nhtsa_id_number}-{formatted_sequential_number}.pdf"
        return await self.download_file(file_url)
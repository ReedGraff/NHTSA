from typing import TYPE_CHECKING, List, Optional
from pydantic import parse_obj_as
import logging

from .models import ComplaintByVehicle, ModelYear, Make, Model, ComplaintByOdiNumber, ComplaintFlatFile

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class ComplaintsAPI:
    """
    API for fetching NHTSA Consumer Complaints information.
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the ComplaintsAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client

    async def get_complaints_by_vehicle(self, make: str, model: str, model_year: int) -> ComplaintByVehicle:
        """
        Make the request to get the complaints for the required combination of Model Year, Make, and Model.

        Args:
            make (str): The make of the vehicle.
            model (str): The model of the vehicle.
            model_year (int): The model year of the vehicle.

        Returns:
            ComplaintByVehicle: A Pydantic model representing a list of complaints for the given vehicle.
        """
        url = f"/complaints/complaintsByVehicle?make={make}&model={model}&modelYear={model_year}"
        response = await self.client._request("GET", url)
        return parse_obj_as(ComplaintByVehicle, response.json())

    async def get_all_model_years(self) -> ModelYear:
        """
        Request a list of available Model Years for a given product type (Vehicle) for complaints.

        Returns:
            ModelYear: A Pydantic model representing a list of available model years.
        """
        url = "/products/vehicle/modelYears?issueType=c"
        response = await self.client._request("GET", url)
        return parse_obj_as(ModelYear, response.json())

    async def get_all_makes_for_model_year(self, model_year: int) -> Make:
        """
        Request a list of vehicle Makes by providing a specific vehicle Model Year for complaints.

        Args:
            model_year (int): The model year to filter by.

        Returns:
            Make: A Pydantic model representing a list of vehicle makes for that model year.
        """
        url = f"/products/vehicle/makes?modelYear={model_year}&issueType=c"
        response = await self.client._request("GET", url)
        return parse_obj_as(Make, response.json())

    async def get_all_models_for_make_and_model_year(self, model_year: int, make: str) -> Model:
        """
        Request a list of vehicle Models by providing the vehicle Model Year and Make for complaints.

        Args:
            model_year (int): The model year to filter by.
            make (str): The make to filter by.

        Returns:
            Model: A Pydantic model representing a list of models for the given model year and make.
        """
        url = f"/products/vehicle/models?modelYear={model_year}&make={make}&issueType=c"
        response = await self.client._request("GET", url)
        return parse_obj_as(Model, response.json())

    async def get_complaints_by_odi_number(self, odi_number: int) -> ComplaintByOdiNumber:
        """
        Request a list of complaints by providing ODI number.

        Args:
            odi_number (int): The ODI number to filter by.

        Returns:
            ComplaintByOdiNumber: A Pydantic model representing a list of complaints for the specified ODI number.
        """
        url = f"/complaints/odinumber?odinumber={odi_number}"
        response = await self.client._request("GET", url)
        return parse_obj_as(ComplaintByOdiNumber, response.json())

    async def download_flat_file(self, file_url: str) -> bytes:
        """
        Downloads a complaint flat file.

        Args:
            file_url (str): The URL of the flat file to download.

        Returns:
            bytes: The content of the downloaded file.
        """
        logger.info(f"Downloading complaint data from: {file_url}")
        response = await self.client._request("GET", file_url, follow_redirects=True, base_url="")
        return response.content

    async def get_flat_file_metadata(self) -> List[ComplaintFlatFile]:
        """
        Returns metadata about available complaint flat files.
        Note: This information is scraped from the HTML documentation and is static.

        Returns:
            List[ComplaintFlatFile]: A list of Pydantic models describing the available flat files.
        """
        # This data is hardcoded based on the provided HTML snippet.
        metadata = [
            ComplaintFlatFile(path="https://static.nhtsa.gov/odi/ffdd/cmpl/FLAT_CMPL.zip", size="331 MB", updated="09/19/2025 06:31:02 AM ET"),
            ComplaintFlatFile(path="https://static.nhtsa.gov/odi/ffdd/cmpl/Import_Instructions_Excel_All.pdf", size="672 KB", updated="02/28/2022 08:52:26 AM ET"),
            ComplaintFlatFile(path="https://static.nhtsa.gov/odi/ffdd/cmpl/COMPLAINTS_RECEIVED_2025-2025.zip", size="14 MB", updated="09/19/2025 05:36:14 AM ET"),
            ComplaintFlatFile(path="https://static.nhtsa.gov/odi/ffdd/cmpl/COMPLAINTS_RECEIVED_2020-2024.zip", size="72 MB", updated="09/18/2025 04:56:42 PM ET"),
            ComplaintFlatFile(path="https://static.nhtsa.gov/odi/ffdd/cmpl/COMPLAINTS_RECEIVED_2015-2019.zip", size="77 MB", updated="09/12/2025 05:48:56 AM ET"),
            ComplaintFlatFile(path="https://static.nhtsa.gov/odi/ffdd/cmpl/COMPLAINTS_RECEIVED_2010-2014.zip", size="69 MB", updated="09/12/2025 05:44:57 AM ET"),
            ComplaintFlatFile(path="https://static.nhtsa.gov/odi/ffdd/cmpl/COMPLAINTS_RECEIVED_2005-2009.zip", size="44 MB", updated="09/12/2025 05:41:46 AM ET"),
            ComplaintFlatFile(path="https://static.nhtsa.gov/odi/ffdd/cmpl/COMPLAINTS_RECEIVED_2000-2004.zip", size="40 MB", updated="08/23/2025 05:42:23 AM ET"),
            ComplaintFlatFile(path="https://static.nhtsa.gov/odi/ffdd/cmpl/COMPLAINTS_RECEIVED_1995-1999.zip", size="14 MB", updated="06/20/2025 07:32:47 AM ET"),
            ComplaintFlatFile(path="https://static.nhtsa.gov/odi/ffdd/cmpl/Import_Instructions_Excel_5-year.pdf", size="604 KB", updated="02/28/2022 08:52:25 AM ET"),
            ComplaintFlatFile(path="https://static.nhtsa.gov/odi/ffdd/cmpl/Import_Instructions_Access.pdf", size="973 KB", updated="02/28/2022 08:52:25 AM ET"),
            ComplaintFlatFile(path="https://static.nhtsa.gov/odi/ffdd/cmpl/CMPL.txt", size="9 KB", updated="04/20/2022 12:37:13 PM ET"),
        ]
        return metadata

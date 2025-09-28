from typing import TYPE_CHECKING, List, Optional, Union, Set, Any
import asyncio
import logging
import re

# Import necessary models from other API modules
from ...api.vin_decoding.models import VinDecodeFlatResult, VinDecodeFlatEntry
from ...api.products.models import VehicleByYmmtResult, VehicleDetailsResult, SafetyIssueManufacturerCommunication
from ...api.safety_issues.models import SafetyIssueByNhtsaIdResult, SafetyIssueAssociatedDocument

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class ToolsAPI:
    """
    API for multi-step, pre-built workflows that combine calls to multiple NHTSA endpoints
    to achieve a specific data retrieval goal. This aims to simplify common, complex
    data retrieval patterns for the user.
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the ToolsAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client

    async def get_tsb_by_mfg_number_only(self, vin: str, mfg_number: str) -> Set[str]:
        """
        raises NotImplementedError
        """
        raise NotImplementedError("This requires accumulating all nhtsa ids, since NHTSA does not support search by mfg number directly. you would need to make a cronjob to get all mfg numbers and index them yourself. Email me if you need to do this, I already have this set up and can give you api access.")

    async def get_tsb_by_mfg_number(self, vin: str, mfg_number: str) -> Set[str]:
        """
        Retrieves all unique document URLs (e.g., PDFs) for a specific Manufacturer Communication Number
        associated with a given VIN. This involves a multi-step process:
        1. Decodes the VIN to get basic vehicle information (Make, Model, Model Year).
        2. Searches for corresponding Vehicle IDs using the obtained Make, Model, and Model Year.
        3. For each identified Vehicle ID, retrieves its detailed safety issues, specifically
           Manufacturer Communications.
        4. Filters these communications to find entries matching the provided Manufacturer
           Communication Number.
        5. For each matching communication, it performs a *second* API call to `safetyIssues/byNhtsaId`
           to get the full details of that specific NHTSA ID, which includes the direct PDF URLs
           within `associatedDocuments`.

        Args:
            vin (str): The Vehicle Identification Number of the vehicle.
            mfg_number (str): The internal Manufacturer Communication Number (e.g., "N212355740").

        Returns:
            Set[str]: A set of unique URLs to the associated documents (e.g., PDF files).
                      Returns an empty set if no matching communications or documents are found,
                      or if an error occurs.
        """
        urls: Set[str] = set()
        try:
            logger.info(f"\n--- Step 1: Decoding VIN {vin} to get basic vehicle info ---")
            decoded_vin_flat: VinDecodeFlatResult = await self.client.vin_decoding.decode_vin_flat_format(
                vin=vin
            )
            # logger.debug(f"Decoded VIN Flat Result: {decoded_vin_flat}")
            decoded_vin = decoded_vin_flat.results[0]

            logger.info(f"\n--- Step 2: Searching for Vehicle ID using Make, Model, and Model Year ---")
            vehicle_by_ymmt_results: VehicleByYmmtResult = await self.client.products.get_vehicle_by_ymmt(
                model_year=decoded_vin.model_year,
                make=decoded_vin.make,
                model=decoded_vin.model
            )
            # logger.debug(f"Vehicle By YMMT Results: {vehicle_by_ymmt_results}")
            vehicle_ids = [vehicle.vehicle_id for vehicle in vehicle_by_ymmt_results.results[:5]] # Limit to first 5. Most options here will only be differences in trim or series, not major changes, so this shouldn't really ever be > 5 results anyways.

            logger.info(f"\n--- Step 3: Retrieving Manufacturer Communications for Vehicle IDs {vehicle_ids} ---")
            vehicle_safety_issues_ids = set() # set to remove duplicates
            tasks = [
                self.client.products.get_vehicle_details_by_id(
                    vehicle_id=vehicle,
                    data="manufacturercommunications",
                    product_detail="all" # Keep this to get as much detail as possible in the first call
                ) for vehicle in vehicle_ids
            ]
            vehicle_details_list: List[VehicleDetailsResult] = await asyncio.gather(*tasks)
            for vehicle, vehicle_details in zip(vehicle_ids, vehicle_details_list):
                # with open(f"vehicle_{vehicle}_details.json", "w", encoding="utf-8", newline="\n") as f:
                #     f.write(vehicle_details.model_dump_json(indent=4))
                vehicle_safety_issues_ids.update([result.nhtsa_id_number for result in vehicle_details.results[0].safety_issues.manufacturer_communications if result.manufacturer_communication_number == mfg_number])
                # step 4 could be nested here, but taking it out to remove duplicates & allow for high throughput async processing
                # this output also technically contains the urls... but we're not going to use them in case of edge cases... We know the url for using the nhtsa id

            logger.info(f"\n--- Step 4: Retrieving Documents for NHTSA IDs {vehicle_safety_issues_ids} ---")
            urls = set()
            issues = list(vehicle_safety_issues_ids)
            issue_tasks = [self.client.safety_issues.get_safety_issues_by_nhtsa_id(nhtsa_id=issue) for issue in issues]
            detailed_responses: List[SafetyIssueByNhtsaIdResult] = await asyncio.gather(*issue_tasks)
            for issue, detailed_safety_issues_response in zip(issues, detailed_responses):
                # logger.debug(f"Detailed Safety Issue for NHTSA ID {issue}: {detailed_safety_issues_response.model_dump_json(indent=4)}")
                for result in (detailed_safety_issues_response.results or []):
                    for mc in (getattr(result, "manufacturer_communications", None) or []):
                        for doc in (getattr(mc, "associated_documents", None) or []):
                            if getattr(doc, "url", None):
                                urls.add(doc.url)

            logger.info(f"\n--- Completed: Found {len(urls)} document URLs for Manufacturer Communication Number {mfg_number} ---")
            return urls

        except Exception as e:
            logger.error(f"An unexpected error occurred during the TSB retrieval workflow for VIN '{vin}' and MFG number '{mfg_number}': {e}", exc_info=True)
            return set()

from typing import TYPE_CHECKING, List, Optional
from pydantic import parse_obj_as
import logging
from datetime import date, datetime

from .models import SafetyIssueByNhtsaIdResult, SafetyIssuesListResult

if TYPE_CHECKING:
    from ...client import NhtsaClient

logger = logging.getLogger(__name__)


class SafetyIssuesAPI:
    """
    API for querying NHTSA Safety Issues, which aggregates complaints, recalls,
    investigations, and manufacturer communications by NHTSA ID or generally.
    """
    def __init__(self, client: "NhtsaClient"):
        """
        Initializes the SafetyIssuesAPI.

        Args:
            client (NhtsaClient): The main client instance.
        """
        self.client = client

    async def get_safety_issues_by_nhtsa_id(self, nhtsa_id: int) -> SafetyIssueByNhtsaIdResult:
        """
        Retrieves detailed safety issues (complaints, recalls, investigations,
        manufacturer communications) for a specific NHTSA ID.

        Args:
            nhtsa_id (int): The NHTSA ID number.

        Returns:
            SafetyIssueByNhtsaIdResult: A Pydantic model representing the aggregated safety issues.
        """
        url = f"/safetyIssues/byNhtsaId"
        params = {"nhtsaId": nhtsa_id}
        response = await self.client._request("GET", url, params=params)
        return parse_obj_as(SafetyIssueByNhtsaIdResult, response.json())

    async def search_safety_issues(
        self,
        offset: int = 0,
        max_results: int = 10,
        sort_by: Optional[str] = "id",
        order: Optional[str] = None # 'asc' or 'desc'
    ) -> SafetyIssuesListResult:
        """
        Searches for general safety issues with pagination and sorting.

        Args:
            offset (int): The starting offset for results (default 0).
            max_results (int): The maximum number of results to return (default 10).
            sort_by (Optional[str]): Field to sort the results by (e.g., "id", "createDate").
            order (Optional[str]): Sort order ("asc" or "desc").

        Returns:
            SafetyIssuesListResult: A Pydantic model representing a list of general safety issue entries.
        """
        url = f"/safetyIssues"
        params = {
            "offset": offset,
            "max": max_results,
            "sort": sort_by
        }
        if order:
            params["order"] = order
        response = await self.client._request("GET", url, params=params)
        return parse_obj_as(SafetyIssuesListResult, response.json())
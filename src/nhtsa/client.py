import httpx
import logging
import asyncio
import os
import pickle
import traceback
from typing import Optional, Dict, Any

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress excessive logging from httpx
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


class NhtsaClient:
    """
    The main client for interacting with the NHTSA APIs.
    This client manages HTTP requests, cookies, and rate limiting.
    """
    BASE_URL = "https://api.nhtsa.gov"
    VPIC_BASE_URL = "https://vpic.nhtsa.dot.gov/api"
    STATIC_FILES_BASE_URL = "https://static.nhtsa.gov"
    NRD_BASE_URL = "https://nrd.api.nhtsa.dot.gov" # New base URL for NRD APIs

    def __init__(self, max_concurrent_requests: int = 5, requests_per_second: int = 2, session_data: Optional[bytes] = None):
        """
        Initializes the NhtsaClient.

        Args:
            max_concurrent_requests (int): The maximum number of concurrent HTTP requests.
            requests_per_second (int): The maximum number of requests allowed per second.
            session_data (Optional[bytes]): Pickled session data to restore a previous session.
        """
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-US,en;q=0.9",
                "user-agent": "NHTSA-SDK/1.0 (Python)",
            },
            follow_redirects=True,
            timeout=30.0,
            limits=httpx.Limits(max_connections=max_concurrent_requests, max_keepalive_connections=max_concurrent_requests)
        )
        self.vpic_client = httpx.AsyncClient(
            base_url=self.VPIC_BASE_URL,
            headers={
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-US,en;q=0.9",
                "user-agent": "NHTSA-SDK/1.0 (Python)",
            },
            follow_redirects=True,
            timeout=30.0,
            limits=httpx.Limits(max_connections=max_concurrent_requests, max_keepalive_connections=max_concurrent_requests)
        )
        self.static_client = httpx.AsyncClient(
            base_url=self.STATIC_FILES_BASE_URL,
            headers={
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "user-agent": "NHTSA-SDK/1.0 (Python)",
            },
            follow_redirects=True,
            timeout=60.0,
            limits=httpx.Limits(max_connections=max_concurrent_requests, max_keepalive_connections=max_concurrent_requests)
        )
        # New client for NRD APIs
        self.nrd_client = httpx.AsyncClient(
            base_url=self.NRD_BASE_URL,
            headers={
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-US,en;q=0.9",
                "user-agent": "NHTSA-SDK/1.0 (Python)",
            },
            follow_redirects=True,
            timeout=30.0,
            limits=httpx.Limits(max_connections=max_concurrent_requests, max_keepalive_connections=max_concurrent_requests)
        )


        self.session_cookies: Dict[str, str] = {}
        
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.request_delay = 1.0 / requests_per_second

        # Initialize API modules
        from .api.safetyservice.index import SafetyServiceAPI
        from .api.recalls.index import RecallsAPI
        from .api.investigations.index import InvestigationsAPI
        from .api.complaints.index import ComplaintsAPI
        from .api.manufacturer_communications.index import ManufacturerCommunicationsAPI
        from .api.car_seat_inspection_locator.index import CarSeatInspectionLocatorAPI
        from .api.vin_decoding.index import VinDecodingAPI
        from .api.static_files.index import StaticFilesAPI
        # New API imports
        from .api.vehicle_crash_test_database.index import VehicleCrashTestDatabaseAPI
        from .api.biomechanics_test_database.index import BiomechanicsTestDatabaseAPI
        from .api.component_test_database.index import ComponentTestDatabaseAPI
        from .api.crash_avoidance_test_database.index import CrashAvoidanceTestDatabaseAPI


        self.safety_service = SafetyServiceAPI(self)
        self.recalls = RecallsAPI(self)
        self.investigations = InvestigationsAPI(self)
        self.complaints = ComplaintsAPI(self)
        self.manufacturer_communications = ManufacturerCommunicationsAPI(self)
        self.car_seat_inspection_locator = CarSeatInspectionLocatorAPI(self)
        self.vin_decoding = VinDecodingAPI(self)
        self.static_files = StaticFilesAPI(self)
        # New API instances
        self.vehicle_crash_test_database = VehicleCrashTestDatabaseAPI(self)
        self.biomechanics_test_database = BiomechanicsTestDatabaseAPI(self)
        self.component_test_database = ComponentTestDatabaseAPI(self)
        self.crash_avoidance_test_database = CrashAvoidanceTestDatabaseAPI(self)


        # Load from session if provided
        if session_data:
            self._load_from_session_data(session_data)

    def get_session_data(self) -> bytes:
        """
        Serializes the current session state (cookies) into bytes.

        Returns:
            bytes: A pickled dictionary containing the session state.
        """
        try:
            data = {
                "session_cookies": dict(self.client.cookies),
                # Include cookies from other clients if they manage separate cookies
                "vpic_cookies": dict(self.vpic_client.cookies),
                "static_cookies": dict(self.static_client.cookies),
                "nrd_cookies": dict(self.nrd_client.cookies),
            }
            return pickle.dumps(data)
        except Exception as e:
            logger.error(f"Failed to serialize NHTSA session data: {e}", exc_info=True)
            return b''

    def _load_from_session_data(self, session_data: bytes) -> bool:
        """
        Loads a session from a bytes object.

        Args:
            session_data (bytes): The pickled session data.

        Returns:
            bool: True if the session was loaded successfully, False otherwise.
        """
        if not session_data:
            return False
        try:
            data = pickle.loads(session_data)
            self.session_cookies = data.get("session_cookies", {})
            for name, value in self.session_cookies.items():
                self.client.cookies.set(name, value)
                self.vpic_client.cookies.set(name, value)
                self.static_client.cookies.set(name, value)
                self.nrd_client.cookies.set(name, value) # Apply cookies to new NRD client

            # Load specific client cookies if they were stored separately
            for name, value in data.get("vpic_cookies", {}).items():
                self.vpic_client.cookies.set(name, value)
            for name, value in data.get("static_cookies", {}).items():
                self.static_client.cookies.set(name, value)
            for name, value in data.get("nrd_cookies", {}).items():
                self.nrd_client.cookies.set(name, value)


            logger.info("Successfully loaded NHTSA session from provided data.")
            return True
        except Exception as e:
            logger.error(f"Failed to load NHTSA session from data: {e}", exc_info=True)
            return False

    async def _request(self, method: str, path: str, use_vpic_client: bool = False, use_static_client: bool = False, use_nrd_client: bool = False, **kwargs) -> httpx.Response:
        """
        Internal request handler with rate limiting and a retry mechanism for timeouts.

        Args:
            method (str): The HTTP method (e.g., "GET", "POST").
            path (str): The URL path for the request.
            use_vpic_client (bool): If True, use the vPIC client.
            use_static_client (bool): If True, use the static files client.
            use_nrd_client (bool): If True, use the NRD client. # New parameter
            **kwargs: Additional keyword arguments to pass to httpx.AsyncClient.request.

        Returns:
            httpx.Response: The HTTP response object.

        Raises:
            httpx.RequestError: If an HTTP request fails.
        """
        if use_static_client:
            current_client = self.static_client
        elif use_vpic_client:
            current_client = self.vpic_client
        elif use_nrd_client: # Use NRD client
            current_client = self.nrd_client
        else:
            current_client = self.client

        async with self.semaphore:
            await asyncio.sleep(self.request_delay)
            for attempt in range(3):  # Try up to 3 times
                try:
                    response = await current_client.request(method, path, **kwargs)
                    response.raise_for_status()
                    # Update session cookies after each successful request
                    self.session_cookies.update(response.cookies)
                    for name, value in response.cookies.items():
                        # Propagate cookies to all clients
                        self.client.cookies.set(name, value)
                        self.vpic_client.cookies.set(name, value)
                        self.static_client.cookies.set(name, value)
                        self.nrd_client.cookies.set(name, value)
                    return response
                except httpx.RequestError as e:
                    logger.warning(f"Request to {path} failed on attempt {attempt + 1}: {e}. Retrying...", exc_info=True)
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                except Exception as e:
                    logger.error(f"An unexpected error occurred during request to {path}: {e}", exc_info=True)
                    raise
            raise httpx.RequestError(f"Failed to complete request to {path} after multiple retries.")

    async def close(self):
        """
        Closes the httpx client sessions.
        """
        await self.client.aclose()
        await self.vpic_client.aclose()
        await self.static_client.aclose()
        await self.nrd_client.aclose() # Close the new NRD client
        logger.info("HTTP client sessions closed.")

import httpx
import logging
import asyncio
# import os
import pickle
# import traceback
import time
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
    NRD_BASE_URL = "https://nrd.api.nhtsa.dot.gov"

    def __init__(self, max_concurrent_requests: int = 5, nhtsa_requests_per_minute: int = 100, session_data: Optional[bytes] = None):
        """
        Initializes the NhtsaClient.

        Args:
            max_concurrent_requests (int): The maximum number of concurrent HTTP requests allowed by httpx.
            nhtsa_requests_per_minute (int): The maximum number of requests allowed per minute for the NHTSA API
                                             to respect the server's rate limit.
            session_data (Optional[bytes]): Pickled session data to restore a previous session.
        """
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-US,en;q=0.9",
                # "user-agent": "NHTSA-SDK/1.0 (Python)",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
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
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
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
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
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
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            },
            follow_redirects=True,
            timeout=30.0,
            limits=httpx.Limits(max_connections=max_concurrent_requests, max_keepalive_connections=max_concurrent_requests)
        )

        self.session_cookies: Dict[str, str] = {}
        
        # Concurrency control for internal requests
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        # Global Rate limiting for NHTSA server (100 requests/minute)
        self.nhtsa_requests_per_minute = nhtsa_requests_per_minute
        self.nhtsa_request_interval = 60.0 / self.nhtsa_requests_per_minute # Seconds per request (e.g., 0.6 seconds)
        self._last_global_request_completion_time = 0.0 # Tracks when the last request (across all concurrent ones) finished its work and rate limiting sleep
        self._global_rate_limit_lock = asyncio.Lock() # Protects access to _last_global_request_completion_time

        # Initialize API modules
        from .api.safetyservice.index import SafetyServiceAPI
        from .api.recalls.index import RecallsAPI
        from .api.investigations.index import InvestigationsAPI
        from .api.complaints.index import ComplaintsAPI
        from .api.manufacturer_communications.index import ManufacturerCommunicationsAPI
        from .api.car_seat_inspection_locator.index import CarSeatInspectionLocatorAPI
        from .api.vin_decoding.index import VinDecodingAPI
        from .api.static_files.index import StaticFilesAPI
        from .api.vehicle_crash_test_database.index import VehicleCrashTestDatabaseAPI
        from .api.biomechanics_test_database.index import BiomechanicsTestDatabaseAPI
        from .api.component_test_database.index import ComponentTestDatabaseAPI
        from .api.crash_avoidance_test_database.index import CrashAvoidanceTestDatabaseAPI
        from .api.nhtsa_database_code_library.index import NhtsaDatabaseCodeLibraryAPI
        from .api.safety_issues.index import SafetyIssuesAPI
        from .api.products.index import ProductsAPI
        from .api.tag_lookup.index import TagLookupAPI
        from .api.vin_lookup_web.index import VinLookupWebAPI
        from .api.tools.index import ToolsAPI


        self.safety_service = SafetyServiceAPI(self)
        self.recalls = RecallsAPI(self)
        self.investigations = InvestigationsAPI(self)
        self.complaints = ComplaintsAPI(self)
        self.manufacturer_communications = ManufacturerCommunicationsAPI(self)
        self.car_seat_inspection_locator = CarSeatInspectionLocatorAPI(self)
        self.vin_decoding = VinDecodingAPI(self)
        self.static_files = StaticFilesAPI(self)
        self.vehicle_crash_test_database = VehicleCrashTestDatabaseAPI(self)
        self.biomechanics_test_database = BiomechanicsTestDatabaseAPI(self)
        self.component_test_database = ComponentTestDatabaseAPI(self)
        self.crash_avoidance_test_database = CrashAvoidanceTestDatabaseAPI(self)
        self.nhtsa_database_code_library = NhtsaDatabaseCodeLibraryAPI(self)
        self.safety_issues = SafetyIssuesAPI(self)
        self.products = ProductsAPI(self)
        self.tag_lookup = TagLookupAPI(self)
        self.vin_lookup_web = VinLookupWebAPI(self)
        self.tools = ToolsAPI(self)


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
            use_nrd_client (bool): If True, use the NRD client.
            **kwargs: Additional keyword arguments to pass to httpx.AsyncClient.request.

        Returns:
            httpx.Response: The HTTP response object.

        Raises:
            httpx.RequestError: If an HTTP request fails after multiple retries.
        """
        if use_static_client:
            current_client = self.static_client
        elif use_vpic_client:
            current_client = self.vpic_client
        elif use_nrd_client:
            current_client = self.nrd_client
        else:
            current_client = self.client

        response = None
        for attempt in range(3):  # Try up to 3 times
            try:
                # 1. Acquire the semaphore to limit concurrent HTTP calls to the server
                async with self.semaphore:
                    # 2. Acquire the global rate limit lock to determine if we need to wait
                    async with self._global_rate_limit_lock:
                        now = time.monotonic()
                        # Calculate when the earliest the *next* request (globally) can begin its network operation.
                        next_allowed_time = self._last_global_request_completion_time + self.nhtsa_request_interval
                        sleep_duration = next_allowed_time - now
                        if sleep_duration > 0:
                            await asyncio.sleep(sleep_duration)
                        # Mark the completion time for this request's rate-limiting slot.
                        # This ensures the global rate is maintained, by dictating when the *next* request can start.
                        self._last_global_request_completion_time = time.monotonic()

                    # 3. Make the actual HTTP request (this happens outside the _global_rate_limit_lock,
                    #    allowing concurrent HTTP operations up to max_concurrent_requests once past the rate limit check)
                    response = await current_client.request(method, path, **kwargs)
                    response.raise_for_status() # This will raise for 4xx/5xx responses

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
                # A request failed (e.g., network error, timeout, or HTTP status error caught by raise_for_status)
                logger.warning(f"Request to {path} failed on attempt {attempt + 1}: {e}. Retrying...", exc_info=True)
                # This failed attempt still consumed a "slot" in terms of rate limiting.
                # The _last_global_request_completion_time was already updated when the request *started* its slot.
                # So, no need to update it again here as it correctly reflects the last point in time a request *began* its slot.
                await asyncio.sleep(2 ** attempt)  # Exponential backoff before next retry
            except Exception as e:
                logger.error(f"An unexpected error occurred during request to {path}: {e}", exc_info=True)
                # For any other exception, re-raise immediately. The rate limit timestamp was set at slot start.
                raise
        # If all retries fail, raise the last encountered error.
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

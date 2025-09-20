# NHTSA SDK
[![PyPI version](https://badge.fury.io/py/nhtsa.svg)](https://badge.fury.io/py/nhtsa)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An unofficial, asynchronous Python SDK for the National Highway Traffic Safety Administration (NHTSA) APIs.

## Overview

This SDK provides a simple, asynchronous client to programmatically access various NHTSA datasets and services, including vehicle safety ratings, recalls, investigations, consumer complaints, manufacturer communications, VIN decoding, and detailed crash/biomechanics/component test data. It handles HTTP requests, rate limiting, and parsing of API responses into clean, consistent Pydantic models. It also provides direct access to static data files for bulk downloads.

## Key Features

<details>
<summary>Expand to see Key Features</summary>

-   **Asynchronous:** Built with `httpx` and `asyncio` for non-blocking I/O.
-   **Comprehensive API Coverage:** Covers all specified API endpoints for Safety Ratings, Recalls, Investigations, Complaints, Manufacturer Communications, Car Seat Inspection Locator, VIN Decoding, Vehicle Crash Test Database, Biomechanics Test Database, Component Test Database, and Crash Avoidance Test Database.
-   **Structured Output:** Converts JSON, and handles parsing of text-based static files into easy-to-use Pydantic models.
-   **Modular Design:** Endpoints are organized into logical API modules (e.g., `recalls`, `vin_decoding`).
-   **Static File Handling:** Provides utilities to download static data files (CSV, PDF, ZIP) directly from NHTSA's static content servers.
-   **Session Management:** Internally manages HTTP sessions and cookies, although most NHTSA endpoints are stateless and do not require complex authentication.
-   **Robust Error Handling & Logging:** Integrates Python's `logging` module for verbose error reporting with stack traces and implements retry mechanisms for transient network issues.

</details>

## Installation

To get started, install the pip package from PyPI:

```bash
pip install nhtsa
```
## How It Works

The NHTSA SDK interacts with various data sources from the NHTSA ecosystem. Below is a breakdown of the API groups, their status in this SDK, and links to their official documentation pages.

<details>
<summary><h3>I. NHTSA Datasets and APIs (`https://api.nhtsa.gov`)</h3></summary>

These APIs primarily use `https://api.nhtsa.gov`.

*   **Ratings API** ([Official Link](https://www.nhtsa.gov/nhtsa-datasets-and-apis#ratings))
    *   **Status: Supported**
    *   Methods for retrieving safety ratings by model year, make, model, and vehicle ID.
*   **Recalls Data & APIs** ([Official Link](https://www.nhtsa.gov/nhtsa-datasets-and-apis#recalls))
    *   **Status: Supported**
    *   Methods for querying recalls by vehicle parameters and campaign number. Also supports downloading associated static data files.
*   **Investigations Data** ([Official Link](https://www.nhtsa.gov/nhtsa-datasets-and-apis#investigations))
    *   **Status: Supported (for file metadata)**
    *   Provides metadata and methods for downloading raw investigation data files. The detailed structure of the data within the downloaded files is not modeled by Pydantic.
*   **Complaints Data & API** ([Official Link](https://www.nhtsa.gov/nhtsa-datasets-and-apis#complaints))
    *   **Status: Supported**
    *   Methods for querying complaints by vehicle parameters and ODI number. Also supports downloading associated static data files.
*   **Manufacturer Communications Data** ([Official Link](https://www.nhtsa.gov/nhtsa-datasets-and-apis#manufacturer-communications))
    *   **Status: Supported (for file metadata and TSB info)**
    *   Provides metadata and methods for downloading static manufacturer communication files (including dynamically generated PDF URLs). The detailed structure of the files themselves is not fully modeled.
*   **Car Seat Inspection Locator API** ([Official Link](https://www.nhtsa.gov/nhtsa-datasets-and-apis#car-seat-inspection-locator))
    *   **Status: Supported**
    *   Methods for finding car seat inspection stations by ZIP code, state, and geographical coordinates, with optional filters.

</details>

---

<details>
<summary><h3>II. vPIC (Vehicle Product Information Catalog) APIs (`https://vpic.nhtsa.dot.gov/api/`)</h3></summary>

These APIs primarily use `https://vpic.nhtsa.dot.gov/api/`. Additional language examples can be found at ([Official Link](https://vpic.nhtsa.dot.gov/api/Home/Index/LanguageExamples)).

*   **Decode VIN**
    *   **Status: Supported**
    *   Decodes a VIN into key-value pairs or a flat format.
*   **Decode VIN Extended**
    *   **Status: Supported**
    *   Decodes a VIN with additional NCSA-related information.
*   **Decode WMI**
    *   **Status: Supported**
    *   Provides information about a World Manufacturer Identifier.
*   **Get WMIs for Manufacturer**
    *   **Status: Supported**
    *   Retrieves WMIs associated with a given manufacturer or vehicle type.
*   **Get All Makes**
    *   **Status: Supported**
    *   Lists all vehicle makes in the vPIC dataset.
*   **Get Parts**
    *   **Status: Supported**
    *   Retrieves ORG information based on type, date range, and manufacturer.
*   **Get All Manufacturers**
    *   **Status: Supported**
    *   Lists all manufacturers, with optional filtering by manufacturer type.
*   **Get Manufacturer Details**
    *   **Status: Supported**
    *   Provides detailed information for specific manufacturers.
*   **Get Makes for Manufacturer by Manufacturer Name**
    *   **Status: Supported**
    *   Returns makes for a specified manufacturer.
*   **Get Makes for Manufacturer by Manufacturer Name and Year**
    *   **Status: Supported**
    *   Returns makes for a manufacturer within a specific model year range.
*   **Get Makes for Vehicle Type by Vehicle Type Name**
    *   **Status: Supported**
    *   Returns makes associated with a particular vehicle type.
*   **Get Vehicle Types for Make by Name**
    *   **Status: Supported**
    *   Returns vehicle types for a specified make name.
*   **Get Vehicle Types for Make by Id**
    *   **Status: Supported**
    *   Returns vehicle types for a specified make ID.
*   **Get Equipment Plant Codes**
    *   **Status: Supported**
    *   Retrieves assigned equipment plant codes.
*   **Get Models for Make**
    *   **Status: Supported**
    *   Returns models for a specified make.
*   **Get Models for MakeId**
    *   **Status: Supported**
    *   Returns models for a specified make ID.
*   **Get Models for Make and a combination of Year and Vehicle Type**
    *   **Status: Supported**
    *   Returns models filtered by make, model year, and vehicle type.
*   **Get Models for Make Id and a combination of Year and Vehicle Type**
    *   **Status: Supported**
    *   Returns models filtered by make ID, model year, and vehicle type.
*   **Get Vehicle Variables List**
    *   **Status: Supported**
    *   Lists all available vehicle-related variables.
*   **Get Vehicle Variable Values List**
    *   **Status: Supported**
    *   Lists all accepted values for a given variable.
*   **Decode VIN (flat format) in a Batch**
    *   **Status: Supported**
    *   Decodes multiple VINs in a single batch request.
*   **Get Canadian vehicle specifications**
    *   **Status: Supported**
    *   Retrieves Canadian vehicle dimension specifications.

</details>

---

<details>
<summary><h3>III. NHTSA Test Databases (NRD) APIs (`https://nrd.api.nhtsa.dot.gov/`)</h3></summary>

These APIs access engineering data from various NHTSA research, test, and compliance programs.
The base URL for these endpoints is `https://nrd.api.nhtsa.dot.gov/`.

*   **Vehicle Crash Test Database API** ([Official Link](https://nrd.api.nhtsa.dot.gov/nhtsa/vehicle/swagger-ui/index.html))
    *   **Status: In Development (Partial Pydantic Mapping)**
    *   Methods for accessing vehicle crash test documents, test results, vehicle models, occupant types, metadata, and detailed vehicle, restraint, occupant, multimedia, intrusion, instrumentation, and barrier information. Includes comprehensive search capabilities. The underlying Pydantic models are being refined to fully represent all complex nested structures.
*   **Biomechanics Test Database API** ([Official Link](https://nrd.api.nhtsa.dot.gov/nhtsa/biomechanics/swagger-ui/index.html))
    *   **Status: In Development (Placeholder Models)**
    *   Methods for accessing biomechanics test documents, test results, occupant types, metadata, and detailed test, restraint, multimedia, instrumentation, dummy occupant, and biological occupant information. Includes comprehensive search capabilities. The underlying Pydantic models are currently placeholders and require detailed definition.
*   **Component Test Database API** ([Official Link](https://nrd.api.nhtsa.dot.gov/swagger-ui/index.html) - points to root for component)
    *   **Status: In Development (Placeholder Models)**
    *   Methods for accessing component test documents, test results, occupant types, metadata, and detailed vehicle, test, multimedia, instrumentation, configuration, and component information. Includes comprehensive search capabilities. The underlying Pydantic models are currently placeholders and require detailed definition.
*   **Crash Avoidance Test Database API** ([Official Link](https://nrd.api.nhtsa.dot.gov/nhtsa/cadb/swagger-ui/index.html))
    *   **Status: In Development (Partial Pydantic Mapping)**
    *   Methods for accessing crash avoidance test data by ID and section, retrieving all test data, documents, and curve data. Includes comprehensive search capabilities. The underlying Pydantic models for nested data are being refined.
*   **NHTSA Database Code Library APIs** ([Official Link](https://nrd.api.nhtsa.dot.gov/swagger-ui/index.html) - shares root with component)
    *   **Status: In Development (Placeholder Models)**
    *   Methods for retrieving test performers, listing all codes, finding/listing models, listing by code name, finding filter classes, and decoding codes. The underlying Pydantic models are currently placeholders and require detailed definition.

</details>

---

<details>
<summary><h3>IV. Other NHTSA Data Sources & Web Portals</h3></summary>

These are primarily links to external web pages, dashboards, or applications, and are **not direct programmatic APIs** for data retrieval. Interaction with these would generally involve web scraping or manual access.

*   **NCSA Section** ([Official Link](https://www.nhtsa.gov/data/national-center-statistics-and-analysis))
    *   **Status: Missing / Out of Scope (Web Portal)**
    *   Links to various NCSA publications, data tools, traffic records, crash data systems, National Driver Register, Data Modernization Project, Regulatory Analysis, and "About NCSA." These are primarily interactive web portals and static reports, not direct data APIs.
*   **Recalls by Manufacturer Dashboard** ([Official Link](https://data.transportation.gov/Automobiles/NHTSA-Recalls-by-Manufacturer/mu99-t4jn))
    *   **Status: Missing / Out of Scope (External Dashboard)**
    *   An interactive dashboard hosted on data.transportation.gov.
*   **Takata Recall Completion Dashboard** ([Official Link](https://data.transportation.gov/Automobiles/Takata-Recall/8u28-hw9f))
    *   **Status: Missing / Out of Scope (External Dashboard)**
    *   Another interactive dashboard hosted on data.transportation.gov.
*   **Standing General Order on Crash Reporting** ([Official Link](https://www.nhtsa.gov/laws-regulations/standing-general-order-crash-reporting))
    *   **Status: Missing / Out of Scope (Web Page)**
    *   A regulatory document web page.
*   **Interpretation File Search** ([Official Link](https://www.nhtsa.gov/nhtsa-interpretation-file-search))
    *   **Status: Missing / Out of Scope (Web Page / Search Interface)**
    *   A web-based search interface for interpretation files.
*   **AV Test** ([Official Link](https://avtest.nhtsa.dot.gov/av-test/home))
    *   **Status: Missing / Out of Scope (External Application/Portal)**
    *   An external application or portal related to automated vehicle testing.
*   **Compliance Test Reports** ([Official Link](https://www.nhtsa.gov/compliance/))
    *   **Status: Missing / Out of Scope (Web Page / Search Interface)**
    *   A web page to search test reports.
*   **Research** ([Official Link](https://www.nhtsa.gov/research))
    *   **Status: Missing / Out of Scope (Web Page)**
    *   General research information page.

</details>

---

## Quick Example

<details>
<summary>Expand to see a Quick Example</summary>

Here is a basic example demonstrating how to retrieve recall information and decode a VIN.

```python
# runner.py
import asyncio
import os
import logging
import traceback
import json
import aiofiles
from dotenv import load_dotenv
from nhtsa.client import NhtsaClient
from nhtsa.api.recalls.models import RecallByVehicle
from nhtsa.api.vin_decoding.models import VinDecodeResult

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Load environment variables from .env file
load_dotenv()

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

async def main():
    """
    Main function to run the NHTSA SDK example with session persistence.
    """
    # Example variables
    model_year_recalls = 2012
    make_recalls = "acura"
    model_recalls = "rdx"
    vin_decode = "5UXWX7C5*BA"
    model_year_vin = 2011

    # --- Session Loading (optional, for persistent sessions) ---
    session_path = os.path.join(__location__, "nhtsa_session.pkl")
    session_data = None
    if os.path.exists(session_path):
        try:
            async with aiofiles.open(session_path, "rb") as sf:
                session_data = await sf.read()
            logger.info("Loaded existing session data from %s", session_path)
        except Exception:
            logger.exception("Failed to read session file; will start a new session.")
    
    # --- Client Initialization ---
    client = NhtsaClient(session_data=session_data)

    try:
        # --- Recalls API Example ---
        logger.info(f"\n--- Recalls API: Getting recalls by vehicle (make={make_recalls}, model={model_recalls}, modelYear={model_year_recalls}) ---")
        recalls_by_vehicle: RecallByVehicle = await client.recalls.get_recalls_by_vehicle(
            make=make_recalls, 
            model=model_recalls, 
            model_year=model_year_recalls
        )
        logger.info(f"Recalls by vehicle for {make_recalls} {model_recalls} {model_year_recalls}:")
        for recall in recalls_by_vehicle.results:
            logger.info(f"- Campaign Number: {recall.nhtsa_campaign_number}, Component: {recall.component}")

        # --- VIN Decoding API Example ---
        logger.info(f"\n--- VIN Decoding API: Decode VIN {vin_decode} for model year {model_year_vin} ---")
        decoded_vin_kv: VinDecodeResult = await client.vin_decoding.decode_vin(
            vin=vin_decode, 
            model_year=model_year_vin
        )
        logger.info(f"Decoded VIN for {vin_decode}:")
        for entry in decoded_vin_kv.results:
            if entry.value: # Only print entries that have a value
                logger.info(f"- {entry.variable}: {entry.value}")

    except Exception as e:
        logger.error(f"An error occurred during the SDK execution: {e}")
        logger.error(traceback.format_exc())
    finally:
        await client.close()
        # --- Session Saving (optional) ---
        try:
            sdata = client.get_session_data()
            if sdata:
                async with aiofiles.open(session_path, "wb") as sf:
                    await sf.write(sdata)
                logger.info("Saved session data to %s", session_path)
            else:
                logger.debug("Client returned empty session data; nothing saved.")
        except Exception:
            logger.exception("Failed to save session data after run.")


if __name__ == "__main__":
    asyncio.run(main())

```

</details>

## Project Structure

<details>
<summary>Expand to see the Project Structure</summary>

The project is organized to separate concerns, with a clear distinction between the client, API logic, and data models.

```
src/nhtsa/
├── __init__.py
├── client.py                      # Holds the main NhtsaClient, session, and base request logic
├── lib/                           # Shared utility files and common Pydantic models
│   ├── models.py                  # Common models like APIResponse, Meta, Pagination, Error
│   └── __init__.py
├── api/
│   ├── __init__.py
│   ├── biomechanics_test_database/
│   │       ├── index.py           # BiomechanicsTestDatabaseAPI class
│   │       └── models.py          # Pydantic models for biomechanics data
│   ├── car_seat_inspection_locator/
│   │       ├── index.py           # CarSeatInspectionLocatorAPI class
│   │       └── models.py          # Pydantic models for car seat inspection data
│   ├── complaints/
│   │       ├── index.py           # ComplaintsAPI class
│   │       └── models.py          # Pydantic models for complaint data
│   ├── component_test_database/
│   │       ├── index.py           # ComponentTestDatabaseAPI class
│   │       └── models.py          # Pydantic models for component test data
│   ├── crash_avoidance_test_database/
│   │       ├── index.py           # CrashAvoidanceTestDatabaseAPI class
│   │       └── models.py          # Pydantic models for crash avoidance data
│   ├── investigations/
│   │       ├── index.py           # InvestigationsAPI class
│   │       └── models.py          # Pydantic models for investigation data
│   ├── manufacturer_communications/
│   │       ├── index.py           # ManufacturerCommunicationsAPI class
│   │       └── models.py          # Pydantic models for manufacturer communication data
│   ├── nhtsa_database_code_library/
│   │       ├── index.py           # NhtsaDatabaseCodeLibraryAPI class
│   │       └── models.py          # Pydantic models for code library data
│   ├── recalls/
│   │       ├── index.py           # RecallsAPI class
│   │       └── models.py          # Pydantic models for recall data
│   ├── safetyservice/
│   │       ├── index.py           # SafetyServiceAPI class
│   │       └── models.py          # Pydantic models for safety rating data
│   ├── static_files/
│   │       ├── index.py           # StaticFilesAPI class for direct file downloads
│   │       └── models.py          # (Currently empty, or for static file metadata)
│   ├── vehicle_crash_test_database/
│   │       ├── index.py           # VehicleCrashTestDatabaseAPI class
│   │       └── models.py          # Pydantic models for vehicle crash test data
│   ├── vin_decoding/
│   │       ├── index.py           # VinDecodingAPI class
│   │       └── models.py          # Pydantic models for VIN decoding data

```

</details>

## Core Components

<details>
<summary>Expand to see Core Components</summary>

### `client.py`

This file contains the `NhtsaClient` class, which is the heart of the SDK. It is responsible for:
-   Managing `httpx.AsyncClient` sessions for the main API (`api.nhtsa.gov`), vPIC API (`vpic.nhtsa.dot.gov`), static files (`static.nhtsa.gov`), and NRD APIs (`nrd.api.nhtsa.dot.gov`).
-   Storing base URLs and common headers for all requests.
-   A private `_request` method that centralizes rate limiting, error handling, verbose logging (with stack traces for errors), and execution of all HTTP requests.
-   Providing access to the various API modules (e.g., `self.recalls`, `self.vin_decoding`, `self.static_files`, `self.vehicle_crash_test_database`).
-   Handling session persistence (saving and loading cookies/state via `pickle`).

### `api/recalls/` (Example API Module)

This module encapsulates all functionality related to vehicle recalls.
-   **`index.py`**: Defines the `RecallsAPI` class. It contains methods like `get_recalls_by_vehicle()` and `get_recalls_by_campaign_number()` which make targeted API calls.
-   **`models.py`**: Defines the Pydantic models (`RecallResult`, `RecallByVehicle`, etc.) that provide the structured output for recall data. This ensures that the user of the SDK always receives a predictable and easy-to-work-with object.

### `api/static_files/` (New API Module for Static Content)

This module is designed for direct interaction with static content hosted on `static.nhtsa.gov`.
-   **`index.py`**: Defines the `StaticFilesAPI` class. It contains a generic `download_file()` method and specific methods like `get_manufacturer_communication_pdf()` to construct and download files based on known URL patterns.
-   **`models.py`**: Currently contains `TSBInfo` to aid in parsing flat files for dynamic URL generation, and can be extended for other static file metadata models.

</details>

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Contributing

Contributions are welcome! Please leave issues or pull requests on the GitHub repository.
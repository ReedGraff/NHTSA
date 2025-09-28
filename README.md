# NHTSA SDK
[![PyPI version](https://badge.fury.io/py/nhtsa.svg)](https://badge.fury.io/py/nhtsa)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An unofficial, asynchronous Python SDK for the National Highway Traffic Safety Administration (NHTSA) APIs.

## Overview

Very comprehensive SDK for accessing NHTSA datasets and services. Supports all documented, as well as most undocumented endpoints discovered through reverse engineering / navigating NHTSA's web applications (Most meaning every single endpoint I have found that does not require CAPTCHA tokens). In addition to pure wrappers for endpoints, this also provides tools for multi-step operations, such as retrieving all document URLs associated for a manufacturer communication number.

Built with `httpx` and `asyncio` for asynchronous, non-blocking I/O. Uses `pydantic` models for structured output.

Most endpoints do not require authentication or API keys, however, and thus session handling and management is a built in feature to this sdk, although not required for most endpoints.

Rate Limiting:
* Having called with the NHTSA it seems as though the standard rate limit is 100-200 requests per minute, however, this has only been confirmed by NHTSA for the vPIC API.
<!--
## Key Features

<details>
<summary>Expand to see Key Features</summary>

-   **Asynchronous:** Built with `httpx` and `asyncio` for non-blocking I/O.
-   **Comprehensive API Coverage:** Covers all specified API endpoints for Safety Ratings, Recalls, Investigations, Complaints, Manufacturer Communications, Car Seat Inspection Locator, VIN Decoding, Vehicle Crash Test Database, Biomechanics Test Database, Component Test Database, Crash Avoidance Test Database, **Safety Issues, Product Information (Vehicles, Tires, Equipment, Child Seats)**, Tag Lookup, and Web VIN Lookup.
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
-->
## How It Works

The NHTSA SDK interacts with various data sources from the NHTSA ecosystem. Below is a breakdown of the high level API groups (by their root url), their status in this SDK, and links to their official documentation pages if available.

<details>
<summary><h3>https://api.nhtsa.gov - APIs</h3></summary>

These APIs primarily use `https://api.nhtsa.gov`.
Most apis are documented at ([Official Link](https://www.nhtsa.gov/nhtsa-datasets-and-apis)). However, some endpoints here were accumulated through reverse engineering and are undocumented. Discovered by navigate applications such as [NHTSA's recall search tool](https://www.nhtsa.gov/recalls). These are noted below.

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
*   **Safety Issues API**
    *   **Status: Supported (Undocumented)**
    *   Methods for retrieving aggregated safety issues (complaints, recalls, investigations, manufacturer communications) by NHTSA ID or through general search.
*   **Products API**
    *   **Status: Supported (Undocumented)**
    *   A consolidated API for retrieving detailed information on various products. Includes methods for:
        *   **Vehicles:** Searching by YMMT (Year, Make, Model, Trim), by VIN (proxy endpoint with CAPTCHA limitation), and general search with extensive safety data.
        *   **Tires:** Searching by query string for safety issues and other attributes.
        *   **Equipment:** Searching by query string for safety issues and other attributes.
        *   **Child Seats:** Retrieving details, available use modes, and searching by query, weight, and height.
*   **Tag Lookup API**
    *   **Status: In Development (Undocumented - Stub - Requires CAPTCHA Token)**
    *   Provides a signature for license plate tag lookups, but calling it will raise a `NotImplementedError` as it requires a Google reCAPTCHA token.
*   **VIN Lookup Web API**
    *   **Status: In Development (Undocumented - Stub - Requires CAPTCHA Token)**
    *   Provides a signature for web-based VIN lookups, but calling it will raise a `NotImplementedError` as it requires a Google reCAPTCHA token.

</details>

---

<details>
<summary><h3>https://vpic.nhtsa.dot.gov/api/ - APIs</h3></summary>

These APIs primarily use `https://vpic.nhtsa.dot.gov/api/`.
In addition to these APIs, NHTSA also offers the full vPIC dataset as a downloadable .bak sql server backup file ([Official Link](https://vpic.nhtsa.dot.gov/api/)).
\* Useful if your application requires >100-200 requests per minute, which is the confirmed rate limit for the vPIC API.

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

If you are looking to use the backup file instead of the API, here is a code stub to get you started once you have restored the .bak file to a SQL Server instance:
```python
from datetime import datetime
import pyodbc # or aioodbc

# Connection details
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=SERVER_NAME_GOES_HERE\\SQLEXPRESS;" # Update with your server name. Most likely you'll use a local SQL Express instance.
    "DATABASE=vPICList_Lite1;"
    "Trusted_Connection=yes;"
)

try:
    start_time = datetime.now()
    cnxn = pyodbc.connect(connection_string)
    cursor = cnxn.cursor()

    # Define values for the parameters you want to include
    vin_to_decode = '3GNAXLEG5TL174166'

    # @includePrivate bit = null -> pass True (for 1) or False (for 0), or None (for NULL)
    include_private_data = False  # This explicitly sets @includePrivate to 1 (True)
    # @year int = null -> pass None to rely on the stored procedure's internal year determination
    model_year_input = None
    # @includeAll bit = null -> pass True (for 1) or False (for 0), or None (for NULL)
    include_all_data = False      # This explicitly sets @includeAll to 1 (True)
    # @NoOutput bit = 0 -> pass False (for 0) to use the default behavior (return results)
    no_output_to_table = False   # This explicitly sets @NoOutput to 0 (False)

    # Call the stored procedure with all parameters in the correct order
    cursor.execute(
        "{CALL [dbo].[spVinDecode](?, ?, ?, ?, ?)}",
        vin_to_decode,
        include_private_data,
        model_year_input,
        include_all_data,
        no_output_to_table
    )

    # Fetch and print results
    results = cursor.fetchall()
    for row in results:
        print(row)
        # print(row[10])

    cursor.close()
    cnxn.close()
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"Duration: {duration.total_seconds()} seconds")

except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print(f"Database error: {sqlstate}")
```

</details>

---

<details>
<summary><h3>https://nrd.api.nhtsa.dot.gov/ - APIs</h3></summary>

The base URL for these endpoints is `https://nrd.api.nhtsa.dot.gov/`.
These APIs access engineering data from various NHTSA research, test, and compliance programs.
Testing/usage for these endpoints is very limited.

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
<summary><h3>Other</h3></summary>

These are primarily links to external web pages, dashboards, or applications, and are **not direct programmatic APIs** for data retrieval. Interaction with these would generally involve web scraping or manual access, something not built out yet.

*   **NCSA Section** ([Official Link](https://www.nhtsa.gov/data/national-center-statistics-and-analysis)) and ([Official Link](https://cdan.dot.gov/))
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

<details>
<summary><h3>Tools - Pre-Built Automations</h3></summary>

These are higher level tools that combine multiple API calls to perform more complex operations. They are built on top of the existing API modules.

*   **Get TSB by MFG Number & VIN**
    *   **Status: Supported**
    *   A tool to retrieve Technical Service Bulletins (TSBs) based on the manufacturer communication number and VIN.
*   **Get TSB by MFG Number**
    *   **Status: Not Supported**
    *   A tool to retrieve Technical Service Bulletins (TSBs) just based on the manufacturer communication number.

## Quick Example

<details id="minimal-example">
<summary>Super minimal example</summary>

Here is a super minimal example demonstrating how to decode a VIN.

```python
import asyncio
from src.nhtsa.client import NhtsaClient

async def main():
    client = NhtsaClient()
    print(f"\n--- VIN Decoding API: Decode VIN Batch ---")
    decoded_vin_batch = await client.vin_decoding.decode_vin_batch(data="3GNDA13D76S000000,2011; 5XYKT3A12CG000000")
    print(f"Decoded VIN Batch (first result): {decoded_vin_batch.results.model_dump_json(indent=2)}")

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
│   ├── products/                  # Consolidated for Vehicles, Tires, Equipment, Child Seats
│   │       ├── index.py           # ProductsAPI class
│   │       └── models.py          # Pydantic models for various product data
│   ├── recalls/
│   │       ├── index.py           # RecallsAPI class
│   │       └── models.py          # Pydantic models for recall data
│   ├── safetyservice/
│   │       ├── index.py           # SafetyServiceAPI class
│   │       └── models.py          # Pydantic models for safety rating data
│   ├── safety_issues/             # For aggregated safety issue queries
│   │       ├── index.py           # SafetyIssuesAPI class
│   │       └── models.py          # Pydantic models for safety issues data
│   ├── static_files/
│   │       ├── index.py           # StaticFilesAPI class for direct file downloads
│   │       └── models.py          # (Currently empty, or for static file metadata)
│   ├── tag_lookup/                # For license plate tag lookups (stubbed)
│   │       ├── index.py           # TagLookupAPI class
│   │       └── models.py          # (Empty - stubbed)
│   ├── tools/                     # Prebuilt tools for multi-step operations
│   │       └── index.py           # Source for the tools
│   ├── vehicle_crash_test_database/
│   │       ├── index.py           # VehicleCrashTestDatabaseAPI class
│   │       └── models.py          # Pydantic models for vehicle crash test data
│   ├── vin_decoding/
│   │       ├── index.py           # VinDecodingAPI class
│   │       └── models.py          # Pydantic models for VIN decoding data
│   └── vin_lookup_web/            # For web-based VIN lookups (stubbed)
│           ├── index.py           # VinLookupWebAPI class
│           └── models.py          # (Empty - stubbed)

```

</details>

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Contributions

Contributions are welcome! Please leave issues or pull requests on the GitHub repository.

Each logical grouping of endpoints is encapsulated in its own module within the `api/` directory. Each module contains:
* An `index.py` file that defines the main API class with methods for each endpoint.
* A `models.py` file that defines the Pydantic models for structured output.
* changes to the core client logic (e.g., session management, request handling) are made in `client.py`.

<!--
Publishing to PyPI:
```
Remove-Item .\dist\* -Recurse -Force
python -m build
python -m twine upload dist/*
```
-->
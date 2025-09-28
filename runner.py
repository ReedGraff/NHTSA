
import asyncio
import os
import logging
import traceback
import json
import aiofiles
from dotenv import load_dotenv
from datetime import date, datetime

# NOTE THAT IF YOU USE THIS AS AN EXTERNAL LIBRARY/IMPORT, YOU MUST IMPORT WITH `from nhtsa` NOT `from src.nhtsa`
from src.nhtsa.client import NhtsaClient
from src.nhtsa.api.recalls.models import RecallByVehicle, ModelYear, Make, Model
from src.nhtsa.api.safetyservice.models import SafetyRatingModelYear, SafetyRatingMake, SafetyRatingModel, VehicleVariant, SafetyRatingResult
from src.nhtsa.api.car_seat_inspection_locator.models import CarSeatInspectionStation
from src.nhtsa.lib.models import APIResponse

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# logging.getLogger("httpx").setLevel(logging.WARNING)
# logging.getLogger("httpcore").setLevel(logging.WARNING)

# Load environment variables from .env file
# load_dotenv()

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

async def main():
    """
    Main function to run the NHTSA SDK example with session persistence.
    """
    # Example variables
    model_year_recalls = 2012
    make_recalls = "acura"
    model_recalls = "rdx"
    campaign_number = "12V176000"

    model_year_safety = 2013
    make_safety = "Acura"
    model_safety = "rdx"
    vehicle_id_safety = 7520

    zip_code_cssi = "63640"
    state_cssi = "NV"
    latitude_cssi = 30.1783
    longitude_cssi = -96.3911
    miles_cssi = 50

    vin_decode = "5UXWX7C5*BA"
    model_year_vin = 2011
    wmi_decode = "1FD"
    manufacturer_wmi = "hon"
    manufacturer_id_wmi = 987
    vehicle_type_wmi = "car"
    parts_type = 565
    from_date_parts = "1/1/2015"
    to_date_parts = "5/5/2015"
    manufacturer_parts = "hon"
    manufacturer_type = "Intermediate"
    manufacturer_details_name = "honda"
    manufacturer_details_id = 988
    vehicle_variable_name = "battery type"
    vehicle_variable_id = 143
    decode_vin_batch_data = "3GNDA13D76S000000,2011; 5XYKT3A12CG000000"
    canadian_vehicle_year = 2011
    canadian_vehicle_make = "Acura"

    # Static file example
    example_tsb_year = 2024
    example_nhtsa_id = 11011232
    example_sequential_num = 1

    # Vehicle Crash Test Database examples
    vctd_test_no = "C200021" # Example from Swagger UI for /get-vehicle-info/{testNo}
    vctd_vehicle_no = "1"
    vctd_occupant_location = "Driver"

    # Biomechanics Test Database examples
    btd_test_no = "B200001"
    btd_curve_no = 1

    # Component Test Database examples
    ctd_test_no = "T200001"
    ctd_curve_no = "1" # from swagger docs
    ctd_conf_no = "1" # from swagger docs
    ctd_comp_no = "1" # from swagger docs

    # NHTSA Database Code Library examples
    ndcl_database_name = "vehicle"
    ndcl_code_name = "BodyClass" # Example from vPIC variable list
    ndcl_code_value = "7" # Example for MULTIPURPOSE PASSENGER VEHICLE (MPV)


    # --- Session Loading ---
    # session_path = os.path.join(__location__, "nhtsa_session.pkl")
    # session_data = None
    # if os.path.exists(session_path):
    #     try:
    #         async with aiofiles.open(session_path, "rb") as sf:
    #             session_data = await sf.read()
    #         logger.info("Loaded existing session data from %s", session_path)
    #     except Exception:
    #         logger.exception("Failed to read session file; will start a new session.")
    
    # --- Client Initialization ---
    # client = NhtsaClient(session_data=session_data)
    client = NhtsaClient()

    try:
        # # Recalls API
        # logger.info(f"\n--- Recalls API: Getting recalls by vehicle (make={make_recalls}, model={model_recalls}, modelYear={model_year_recalls}) ---")
        # recalls_by_vehicle = await client.recalls.get_recalls_by_vehicle(make=make_recalls, model=model_recalls, model_year=model_year_recalls)
        # logger.info(f"Recalls by vehicle: {recalls_by_vehicle.model_dump_json(indent=2)}")

        # logger.info("\n--- Recalls API: Getting all model years for recalls ---")
        # all_recall_model_years = await client.recalls.get_all_model_years()
        # logger.info(f"All recall model years (first 5): {all_recall_model_years.results[:5]}")

        # logger.info(f"\n--- Recalls API: Getting all makes for model year {model_year_recalls} for recalls ---")
        # all_recall_makes = await client.recalls.get_all_makes_for_model_year(model_year=model_year_recalls)
        # logger.info(f"All recall makes for {model_year_recalls} (first 5): {all_recall_makes.results[:5]}")

        # logger.info(f"\n--- Recalls API: Getting all models for make={make_recalls} and modelYear={model_year_recalls} for recalls ---")
        # all_recall_models = await client.recalls.get_all_models_for_make_and_model_year(make=make_recalls, model_year=model_year_recalls)
        # logger.info(f"All recall models for {make_recalls} {model_year_recalls} (first 5): {all_recall_models.results[:5]}")

        # logger.info(f"\n--- Recalls API: Getting recalls by campaign number {campaign_number} ---")
        # recalls_by_campaign = await client.recalls.get_recalls_by_campaign_number(campaign_number=campaign_number)
        # logger.info(f"Recalls by campaign number: {recalls_by_campaign.model_dump_json(indent=2)}")

        # # Safety Service API
        # logger.info(f"\n--- Safety Service API: Get available vehicle variants for {model_year_safety} {make_safety} {model_safety} ---")
        # safety_variants = await client.safety_service.get_vehicle_variants(model_year=model_year_safety, make=make_safety, model=model_safety)
        # logger.info(f"Safety variants: {safety_variants.model_dump_json(indent=2)}")

        # logger.info(f"\n--- Safety Service API: Get safety ratings for VehicleId {vehicle_id_safety} ---")
        # safety_ratings_by_vehicle_id = await client.safety_service.get_safety_ratings_by_vehicle_id(vehicle_id=vehicle_id_safety)
        # logger.info(f"Safety ratings by VehicleId: {safety_ratings_by_vehicle_id.model_dump_json(indent=2)}")

        # logger.info("\n--- Safety Service API: Get all model years for safety ratings ---")
        # all_safety_model_years = await client.safety_service.get_all_model_years()
        # logger.info(f"All safety model years (first 5): {all_safety_model_years.results[:5]}")

        # logger.info(f"\n--- Safety Service API: Get all makes for model year {model_year_safety} for safety ratings ---")
        # all_safety_makes = await client.safety_service.get_all_makes_for_model_year(model_year=model_year_safety)
        # logger.info(f"All safety makes for {model_year_safety} (first 5): {all_safety_makes.results[:5]}")

        # logger.info(f"\n--- Safety Service API: Get all models for make={make_safety} and modelYear={model_year_safety} for safety ratings ---")
        # all_safety_models = await client.safety_service.get_all_models_for_make_and_model_year(make=make_safety, model_year=model_year_safety)
        # logger.info(f"All safety models for {make_safety} {model_year_safety} (first 5): {all_safety_models.results[:5]}")

        # # Car Seat Inspection Locator API
        # logger.info(f"\n--- Car Seat Inspection Locator API: Get stations by ZIP code {zip_code_cssi} ---")
        # cssi_by_zip = await client.car_seat_inspection_locator.get_stations_by_zip_code(zip_code=zip_code_cssi)
        # logger.info(f"CSSI Stations by ZIP: {cssi_by_zip.model_dump_json(indent=2)}")

        # logger.info(f"\n--- Car Seat Inspection Locator API: Get stations by state {state_cssi} ---")
        # cssi_by_state = await client.car_seat_inspection_locator.get_stations_by_state(state_abbreviation=state_cssi)
        # logger.info(f"CSSI Stations by State (first 2): {cssi_by_state.results[:2]}")

        # logger.info(f"\n--- Car Seat Inspection Locator API: Get stations by geographical location (lat={latitude_cssi}, long={longitude_cssi}, miles={miles_cssi}) ---")
        # cssi_by_geo = await client.car_seat_inspection_locator.get_stations_by_geo_location(lat=latitude_cssi, long=longitude_cssi, miles=miles_cssi)
        # logger.info(f"CSSI Stations by Geo (first 2): {cssi_by_geo.results[:2]}")

        # logger.info(f"\n--- Car Seat Inspection Locator API: Get stations by ZIP code {zip_code_cssi} with Spanish-speaking filter ---")
        # cssi_by_zip_spanish = await client.car_seat_inspection_locator.get_stations_by_zip_code(zip_code=zip_code_cssi, lang_spanish=True)
        # logger.info(f"CSSI Stations by ZIP (Spanish): {cssi_by_zip_spanish.model_dump_json(indent=2)}")

        # logger.info(f"\n--- Car Seat Inspection Locator API: Get stations by ZIP code {zip_code_cssi} with CPS Week filter ---")
        # cssi_by_zip_cpsweek = await client.car_seat_inspection_locator.get_stations_by_zip_code(zip_code=zip_code_cssi, cps_week=True)
        # logger.info(f"CSSI Stations by ZIP (CPS Week): {cssi_by_zip_cpsweek.model_dump_json(indent=2)}")

        # # VIN Decoding API
        # logger.info(f"\n--- VIN Decoding API: Decode VIN {vin_decode} (Key-Value) ---")
        # decoded_vin_kv = await client.vin_decoding.decode_vin(vin=vin_decode, model_year=model_year_vin)
        # logger.info(f"Decoded VIN (Key-Value): {decoded_vin_kv.model_dump_json(indent=2)}")

        # logger.info(f"\n--- VIN Decoding API: Decode VIN {vin_decode} (Flat Format) ---")
        # decoded_vin_flat = await client.vin_decoding.decode_vin_flat_format(vin=vin_decode, model_year=model_year_vin)
        # logger.info(f"Decoded VIN (Flat Format): {decoded_vin_flat.model_dump_json(indent=2)}")

        # logger.info(f"\n--- VIN Decoding API: Decode VIN Extended {vin_decode} (Key-Value) ---")
        # decoded_vin_extended_kv = await client.vin_decoding.decode_vin_extended(vin=vin_decode, model_year=model_year_vin)
        # logger.info(f"Decoded VIN Extended (Key-Value): {decoded_vin_extended_kv.model_dump_json(indent=2)}")

        # logger.info(f"\n--- VIN Decoding API: Decode VIN Extended {vin_decode} (Flat Format) ---")
        # decoded_vin_extended_flat = await client.vin_decoding.decode_vin_extended_flat_format(vin=vin_decode, model_year=model_year_vin)
        # logger.info(f"Decoded VIN Extended (Flat Format): {decoded_vin_extended_flat.model_dump_json(indent=2)}")

        # logger.info(f"\n--- VIN Decoding API: Decode WMI {wmi_decode} ---")
        # decoded_wmi = await client.vin_decoding.decode_wmi(wmi=wmi_decode)
        # logger.info(f"Decoded WMI: {decoded_wmi.model_dump_json(indent=2)}")

        # logger.info(f"\n--- VIN Decoding API: Get WMIs for Manufacturer '{manufacturer_wmi}' ---")
        # wmis_by_manufacturer = await client.vin_decoding.get_wmis_for_manufacturer(manufacturer=manufacturer_wmi)
        # logger.info(f"WMIs for Manufacturer (first 2): {wmis_by_manufacturer.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get WMIs for Manufacturer ID {manufacturer_id_wmi} ---")
        # wmis_by_manufacturer_id = await client.vin_decoding.get_wmis_for_manufacturer(manufacturer=str(manufacturer_id_wmi))
        # logger.info(f"WMIs for Manufacturer ID (first 2): {wmis_by_manufacturer_id.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get WMIs for Manufacturer '{manufacturer_wmi}' and Vehicle Type '{vehicle_type_wmi}' ---")
        # wmis_by_manufacturer_and_type = await client.vin_decoding.get_wmis_for_manufacturer(manufacturer=manufacturer_wmi, vehicle_type=vehicle_type_wmi)
        # logger.info(f"WMIs for Manufacturer and Type (first 2): {wmis_by_manufacturer_and_type.results[:2]}")

        # logger.info("\n--- VIN Decoding API: Get All Makes ---")
        # all_makes = await client.vin_decoding.get_all_makes()
        # logger.info(f"All Makes (first 5): {all_makes.results[:5]}")

        # logger.info(f"\n--- VIN Decoding API: Get Parts (type={parts_type}, fromDate={from_date_parts}, toDate={to_date_parts}) ---")
        # parts = await client.vin_decoding.get_parts(type=parts_type, from_date=from_date_parts, to_date=to_date_parts)
        # logger.info(f"Parts (first 2): {parts.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Parts by Manufacturer (type={parts_type}, fromDate={from_date_parts}, toDate={to_date_parts}, manufacturer={manufacturer_parts}) ---")
        # parts_by_manufacturer = await client.vin_decoding.get_parts(type=parts_type, from_date=from_date_parts, to_date=to_date_parts, manufacturer=manufacturer_parts)
        # logger.info(f"Parts by Manufacturer (first 2): {parts_by_manufacturer.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get All Manufacturers (page=2) ---")
        # all_manufacturers_page_2 = await client.vin_decoding.get_all_manufacturers(page=2)
        # logger.info(f"All Manufacturers (page 2, first 2): {all_manufacturers_page_2.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get All Manufacturers by Type '{manufacturer_type}' (page=2) ---")
        # manufacturers_by_type = await client.vin_decoding.get_all_manufacturers(manufacturer_type=manufacturer_type, page=2)
        # logger.info(f"Manufacturers by Type (page 2, first 2): {manufacturers_by_type.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Manufacturer Details by Name '{manufacturer_details_name}' ---")
        # manufacturer_details_name_result = await client.vin_decoding.get_manufacturer_details(manufacturer=manufacturer_details_name)
        # logger.info(f"Manufacturer Details by Name (first 1): {manufacturer_details_name_result.results[:1]}")

        # logger.info(f"\n--- VIN Decoding API: Get Manufacturer Details by ID '{manufacturer_details_id}' ---")
        # manufacturer_details_id_result = await client.vin_decoding.get_manufacturer_details(manufacturer=str(manufacturer_details_id))
        # logger.info(f"Manufacturer Details by ID: {manufacturer_details_id_result.model_dump_json(indent=2)}")

        # logger.info(f"\n--- VIN Decoding API: Get Makes for Manufacturer '{manufacturer_details_name}' ---")
        # makes_for_manufacturer = await client.vin_decoding.get_makes_for_manufacturer(manufacturer=manufacturer_details_name)
        # logger.info(f"Makes for Manufacturer (first 2): {makes_for_manufacturer.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Makes for Manufacturer ID '{manufacturer_details_id}' ---")
        # makes_for_manufacturer_id = await client.vin_decoding.get_makes_for_manufacturer(manufacturer=str(manufacturer_details_id))
        # logger.info(f"Makes for Manufacturer ID (first 2): {makes_for_manufacturer_id.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Makes for Manufacturer 'mer' and Year 2014 ---")
        # makes_for_manufacturer_and_year = await client.vin_decoding.get_makes_for_manufacturer_and_year(manufacturer="mer", year=2014)
        # logger.info(f"Makes for Manufacturer 'mer' and Year 2014 (first 2): {makes_for_manufacturer_and_year.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Makes for Manufacturer ID 988 and Year 2014 ---")
        # makes_for_manufacturer_id_and_year = await client.vin_decoding.get_makes_for_manufacturer_and_year(manufacturer="988", year=2014)
        # logger.info(f"Makes for Manufacturer ID 988 and Year 2014 (first 2): {makes_for_manufacturer_id_and_year.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Makes for Vehicle Type 'car' ---")
        # makes_for_vehicle_type = await client.vin_decoding.get_makes_for_vehicle_type(vehicle_type_name="car")
        # logger.info(f"Makes for Vehicle Type 'car' (first 2): {makes_for_vehicle_type.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Vehicle Types for Make 'merc' ---")
        # vehicle_types_for_make = await client.vin_decoding.get_vehicle_types_for_make(make_name="merc")
        # logger.info(f"Vehicle Types for Make 'merc' (first 2): {vehicle_types_for_make.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Vehicle Types for Make ID 450 ---")
        # vehicle_types_for_make_id = await client.vin_decoding.get_vehicle_types_for_make_id(make_id=450)
        # logger.info(f"Vehicle Types for Make ID 450 (first 2): {vehicle_types_for_make_id.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Equipment Plant Codes for 2015, type 1, all reports ---")
        # equipment_plant_codes = await client.vin_decoding.get_equipment_plant_codes(year=2015, equipment_type=1, report_type="all")
        # logger.info(f"Equipment Plant Codes (first 2): {equipment_plant_codes.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Models for Make 'honda' ---")
        # models_for_make = await client.vin_decoding.get_models_for_make(make_name="honda")
        # logger.info(f"Models for Make 'honda' (first 2): {models_for_make.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Models for Make ID 440 ---")
        # models_for_make_id = await client.vin_decoding.get_models_for_make_id(make_id=440)
        # logger.info(f"Models for Make ID 440 (first 2): {models_for_make_id.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Models for Make 'honda', Year 2015 ---")
        # models_for_make_year = await client.vin_decoding.get_models_for_make_year(make_name="honda", model_year=2015)
        # logger.info(f"Models for Make 'honda', Year 2015 (first 2): {models_for_make_year.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Models for Make 'honda', Vehicle Type 'truck' ---")
        # models_for_make_vehicle_type = await client.vin_decoding.get_models_for_make_year(make_name="honda", vehicle_type="truck")
        # logger.info(f"Models for Make 'honda', Vehicle Type 'truck' (first 2): {models_for_make_vehicle_type.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Models for Make 'honda', Year 2015, Vehicle Type 'truck' ---")
        # models_for_make_year_vehicle_type = await client.vin_decoding.get_models_for_make_year(make_name="honda", model_year=2015, vehicle_type="truck")
        # logger.info(f"Models for Make 'honda', Year 2015, Vehicle Type 'truck': {models_for_make_year_vehicle_type.model_dump_json(indent=2)}")

        # logger.info(f"\n--- VIN Decoding API: Get Models for Make ID 474, Year 2015 ---")
        # models_for_make_id_year = await client.vin_decoding.get_models_for_make_id_year(make_id=474, model_year=2015)
        # logger.info(f"Models for Make ID 474, Year 2015 (first 2): {models_for_make_id_year.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Models for Make ID 474, Vehicle Type 'truck' ---")
        # models_for_make_id_vehicle_type = await client.vin_decoding.get_models_for_make_id_year(make_id=474, vehicle_type="truck")
        # logger.info(f"Models for Make ID 474, Vehicle Type 'truck' (first 2): {models_for_make_id_vehicle_type.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Models for Make ID 474, Year 2015, Vehicle Type 'truck' ---")
        # models_for_make_id_year_vehicle_type = await client.vin_decoding.get_models_for_make_id_year(make_id=474, model_year=2015, vehicle_type="truck")
        # logger.info(f"Models for Make ID 474, Year 2015, Vehicle Type 'truck': {models_for_make_id_year_vehicle_type.model_dump_json(indent=2)}")

        # logger.info("\n--- VIN Decoding API: Get Vehicle Variables List ---")
        # vehicle_variables = await client.vin_decoding.get_vehicle_variable_list()
        # logger.info(f"Vehicle Variables List (first 2): {vehicle_variables.results[:2]}")

        # logger.info(f"\n--- VIN Decoding API: Get Vehicle Variable Values List for '{vehicle_variable_name}' ---")
        # variable_values_by_name = await client.vin_decoding.get_vehicle_variable_values_list(variable_search_param=vehicle_variable_name)
        # logger.info(f"Variable Values for '{vehicle_variable_name}': {variable_values_by_name.model_dump_json(indent=2)}")

        # logger.info(f"\n--- VIN Decoding API: Get Vehicle Variable Values List for ID '{vehicle_variable_id}' ---")
        # variable_values_by_id = await client.vin_decoding.get_vehicle_variable_values_list(variable_search_param=str(vehicle_variable_id))
        # logger.info(f"Variable Values for ID '{vehicle_variable_id}': {variable_values_by_id.model_dump_json(indent=2)}")

        logger.info(f"\n--- VIN Decoding API: Decode VIN Batch ---")
        decoded_vin_batch = await client.vin_decoding.decode_vin_batch(data=decode_vin_batch_data)
        logger.info(f"Decoded VIN Batch (first result): {decoded_vin_batch.results[0].model_dump_json(indent=2)}")

        # logger.info(f"\n--- VIN Decoding API: Get Canadian Vehicle Specifications for Year {canadian_vehicle_year}, Make '{canadian_vehicle_make}' ---")
        # canadian_specs = await client.vin_decoding.get_canadian_vehicle_specifications(year=canadian_vehicle_year, make=canadian_vehicle_make)
        # logger.info(f"Canadian Vehicle Specs (first result): {canadian_specs.results[0].model_dump_json(indent=2)}")


        # # New Static Files API example
        # logger.info(f"\n--- Static Files API: Downloading Manufacturer Communication PDF ---")
        # try:
        #     tsbs_zip_url = "https://static.nhtsa.gov/odi/ffdd/tsbs/TSBS_RECEIVED_2025-2025.zip"
        #     zip_content = await client.static_files.download_file(tsbs_zip_url)
            
        #     temp_zip_path = os.path.join(__location__, "TSBS_RECEIVED_2025-2025.zip")
        #     async with aiofiles.open(temp_zip_path, "wb") as f:
        #         await f.write(zip_content)
            
        #     import zipfile
        #     extracted_tsbs_txt_path = None
        #     with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
        #         for file_name in zip_ref.namelist():
        #             if file_name.endswith('.txt'):
        #                 zip_ref.extract(file_name, __location__)
        #                 extracted_tsbs_txt_path = os.path.join(__location__, file_name)
        #                 break
            
        #     if extracted_tsbs_txt_path:
        #         logger.info(f"Extracted TSBS.txt to: {extracted_tsbs_txt_path}")
        #         async with aiofiles.open(extracted_tsbs_txt_path, 'rb') as f:
        #             tsbs_txt_content = await f.read()

        #         tsb_info_list = client.manufacturer_communications.get_tsb_information_from_flat_file_from_content(tsbs_txt_content)
        #         if tsb_info_list:
        #             first_tsb = tsb_info_list[0]
        #             # The example URL uses NHTSA ID number, not TSB_Document_ID for MC-XXXX-0001.pdf pattern
        #             pdf_content = await client.static_files.get_manufacturer_communication_pdf(
        #                 year=example_tsb_year, # Using hardcoded year as per the example PDF URL format
        #                 nhtsa_id_number=first_tsb.nhtsa_id_number,
        #                 sequential_number=example_sequential_num
        #             )
        #             pdf_output_path = os.path.join(__location__, f"MC-{first_tsb.nhtsa_id_number}-{example_sequential_num:04d}.pdf")
        #             async with aiofiles.open(pdf_output_path, "wb") as f:
        #                 await f.write(pdf_content)
        #             logger.info(f"Downloaded example Manufacturer Communication PDF to: {pdf_output_path}")
        #         else:
        #             logger.warning("No TSB information extracted from the flat file to generate PDF URL.")
        #     else:
        #         logger.warning(f"Could not find a .txt file in {tsbs_zip_url} after downloading.")
            
        # except Exception as e:
        #     logger.error(f"Error downloading or processing static file: {e}", exc_info=True)


        # # New NRD APIs Examples
        # logger.info(f"\n--- Vehicle Crash Test Database API: Get all test data ---")
        # vctd_all_test_data = await client.vehicle_crash_test_database.get_all_test_data(count=1)
        # logger.info(f"VCTD All Test Data (first result): {vctd_all_test_data.meta.model_dump_json(indent=2)}")

        # logger.info(f"\n--- Vehicle Crash Test Database API: Find vehicle documents by test no '{vctd_test_no}' ---")
        # vctd_documents = await client.vehicle_crash_test_database.find_vehicle_documents_by_test_no(test_no=vctd_test_no)
        # logger.info(f"VCTD Documents for '{vctd_test_no}' (meta): {vctd_documents.meta.model_dump_json(indent=2)}")

        # logger.info(f"\n--- Biomechanics Test Database API: Get all test data ---")
        # btd_all_test_data = await client.biomechanics_test_database.get_all_test_data(count=1)
        # logger.info(f"BTD All Test Data (first result): {btd_all_test_data.meta.model_dump_json(indent=2)}")
        
        # logger.info(f"\n--- Biomechanics Test Database API: Get test details for '{btd_test_no}' ---")
        # btd_test_details = await client.biomechanics_test_database.get_test_details(test_no=btd_test_no)
        # logger.info(f"BTD Test Details for '{btd_test_no}' (meta): {btd_test_details.meta.model_dump_json(indent=2)}")

        # logger.info(f"\n--- Component Test Database API: Get all test data ---")
        # ctd_all_test_data = await client.component_test_database.get_all_test_data(count=1)
        # logger.info(f"CTD All Test Data (first result): {ctd_all_test_data.meta.model_dump_json(indent=2)}")

        # logger.info(f"\n--- Component Test Database API: Get component information for '{ctd_test_no}' ---")
        # ctd_component_info = await client.component_test_database.get_component_information(test_no=ctd_test_no)
        # logger.info(f"CTD Component Info for '{ctd_test_no}' (meta): {ctd_component_info.meta.model_dump_json(indent=2)}")

        # logger.info(f"\n--- Crash Avoidance Test Database API: Get all test data ---")
        # cadb_all_test_data = await client.crash_avoidance_test_database.get_all_test_data()
        # logger.info(f"CADB All Test Data (first entry test_id): {cadb_all_test_data[0].test_id if cadb_all_test_data else 'N/A'}")

        # logger.info(f"\n--- Crash Avoidance Test Database API: Get test data by ID (assuming one from above) ---")
        # if cadb_all_test_data:
        #     cadb_single_test_data = await client.crash_avoidance_test_database.get_test_data_by_id(test_id=cadb_all_test_data[0].test_id)
        #     logger.info(f"CADB Single Test Data (testID): {cadb_single_test_data.test_id}")


        # logger.info(f"\n--- NHTSA Database Code Library API: Get test performers for database '{ndcl_database_name}' ---")
        # ndcl_test_performers = await client.nhtsa_database_code_library.get_test_performers(database=ndcl_database_name)
        # logger.info(f"NDCL Test Performers (meta): {ndcl_test_performers.meta.model_dump_json(indent=2)}")

        # logger.info(f"\n--- NHTSA Database Code Library API: Decode by code name '{ndcl_code_name}' and code '{ndcl_code_value}' ---")
        # ndcl_decode_code = await client.nhtsa_database_code_library.decode_by_code_name_and_code(code_name=ndcl_code_name, code=ndcl_code_value)
        # logger.info(f"NDCL Decoded Code (meta): {ndcl_decode_code.meta.model_dump_json(indent=2)}")


    except Exception as e:
        logger.error(f"An error occurred during the SDK execution: {e}")
        logger.error(traceback.format_exc())
    finally:
        await client.close()
        # --- Session Saving ---
        # try:
        #     sdata = client.get_session_data()
        #     if sdata:
        #         async with aiofiles.open(session_path, "wb") as sf:
        #             await sf.write(sdata)
        #         logger.info("Saved session data to %s", session_path)
        #     else:
        #         logger.debug("Client returned empty session data; nothing saved.")
        # except Exception:
        #     logger.exception("Failed to save session data after run.")


if __name__ == "__main__":
    asyncio.run(main())

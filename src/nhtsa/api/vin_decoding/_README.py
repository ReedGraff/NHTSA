# Actual logic behind vin decoding
# Here lies the internal logic within the backup database for vin decoding.


from datetime import datetime
import pyodbc

# Connection details
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=LAPTOP-24LAANEQ\\SQLEXPRESS;"
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











# General meaning of each character in a VIN:
# [1]: represents the country of manufacture
# [2]: represents the manufacturer
# [3]: represents the vehicle type or manufacturing division (if the 3rd character is '9', it indicates a special vehicle type)
# [4-8]: vehicle's brand, body style, engine type, model series, etc.
#   [7]: Currently used in NA by many manufacturers for year disambiguation. For the current cycle: if the vehicle type id is 2 or 7 (Passenger Car, Multipurpose Passenger Vehicle (MPV)), or (if it's 3 (Truck) and the truck type id is 1 (light truck)) and the 7th character is a number, then the model year would be in the previous cycle. But if the 7th character is a letter, then the model year would be in the current cycle.
# [9]: check digit (used to validate the VIN)
# [10]: model year (this is an alphanumeric character that represents the year, rotating every 30 years, however, a map for the first 11 characters is maintained to provide a definitive year). Characters may not be (I, O, Q, U, Z, 0), as to avoid confusion with similar-looking characters.
# [11]: plant code (where the vehicle was assembled)
# [12-17]: unique serial number of the vehicle

# General meaning of the VIN standard
# Current VIN Standard: https://www.iso.org/standard/52200.html (ISO 3779)
# Cycles in 30 year increments. The current cycle started in 2010 and will end in 2039.

# Procedure for decoding a VIN:
# 1. Initialize variables and parameters
#    - @v (VIN input), @includePrivate, @year, @includeAll, @NoOutput
#    - Internal variables: @make, @includeNotPublicilyAvailable, @vin (sanitized), @modelYear, @modelYearSource, @conclusive, @e12, @ReturnCode, @descriptor, @dmy, @rmy, @omy, @do3and4
#    - Declare a table variable @DecItem to store decoding results for multiple passes

# 2. Pre-process VIN
#    - Strip leading/trailing spaces from @v
#    - Convert @v to uppercase
#    - Store the sanitized VIN in @vin

# 3. Extract VIN Descriptor
#    - Call dbo.fVinDescriptor(@vin) to get the descriptor (first 11 or 14 characters, with 9th char replaced by '*').
#      - fVinDescriptor logic:
#          - Pads the VIN to 17 characters with '*' if shorter.
#          - Replaces the 9th character with '*'.
#          - Returns the first 11 characters of the modified VIN.
#          - If the 3rd character of the *original* VIN is '9' (special vehicle type), it returns the first 14 characters.
#          - Converts the final descriptor to uppercase.
#    - Store the result in @descriptor.

# 4. Derive Year (Primary Attempt: VinDescriptor table)
#    - Attempt to retrieve ModelYear from the `VinDescriptor` table using the @descriptor.
#    - Store the result in @dmy.
#    - If @dmy is found AND is within a reasonable range (1980 to current_year + 2):
#        - Set @conclusive to 1 (year is known).
#        - Determine @e12 (Error 12): if a @year was provided by the user and it doesn't match @dmy, set @e12 to 1.
#        - Call dbo.spVinDecode_Core (Pass 1) with the @vin, @dmy (model year from table), @descriptor (as modelYearSource), @conclusive, @e12.
#        - This pass populates the @DecItem table with decoded attributes based on the @dmy.

# 5. Derive Year (Secondary Attempt: 10th VIN Character and Multiple Passes)
#    - ELSE (if @dmy was not found or was out of range):
#        - Call dbo.fVinModelYear2(@vin) to derive the model year from the 10th character of the VIN.
#          - fVinModelYear2 logic:
#              - Extracts the 10th character.
#              - Maps the 10th character to a base year (e.g., 'A'->2010, 'B'->2011, '1'->2031). (Note: I, O, Q, U, Z, 0 are excluded from 10th position for model year).
#              - Retrieves WMI, VehicleType, and TruckType for the VIN.
#              - Checks for specific vehicle types (Passenger Car, MPV, Light Truck) and the 7th VIN character (numeric vs. alphabetic) to determine if the year should be shifted back by 30 years (previous cycle).
#              - If the derived model year is greater than (current_year + 2), subtracts 30 years to get the previous cycle year.
#              - If the year derivation is not conclusive (e.g., no matching WMI or conflicting rules), it returns a negative value (-modelYear), indicating uncertainty.
#        - Store the primary derived year in @rmy.
#        - Set @conclusive based on `fVinModelYear2`'s return value (negative means not conclusive).
#        - If @rmy is negative (model year uncertain):
#            - Calculate an alternate model year (@omy) by adding/subtracting 30 years to @rmy (e.g., if @rmy is -2015, @omy becomes 2015-30 = 1985).
#            - Set @rmy to its positive counterpart.
#            - Set @conclusive to 0.

#        - Check if a @year was provided by the user:
#            - If the user-provided @year is within the valid range (1980 to current_year + 2):
#                - IF the user-provided @year matches either @rmy or @omy:
#                    - Set @do3and4 to 1 (proceed with passes 3 and 4).
#                - ELSE (user-provided year does not match the 10th digit derived years):
#                    - Set @modelYearSource to the user-provided @year.
#                    - Call dbo.spVinDecode_Core (Pass 2) using the user-provided @year, with @conclusive=1 and @e12=1.
#                    - Update @do3and4: if Pass 2 resulted in 'No detailed data available' (error code 8) AND @rmy exists, then set @do3and4 to 1 to try other passes. This allows for fallback if the user's year doesn't work well.
#            - ELSE (user-provided @year is out of range or not provided), @do3and4 remains 1 initially.

#        - If @do3and4 is 1 (meaning either the user's year matched, or no user year, or user year failed but fallback is enabled):
#            - Determine @e12 for @rmy: if a @year was provided by the user and it doesn't match @rmy, set @e12 to 1.
#            - Call dbo.spVinDecode_Core (Pass 3) with @vin, @rmy (primary 10th char derived year), @modelYearSource, @conclusive, @e12.
#            - If @omy is not null (meaning there was an alternate year due to uncertainty):
#                - Determine @e12 for @omy: if a @year was provided by the user and it doesn't match @omy, set @e12 to 1.
#                - Call dbo.spVinDecode_Core (Pass 4) with @vin, @omy (alternate 10th char derived year), @modelYearSource, @conclusive, @e12.

# 6. spVinDecode_Core Logic (detailed for each pass)
#    - Receives: @pass (identifies the decoding attempt), @vin, @modelYear (for this pass), @modelYearSource, @conclusive, @Error12, @includeAll, @includePrivate, @includeNotPublicilyAvailable, @ReturnCode (output).
#    - Extracts WMI using dbo.fVinWMI(@vin).
#    - Extracts key characters from VIN (positions 4-8. or if the vin > 9 chars, then it appends a "|" and then the chars 10-17) for pattern matching.
#    - Retrieves @wmiId from the `Wmi` table, considering `PublicAvailabilityDate` and `@includeNotPublicilyAvailable`.
#    - If @wmiId is null (manufacturer not registered):
#        - Add error code '7' to @ReturnCode.
#    - ELSE:
#        - Populates @DecodingItem table with data from various sources:
#            - **Pattern-based decoding:** Joins `Pattern` table with `Element`, `VinSchema`, and `Wmi_VinSchema` based on WMI, VIN keys, and the @modelYear of the current pass. Excludes specific elements.
#               - First, get all matching rows from the [Pattern Table], based on the keys variable (just part of the vin).
#               - Joins these with Element (Pattern.ElementId & Element.Id).
#               - Joins these with VinSchema (Pattern.VinSchemaId & VinSchema.Id).
#               - Joins these with Wmi_VinSchema (Wmi_VinSchema.VinSchemaId & Pattern.VinSchemaId). Where also valid for the model year of the current pass.
#               - Joins these with Wmi (Wmi.Id & Wmi_VinSchema.WmiId)
#               - Removes patterns taht decode the make, manufacturere, model year, and vehicle type (these are prioritized by wmi table data)
#               - Relevant keys/tables used here:
#                   - [Pattern Table]:
#                       - Id
#                       - VinSchemaId (links to a broader set of rules for the vehicle type. Basically, onl)
#                       - Keys (patterns to match against the @keys variable, which represents parts of the vin)
#                       - ElementId (represents the id which is joined to the element table)
#                       - AttributeId (the value for this attribute, representing another table to join to get the actual value. aka trasmission.id)
#                   - [Element Table]:
#                       - Id
#                       - Name
#                       - Code
#                       - LookupTable
#                       - Description
#                       - IsPrivate
#                       - GroupName
#                       - DataType
#                       - MinAllowedValue
#                       - MaxAllowedValue
#                       - IsQS
#                       - Decode
#                       - weight
#                   - [VinSchema Table]:
#                       - Id
#                       - Name
#                       - sourcewmi
#                       - CreatedOn
#                       - UpdatedOn
#                       - Notes
#                       - TobeQCed
#                   - [Wmi_VinSchema Table]:
#                       - Id
#                       - WmiId
#                       - VinSchemaId
#                       - YearFrom
#                       - YearTo
#                       - OrgId
#                   - [Wmi Table]:
#                       - Id
#                       - Wmi
#                       - ManufacturerId
#                       - MakeId
#                       - VehicleTypeId
#                       - CreatedOn
#                       - UpdatedOn
#                       - CountryId
#                       - PublicAvailabilityDate
#                       - TruckTypeId
#                       - ProcessedOn
#                       - NonCompliant
#                       - NonCompliantReason
#                       - NonCompliantSetByOVSC
#            - **Engine Model Pattern:** If an `EngineModel` is identified, additional patterns from `EngineModelPattern` are inserted.
#               - Basically supplements the above pattern matching with additional patterns based on the engine model.
#            - **Vehicle Type:** Inserts VehicleType from the `Wmi` table.
#               - Additionally supplements the above pattern matching with the vehicle type from the wmi table.
#            - **Manufacturer Name and ID:** Inserts Manufacturer Name and ID from the `Wmi` table.
#               - Additionally supplements the above pattern matching with the manufacturer name and id from the wmi table.
#            - **Model Year:** Inserts the @modelYear of the current pass.
#               - Literally inserts the model year of the current pass into the decoding items.
#            - **Formula Patterns:** Inserts data from `Pattern` table where keys contain '#', using substring extraction on the VIN.
#               - Effectively the same as Pattern-based decoding, but instead of using external table references, it uses formulas to extract values directly from the VIN using the @key string.
#        - **Prioritize Decoding Items:** Deletes duplicate decoding items for the same element, keeping the one with the highest priority, then latest creation date, then shortest key, then smallest ID.
#        - **Model/Make Resolution:**
#            - If a Model is identified (ElementId = 28), it uses `Make_Model` to derive Make information.
#            - If no Model is found, it attempts to derive Make if there's only one Make associated with the WMI.
#        - **Conversions:** Iterates through `Conversion` rules to calculate new attribute values (e.g., Displacement CC to CI) and inserts them into @DecodingItem if not already present.
#        - **Vehicle Specification Patterns:**
#            - Identifies relevant `VehicleSpecSchema` and `VSpecSchemaPattern` based on WMI, VehicleType, Model, and ModelYear.
#            - Filters patterns based on existing decoded elements.
#            - Inserts non-key attributes from matching `VehicleSpecPattern` into @DecodingItem.
#        - **Error Code Calculation:**
#            - Calls dbo.spVinDecode_ErrorCode(@vin, @modelYear, @decodingItem, @ReturnCode OUTPUT, @CorrectedVIN OUTPUT, @ErrorBytes OUTPUT, @UnUsedPositions OUTPUT).
#              - spVinDecode_ErrorCode logic:
#                  - Initializes @CorrectedVIN, @ErrorBytes, @ReturnCode.
#                  - Validates VIN length and WMI.
#                  - Retrieves `WMIYearValidChars` (or uses `fExtractValidCharsPerWmiYear` if cache is empty) for the WMI and @modelYear of the current pass. This table contains valid characters for VIN positions 4-8 and 11.
#                  - Iterates through VIN characters (positions 4 to 14, excluding 9 and 10 initially):
#                      - If the character does not match valid characters for that position, it's marked as an error ('!').
#                      - Collects possible valid replacements for erroneous characters.
#                  - If only one error is found:
#                      - If there's only one valid replacement, `CorrectedVIN` is updated, and error code '2' is set.
#                      - If multiple valid replacements, it attempts to calculate the check digit for each replacement. If one works, `CorrectedVIN` is updated and error code '3' is set. Otherwise, error code '4' is set.
#                  - If multiple errors are found, error code '5' is set.
#                  - Checks for "unused positions" (VIN characters that don't match any patterns). If found, error code '14' is added.
#        - **Additional Error/Warning Handling:**
#            - Adds error code '9' if specific BodyStyle (AttributeId = 64) is found.
#            - Adds error code '10' if specific BodyStyle attributes indicate an off-road vehicle.
#            - Adds error code '11' if @modelYear is null.
#            - Checks for invalid characters based on position rules (e.g., 10th character cannot be I, O, Q, U, Z, 0; positions >=15 must be numbers for certain types). Adds error code '400'.
#            - Adds error code '12' if @Error12 (model year discrepancy) is true.
#        - **Default Values:** Inserts default values from `DefaultValue` table for elements not yet decoded, based on VehicleType.
#        - **VIN Length Check:** Adds error code '6' if VIN length is less than 17.
#        - **Check Digit Validation:**
#            - Calculates the check digit using dbo.fVINCheckDigit2(@vin, @isCarmpvLT).
#            - If calculated check digit does not match the 9th VIN character AND it's not a `VinException` for check digit:
#                - Adds error code '1' to @ReturnCode.
#        - **Final Return Code Assignment:**
#            - If no "major" errors (7, 8, 1, 4, 5, 6, 11, 400), prepends '0' to @ReturnCode.
#            - Adds error code '14' if no model was identified and '0' is present.
#        - **Additional Decoding Info:** Appends specific text for certain error codes (4, 5, 14, 400).
#        - Adds "Incomplete Vehicle Warning" for specific vehicle types/body styles.
#        - If @conclusive is 0 (model year uncertain), adds a warning message.
#        - Populates @DecodingItem with error-related information (Corrected VIN, Error Codes, Error Messages, Error Bytes, Additional Info, VinDescriptor).

# 7. Determine the Best Decoding Pass
#    - Counts the number of distinct DecodingId (passes) in @DecItem.
#    - Creates a temporary table #x to aggregate metrics for each pass:
#        - DecodingId
#        - ErrorCodes (from ElementId 143 in @DecItem)
#        - ErrorValue (calculated using dbo.fErrorValue(@ErrorCodes), which sums weights of individual error codes)
#        - ElementsWeight (sum of `weight` from `Element` table for non-null decoded values)
#        - Patterns (count of items from 'Pattern' or 'EngineModelPattern' sources with non-empty values)
#        - ModelYear (from ElementId 29 in @DecItem, with a bonus if it matches the user-provided @year)
#    - Selects the @bestPass by ordering #x:
#        - `ErrorValue` DESC (prioritizes passes with fewer/less severe errors, as `ErrorValue` is typically negative, so higher value is better/less negative).
#        - `ElementsWeight` DESC (more decoded elements are better).
#        - `Patterns` DESC (more patterns matched are better).
#        - `ModelYear` DESC (higher model year is preferred, with a strong bonus for matching user-provided year).
#    - Deletes all decoding items from @DecItem that do not belong to the @bestPass.

# 8. Final Processing and Output
#    - Updates `TobeQCed` flag in @DecItem for items from specific sources (`Pattern`, `Formula`, `EngineModelPattern`, `Conversion`) if their `VinSchema` is marked `TobeQCed`.
#    - If `@includeNotPublicilyAvailable` is false, deletes items where `TobeQCed` is true.
#    - Replaces 'XXX' placeholder values in @DecItem with actual lookup names by calling dbo.fElementAttributeValue.
#    - If @NoOutput is 0 (return results directly):
#        - Selects and orders final decoded attributes from @DecItem and `Element` tables, filtering by `@includeAll` and `@includePrivate`.
#    - ELSE (@NoOutput is 1, output to table):
#        - Inserts the final decoded attributes into the `DecodingOutput` table, with similar filtering and ordering.

# Values
# WMI: will represent the first 3 characters of the VIN. or if the 3rd character is '9', the WMI will include characters 12-14. making the WMI 6 characters (1, 2, 3, 12, 13, 14)). For each wmi, there are:
#   Id
#   Wmi
#   ManufacturerId
#   MakeId
#   VehicleTypeId
#   CreatedOn
#   UpdatedOn
#   CountryId
#   PublicAvailabilityDate
#   TruckTypeId (null, 1 = "Light Trucks", 2 = "Medium/Heavy Trucks") # This is assumed based on usage.
#   ProcessedOn
#   NonCompliant
#   NonCompliantReason
#   NonCompliantSetByOVSC

# vin decoding output:


# Procedures (db --> programmability --> stored procedures)
## spVinDecode
"""
USE [vPICList_Lite1]
GO
/****** Object:  StoredProcedure [dbo].[spVinDecode]    Script Date: 9/24/2025 8:05:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER PROCEDURE [dbo].[spVinDecode]
	@v varchar(50),              /* vin input */
	@includePrivate bit = null,  /* include private data */
	@year int = null,            /* year input (optional since most vins include the year) */
	@includeAll bit = null,      /* include all data */
	@NoOutput bit = 0            /* if 1, outputs to DecodingOutput table instead of returning results */
as 
begin
	SET NOCOUNT ON;

	declare 
		@make varchar(50) = null, 
		@includeNotPublicilyAvailable bit = null, 
		@vin varchar(17) = '', 
		@modelYear int, 
		@modelYearSource varchar(20) = '***X*|Y',
		@conclusive bit = 0, 
		@e12 bit = 0 

	declare @ReturnCode varchar(100) = ''
	set @vin = upper(LTRIM(RTRIM(@v))) /* trims leading / trailing spaces */
	declare @descriptor varchar(17) = dbo.fVinDescriptor(@vin) /* returns the vin minus the serial number. or in special cases including the first 3 digits of the serial number for special vehicle types */
	declare @dmy int = null


	set @dmy = (select ModelYear from VinDescriptor where Descriptor = @descriptor) /* Gets the model year from the VinDescriptor table, using the full first 11 or 14 digits. Not purely relying on the 10th digit. If there is no match, this will be null */
	
	declare @rmy int, @omy int
	declare @DecItem [tblDecodingItem] /* table where the entire output will be stored */

	if @dmy between 1980 and (year(getdate()) + 2) /* if model year is between 1980 and 2 years in the future */
	begin
		select @conclusive=1, @e12 = iif (@year is not null and @dmy is not null and @year <> @dmy, 1, 0) /* basically, if the year was found in the table, then we set the year as conslusive (AKA known), otherwise it is 0. also sets the variable e12 if the model year from the table and the year from the user don't match, otherwise it is false */
		insert into @DecItem ([DecodingId],[CreatedOn],[PatternId],[Keys],[VinSchemaId],[WmiId],[ElementId],[AttributeId],[Value],[Source],[Priority],[TobeQCed]) /* creates a bunch of rows in the output table */
		exec [dbo].[spVinDecode_Core] 1, @vin, @dmy, @descriptor, @conclusive, @e12, @includeAll, @includePrivate, @includeNotPublicilyAvailable, @ReturnCode output
	end
	else
	begin /* if model year is not between 1980 and 2 years in the future */
		select @rmy = dbo.fVinModelYear2 (upper(@vin)), @conclusive = 1 /* gets the model year from the 10th character of the vin. sets conclusive to true. it will return a negative number if the model year is uncertain */
		if @rmy < 0 /* if model year uncertain */
			select @omy = -@rmy-30, @rmy = -@rmy,  @conclusive = 0 /* creates an alternate model year */

		declare @do3and4 bit = 1
		if @year between 1980 and (year(getdate()) + 2)
		begin
			if (@year = @rmy or @year = @omy) /* if the year from the user matches either of the model years */
				set @do3and4 = 1 /* nothing changes */
			else
			begin
				set @modelYearSource = cast(@year as varchar)

				insert into @DecItem ([DecodingId],[CreatedOn],[PatternId],[Keys],[VinSchemaId],[WmiId],[ElementId],[AttributeId],[Value],[Source],[Priority],[TobeQCed])
				exec [dbo].[spVinDecode_Core] 2, @vin, @year, @modelYearSource, 1, 1, @includeAll, @includePrivate, @includeNotPublicilyAvailable, @ReturnCode output
				set @do3and4 = iif(@ReturnCode like '% 8 %' and (@rmy is not null), 1, 0)  

			end
		end
		
		if @do3and4 = 1
		begin
			select @e12 = iif (@year is not null and @rmy is not null and @year <> @rmy, 1, 0)
			insert into @DecItem ([DecodingId],[CreatedOn],[PatternId],[Keys],[VinSchemaId],[WmiId],[ElementId],[AttributeId],[Value],[Source],[Priority],[TobeQCed])
			exec [dbo].[spVinDecode_Core] 3, @vin, @rmy, @modelYearSource, @conclusive, @e12, @includeAll, @includePrivate, @includeNotPublicilyAvailable, @ReturnCode output
			if not @omy is null
			begin
				select @e12 = iif (@year is not null and @omy is not null and @year <> @omy, 1, 0)
				insert into @DecItem ([DecodingId],[CreatedOn],[PatternId],[Keys],[VinSchemaId],[WmiId],[ElementId],[AttributeId],[Value],[Source],[Priority],[TobeQCed])
				exec [dbo].[spVinDecode_Core] 4, @vin, @omy, @modelYearSource, @conclusive, @e12, @includeAll, @includePrivate, @includeNotPublicilyAvailable, @ReturnCode output
			end
		end
		
	end

	declare @bestPass int = 0 
	declare @passes int = (select count (distinct decodingId) from @DecItem)

	CREATE TABLE #x(
		DecodingId int null, 
		ErrorCodes varchar(100) null, 
		ErrorValue int null,
		ElementsWeight int null , 
		Patterns int null , 
		ModelYear int
) 
	insert into #x
	select err.* , el.ElementsWeight, p.Patterns, my.ModelYear + my.ModelYearBonus as ModelYear
	from 
	(	
		select distinct DecodingId
		from @DecItem 
	) a 
	left outer join
	(	
		select DecodingId, Value as ErrorCodes, dbo.fErrorValue(Value) ErrorValue
		from @DecItem 
		where ElementId = 143
	) err on a.DecodingId = err.DecodingId
	left outer join
	(	
		select DecodingId, sum(weight) as ElementsWeight
		from (
			select distinct DecodingId, d.ElementId, e.weight
			from @DecItem d inner join Element e on d.ElementId = e.id 
			where isnull(d.Value, '') <> '' and e.weight is not null
		) t
		group by DecodingId
	) el on err.DecodingId = el.DecodingId
	left outer join
	(	
		select DecodingId, count(*) as Patterns
		from @DecItem d 
		where Source in ('Pattern', 'EngineModelPattern' ) and isnull(Value, '') not in ('', 'Not Applicable')
		group by DecodingId
	) p on err.DecodingId = p.DecodingId
	left outer join
	(	
		select DecodingId, cast(Value as int) as ModelYear, case when @year = value then 10000 else 0 end as ModelYearBonus
		from @DecItem 
		where ElementId = 29
	) my on a.DecodingId = my.DecodingId

	select top 1 @bestPass = DecodingId from #x order by ErrorValue desc, ElementsWeight desc, Patterns desc, modelYear desc 

	delete @DecItem where decodingid <> @bestPass

	update @DecItem 
	set TobeQCed = vs.TobeQCed
	from @DecItem d inner join VinSchema vs on d.VinSchemaId = vs.Id and vs.TobeQCed = 1
	where lower(left(isnull(d.Source, ''), 7)) in ('pattern', 'formula', 'enginem', 'convers')

	if isnull(@includeNotPublicilyAvailable, 0) = 0 
		delete 
		from @DecItem 
		where TobeQCed = 1

	update @DecItem	
	set value = case when e.LookupTable is null then t.AttributeId else dbo.fElementAttributeValue (t.ElementId, t.AttributeId) end
	from @DecItem t inner join Element e on t.ElementId = e.Id
	where t.Value = 'XXX' 


	if @NoOutput = 0 
	begin
		select 
			e.GroupName, 
			e.Name as Variable, 
			REPLACE(REPLACE(REPLACE(t.Value, CHAR(9), ' '), CHAR(13), ' '), CHAR(10), ' ') as Value, 
			t.PatternId, 
			t.VinSchemaId, 
			t.Keys, 
			e.id as ElementId, 
			t.AttributeId, 
			t.CreatedOn as CreatedOn, 
			t.WmiId,
			e.Code, 
			e.DataType, 
			e.Decode,
			t.Source, 
			t.ToBeQCed as ToBeQCd
		from 
			Element e with (nolock)
			left outer join @DecItem t on t.ElementId = e.Id
		where 
			(isnull(e.Decode, '') <> '') 
			and ((@includeAll) = 1 or (isnull(@includeAll, 0) = 0 and not t.ElementId is null)) 
			and (@includePrivate = 1 or isnull(e.IsPrivate, 0) = 0 ) 
		order by 
			case isnull(e.GroupName, '')
				when '' then 0
				when 'General' then 1
				when 'Exterior / Body' then 2
				when 'Exterior / Dimension' then 3
				when 'Exterior / Truck' then 4
				when 'Exterior / Trailer' then 5
				when 'Exterior / Wheel tire' then 6
				when 'Exterior / Motorcycle' then 7
				when 'Exterior / Bus' then 8
				when 'Interior' then 9
				when 'Interior / Seat' then 10
				when 'Mechanical / Transmission' then 11
				when 'Mechanical / Drivetrain' then 12
				when 'Mechanical / Brake' then 13
				when 'Mechanical / Battery' then 14
				when 'Mechanical / Battery / Charger' then 15
				when 'Engine' then 16
				when 'Passive Safety System' then 17
				when 'Passive Safety System / Air Bag Location' then 18
				when 'Active Safety System' then 19
				when 'Active Safety System / Maintaining Safe Distance' then 20
				when 'Active Safety System / Forward Collision Prevention' then 21
				when 'Active Safety System / Lane and Side Assist' then 22
				when 'Active Safety System / Backing Up and Parking' then 23
				when 'Active Safety System / 911 Notification' then 24
				when 'Active Safety System / Lighting Technologies' then 25
				when 'Internal' then 26
				else 99 end
			, e.Id
	end
	else
	begin
		insert into DecodingOutput (GroupName, Variable, Value, PatternId, VinSchemaId, Keys, ElementId, AttributeId, CreatedOn, WmiId, Code, DataType, Decode, Source)
		select 
			e.GroupName, 
			e.Name as Variable, 
			REPLACE(REPLACE(REPLACE(t.Value, CHAR(9), ' '), CHAR(13), ' '), CHAR(10), ' ') as Value, 
			t.PatternId, 
			t.VinSchemaId, 
			t.Keys, 
			e.id as ElementId, 
			t.AttributeId, 
			t.CreatedOn as CreatedOn, 
			t.WmiId,
			e.Code, 
			e.DataType, 
			e.Decode,
			t.Source 
		from 
			Element e with (nolock)
			left outer join @DecItem t on t.ElementId = e.Id
		where 
			(isnull(e.Decode, '') <> '') 
			and ((@includeAll) = 1 or (isnull(@includeAll, 0) = 0 and not t.ElementId is null)) 
			and (@includePrivate = 1 or isnull(e.IsPrivate, 0) = 0 ) 
		order by 
			case isnull(e.GroupName, '')
				when '' then 0
				when 'General' then 1
				when 'Exterior / Body' then 2
				when 'Exterior / Dimension' then 3
				when 'Exterior / Truck' then 4
				when 'Exterior / Trailer' then 5
				when 'Exterior / Wheel tire' then 6
				when 'Exterior / Motorcycle' then 7
				when 'Exterior / Bus' then 8
				when 'Interior' then 9
				when 'Interior / Seat' then 10
				when 'Mechanical / Transmission' then 11
				when 'Mechanical / Drivetrain' then 12
				when 'Mechanical / Brake' then 13
				when 'Mechanical / Battery' then 14
				when 'Mechanical / Battery / Charger' then 15
				when 'Engine' then 16
				when 'Passive Safety System' then 17
				when 'Passive Safety System / Air Bag Location' then 18
				when 'Active Safety System' then 19
				when 'Active Safety System / Maintaining Safe Distance' then 20
				when 'Active Safety System / Forward Collision Prevention' then 21
				when 'Active Safety System / Lane and Side Assist' then 22
				when 'Active Safety System / Backing Up and Parking' then 23
				when 'Active Safety System / 911 Notification' then 24
				when 'Active Safety System / Lighting Technologies' then 25
				when 'Internal' then 26
				else 99 end
			, e.Id
	end
	
end
"""

## spVinDecode_Core
"""
USE [vPICList_Lite1]
GO
/****** Object:  StoredProcedure [dbo].[spVinDecode_Core]    Script Date: 9/24/2025 9:02:05 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

ALTER PROCEDURE [dbo].[spVinDecode_Core]
	@pass int,                                   /*  */
	@vin varchar(17),                            /* full vin */
	@modelYear int ,                             /* model year */
	@modelYearSource varchar(20) = '',           /*  */
	@conclusive bit = 0,                         /*  */
	@Error12 bit = 0,                            /*  */
	@includeAll bit = null,                      /*  */
	@includePrivate bit = null,                  /*  */
	@includeNotPublicilyAvailable bit = null,    /*  */
	@ReturnCode varchar(100) OUTPUT              /*  */
as
begin
set @ReturnCode = ''





Declare 		
	@wmi varchar(6) = dbo.fVinWMI(@vin), 
	@keys varchar(50) = '', 
	@wmiId int, 
	@patternId int, 
	@vinSchemaId int, 
	@formulaKeys nvarchar(14) = '',
	@cnt int = 0

declare 
	@descriptor varchar(17) = dbo.fVinDescriptor(@vin) 

	if LEN(@vin) > 3
	Begin
		set @keys = SUBSTRING(@vin, 4, 5)
		if LEN(@vin) > 9
			set @keys  = @keys + '|' + SUBSTRING(@vin, 10, 8)
	end


declare 
	@CorrectedVIN varchar(17), 
	@ErrorBytes varchar(500), 
	@AdditionalDecodingInfo varchar(500), 
	@UnUsedPositions varchar(500)

	select @wmiId = Id from Wmi with (nolock) where Wmi = @wmi and (@includeNotPublicilyAvailable = 1 or (PublicAvailabilityDate <= getdate()))
	if @wmiid is null
	begin
		select @ReturnCode = @ReturnCode + ' 7 ', @CorrectedVIN = '', @ErrorBytes = ''
	end
	else
	begin
		
		
		declare @DecodingItem [tblDecodingItem]
		
		INSERT INTO @DecodingItem ([DecodingId], [Source], [CreatedOn], [Priority], [PatternId], [Keys], [VinSchemaId], [WmiId], [ElementId], [AttributeId], [Value], TobeQCed)
		SELECT 
			@pass, 
			'Pattern', 
			isnull(p.UpdatedOn, p.CreatedOn), 
			wvs.YearFrom, 
			p.Id, 
			upper(p.Keys), 
			p.VinSchemaId, 
			wvs.WmiId, 
			p.ElementId,
			p.AttributeId, 
			'XXX', 
			vs.TobeQCed
		FROM 
			dbo.Pattern AS p with (nolock) 
			INNER JOIN dbo.Element E with (nolock) ON P.ElementId = E.Id
			INNER JOIN dbo.VinSchema VS with (nolock) on p.VinSchemaId = vs.Id
			INNER JOIN dbo.Wmi_VinSchema AS wvs with (nolock) ON vs.Id = wvs.VinSchemaId and ((@modelYear  is null) or (@modelYear between wvs.YearFrom and isnull(wvs.YearTo, 2999))) 
			INNER JOIN dbo.Wmi AS w with (nolock) ON wvs.WmiId = w.Id and w.Wmi = @wmi
		WHERE   
			@keys like replace(p.Keys, '*', '_') + '%' 
			and not p.ElementId in  (26, 27, 29, 39) 
			and not E.Decode is null 
			and (isnull(e.IsPrivate, 0) = 0 or @includePrivate = isnull(e.IsPrivate, 0))
			and (@includeNotPublicilyAvailable = 1 or (w.PublicAvailabilityDate <= getdate()))
			and (@includeNotPublicilyAvailable = 1 or (isnull(vs.TobeQCed, 0) = 0))


		
		declare @EngineModel varchar(500), @k varchar(50)
		
		select top 1 @EngineModel = attributeid, @patternId = PatternId, @vinSchemaId = VinSchemaId, @k = Keys
		from @DecodingItem 
		where DecodingId = @pass and ElementId = 18 
		order by [Priority] desc

		if not @EngineModel is null
			INSERT INTO @DecodingItem ([DecodingId], [Source], [CreatedOn], [Priority], [PatternId], [Keys], [VinSchemaId], [WmiId], [ElementId], [AttributeId], [Value])
			SELECT 
				@pass, 'EngineModelPattern', isnull(p.UpdatedOn, p.CreatedOn), 50, 
				@patternId, @k, @vinSchemaId, @wmiId, p.ElementId,  
				p.AttributeId, 'XXX' 
			FROM 
				EngineModel em with (nolock) 
				inner join dbo.EngineModelPattern AS p with (nolock) on em.Id = p.EngineModelId
				INNER JOIN dbo.Element E with (nolock) ON P.ElementId = E.Id
			WHERE   
				em.Name = @EngineModel

		
		INSERT INTO @DecodingItem ([DecodingId], [Source], CreatedOn, [Priority], [PatternId], [Keys], [VinSchemaId], [WmiId], [ElementId], [AttributeId], [Value])
		select 
			@pass, 'VehType', isnull(w.UpdatedOn, w.CreatedOn), 100, 
			null, upper(@wmi) as keys , null, w.Id as WmiId, 39, 
			CAST(t.Id as varchar), upper(t.Name) as Value
		from wmi w with (nolock) 
			join VehicleType t with (nolock) on t.Id = w.VehicleTypeId
		where Wmi = @wmi
			and (@includeNotPublicilyAvailable =1 or (w.PublicAvailabilityDate <= getdate()))

		
		declare @MfrId int, @MfrName varchar(500)
		select @MfrId = t.Id, @MfrName = upper(t.Name) 
		from wmi w with (nolock) 
			join Manufacturer t with (nolock) on t.Id = w.ManufacturerId
		where Wmi = @wmi
			and (@includeNotPublicilyAvailable =1 or (w.PublicAvailabilityDate <= getdate()))

		INSERT INTO @DecodingItem ([DecodingId], [Source], [Priority], [PatternId], [Keys], [VinSchemaId], [WmiId], [ElementId], [AttributeId], [Value])
		select @pass, 'Manuf. Name', 100, null, upper(@wmi) as keys, null, @WmiId as WmiId, 27, CAST(@MfrId as varchar), @MfrName as Value

		INSERT INTO @DecodingItem ([DecodingId], [Source], [Priority], [PatternId], [Keys], [VinSchemaId], [WmiId], [ElementId], [AttributeId], [Value])
		select @pass, 'Manuf. Id', 100, null, upper(@wmi) as keys, null, @WmiId AS wMIiD, 157, CAST(@MfrId as varchar), CAST(@MfrId as varchar)

		
		INSERT INTO @DecodingItem ([DecodingId], [Source], [Priority], [PatternId], [Keys], [VinSchemaId], [WmiId], [ElementId], [AttributeId], [Value])
		select 
			@pass, 'ModelYear', 100, 
			null, @modelYearSource , null, null, 29, 
			CAST(@modelYear as varchar), CAST(@modelYear as varchar) as Value
		where not @modelYear is null
		
		
		set @formulaKeys = @keys				
		set @formulaKeys = replace(@formulaKeys,1,'#')
		set @formulaKeys = replace(@formulaKeys,2,'#')
		set @formulaKeys = replace(@formulaKeys,3,'#')
		set @formulaKeys = replace(@formulaKeys,4,'#')
		set @formulaKeys = replace(@formulaKeys,5,'#')
		set @formulaKeys = replace(@formulaKeys,6,'#')
		set @formulaKeys = replace(@formulaKeys,7,'#')
		set @formulaKeys = replace(@formulaKeys,8,'#')
		set @formulaKeys = replace(@formulaKeys,9,'#')
		set @formulaKeys = replace(@formulaKeys,0,'#')

		INSERT INTO @DecodingItem ([DecodingId], [Source], CreatedOn, [Priority], [PatternId], [Keys], [VinSchemaId], [WmiId], [ElementId], [AttributeId], [Value])
		select 
			@pass, 'Formula Pattern', isnull(p.UpdatedOn, p.CreatedOn), 100, 
			p.Id, p.Keys as Keys, p.VinSchemaId, null, p.ElementId, 
			p.AttributeId, SUBSTRING(@keys, CHARINDEX('#', p.keys), ((len(p.keys) - charindex('#', REVERSE(p.Keys)) + 1) - (CHARINDEX('#', p.keys)) + 1)) as value
		FROM  
			dbo.Pattern AS p with (nolock) 
			INNER JOIN dbo.Element E with (nolock) ON P.ElementId = E.Id 
		WHERE   
			p.VinSchemaId in 
				( 
					SELECT wvs.VinSchemaId  
					FROM dbo.Wmi AS w with (nolock) 
						INNER JOIN dbo.Wmi_VinSchema AS wvs with (nolock) ON w.Id = wvs.WmiId and ((@modelYear  is null) or (@modelYear between wvs.YearFrom and isnull(wvs.YearTo, 2999))) 
					WHERE w.Wmi = @wmi and ((@modelYear  is null) or (@modelYear between wvs.YearFrom and isnull(wvs.YearTo, 2999)))
						and (@includeNotPublicilyAvailable =1 or (w.PublicAvailabilityDate <= getdate()))
				) 
			and CHARINDEX('#', p.keys) > 0 
			and not p.ElementId in  (26, 27, 29, 39) 
			and @formulaKeys like replace(p.Keys, '*', '_') + '%' 

		
		delete 
		from @DecodingItem 
		where Id IN
		(
			SELECT Id FROM 
			(
				SELECT d.Id, RANK() OVER (PARTITION BY ElementId ORDER BY Priority DESC, createdon DESC, LEN(REPLACE(ISNULL(D.Keys, ''), '*', '')), ID) AS RankResult
				FROM @DecodingItem D 
				
				WHERE DecodingId = @pass and D.ElementId NOT IN (121, 129, 150, 154, 155, 114, 169, 186)
			) t WHERE t.RankResult > 1
		)

		
		declare @modelId int
		select @modelId = attributeid from @DecodingItem where DecodingId = @pass and ElementId = 28 
		
		if not @modelId is null
		begin
			
			INSERT INTO @DecodingItem ([DecodingId], [Source], [Priority], [PatternId], [Keys], [VinSchemaId], [WmiId], [ElementId], [AttributeId], [Value])
			SELECT     
				@pass, 'pattern - model', 1000, 
				di.PatternId, di.Keys, di.VinSchemaId, null as WmiId, 26 AS ElementId, 
				mk.Id AS AttributId, upper(mk.Name) AS Value
			FROM         
				dbo.Make_Model AS mm with (nolock) 
				INNER JOIN dbo.Make AS mk with (nolock) ON mm.MakeId = mk.Id 
				INNER JOIN @DecodingItem AS di ON mm.ModelId = di.AttributeId and di.DecodingId = @pass
			WHERE     
				(di.ElementId = 28) 
				AND (di.DecodingId = @pass)
		end
		else
		begin
			
			
			select @cnt = count(*)
			from wmi w with (nolock) 
				join Wmi_Make wm with (nolock) on wm.WmiId = w.Id
				join Make t with (nolock) on t.Id = wm.MakeId
			where Wmi = @wmi
				and (@includeNotPublicilyAvailable = 1 or (w.PublicAvailabilityDate <= getdate()))
			if @cnt = 1 
			begin
				INSERT INTO @DecodingItem ([DecodingId], [Source], [CreatedOn], [Priority], [PatternId], [Keys], [VinSchemaId], [WmiId], [ElementId], [AttributeId], [Value])
				select 
					@pass, 'Make', isnull(w.UpdatedOn, w.CreatedOn), -100, 
					null, @wmi as keys , null, w.Id as WmiId, 26, 
					CAST(t.Id as varchar), upper(t.Name) as Value
				from wmi w with (nolock) 
					join Wmi_Make wm with (nolock) on wm.WmiId = w.Id
					join Make t with (nolock) on t.Id = wm.MakeId
				where Wmi = @wmi
				and (@includeNotPublicilyAvailable = 1 or (w.PublicAvailabilityDate <= getdate()))
			end
		end

		
		
		
	declare 
			@fromElementId int, 
			@toElementId int,
			@formula nvarchar(max),
			@params nvarchar(max),
			@sql nvarchar(max),
			@value varchar(500),
			@conversionId int,
			@dataType varchar(50)
			
			
			


	DECLARE crsr CURSOR STATIC LOCAL FOR
		SELECT di.Keys, di.ElementId, di.AttributeId, c.ToElementId, c.Formula , c.id, e.DataType, di.PatternId, di.VinSchemaId, di.WmiId
		FROM @DecodingItem DI 
			inner join conversion c with (nolock) on di.ElementId = c.FromElementId
			inner join Element e with (nolock) on c.ToElementId = e.Id
		where di.DecodingId = @pass
		ORDER BY di.priority DESC, DI.CreatedOn Desc
	OPEN crsr

	WHILE 1 = 1
	BEGIN
		FETCH crsr INTO @keys, @fromElementId, @value, @toElementId, @formula, @conversionId, @dataType, @patternId, @vinschemaId, @wmiId
		IF @@fetch_status <> 0
			BREAK

		
		IF NOT EXISTS(SELECT 1 FROM @DecodingItem WHERE DecodingId = @pass and  ElementId = @toElementId)
		BEGIN
			
			set @formula = replace(@formula, '#x#', @value)

			if lower(@dataType) = 'decimal'
				set @dataType = @dataType + '(12, 2)'
			if lower(@dataType) = 'int'
				set @formula = ' CONVERT(int, ROUND(' + @formula + ', 0)) '

			set @sql = 'select @result = ' + @formula
			
			set @params = N'@result varchar(500) output'


			declare @result varchar(500) = ''
			begin try 
				exec sp_executesql @sql, @params, @result = @result out
			end try 
			begin catch 
				set @result = '0'
			end catch 
			
			INSERT INTO @DecodingItem ([DecodingId], [Source], [Priority], [PatternId], [Keys], [VinSchemaId], [WmiId], [ElementId], [AttributeId], [Value])
			values (@pass, left('Conversion ' + CAST(@conversionId as varchar)+ ': ' + @formula, 50), 100, @patternId, @keys, @vinschemaId, @wmiId, @toElementId, @result, @result)

		end

	END
	DEALLOCATE crsr



		declare @tVehicleType int
		select top 1 @tVehicleType = attributeid from @DecodingItem where DecodingId = @pass and elementid = 39

		declare @tmpPatterns table (id int, TobeQCed bit null)
		declare @tmpPatternsEx table (id int, a int, b int)

		insert into @tmpPatterns 
		select distinct sp.id, s.TobeQCed
		from VehicleSpecSchema s with (nolock) 
			inner join VSpecSchemaPattern sp with (nolock) on s.id = sp.SchemaId
			inner join VehicleSpecPattern p with (nolock) on sp.Id = p.VSpecSchemaPatternId
			inner join VehicleSpecSchema_Model vssm with (nolock) on vssm.VehicleSpecSchemaId = s.id
			left outer join VehicleSpecSchema_Year vssy with (nolock) on vssy.VehicleSpecSchemaId = s.id
			inner join Wmi_Make wm with (nolock) on wm.MakeId = s.makeid
			inner join wmi with (nolock) on wmi.id = wm.WmiId
		where 1 = 1
			and wmi.wmi = @wmi
			and s.VehicleTypeId = @tVehicleType
			and vssm.ModelId = @modelId
			and (vssy.Year = @modelYear or vssy.Id is null) 
			and p.IsKey=1
			and (@includeNotPublicilyAvailable = 1 or (isnull(s.TobeQCed, 0) = 0))

		insert into @tmpPatternsEx (id, a, b) 
		select 
			p.VSpecSchemaPatternId, count(*) as cntTotal, count (distinct d.id) as cntMatch
		from
			VehicleSpecPattern p with (nolock) 
			inner join @tmpPatterns ptrn on p.VSpecSchemaPatternId = ptrn.id 
			left outer join @DecodingItem d on d.DecodingId = @pass and p.ElementId = d.ElementId and p.AttributeId = d.AttributeId
		where 
			p.IsKey = 1
		group by p.VSpecSchemaPatternId
		having count(*) <> count(distinct d.id)

		delete from @tmpPatterns where id in (select id from @tmpPatternsEx) 

		declare @tbl1 table (
			IsKey bit, 
			vSpecSchemaId int, 
			vSpecPatternId int, 
			ElementId int, 
			AttributeId varchar(500), 
			ChangedOn datetime null,
			TobeQCed bit null
		)

		insert into @tbl1 
			(iskey, vSpecSchemaId, vSpecPatternId, ElementId, AttributeId, ChangedOn, TobeQCed)
		SELECT distinct
			vsp.IsKey, vsvp.SchemaId, vsp.vspecschemapatternid, vsp.ElementId, vsp.AttributeId, isnull(vsp.UpdatedOn, vsp.CreatedOn), ptrn.TobeQCed
		FROM 
			VehicleSpecPattern vsp with (nolock) 
			inner join VSpecSchemaPattern vsvp with (nolock) on vsvp.id = vsp.vspecschemapatternid
			inner join @tmpPatterns ptrn on vsvp.id = ptrn.id
		WHERE   
			vsp.IsKey = 0
			and vsp.ElementId not in (
				select elementid 
				from @DecodingItem 
				where DecodingId = @pass and elementid not in (1, 114, 121, 129, 150, 154, 155, 169, 186)
			)

		
		; WITH cte AS (
			SELECT elementid,
				row_number() OVER(PARTITION BY elementid order by attributeid) AS [rn]
			FROM @tbl1  
		)
		DELETE cte WHERE [rn] > 1

		INSERT INTO 
			@DecodingItem ([DecodingId], [Source], [CreatedOn], [Priority], [PatternId], [Keys], [VinSchemaId], [WmiId], [ElementId], [AttributeId], [Value], TobeQCed)
		SELECT distinct
			@pass, 'Vehicle Specs', ChangedOn, -100, vSpecPatternId, '', vSpecSchemaId, null, ElementId, AttributeId, 
			'XXX' 
			, TobeQCed
		FROM 
			@tbl1
	
		
		if (select COUNT(*) from @DecodingItem where DecodingId = @pass and not PatternId is null) = 0
		begin
			
			select @ReturnCode = @ReturnCode + ' 8 ', @CorrectedVIN = '', @ErrorBytes = ''
		end
		else
		begin
			
			
			
			
			exec spVinDecode_ErrorCode @vin, @modelYear, @decodingItem
				, @ReturnCode OUTPUT
				, @CorrectedVIN OUTPUT
				, @ErrorBytes OUTPUT
				, @UnUsedPositions OUTPUT
		end
	end 

	
	if exists(select 1 from @DecodingItem where DecodingId = @pass and ElementId = 5 and AttributeId = 64)
	begin
		select @ReturnCode = @ReturnCode + ' 9 '
	end
	

	
	declare @isOffRoad bit = 0 
	if exists(select 1 from @DecodingItem where ElementId = 5 and AttributeId in (69, 84, 86, 88, 97, 105, 113, 124, 126, 127) and DecodingId = @pass)
	begin
		select @ReturnCode = @ReturnCode + ' 10 '
		set @isOffRoad = 1 
	end
	

	
	If @modelYear is null
	begin
		select @ReturnCode = @ReturnCode + ' 11 '
	end

	

	declare @vehicleType varchar(500) = (select AttributeId from @DecodingItem where DecodingId = @pass and ElementId = 39)
	

	
	declare @isVinExceptionCheckDigit bit = 0
	if exists(select 1 from VinException where VIN = @vin and CheckDigit = 1)
	begin
		
		set @isVinExceptionCheckDigit = 1
	end

	
	
	DECLARE @invalidChars VARCHAR(500) = ''
	DECLARE @startPos INT = 13 
		, @x_vehicleTypeId INT, @x_truckTypeId INT, @j INT = 0, @chr varCHAR(10) = ''
		, @isCarMpvLT bit = 0 
	IF SUBSTRING(@vin, 3, 1) = '9'
		SET @startPos = 15 
	ELSE
    begin
		SELECT @x_vehicleTypeId = vehicleTypeId, @x_truckTypeId = truckTypeId FROM dbo.Wmi with (nolock) WHERE wmi = @wmi
		IF @x_vehicleTypeId IN (2, 7) OR (@x_vehicleTypeId = 3 AND @x_truckTypeId = 1) 
			select @startPos = 13, @isCarmpvLT = 1 
		else
			SET @startPos = 14 
	end
	
	WHILE @j < LEN(@vin)
	BEGIN
		SET @j = @j + 1
		IF @j = 9 and (@isOffRoad = 1 or @isVinExceptionCheckDigit = 1)  
			CONTINUE;
		SET @chr = SUBSTRING(@vin, @j, 1)
		IF 
			@j <> 9 AND @j < @startPos AND @chr NOT LIKE '[0-9ABCDEFGHJKLMNPRSTUVWXYZ*]' 
			OR 
			@j <> 9 AND @j >= @startPos AND @chr NOT LIKE '[0-9*]' 
			OR 
			@j = 9  AND @chr NOT LIKE '[0-9X*]' 
			
			
			OR 
			@j = 10 AND @chr NOT LIKE '[1-9ABCDEFGHJKLMNPRSTVWXY]' 
		BEGIN
			IF @chr = ' '
				SET @chr = '_'
			IF @CorrectedVIN = ''
				SET @CorrectedVIN = @vin
			SET @invalidChars = @invalidChars + ', ' + CAST(@j AS VARCHAR(2)) + ':' + @chr
			SET @CorrectedVIN = LEFT(@CorrectedVIN, @j-1) + '!' + SUBSTRING(@CorrectedVIN, @j+1, 100)
		END
    END
	IF @invalidChars <> ''
		set @ReturnCode = @ReturnCode + ' 400 ' 
	

	 
	if isnull(@Error12, 0) = 1
	begin
		
		
		
			select @ReturnCode = @ReturnCode + ' 12 ' 
	end
	

	
	INSERT INTO @DecodingItem ([DecodingId], [Source], [CreatedOn], [Priority], [PatternId], [Keys], [VinSchemaId], [WmiId], [ElementId], [AttributeId], [Value])
	SELECT 
		@pass, 
		'Default', 
		isnull(dv.UpdatedOn, dv.CreatedOn),
		10,		
		null,	
		null,	
		null,	
		null,	
		dv.ElementId, 
		dv.DefaultValue,
		case when e.datatype='lookup' and dv.DefaultValue = '0' then 'Not Applicable' else 
		'XXX' 
		end 
	FROM 
		DefaultValue dv with (nolock) 
		inner join element e with (nolock) on dv.ElementId = e.id
	where dv.VehicleTypeId = @vehicleType and dv.DefaultValue is not null and dv.elementid not in (select distinct elementid from @DecodingItem where DecodingId = @pass)
	

	
	if LEN(@vin) < 17 
		select @ReturnCode = @ReturnCode + ' 6 '
	else
	begin
		declare @CD char(1) = SUBSTRING(@vin, 9, 1)
		declare @calcCD char(1) = ''
		set @calcCD = dbo.[fVINCheckDigit2](@vin, @isCarmpvLT)
		IF (@cd <> @calcCD) and (@isVinExceptionCheckDigit = 0) 
			begin	
				set @ReturnCode = @ReturnCode + ' 1 ' 
			end
	END
	

	
	declare @errors varchar(100) = @ReturnCode
	set @errors = replace(@errors, ' 9 ', '')
	set @errors = replace(@errors, ' 10 ', '')
	set @errors = replace(@errors, ' 12 ', '')
	set @errors = ltrim(rtrim(@errors))

	if @errors = '' or @errors = '14'
		set @ReturnCode = ' 0 ' + @ReturnCode  
	

	
	select @cnt = count(*) from @DecodingItem where ElementId = 28
	if @ReturnCode like '% 0 %' and @cnt = 0
		select @ReturnCode = @ReturnCode + ' 14 '


	if @ReturnCode like '% 4 %'
		select @AdditionalDecodingInfo = isnull(additionalerrortext,'') from ErrorCode with (nolock) where id = 4
	if @ReturnCode like '% 5 %'
		select @AdditionalDecodingInfo = isnull(additionalerrortext,'') from ErrorCode with (nolock) where id = 5
	if @ReturnCode like '% 14 %'
		select @AdditionalDecodingInfo = rtrim(ltrim(isnull(@AdditionalDecodingInfo, '') + ' Unused position(s): ' + @UnUsedPositions + '; '))
	if @ReturnCode like '% 400 %'
		select @AdditionalDecodingInfo = rtrim(ltrim(isnull(@AdditionalDecodingInfo, '') + ' Invalid character(s): ' + SUBSTRING(@invalidChars, 3, LEN(@invalidChars)-2) + '; '))

	
	if @vehicleType = 10 or exists(select 1 from @DecodingItem where ElementId = 5 and AttributeId in (65, 107, 70, 74, 63, 72, 112, 62, 64, 76, 78, 71, 77, 67, 116, 75) and DecodingId = @pass)
		select @AdditionalDecodingInfo = rtrim(ltrim(isnull(@AdditionalDecodingInfo, '') + ' Incomplete Vehicle Warning - Please be advised that the vehicle may have been altered and may not be an accurate representation of the vehicle in its current condition. '))

	if @conclusive = 0 
		set @AdditionalDecodingInfo = rtrim(ltrim(isnull(@AdditionalDecodingInfo, '') + ' The Model Year decoded for this VIN may be incorrect. If you know the Model year, please enter it and decode again to get more accurate information. '))


	declare @offRoadNote varchar(100) = ' NOTE: Disregard if this is an off-road vehicle PIN, as check digit calculation may not be accurate.'
	declare @checkDigitExclusionNote varchar(150) = ' NOTE: Check Digit Exception - The check digit was given an exception based on data from the OEM indicating an error on production.'

	declare @errorMessages varchar(max) = null
	declare @errorCodes varchar(500) = null
	declare @oneError varchar(10) = ''
	
	select 
		@errorMessages = isnull(ltrim(rtrim(@errorMessages)) + '; ' + name, name), 
		@errorCodes = isnull(ltrim(rtrim(@errorCodes)) + ',' + cast(id as varchar), cast(id as varchar)),
		@oneError = Id 
	from 
		(
			select id, Name + case 
				when @isOffRoad = 1 and id = 1 then @offRoadNote 
				when @isVinExceptionCheckDigit = 1 and id = 0 then @checkDigitExclusionNote 
				else '' end as Name from ErrorCode with (nolock) 
		) as t 
	where @ReturnCode like '% ' + cast(id as varchar) + ' %' 
	order by id


	select @errorMessages = left(@errorMessages, 500)

	INSERT INTO @DecodingItem ([DecodingId], [Source], [Priority], [PatternId], [Keys], [VinSchemaId], [WmiId], [ElementId], [AttributeId], [Value])
	SELECT 
		@pass, 'Corrections', 999, 
		null, '', null, null, p.ElementId, 
		p.AttributeId, p.Value as Value
	FROM 
		(
			select 142 as ElementId, @CorrectedVIN as AttributeId, @CorrectedVIN as Value
			union 
			select 143, @errorCodes, @errorCodes 
			union 
			select 191, @errorMessages, @errorMessages 
			union 
			select 144, @ErrorBytes, @ErrorBytes
			union 
			select 156, @AdditionalDecodingInfo, @AdditionalDecodingInfo
			union 
			select 196, @descriptor, @descriptor 
		) p 
	
	select [DecodingId],[CreatedOn],[PatternId],[Keys],[VinSchemaId],[WmiId],[ElementId],[AttributeId],[Value],[Source],[Priority],[TobeQCed]
	from @DecodingItem
END
"""

## spVinDecode_ErrorCode
"""
USE [vPICList_Lite1]
GO
/****** Object:  StoredProcedure [dbo].[spVinDecode_ErrorCode]    Script Date: 9/24/2025 9:02:24 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

ALTER PROCEDURE [dbo].[spVinDecode_ErrorCode] 
	@vin varchar(50), 
	@modelYear int,
	@Decodingitem [tblDecodingItem] readonly,
	@ReturnCode varchar(100) OUTPUT,
	@CorrectedVIN varchar(17) OUTPUT, 
	@ErrorBytes varchar(500) OUTPUT,
	@UnUsedPositions varchar(500) OUTPUT
as
begin




	select @CorrectedVIN = '', @ErrorBytes = '', @ReturnCode = ''

	set @vin = LTRIM(RTRIM(@vin))
	
	declare @wmi varchar(6) = dbo.fVinWMI(@vin)
	declare @corrected varchar (17) = '', @possibilities varchar(50) = '', @replacements varchar(2000) = '', @x varchar(50)
	declare @i int = 3, @n int = 14, @c char(1), @cntTotal int, @cntMatch int, @r varchar(50), @cntErrors int = 0
	declare @lastErrorPos int = 0, @lastReplacements varchar(50) 

	if LEN(@wmi) < 3
	begin
		
		select @ReturnCode = @ReturnCode + ' 6 '
		return
	end

	declare @tmp [tblPosChar] 

	INSERT @tmp (p, c)
	select distinct position, [char] 
	from WMIYearValidChars with (nolock) 
	where wmi = @wmi and year = @modelYear 
		and @wmi not in (select distinct wmi from WMIYearValidChars_CacheExceptions)
	order by position, [char]

	if(@@ROWCOUNT = 0)
	begin
		INSERT @tmp (p, c)
		select distinct p , c from dbo.fExtractValidCharsPerWmiYear (@wmi, @modelYear) order by p, c
	end

	if LEN(@wmi) = 6
		set @n = 11

	while (@i < @n) and (@i < len(@vin))
	begin
		set @i = @i + 1
		set @c = SUBSTRING(@vin, @i, 1)

		if @i = 9 or @i = 10 
		begin
			set @r = @c
			
		end
		else
		begin
			select @cntTotal = COUNT(*) from @tmp where p = @i
			select @cntMatch = COUNT(*) from @tmp where p = @i and c = @c
			
			if @cntTotal > 0
			begin
				
				if @cntMatch > 0
				begin
					
					set @r = @c
				end
				else
				begin 
					
					set @r = '!'
					set @x = ''
					select @x = @x + c from @tmp where p=@i order by c
					set @replacements = @replacements + '(' + CAST(@i as varchar) + ':' + @x +')'
					set @cntErrors = @cntErrors + 1
					set @lastErrorPos = @i
					set @lastReplacements = @x
				end
			end
			else
			begin
				
					set @r = @c 
				
				
			end 
		end
		set @corrected = @corrected + @r
	end

	if len(@wmi) = 3
		set @corrected = @wmi + @corrected
	else
		set @corrected = left(@wmi, 3) + @corrected + RIGHT(@wmi, 3)

	if LEN(@vin) > LEN(@corrected)
		set @corrected = @corrected + SUBSTRING(@vin, LEN(@corrected)+1, 3)

	IF @cntErrors = 1 
	begin
		

		if len(@lastReplacements) = 1
		begin
			
			set @corrected = substring(@vin, 1, @lastErrorPos-1) + @lastReplacements + substring(@vin, @lastErrorPos+1, 17-@lastErrorPos) 
			select @ReturnCode = @ReturnCode + ' 2 ', @CorrectedVin = @Corrected, @ErrorBytes = @replacements
		end
		else
		begin
			declare @tmpVin varchar(17), @goodReplacements int = 0, @NewReplacements varchar(50) = '', @Corrected1 varchar(17)
			
			set @i = 0
			while @i<len(@lastReplacements)
			begin
				set @i = @i + 1
				
				set @c = SUBSTRING(@lastReplacements, @i, 1) 
				set @tmpVin = substring(@vin, 1, @lastErrorPos-1) + @c + substring(@vin, @lastErrorPos+1, 17-@lastErrorPos) 
				if SUBSTRING(@tmpVin, 9, 1) = dbo.[fVINCheckDigit](@tmpVin) 
				begin
					set @goodReplacements = @goodReplacements + 1
					set @NewReplacements = @NewReplacements + @c
					set @Corrected1 = @tmpVin
				end
				
			end

			if @goodReplacements = 1
			begin
				
				select @ReturnCode = @ReturnCode + ' 3 ', @CorrectedVin = @Corrected1, @ErrorBytes = '(' + CAST(@lastErrorPos as varchar) + ':' + @NewReplacements +')'
			end 
			else
			begin
				
				select @ReturnCode = @ReturnCode + ' 4 ', @CorrectedVin = @Corrected, @ErrorBytes = '(' + CAST(@lastErrorPos as varchar) + ':' + @lastReplacements +')'
			end
		end
	end

	IF @cntErrors > 1 
	begin
		
		select @ReturnCode = @ReturnCode + ' 5 ' , @CorrectedVin = @Corrected, @ErrorBytes = @replacements
	end
	
	

	declare @tmp1 [tblPosChar] 

	declare @Y tblPosChar 

	declare @chr char(1), @key varchar(100), @b bit = 0, @unUsedPos varchar(100) = ''
	
	set @i = (select min (id) from @decodingitem)
	while @i <= (select max (id) from @decodingitem)
	begin
		select @key = null
		select @key = keys from @decodingitem where id = @i and source like '%pattern%'
		if isnull(@key, '') <> ''
		begin
			insert into @tmp1 select * from dbo.fValidCharsInKey (@key) where chr <> '|'
		end
		set @i = @i + 1
	end
	
	insert into @y select distinct * from @tmp1 
	
	set @i = 3
	declare @ubound int = 11 
	if len (@vin) < @ubound
		set @ubound = len (@vin)

	while @i < @ubound
	begin
		set @i = @i + 1
		
		if not @i in (4, 5, 6, 7, 8, 11) 
			continue

		set @chr = SUBSTRING(@vin, @i, 1)
		set @b = 0
		if exists(select c from @y where p +3 = @i and c = @chr)
			set @b = 1
		if @b = 0
			set @unUsedPos = @unUsedPos + ' ' + cast(@i as varchar) 
		
	end
	

	set @unUsedPos = replace(ltrim(rtrim(@unUsedPos)), ' ', ',')
	
	IF @unUsedPos <> '' 
	begin
		
		select @ReturnCode = @ReturnCode + ' 14 ' , @UnUsedPositions = @unUsedPos 
	end
END
"""


# Table-Valued Functions (db --> programmability --> functions)
## fExtractVlidCharsPerWmiYear
"""
USE [vPICList_Lite1]
GO
/****** Object:  UserDefinedFunction [dbo].[fExtractValidCharsPerWmiYear]    Script Date: 9/24/2025 8:16:03 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER function [dbo].[fExtractValidCharsPerWmiYear]
(	@wmi varchar(10),
	@year smallint
)
returns @tbl table
(	
	p smallint, 
	c char(1)
)
AS
BEGIN

	declare @keys varchar(50)
	
	DECLARE cursor_wmiy CURSOR FOR 
		SELECT distinct p.Keys
		FROM 
			dbo.Wmi AS w 
			INNER JOIN dbo.Wmi_VinSchema AS wvs ON w.Id = wvs.WmiId 
			INNER JOIN dbo.VinSchema AS vs ON wvs.VinSchemaId = vs.Id 
			INNER JOIN dbo.Pattern AS p ON vs.Id = p.VinSchemaId
		WHERE     
			(w.Wmi = @wmi)
			and @year between wvs.YearFrom and ISNULL(wvs.YearTo, 2999)
	OPEN cursor_wmiy
	
	WHILE 1 = 1
	BEGIN
		FETCH NEXT FROM cursor_wmiy INTO @keys
		if @@FETCH_STATUS <> 0
			break
		
		insert into @tbl (p, c)
		select pos + 3, chr  
		from dbo.fValidCharsInKey(@keys) 
		
	END

	CLOSE cursor_wmiy
	DEALLOCATE cursor_wmiy
	
	return
END
"""

## fValidCharsInKey
"""
USE [vPICList_Lite1]
GO
/****** Object:  UserDefinedFunction [dbo].[fValidCharsInKey]    Script Date: 9/24/2025 8:16:36 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

ALTER function [dbo].[fValidCharsInKey] (
	@str varchar(50)
)
returns @tbl table(
	pos smallint,
	chr char(1)
)
as
Begin		
	declare @validchars as varchar(50) =  'ABCDEFGHJKLMNPRSTUVWXYZ0123456789'
	declare @strict bit = 1 

	declare 
		@n int = len(@str),
		@s char(1),
		@inside bit = 0, 
		@ind int = 0,
		@i int = 0, 
		@start int = 0,
		@j smallint = 0,
		@chars varchar(50)

	WHILE @i < @n
	BEGIN
		set @i = @i + 1
		set @s = SUBSTRING (@str, @i, 1)
		
		if @s = '[' and @inside = 0
		begin
			
			set @inside = 1
			set @start = @i
			continue
		end

		if @inside = 0
		begin
			
			set @ind = @ind + 1
			
			
			
			
			if @s = '#'
			begin
				
				insert into @tbl values (@ind, '0')
				insert into @tbl values (@ind, '1')
				insert into @tbl values (@ind, '2')
				insert into @tbl values (@ind, '3')
				insert into @tbl values (@ind, '4')
				insert into @tbl values (@ind, '5')
				insert into @tbl values (@ind, '6')
				insert into @tbl values (@ind, '7')
				insert into @tbl values (@ind, '8')
				insert into @tbl values (@ind, '9')
				continue
			end

			
			if @s = '*' 
			begin
				if @strict = 0
				begin
					set @chars = @validchars
					set @j = 0
					WHILE @j < LEN (@chars)
					BEGIN
						set @j = @j + 1
						set @s = SUBSTRING (@chars, @j, 1)
						insert into @tbl values (@ind, @s)
					END
				end
				continue
			end
			
			
			insert into @tbl values (@ind, @s)
			continue
		end
		

		if @s = ']' and @inside = 1
		begin
			
			set @ind = @ind + 1
			declare @pattern varchar(50) = substring(@str, @start, @i - @start + 1)
			
			
			set @chars = dbo.fValidCharsInRegEx (@pattern)
			set @j = 0
			WHILE @j < LEN (@chars)
			BEGIN
				set @j = @j + 1
				set @s = SUBSTRING (@chars, @j, 1)
				if @s <> '*' and @s <> '|'
					insert into @tbl values (@ind, @s)
			END
			
			set @inside = 0
			set @start = 0
			continue
		end

	END

	return 
END	

"""


# Scalar-Valued Functions (db --> programmability --> functions)
## fElementAttributeValue
"""
USE [vPICList_Lite1]
GO
/****** Object:  UserDefinedFunction [dbo].[fElementAttributeValue]    Script Date: 9/24/2025 8:13:42 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
 
ALTER FUNCTION [dbo].[fElementAttributeValue] ( @ElementId int, @AttributeId varchar(500)) RETURNS varchar(2000) AS 
 BEGIN 
 DECLARE @v varchar(2000) = @AttributeId 
 	 if @ElementId = 2 begin select @v = [Name] from [BatteryType] where Id = @AttributeId ; return @v end
 if @ElementId = 3 begin select @v = [Name] from [BedType] where Id = @AttributeId ; return @v end
 if @ElementId = 4 begin select @v = [Name] from [BodyCab] where Id = @AttributeId ; return @v end
 if @ElementId = 5 begin select @v = [Name] from [BodyStyle] where Id = @AttributeId ; return @v end
 if @ElementId = 10 begin select @v = [Name] from [DestinationMarket] where Id = @AttributeId ; return @v end
 if @ElementId = 15 begin select @v = [Name] from [DriveType] where Id = @AttributeId ; return @v end
 if @ElementId = 23 begin select @v = [Name] from [EntertainmentSystem] where Id = @AttributeId ; return @v end
 if @ElementId = 24 begin select @v = [Name] from [FuelType] where Id = @AttributeId ; return @v end
 if @ElementId = 25 begin select @v = [Name] from [GrossVehicleWeightRating] where Id = @AttributeId ; return @v end
 if @ElementId = 26 begin select @v = [Name] from [Make] where Id = @AttributeId ; return @v end
 if @ElementId = 27 begin select @v = [Name] from [Manufacturer] where Id = @AttributeId ; return @v end
 if @ElementId = 28 begin select @v = [Name] from [Model] where Id = @AttributeId ; return @v end
 if @ElementId = 36 begin select @v = [Name] from [Steering] where Id = @AttributeId ; return @v end
 if @ElementId = 37 begin select @v = [Name] from [Transmission] where Id = @AttributeId ; return @v end
 if @ElementId = 39 begin select @v = [Name] from [VehicleType] where Id = @AttributeId ; return @v end
 if @ElementId = 42 begin select @v = [Name] from [BrakeSystem] where Id = @AttributeId ; return @v end
 if @ElementId = 55 begin select @v = [Name] from [AirBagLocations] where Id = @AttributeId ; return @v end
 if @ElementId = 56 begin select @v = [Name] from [AirBagLocations] where Id = @AttributeId ; return @v end
 if @ElementId = 60 begin select @v = [Name] from [WheelBaseType] where Id = @AttributeId ; return @v end
 if @ElementId = 62 begin select @v = [Name] from [ValvetrainDesign] where Id = @AttributeId ; return @v end
 if @ElementId = 64 begin select @v = [Name] from [EngineConfiguration] where Id = @AttributeId ; return @v end
 if @ElementId = 65 begin select @v = [Name] from [AirBagLocFront] where Id = @AttributeId ; return @v end
 if @ElementId = 66 begin select @v = [Name] from [FuelType] where Id = @AttributeId ; return @v end
 if @ElementId = 67 begin select @v = [Name] from [FuelDeliveryType] where Id = @AttributeId ; return @v end
 if @ElementId = 69 begin select @v = [Name] from [AirBagLocKnee] where Id = @AttributeId ; return @v end
 if @ElementId = 72 begin select @v = [Name] from [EVDriveUnit] where Id = @AttributeId ; return @v end
 if @ElementId = 75 begin select @v = [Name] from [Country] where Id = @AttributeId ; return @v end
 if @ElementId = 78 begin select @v = [Name] from [Pretensioner] where Id = @AttributeId ; return @v end
 if @ElementId = 79 begin select @v = [Name] from [SeatBeltsAll] where Id = @AttributeId ; return @v end
 if @ElementId = 81 begin select @v = [Name] from [AdaptiveCruiseControl] where Id = @AttributeId ; return @v end
 if @ElementId = 86 begin select @v = [Name] from [ABS] where Id = @AttributeId ; return @v end
 if @ElementId = 87 begin select @v = [Name] from [AutoBrake] where Id = @AttributeId ; return @v end
 if @ElementId = 88 begin select @v = [Name] from [BlindSpotMonitoring] where Id = @AttributeId ; return @v end
 if @ElementId = 96 begin select @v = [Name] from [vNCSABodyType] where Id = @AttributeId ; return @v end
 if @ElementId = 97 begin select @v = [Name] from [vNCSAMake] where Id = @AttributeId ; return @v end
 if @ElementId = 98 begin select @v = [Name] from [vNCSAModel] where Id = @AttributeId ; return @v end
 if @ElementId = 99 begin select @v = [Name] from [ECS] where Id = @AttributeId ; return @v end
 if @ElementId = 100 begin select @v = [Name] from [TractionControl] where Id = @AttributeId ; return @v end
 if @ElementId = 101 begin select @v = [Name] from [ForwardCollisionWarning] where Id = @AttributeId ; return @v end
 if @ElementId = 102 begin select @v = [Name] from [LaneDepartureWarning] where Id = @AttributeId ; return @v end
 if @ElementId = 103 begin select @v = [Name] from [LaneKeepSystem] where Id = @AttributeId ; return @v end
 if @ElementId = 104 begin select @v = [Name] from [RearVisibilityCamera] where Id = @AttributeId ; return @v end
 if @ElementId = 105 begin select @v = [Name] from [ParkAssist] where Id = @AttributeId ; return @v end
 if @ElementId = 107 begin select @v = [Name] from [AirBagLocations] where Id = @AttributeId ; return @v end
 if @ElementId = 116 begin select @v = [Name] from [TrailerType] where Id = @AttributeId ; return @v end
 if @ElementId = 117 begin select @v = [Name] from [TrailerBodyType] where Id = @AttributeId ; return @v end
 if @ElementId = 122 begin select @v = [Name] from [CoolingType] where Id = @AttributeId ; return @v end
 if @ElementId = 126 begin select @v = [Name] from [ElectrificationLevel] where Id = @AttributeId ; return @v end
 if @ElementId = 127 begin select @v = [Name] from [ChargerLevel] where Id = @AttributeId ; return @v end
 if @ElementId = 135 begin select @v = [Name] from [Turbo] where Id = @AttributeId ; return @v end
 if @ElementId = 143 begin select @v = [Name] from [ErrorCode] where Id = @AttributeId ; return @v end
 if @ElementId = 145 begin select @v = [Name] from [AxleConfiguration] where Id = @AttributeId ; return @v end
 if @ElementId = 148 begin select @v = [Name] from [BusFloorConfigType] where Id = @AttributeId ; return @v end
 if @ElementId = 149 begin select @v = [Name] from [BusType] where Id = @AttributeId ; return @v end
 if @ElementId = 151 begin select @v = [Name] from [CustomMotorcycleType] where Id = @AttributeId ; return @v end
 if @ElementId = 152 begin select @v = [Name] from [MotorcycleSuspensionType] where Id = @AttributeId ; return @v end
 if @ElementId = 153 begin select @v = [Name] from [MotorcycleChassisType] where Id = @AttributeId ; return @v end
 if @ElementId = 168 begin select @v = [Name] from [TPMS] where Id = @AttributeId ; return @v end
 if @ElementId = 170 begin select @v = [Name] from [DynamicBrakeSupport] where Id = @AttributeId ; return @v end
 if @ElementId = 171 begin select @v = [Name] from [PedestrianAutomaticEmergencyBraking] where Id = @AttributeId ; return @v end
 if @ElementId = 172 begin select @v = [Name] from [AutoReverseSystem] where Id = @AttributeId ; return @v end
 if @ElementId = 173 begin select @v = [Name] from [AutomaticPedestrainAlertingSound] where Id = @AttributeId ; return @v end
 if @ElementId = 174 begin select @v = [Name] from [CAN_AACN] where Id = @AttributeId ; return @v end
 if @ElementId = 175 begin select @v = [Name] from [EDR] where Id = @AttributeId ; return @v end
 if @ElementId = 176 begin select @v = [Name] from [KeylessIgnition] where Id = @AttributeId ; return @v end
 if @ElementId = 177 begin select @v = [Name] from [DaytimeRunningLight] where Id = @AttributeId ; return @v end
 if @ElementId = 178 begin select @v = [Name] from [LowerBeamHeadlampLightSource] where Id = @AttributeId ; return @v end
 if @ElementId = 179 begin select @v = [Name] from [SemiautomaticHeadlampBeamSwitching] where Id = @AttributeId ; return @v end
 if @ElementId = 180 begin select @v = [Name] from [AdaptiveDrivingBeam] where Id = @AttributeId ; return @v end
 if @ElementId = 183 begin select @v = [Name] from [RearCrossTrafficAlert] where Id = @AttributeId ; return @v end
 if @ElementId = 184 begin select @v = [Name] from [GrossVehicleWeightRating] where Id = @AttributeId ; return @v end
 if @ElementId = 185 begin select @v = [Name] from [GrossVehicleWeightRating] where Id = @AttributeId ; return @v end
 if @ElementId = 190 begin select @v = [Name] from [GrossVehicleWeightRating] where Id = @AttributeId ; return @v end
 if @ElementId = 192 begin select @v = [Name] from [RearAutomaticEmergencyBraking] where Id = @AttributeId ; return @v end
 if @ElementId = 193 begin select @v = [Name] from [BlindSpotIntervention] where Id = @AttributeId ; return @v end
 if @ElementId = 194 begin select @v = [Name] from [LaneCenteringAssistance] where Id = @AttributeId ; return @v end
 if @ElementId = 195 begin select @v = [Name] from [NonLandUse] where Id = @AttributeId ; return @v end
 if @ElementId = 200 begin select @v = [Name] from [FuelTankType] where Id = @AttributeId ; return @v end
 if @ElementId = 201 begin select @v = [Name] from [FuelTankMaterial] where Id = @AttributeId ; return @v end
 if @ElementId = 202 begin select @v = [Name] from [CombinedBrakingSystem] where Id = @AttributeId ; return @v end
 if @ElementId = 203 begin select @v = [Name] from [WheelieMitigation] where Id = @AttributeId ; return @v end
 
 	RETURN @v 
 END
"""

## fErrorValue
"""
USE [vPICList_Lite1]
GO
/****** Object:  UserDefinedFunction [dbo].[fErrorValue]    Script Date: 9/24/2025 8:13:57 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER function [dbo].[fErrorValue] (
	@str varchar(100)
)
returns int
as
Begin		

	declare @w int = 0
	select @w = @w + weight	from ErrorCode where ','+@str+',' like '%,' + cast(id as varchar) + ',%'
	return @w
end
"""

## fValidCharsInRegEx:
"""
USE [vPICList_Lite1]
GO
/****** Object:  UserDefinedFunction [dbo].[fValidCharsInRegEx]    Script Date: 9/24/2025 8:14:13 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

ALTER function [dbo].[fValidCharsInRegEx] (
	@str varchar(50)
)
returns varchar(50)
as
Begin		
	set @str = UPPER(@str)

	
	if CHARINDEX ('-', @str) = 0 and CHARINDEX ('^', @str) = 0
		return replace(replace(@str, ']', ''), '[', '')
	
	declare @validchars as varchar(50) =  'ABCDEFGHJKLMNPRSTUVWXYZ0123456789'
	declare @result varchar(50) = ''
	DECLARE @i int = 0, @n int = len(@validchars), @s char(1)
	
	while @i < @n
	begin
		set @i = @i + 1
		set @s = SUBSTRING (@validchars, @i, 1)
		
		if @s like @str
			set @result = @result + @s
	end
	
	return @result

END
"""
## fVINCheckDigit:
"""
USE [vPICList_Lite1]
GO
/****** Object:  UserDefinedFunction [dbo].[fVINCheckDigit]    Script Date: 9/24/2025 8:14:35 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

ALTER function [dbo].[fVINCheckDigit] ( @strVIN AS VARCHAR(17) )
RETURNS VARCHAR (4)
AS
BEGIN
    DECLARE 
        @TempString AS VARCHAR(4) = '',
		@sVINChar AS VARCHAR(1) = '',
		@patternDefault AS VARCHAR(50)		= '[a-h,j-n,p,r-z,0-9]',  
		@patternMY AS VARCHAR(50)			= '[a-h,j-n,p,r-t,v-y,1-9]',  
		@patternNumbersOnly AS VARCHAR(50)	= '[0-9]',  
		@pattern AS VARCHAR(50)

    DECLARE 
		@temp REAL,
        @TempDigit AS REAL = 0,
        @CalcDigit AS REAL = 0
    DECLARE 
		@CalcTemp AS INT = 0,
		@i AS INT 
	DECLARE @valid bit
   
    SET @i = 1
    IF LEN(@strVIN) = 17
        BEGIN
            SET @CalcDigit = 0
            WHILE @i <= LEN(@strVIN)
                BEGIN
                    SET @sVINChar = SUBSTRING(@strVIN, @i, 1)
					
					set @pattern = case 
						when @i = 10 then @patternMY
						when @i in (13, 14) and SUBSTRING(@strVIN, 3, 1) = '9' then @patternDefault
						when @i in (13, 14) and SUBSTRING(@strVIN, 3, 1) <> '9' then @patternNumbersOnly
						when @i >= 15 then @patternNumbersOnly
						else @patternDefault
						end
					
					if not @sVINChar like @pattern 
						return '?'  
	
                    SET @CalcTemp = CASE @sVINChar
                                      WHEN '0' THEN 0
									  WHEN '1' THEN 1
                                      WHEN '2' THEN 2
                                      WHEN '3' THEN 3
                                      WHEN '4' THEN 4
                                      WHEN '5' THEN 5
                                      WHEN '6' THEN 6
                                      WHEN '7' THEN 7
                                      WHEN '8' THEN 8
                                      WHEN '9' THEN 9
                                      WHEN 'A' THEN 1
                                      WHEN 'B' THEN 2
                                      WHEN 'C' THEN 3
                                      WHEN 'D' THEN 4
                                      WHEN 'E' THEN 5
                                      WHEN 'F' THEN 6
                                      WHEN 'G' THEN 7
                                      WHEN 'H' THEN 8
                                      WHEN 'J' THEN 1
                                      WHEN 'K' THEN 2
                                      WHEN 'L' THEN 3
                                      WHEN 'M' THEN 4
                                      WHEN 'N' THEN 5
                                      WHEN 'P' THEN 7
                                      WHEN 'R' THEN 9
                                      WHEN 'S' THEN 2
                                      WHEN 'T' THEN 3
                                      WHEN 'U' THEN 4
                                      WHEN 'V' THEN 5
                                      WHEN 'W' THEN 6
                                      WHEN 'X' THEN 7
                                      WHEN 'Y' THEN 8
                                      WHEN 'Z' THEN 9
                                      ELSE -1
                                    END


                    SET @CalcDigit = @CalcDigit
                        + CASE @i
                            WHEN 1 THEN ( @CalcTemp * 8 )
                            WHEN 2 THEN ( @CalcTemp * 7 )
                            WHEN 3 THEN ( @CalcTemp * 6 )
                            WHEN 4 THEN ( @CalcTemp * 5 )
                     WHEN 5 THEN ( @CalcTemp * 4 )
                            WHEN 6 THEN ( @CalcTemp * 3 )
                            WHEN 7 THEN ( @CalcTemp * 2 )
                            WHEN 8 THEN ( @CalcTemp * 10 )
                            WHEN 9 THEN 0
                            WHEN 10 THEN ( @CalcTemp * 9 )
                            WHEN 11 THEN ( @CalcTemp * 8 )
                            WHEN 12 THEN ( @CalcTemp * 7 )
                            WHEN 13 THEN ( @CalcTemp * 6 )
                            WHEN 14 THEN ( @CalcTemp * 5 )
                            WHEN 15 THEN ( @CalcTemp * 4 )
                            WHEN 16 THEN ( @CalcTemp * 3 )
                            WHEN 17 THEN ( @CalcTemp * 2 )
                          END
                    SET @i = @i + 1
                END
            SET @temp = @CalcDigit / 11
            SET @TempDigit = ROUND(( @temp - CAST(@temp AS INT) ) * 11, 2, 0);
            SET @TempString = CAST(@TempDigit AS VARCHAR(10))
            SET @TempString = CASE LEN(LTRIM(RTRIM(@TempString)))
                                WHEN 1 THEN ' ' + @TempString
                                ELSE @TempString
                              END
            IF @TempString = '10'
                SET @TempString = 'X' 
            ELSE
                SET @TempString = SUBSTRING(@TempString, 2, 1)

        END
    RETURN(@TempString)
END

"""

## fVINCheckDigit2
"""
USE [vPICList_Lite1]
GO
/****** Object:  UserDefinedFunction [dbo].[fVINCheckDigit2]    Script Date: 9/24/2025 8:14:53 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

ALTER function [dbo].[fVINCheckDigit2] ( 
	@strVIN AS VARCHAR(17) , 
	@isCarmpvLT bit

)
RETURNS VARCHAR (4)
AS
BEGIN
    DECLARE 
        @TempString AS VARCHAR(4) = '',
		@sVINChar AS VARCHAR(1) = '',
		@patternDefault AS VARCHAR(50)		= '[a-h,j-n,p,r-z,0-9]',  
		@patternMY AS VARCHAR(50)			= '[a-h,j-n,p,r-t,v-y,1-9]',  
		@patternNumbersOnly AS VARCHAR(50)	= '[0-9]',  
		@pattern AS VARCHAR(50)

    DECLARE 
		@temp REAL,
        @TempDigit AS REAL = 0,
        @CalcDigit AS REAL = 0
    DECLARE 
		@CalcTemp AS INT = 0,
		@i AS INT 
	DECLARE @valid bit
   
    SET @i = 1
    IF LEN(@strVIN) = 17
        BEGIN
            SET @CalcDigit = 0
            WHILE @i <= LEN(@strVIN)
                BEGIN
                    SET @sVINChar = SUBSTRING(@strVIN, @i, 1)
					
					set @pattern = case 
						when @i = 10 then @patternMY
						
						when @i = 13 and SUBSTRING(@strVIN, 3, 1) <> '9' and @isCarmpvLT = 1 then @patternNumbersOnly
						when @i = 14 and SUBSTRING(@strVIN, 3, 1) <> '9' then @patternNumbersOnly
						when @i >= 15 then @patternNumbersOnly
						else @patternDefault
						end
					
					if not @sVINChar like @pattern 
						return '?'  
	
                    SET @CalcTemp = CASE @sVINChar
                                      WHEN '0' THEN 0
									  WHEN '1' THEN 1
                                      WHEN '2' THEN 2
                                      WHEN '3' THEN 3
                                      WHEN '4' THEN 4
                                      WHEN '5' THEN 5
                                      WHEN '6' THEN 6
                                      WHEN '7' THEN 7
                                      WHEN '8' THEN 8
                                      WHEN '9' THEN 9
                                      WHEN 'A' THEN 1
                                      WHEN 'B' THEN 2
                                      WHEN 'C' THEN 3
                                      WHEN 'D' THEN 4
                                      WHEN 'E' THEN 5
                                      WHEN 'F' THEN 6
                                      WHEN 'G' THEN 7
                                      WHEN 'H' THEN 8
                                      WHEN 'J' THEN 1
                                      WHEN 'K' THEN 2
                                      WHEN 'L' THEN 3
                                      WHEN 'M' THEN 4
                                      WHEN 'N' THEN 5
                                      WHEN 'P' THEN 7
                                      WHEN 'R' THEN 9
                                      WHEN 'S' THEN 2
                                      WHEN 'T' THEN 3
                                      WHEN 'U' THEN 4
                                      WHEN 'V' THEN 5
                                      WHEN 'W' THEN 6
                                      WHEN 'X' THEN 7
                                      WHEN 'Y' THEN 8
                                      WHEN 'Z' THEN 9
                                      ELSE -1
                                    END


                    SET @CalcDigit = @CalcDigit
                        + CASE @i
                            WHEN 1 THEN ( @CalcTemp * 8 )
                            WHEN 2 THEN ( @CalcTemp * 7 )
                            WHEN 3 THEN ( @CalcTemp * 6 )
                            WHEN 4 THEN ( @CalcTemp * 5 )
                            WHEN 5 THEN ( @CalcTemp * 4 )
                            WHEN 6 THEN ( @CalcTemp * 3 )
                            WHEN 7 THEN ( @CalcTemp * 2 )
                            WHEN 8 THEN ( @CalcTemp * 10 )
                            WHEN 9 THEN 0
                            WHEN 10 THEN ( @CalcTemp * 9 )
                            WHEN 11 THEN ( @CalcTemp * 8 )
                            WHEN 12 THEN ( @CalcTemp * 7 )
                            WHEN 13 THEN ( @CalcTemp * 6 )
                            WHEN 14 THEN ( @CalcTemp * 5 )
                            WHEN 15 THEN ( @CalcTemp * 4 )
                            WHEN 16 THEN ( @CalcTemp * 3 )
                            WHEN 17 THEN ( @CalcTemp * 2 )
                          END
                    SET @i = @i + 1
                END
            SET @temp = @CalcDigit / 11
            SET @TempDigit = ROUND(( @temp - CAST(@temp AS INT) ) * 11, 2, 0);
            SET @TempString = CAST(@TempDigit AS VARCHAR(10))
            SET @TempString = CASE LEN(LTRIM(RTRIM(@TempString)))
                                WHEN 1 THEN ' ' + @TempString
                                ELSE @TempString
                              END
            IF @TempString = '10'
                SET @TempString = 'X' 
            ELSE
                SET @TempString = SUBSTRING(@TempString, 2, 1)

        END
    RETURN(@TempString)
END
"""


## fVinDescriptor
"""
USE [vPICList_Lite1]
GO
/****** Object:  UserDefinedFunction [dbo].[fVinDescriptor]    Script Date: 9/24/2025 8:11:46 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER function [dbo].[fVinDescriptor]
(
	@vin varchar(17)
)
RETURNS varchar(17)
AS
BEGIN
	DECLARE @vehicleDescriptor varchar(17)              
	set @vin = left(ltrim(rtrim(@VIN)) + '*****************', 17) /* pads the right side with asterisks if the VIN is less than 17 characters */
	set @vin = STUFF(@vin, 9, 1, '*') /* replaces the 9th character with an asterisk */

	set @vehicleDescriptor = left(@vin, 11) /* sets the vin to exclude the vehicle serial number */
	if SUBSTRING(@VIN, 3, 1) = '9' /* if the 3rd character is '9' from the original vin (aka a special vehicle type), the first 3 characters of the serial numbers are kept, meaning. */
		set @vehicleDescriptor = left(@vin, 14)

	return upper(@vehicleDescriptor)
END
"""

## fvvinModelYear2
"""
USE [vPICList_Lite1]
GO
/****** Object:  UserDefinedFunction [dbo].[fVinModelYear2]    Script Date: 9/24/2025 8:15:16 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER function [dbo].[fVinModelYear2] (
	@vin varchar(50)
)
returns int
as
Begin		

	declare @pos10 char(10), @modelYear int = null
	declare @conclusive bit = 0 

	set @vin = upper(@vin)
	if LEN(@vin) >= 10
	begin

		select @pos10 = substring(@vin, 10, 1)

		if @pos10 like '[A-H]'
			set @modelYear = 2010 + ascii(@pos10) - ASCII('A')
		if @pos10 like '[J-N]'
			set @modelYear = 2010 + ascii(@pos10) - ASCII('A') -1
		if @pos10 = 'P'
			set @modelYear = 2023
		if @pos10 like '[R-T]'
			set @modelYear = 2010 + ascii(@pos10) - ASCII('A') -3
		if @pos10 like '[V-Y]'
			set @modelYear = 2010 + ascii(@pos10) - ASCII('A') -4
		if @pos10 like '[1-9]'
			set @modelYear = 2031 + ascii(@pos10) - ASCII('1')

		if not (@modelYear is null) /* if the model year was successfully determined */
		begin

			declare @wmi varchar(6) = null, @vehicleTypeId int = null, @truckTypeId int = null
			set @wmi = dbo.fVinWMI(@vin)
			if not (@wmi is null)
			begin
				select @vehicleTypeId = vehicleTypeId, @truckTypeId = truckTypeId from wmi where wmi = @wmi

				declare @carLT int = 0 
				if @vehicleTypeId in (2, 7) or (@vehicleTypeId = 3 and @truckTypeId = 1) /* if the vehicle type id is 2 or 7 (Passenger Car, Multipurpose Passenger Vehicle (MPV)), or if it's 3 (Truck) and the truck type id is 1 (light truck) */
					set @carLT = 1 

				IF (@carLT = 1) and (substring(@vin, 7, 1) like '[0-9]') /* if carLT = 1 and the 7th character is a number, then the model year would be in the previous cycle */
				begin
					set @modelYear = @modelYear - 30
					set @conclusive = 1
				end
				IF (@carLT = 1) and (substring(@vin, 7, 1) like '[A-Z]') /* if carLT = 1 and the 7th character is a letter, then the model year would be in the current cycle */
				begin
					set @conclusive = 1
				end
			end

			if @modelYear > datepart(year, dateadd(year, 2, getdate())) /* if the model year is greater than 2 years from now */
			begin
				set @modelYear = @modelYear - 30
				set @conclusive = 1
			end

		end

	end

	if @conclusive <> 1
		set @modelYear = - @modelYear

	return @modelYear

end
"""

## fVinWMI
"""
USE [vPICList_Lite1]
GO
/****** Object:  UserDefinedFunction [dbo].[fVinWMI]    Script Date: 9/24/2025 8:15:35 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

ALTER function [dbo].[fVinWMI] (
	@vin varchar(50)
)
returns varchar(6)
as
Begin
	declare @wmi varchar(6)

	if LEN(@vin) > 3
		set @wmi = LEFT(@vin, 3)
	else
		set @wmi = @vin

	if SUBSTRING(@wmi, 3,1) = '9' and LEN(@vin) >= 14
		set @wmi = @wmi + substring(@vin, 12, 3)

	return @wmi
END
"""




# Tables:
"""

================================================================================
Table: [dbo].[ABS]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[ABS]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[AdaptiveCruiseControl]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[AdaptiveCruiseControl]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[AdaptiveDrivingBeam]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[AdaptiveDrivingBeam]:
Id | Name
---------
1 | Standard
2 | Not Available
3 | Optional

================================================================================
Table: [dbo].[AirBagLocations]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[AirBagLocations]:
Id | Name
---------
5 | 1st and 2nd and 3rd Rows
4 | 1st and 2nd Rows
3 | 1st Row (Driver and Passenger)
6 | All Rows
1 | Driver Seat Only
2 | Passenger Seat Only

================================================================================
Table: [dbo].[AirBagLocFront]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[AirBagLocFront]:
Id | Name
---------
3 | 1st Row (Driver and Passenger)
1 | Driver Seat Only

================================================================================
Table: [dbo].[AirBagLocKnee]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[AirBagLocKnee]:
Id | Name
---------
3 | 1st Row (Driver and Passenger)
1 | Driver Seat Only
2 | Passenger Seat Only

================================================================================
Table: [dbo].[AutoBrake]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[AutoBrake]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[AutomaticPedestrainAlertingSound]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[AutomaticPedestrainAlertingSound]:
Id | Name
---------
1 | Standard
2 | Not Available
3 | Optional

================================================================================
Table: [dbo].[AutoReverseSystem]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[AutoReverseSystem]:
Id | Name
---------
1 | Standard
2 | Not Available
3 | Optional

================================================================================
Table: [dbo].[AxleConfiguration]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[AxleConfiguration]:
Id | Name
---------
4 | Independent Axle
1 | SBA - Set-Back Axle
2 | SFA - Set-Forward Axle
5 | Single
3 | Tandem

================================================================================
Table: [dbo].[BatteryType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[BatteryType]:
Id | Name
---------
4 | Cobalt Dioxide/Cobalt
8 | Iron Phosphate/FePo
1 | Lead Acid/Lead
3 | Lithium-Ion/Li-Ion
7 | Manganese Oxide Spinel/MnO
2 | Nickel-Metal-Hydride/NiMH
6 | Nickle-Cobalt-Aluminum/NCA
5 | Nickle-Cobalt-Manganese/NCM
9 | Silicon

================================================================================
Table: [dbo].[BedType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[BedType]:
Id | Name
---------
3 | Extended
1 | Long
2 | Short
4 | Standard

================================================================================
Table: [dbo].[BlindSpotIntervention]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[BlindSpotIntervention]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[BlindSpotMonitoring]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[BlindSpotMonitoring]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[BodyCab]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[BodyCab]:
Id | Name
---------
4 | Crew/Super Crew/Crew Max
2 | Extra/Super/Quad/Double/King/Extended
12 | MDHD: Cab Beside Engine
8 | MDHD: CAE (Cab Above Engine)
7 | MDHD: CBE (Cab Behind Engine)
6 | MDHD: COE (Cab Over Engine)
5 | MDHD: Conventional
9 | MDHD: LCF (Low Cab Forward)
11 | MDHD: Non-Tilt
10 | MDHD: Tilt

================================================================================
Table: [dbo].[BodyStyle]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[BodyStyle]:
Id | Name
---------
128 | Ambulance
16 | Bus
73 | Bus - School Bus
95 | Cargo Van
1 | Convertible/Cabriolet
3 | Coupe
8 | Crossover Utility Vehicle (CUV)
130 | Fire Apparatus
5 | Hatchback/Liftback/Notchback
65 | Incomplete

================================================================================
Table: [dbo].[BrakeSystem]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[BrakeSystem]:
Id | Name
---------
1 | Air
3 | Air and Hydraulic
4 | Electric
2 | Hydraulic
5 | Mechanical

================================================================================
Table: [dbo].[BusFloorConfigType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[BusFloorConfigType]:
Id | Name
---------
2 | Lift/Raised
4 | Low Floor
1 | Normal
3 | Sleeper Coach

================================================================================
Table: [dbo].[BusType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[BusType]:
Id | Name
---------
1 | Commuter Coach
2 | Double Deck Coach
6 | Entertainer Coach
7 | Motorhome
3 | Tourist Coach
5 | Transit Bus
4 | Urban Bus

================================================================================
Table: [dbo].[CAN_AACN]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[CAN_AACN]:
Id | Name
---------
1 | Standard
2 | Not Available
3 | Optional

================================================================================
Table: [dbo].[ChargerLevel]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[ChargerLevel]:
Id | Name
---------
1 | Level 1 AC Charger (typically 16A 120V 1.9kW or 13-16A 240V 3kW) may incorporate standard domestic power cord.
2 | Level 2 AC Charger (up to 80A, 208-240V AC, up to 20kW from single- or three-phase AC) cables permanently fixed to charging station.
3 | Level 3 DC Charger or fast charger (up to 400A, up to 600V DC, up to 240kW)

================================================================================
Table: [dbo].[CombinedBrakingSystem]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[CombinedBrakingSystem]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[Conversion]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
FromElementId                  int                  No                                                 
ToElementId                    int                  No                                                 
Formula                        nvarchar             No                                                 

First 10 rows from [dbo].[Conversion]:
Id | FromElementId | ToElementId | Formula
------------------------------------------
1 | 11 | 12 | #x# / 16.387064 
2 | 12 | 11 | #x# * 16.387064 
3 | 11 | 13 | #x# / 1000.
4 | 13 | 11 | #x# * 1000
5 | 12 | 13 | #x# * 0.016387064 
7 | 13 | 12 | #x# / 0.016387064 

================================================================================
Table: [dbo].[CoolingType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[CoolingType]:
Id | Name
---------
1 | Air
2 | Water

================================================================================
Table: [dbo].[Country]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 
displayorder                   int                  Yes                                                

First 10 rows from [dbo].[Country]:
Id | Name | displayorder
------------------------
1 | CANADA | 999
2 | GERMANY | 999
3 | JAPAN | 999
4 | TAIWAN | 999
5 | UNITED KINGDOM (UK) | 999
6 | UNITED STATES (USA) | 1
7 | AUSTRIA | 999
8 | CHINA | 999
9 | ITALY | 999
10 | SOUTH AFRICA | 999

================================================================================
Table: [dbo].[CustomMotorcycleType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[CustomMotorcycleType]:
Id | Name
---------
13 | Bagger
15 | Base
7 | Bobber
20 | Cafe Racer
2 | Chopper/Chopped
18 | Cruising
17 | Drag
6 | Dresser
10 | Drop Seat
12 | Hot Rod

================================================================================
Table: [dbo].[DaytimeRunningLight]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[DaytimeRunningLight]:
Id | Name
---------
1 | Standard
2 | Not Available
3 | Optional

================================================================================
Table: [dbo].[DecodingOutput]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
AddedOn                        datetime             No                                                 
GroupName                      varchar              Yes                                                
Variable                       varchar              Yes                                                
Value                          varchar              Yes                                                
Keys                           varchar              Yes                                                
WmiId                          int                  Yes                                                
PatternId                      int                  Yes                                                
VinSchemaId                    int                  Yes                                                
ElementId                      int                  Yes                                                
AttributeId                    varchar              Yes                                                
CreatedOn                      datetime             Yes                                                
Code                           varchar              Yes                                                
DataType                       varchar              Yes                                                
Decode                         varchar              Yes                                                
Source                         varchar              Yes                                                

First 10 rows from [dbo].[DecodingOutput]:
...table is empty...

================================================================================
Table: [dbo].[DefaultValue]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
ElementId                      int                  No                                                 
VehicleTypeId                  int                  No                                                 
DefaultValue                   varchar              Yes                                                
CreatedOn                      datetime             Yes                                                
UpdatedOn                      datetime             Yes                                                

First 10 rows from [dbo].[DefaultValue]:
Id | ElementId | VehicleTypeId | DefaultValue | CreatedOn | UpdatedOn
---------------------------------------------------------------------
1 | 3 | 1 | 0 | 2019-12-21 20:26:30.583000 | None
2 | 4 | 1 | 0 | 2019-12-21 20:26:30.583000 | None
3 | 16 | 1 | 0 | 2019-12-21 20:26:30.583000 | None
4 | 25 | 1 | 10 | 2019-12-21 20:26:30.583000 | None
5 | 81 | 1 | 0 | 2019-12-21 20:26:30.583000 | None
6 | 82 | 1 | 0 | 2019-12-21 20:26:30.583000 | None
7 | 87 | 1 | 0 | 2019-12-21 20:26:30.583000 | None
8 | 88 | 1 | 0 | 2019-12-21 20:26:30.583000 | None
9 | 101 | 1 | 0 | 2019-12-21 20:26:30.583000 | None
10 | 102 | 1 | 0 | 2019-12-21 20:26:30.583000 | None

================================================================================
Table: [dbo].[DEFS_Body]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
ID                             smallint             No                                                 
DEF                            varchar              Yes                                                
BODY_TYPE                      varchar              Yes                                                
FROM_YEAR                      smallint             No                                                 
TO_YEAR                        smallint             Yes                                                
MODE                           smallint             No                                                 

First 10 rows from [dbo].[DEFS_Body]:
ID | DEF | BODY_TYPE | FROM_YEAR | TO_YEAR | MODE
-------------------------------------------------
-4 | R | None | 2020 | None | 16
-3 | X | None | 2020 | None | 16
-2 | T | None | 2020 | None | 16
-1 | Blank | None | 1994 | None | -1
1 | Convertible(excludes sun-roof,t-bar) | 01 | 1994 | None | -1
2 | 2-door sedan,hardtop,coupe | 01 | 1994 | None | -1
3 | 3-door/2-door hatchback | 01 | 1994 | None | -1
4 | 4-door sedan, hardtop | 01 | 1994 | None | -1
5 | 5-door/4-door hatchback | 01 | 1994 | None | -1
6 | Station Wagon (excluding van and truck based) | 01 | 1994 | None | -1

================================================================================
Table: [dbo].[DEFS_Make]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
ID                             smallint             No                                                 
DEF                            varchar              Yes                                                
NCIC_CODE                      varchar              Yes                                                
MAKE_TYPE                      varchar              Yes                                                
FROM_YEAR                      smallint             No                                                 
TO_YEAR                        smallint             Yes                                                
MODE                           smallint             No                                                 

First 10 rows from [dbo].[DEFS_Make]:
ID | DEF | NCIC_CODE | MAKE_TYPE | FROM_YEAR | TO_YEAR | MODE
-------------------------------------------------------------
-4 | R | None | None | 2020 | None | 16
-3 | X | None | None | 2020 | None | 16
-2 | T | None | None | 2020 | None | 16
-1 | Blank | None | None | 1998 | 2009 | -1
-1 | Blank | None | None | 2005 | None | -1
1 | American Motors* | AMER | 1 | 1994 | 2009 | -1
1 | American Motors | AMER | 1 | 2010 | None | -1
2 | Jeep (Includes Willys**/Kaiser-Jeep | JEEP | 1 | 1994 | 2009 | -1
2 | Jeep / Kaiser-Jeep / Willys- Jeep | JEEP | 1 | 2010 | 2024 | -1
2 | Jeep / Kaiser Jeep / Willys Jeep | JEEP | 1 | 2025 | None | -1

================================================================================
Table: [dbo].[DEFS_Model]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
MAKE                           smallint             No                                                 
ID                             smallint             No                                                 
DEF                            varchar              Yes                                                
MODEL_TYPE                     varchar              Yes                                                
INCLUDES                       varchar              Yes                                                
FROM_YEAR                      smallint             No                                                 
TO_YEAR                        smallint             Yes                                                
MODE                           smallint             No                                                 

First 10 rows from [dbo].[DEFS_Model]:
MAKE | ID | DEF | MODEL_TYPE | INCLUDES | FROM_YEAR | TO_YEAR | MODE
--------------------------------------------------------------------
-4 | -4 | R | None | None | 2020 | None | 16
-4 | -3 | X | None | None | 2020 | None | 16
-4 | -2 | T | None | None | 2020 | None | 16
-3 | -4 | R | None | None | 2020 | None | 16
-3 | -3 | X | None | None | 2020 | None | 16
-3 | -2 | T | None | None | 2020 | None | 16
-2 | -4 | R | None | None | 2020 | None | 16
-2 | -3 | X | None | None | 2020 | None | 16
-2 | -2 | T | None | None | 2020 | None | 16
-1 | -1 | Blank | None | None | 1994 | None | -1

================================================================================
Table: [dbo].[DestinationMarket]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[DestinationMarket]:
Id | Name
---------
1 | 49 States (Except California)
2 | 50 States
23 | Alaska
33 | Arabian Countries
25 | Australia
27 | Brazil
3 | California
4 | Canada
31 | Canada and Other Export Market (BUX) 
28 | Canada, Mexico, Other Export Market (BUX)

================================================================================
Table: [dbo].[DriveType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[DriveType]:
Id | Name
---------
21 | 10x10
15 | 10x4
16 | 10x6
23 | 10x8
17 | 12x4
18 | 12x6
19 | 14x4
22 | 14x6
24 | 2WD/4WD
2 | 4WD/4-Wheel Drive/4x4

================================================================================
Table: [dbo].[DynamicBrakeSupport]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[DynamicBrakeSupport]:
Id | Name
---------
1 | Standard
2 | Not Available
3 | Optional

================================================================================
Table: [dbo].[ECS]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[ECS]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[EDR]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[EDR]:
Id | Name
---------
1 | Standard
2 | Not Available
3 | Optional

================================================================================
Table: [dbo].[ElectrificationLevel]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[ElectrificationLevel]:
Id | Name
---------
4 | BEV (Battery Electric Vehicle)
5 | FCEV (Fuel Cell Electric Vehicle)
9 | HEV (Hybrid Electric Vehicle) - Level Unknown
1 | Mild HEV (Hybrid Electric Vehicle)
3 | PHEV (Plug-in Hybrid Electric Vehicle)
2 | Strong HEV (Hybrid Electric Vehicle)

================================================================================
Table: [dbo].[Element]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 
Code                           varchar              Yes                                                
LookupTable                    varchar              Yes                                                
Description                    varchar              Yes                                                
IsPrivate                      bit                  Yes                                                
GroupName                      varchar              Yes                                                
DataType                       varchar              Yes                                                
MinAllowedValue                int                  Yes                                                
MaxAllowedValue                int                  Yes                                                
IsQS                           bit                  Yes                                                
Decode                         varchar              Yes                                                
weight                         int                  Yes                                                

First 10 rows from [dbo].[Element]:
Id | Name | Code | LookupTable | Description | IsPrivate | GroupName | DataType | MinAllowedValue | MaxAllowedValue | IsQS | Decode | weight
--------------------------------------------------------------------------------------------------------------------------------------------
1 | Other Battery Info | BatteryInfo | None | <p>This field stores any other battery information that does not belong to any of the other battery related fields.</p> | False | Mechanical / Battery | string | None | None | None | Pattern | None
2 | Battery Type | BatteryType | BatteryType | <p>Battery type field stores the battery chemistry type for anode, cathode.</p> | False | Mechanical / Battery | lookup | None | None | True | Pattern | None
3 | Bed Type | BedType | BedType | <p>Bed type is the type of bed (the open back) used for pickup trucks. The common values are standard, short, long, extended.</p> | False | Exterior / Truck | lookup | None | None | True | Pattern | None
4 | Cab Type | BodyCabType | BodyCab | <p>Cab type applies to both pickup truck and other medium- and heavy-duty trucks. The cab or cabin of a truck is the inside space in a truck where the driver is seated. For pickup trucks, the cab type is categorized by the combination number of doors and number of rows for seating. For medium- and heavy-duty trucks (MDHD), the cab type is categorized by the relative location of engine and cab.</p><p>For pickup trucks, there are four cab types.</p><ul><li>Regular: 2 door, 1 row of seats</li><li>Extra/Super/Quad/Double/King/Extended: 2 doors, 2 rows of seats</li><li>Crew/Super Crew/Crew Max: 4 doors, 2 rows of seats</li><li>Mega: 4 doors, 2 rows of seats (with a bigger cabin than crew cab type)</li></ul><p>For medium- and heavy-duty (MDHD) trucks, there are several categories as listed below.</p><ul><li>Cab Beside Engine</li><li>CAE: Cab Above Engine</li><li>CBE: Cab Behind Engine</li><li>COE: Cab Over Engine or Flat Nose: Driver sits on top of the front axle and engine</li><li>LCF: Low Cab Forward</li><li>Conventional: Driver sits behind the engine</li><li>Non-Tilt</li><li>Tilt</li></ul> | False | Exterior / Truck | lookup | None | None | True | Pattern | None
5 | Body Class | BodyClass | BodyStyle | <p>Body Class presents the body type based on 49 CFR 565.12(b): "Body type means the general configuration or shape of a vehicle distinguished by such characteristics as the number of doors or windows, cargo-carrying features and the roofline (e.g., sedan, fastback, hatchback)." Definitions are not provided for individual body types in the regulation.</p> | False | Exterior / Body | lookup | None | None | True | Pattern | 99
8 | Country Name | Country | Country | <p>The country in which the manufacturer is located. This is taken from the WMI.</p> | False | None | lookup | None | None | None | None | None
9 | Engine Number of Cylinders | EngineCylinders | None | <p>This is a numerical field to store the number of cylinders in an engine. Common values for passenger cars are 4 or 6.</p> | False | Engine | int | 1 | 16 | None | Pattern | 88
10 | Destination Market | DestinationMarket | DestinationMarket | <p>Destination Market is the market where the vehicle is intended to be sold.</p> | False | General | lookup | None | None | None | Pattern | None
11 | Displacement (CC) | DisplacementCC | None | <p>Engine displacement (in cubic centimeters) is the volume swept by all the pistons inside the cylinders of a reciprocating engine in a single movement from top dead center to bottom dead center.</p> | False | Engine | decimal | 15 | 9999 | None | Pattern | 98
12 | Displacement (CI) | DisplacementCI | None | <p>Engine displacement (in cubic inches) is the volume swept by all the pistons inside the cylinders of a reciprocating engine in a single movement from top dead center to bottom dead center.</p> | False | Engine | decimal | 10 | 3000 | None | Pattern | None

================================================================================
Table: [dbo].[EngineConfiguration]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[EngineConfiguration]:
Id | Name
---------
5 | Horizontally opposed (boxer)
1 | In-Line
3 | Rotary
2 | V-Shaped
4 | W Shaped

================================================================================
Table: [dbo].[EngineModel]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 
Description                    varchar              Yes                                                

First 10 rows from [dbo].[EngineModel]:
Id | Name | Description
-----------------------
28 | 3306 | Caterpillar: CAT 3306
29 | 3406 | Caterpillar: CAT 3406
30 | C18 | Caterpillar: CAT C18
31 | C7 | Caterpillar: C7
32 | 3176 | Caterpillar: CAT 3176
33 | C9 | Caterpillar: CAT C9
34 | PX-9 | Cummins: PACCAR PX-9
35 | MX-11 | PACCAR: PACCAR MX-11
36 | PACCAR PX-6/PX-7 | PACCAR: PX-6/PX-7
37 | PX-8 | Cummins: PACCAR PX-8

================================================================================
Table: [dbo].[EngineModelPattern]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
EngineModelId                  int                  No                                                 
ElementId                      int                  No                                                 
AttributeId                    varchar              No                                                 
CreatedOn                      datetime             Yes                                                
UpdatedOn                      datetime             Yes                                                

First 10 rows from [dbo].[EngineModelPattern]:
Id | EngineModelId | ElementId | AttributeId | CreatedOn | UpdatedOn
--------------------------------------------------------------------
1 | 28 | 9 | 6 | 2016-03-02 16:47:05.727000 | None
2 | 28 | 17 | 4 | 2016-03-02 16:47:05.750000 | None
3 | 28 | 24 | 1 | 2016-03-02 16:47:05.763000 | None
4 | 28 | 64 | 1 | 2016-03-02 16:47:05.777000 | None
9 | 29 | 9 | 6 | 2016-03-02 16:51:48.743000 | None
10 | 29 | 17 | 4 | 2016-03-02 16:51:48.743000 | None
11 | 29 | 24 | 1 | 2016-03-02 16:51:48.747000 | None
12 | 29 | 64 | 1 | 2016-03-02 16:51:48.747000 | None
13 | 30 | 9 | 6 | 2016-03-02 16:51:48.750000 | None
14 | 30 | 17 | 4 | 2016-03-02 16:51:48.750000 | None

================================================================================
Table: [dbo].[EntertainmentSystem]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[EntertainmentSystem]:
Id | Name
---------
2 | CD + Stereo
1 | Rear Entertainment System

================================================================================
Table: [dbo].[ErrorCode]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 
AdditionalErrorText            varchar              Yes                                                
weight                         int                  Yes                                                

First 10 rows from [dbo].[ErrorCode]:
Id | Name | AdditionalErrorText | weight
----------------------------------------
0 | 0 - VIN decoded clean. Check Digit (9th position) is correct | None | 0
1 | 1 - Check Digit (9th position) does not calculate properly | None | -5
2 | 2 - VIN corrected, error in one position  | None | -100
3 | 3 - VIN corrected, error in one position (assuming Check Digit is correct) | None | -100
4 | 4 - VIN corrected, error in one position only (indicated by ! in Suggested VIN), multiple matches found | In the Possible values section, the Numeric value before the : indicates the position in error and the values after the : indicate the possible values that are allowed in this position. | -200
5 | 5 - VIN has errors in few positions | The error positions are indicated by ! in Suggested VIN. In the Possible values section, each pair of parenthesis indicate information about each error position in VIN . The Numeric value before the : indicates the position in error and the values after the : indicate the possible values that are allowed in this position | -300
6 | 6 - Incomplete VIN | None | -10
7 | 7 - Manufacturer is not registered with NHTSA for sale or importation in the U.S. for use on U.S roads; Please contact the manufacturer directly for more information | None | -10000
8 | 8 - No detailed data available currently | None | -1000
9 | 9 - Glider Warning - A "Glider" is not a "motor vehicle", as defined in 49 U.S.C. 30102(a)(6), and cannot be assigned a VIN that meets 49 CFR Part 565 requirements | None | 0

================================================================================
Table: [dbo].[EVDriveUnit]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[EVDriveUnit]:
Id | Name
---------
1 | Dual Motor
2 | Single Motor

================================================================================
Table: [dbo].[ForwardCollisionWarning]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[ForwardCollisionWarning]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[FuelDeliveryType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[FuelDeliveryType]:
Id | Name
---------
6 | Common Rail Direct Injection Diesel (CRDI)
9 | Compression Ignition
2 | Lean-Burn Gasoline Direct Injection (LBGDI)
3 | Multipoint Fuel Injection (MPFI)
4 | Sequential Fuel Injection (SFI)
1 | Stoichiometric Gasoline Direct Injection (SGDI)
5 | Throttle Body Fuel Injection (TBI)
10 | Transistor Controlled Ignition (TCI)
7 | Unit Injector Direct Injection Diesel (UDI)

================================================================================
Table: [dbo].[FuelTankMaterial]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[FuelTankMaterial]:
Id | Name
---------
2 | Aluminum alloy
3 | Fiberglass composite
5 | Injection-molded plastic
6 | Injection-molded plastic covered by metal
4 | Other composite
1 | Steel

================================================================================
Table: [dbo].[FuelTankType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[FuelTankType]:
Id | Name
---------
4 | Perimeter mount
1 | Saddle
3 | Submerged in frame
2 | Under seat

================================================================================
Table: [dbo].[FuelType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[FuelType]:
Id | Name
---------
8 | Compressed Hydrogen/Hydrogen
6 | Compressed Natural Gas (CNG)
1 | Diesel
2 | Electric
10 | Ethanol (E85)
15 | Flexible Fuel Vehicle (FFV)
18 | Fuel Cell
4 | Gasoline
7 | Liquefied Natural Gas (LNG)
9 | Liquefied Petroleum Gas (propane or LPG)

================================================================================
Table: [dbo].[GrossVehicleWeightRating]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 
SortOrder                      int                  Yes                                                
MinRangeWeight                 int                  Yes                                                
MaxRangeWeight                 int                  Yes                                                

First 10 rows from [dbo].[GrossVehicleWeightRating]:
Id | Name | SortOrder | MinRangeWeight | MaxRangeWeight
-------------------------------------------------------
1 | Class 1: 6,000 lb or less (2,722 kg or less) | 5 | 0 | 6000
2 | Class 2: 6,001 - 10,000 lb (2,722 - 4,536 kg) | 10 | 6001 | 10000
4 | Class 3: 10,001 - 14,000 lb (4,536 - 6,350 kg) | 11 | 10001 | 14000
5 | Class 4: 14,001 - 16,000 lb (6,350 - 7,258 kg) | 12 | 14001 | 16000
6 | Class 5: 16,001 - 19,500 lb (7,258 - 8,845 kg) | 13 | 16001 | 19500
7 | Class 6: 19,501 - 26,000 lb (8,845 - 11,794 kg) | 14 | 19501 | 26000
8 | Class 7: 26,001 - 33,000 lb (11,794 - 14,969 kg) | 15 | 26001 | 33000
9 | Class 8: 33,001 lb and above (14,969 kg and above) | 16 | 33001 | 99999999
10 | Class 1A: 3,000 lb or less (1,360 kg or less) | 1 | 0 | 3000
11 | Class 1B: 3,001 - 4,000 lb (1,360 - 1,814 kg) | 2 | 3001 | 4000

================================================================================
Table: [dbo].[KeylessIgnition]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[KeylessIgnition]:
Id | Name
---------
1 | Standard
2 | Not Available
3 | Optional

================================================================================
Table: [dbo].[LaneCenteringAssistance]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[LaneCenteringAssistance]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[LaneDepartureWarning]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[LaneDepartureWarning]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[LaneKeepSystem]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[LaneKeepSystem]:
Id | Name
---------
4 | Not Available
5 | Optional
1 | Standard

================================================================================
Table: [dbo].[LowerBeamHeadlampLightSource]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[LowerBeamHeadlampLightSource]:
Id | Name
---------
1 | Halogen
2 | HID
3 | LED
4 | Other
5 | Halogen, HID
6 | Halogen, LED
7 | Halogen, Other
8 | HID, LED
9 | HID, Other
10 | LED, Other

================================================================================
Table: [dbo].[Make]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 
CreatedOn                      datetime             Yes                                                
UpdatedOn                      datetime             Yes                                                

First 10 rows from [dbo].[Make]:
Id | Name | CreatedOn | UpdatedOn
---------------------------------
440 | Aston Martin | None | None
441 | Tesla | None | None
442 | Jaguar | None | None
443 | Maserati | None | None
444 | Land Rover | None | None
445 | Rolls-Royce | None | 2024-06-07 12:47:26.073000
446 | BUELL (EBR) | None | None
447 | Jialing | None | None
448 | Toyota | None | None
449 | Mercedes-Benz | None | None

================================================================================
Table: [dbo].[Make_Model]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
MakeId                         int                  No                                                 
ModelId                        int                  No                                                 
CreatedOn                      datetime             Yes                                                
UpdatedOn                      datetime             Yes                                                

First 10 rows from [dbo].[Make_Model]:
Id | MakeId | ModelId | CreatedOn | UpdatedOn
---------------------------------------------
1 | 440 | 1684 | None | None
2 | 441 | 1685 | None | None
3 | 440 | 1686 | None | None
4 | 440 | 1687 | None | None
5 | 440 | 1688 | None | None
6 | 445 | 1689 | None | None
7 | 445 | 1690 | None | None
8 | 445 | 1691 | None | None
9 | 446 | 1692 | None | None
10 | 446 | 1693 | None | None

================================================================================
Table: [dbo].[Manufacturer]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[Manufacturer]:
Id | Name
---------
955 | TESLA, INC.
956 | ASTON MARTIN LAGONDA LIMITED
957 | BMW OF NORTH AMERICA, LLC
958 | JAGUAR LAND ROVER NA, LLC
959 | MASERATI NORTH AMERICA, INC.
960 | ROLLS ROYCE MOTOR CARS
961 | BUELL MOTORCYCLE CO.
962 | TOYOTA MOTOR NORTH AMERICA, INC
964 | MERCEDES-BENZ USA, LLC (SPRINTER)
965 | FULMER FABRICATIONS

================================================================================
Table: [dbo].[Manufacturer_Make]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
ManufacturerId                 int                  No                                                 
MakeId                         int                  No                                                 

First 10 rows from [dbo].[Manufacturer_Make]:
Id | ManufacturerId | MakeId
----------------------------
81 | 956 | 440
80 | 955 | 441
83 | 958 | 442
1081 | 1079 | 442
82 | 959 | 443
5476 | 15956 | 443
186 | 1079 | 444
84 | 960 | 445
85 | 961 | 446
144 | 1011 | 447

================================================================================
Table: [dbo].[Model]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 
CreatedOn                      datetime             Yes                                                
UpdatedOn                      datetime             Yes                                                

First 10 rows from [dbo].[Model]:
Id | Name | CreatedOn | UpdatedOn
---------------------------------
1684 | V8 Vantage | None | None
1685 | Model S | None | None
1686 | DBS | None | None
1687 | DB9 | None | None
1688 | Rapide | None | None
1689 | Phantom | None | None
1690 | Ghost | None | None
1691 | Wraith | None | None
1692 | R series | None | None
1693 | S Series | None | None

================================================================================
Table: [dbo].[MotorcycleChassisType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[MotorcycleChassisType]:
Id | Name
---------
3 | Autocycle (Open or Closed)
4 | Reverse Trike
2 | Three-Wheeler - Other
1 | Trike

================================================================================
Table: [dbo].[MotorcycleSuspensionType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[MotorcycleSuspensionType]:
Id | Name
---------
1 | Hardtail/Rigid Frame
4 | Rubber Mount
2 | Softail
3 | Swingarm/Wing Fork/Pivoted Fork

================================================================================
Table: [dbo].[NonLandUse]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[NonLandUse]:
Id | Name
---------
1 | Air
3 | Air and Water
2 | Water

================================================================================
Table: [dbo].[ParkAssist]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[ParkAssist]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[Pattern]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
VinSchemaId                    int                  No                                                 
Keys                           varchar              No                                                 
ElementId                      int                  No                                                 
AttributeId                    varchar              No                                                 
CreatedOn                      datetime             Yes                                                
UpdatedOn                      datetime             Yes                                                

First 10 rows from [dbo].[Pattern]:
Id | VinSchemaId | Keys | ElementId | AttributeId | CreatedOn | UpdatedOn
-------------------------------------------------------------------------
14 | 2225 | *B | 37 | 3 | 2015-03-04 10:03:54.630000 | None
16 | 2225 | *D | 37 | 2 | 2015-03-04 10:04:17.107000 | None
18 | 2225 | *F | 37 | 8 | 2015-03-04 10:05:33.893000 | None
19 | 2225 | H | 55 | 6 | 2015-03-04 10:21:13.087000 | None
24 | 2225 | **BA | 5 | 5 | 2015-03-04 10:33:34.057000 | None
26 | 2225 | **BA | 14 | 2 | 2015-03-04 10:33:34.083000 | None
27 | 2225 | **BA | 33 | 2 | 2015-03-04 10:33:34.097000 | None
29 | 2225 | **BA | 61 | 1 | 2015-03-04 10:33:34.123000 | None
32 | 2225 | **BB | 5 | 1 | 2015-03-04 10:36:56.767000 | None
34 | 2225 | **BB | 14 | 2 | 2015-03-04 10:36:56.777000 | None

================================================================================
Table: [dbo].[PedestrianAutomaticEmergencyBraking]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[PedestrianAutomaticEmergencyBraking]:
Id | Name
---------
1 | Standard
2 | Not Available
3 | Optional

================================================================================
Table: [dbo].[Pretensioner]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[Pretensioner]:
Id | Name
---------
2 | No
1 | Yes

================================================================================
Table: [dbo].[RearAutomaticEmergencyBraking]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[RearAutomaticEmergencyBraking]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[RearCrossTrafficAlert]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[RearCrossTrafficAlert]:
Id | Name
---------
1 | Standard
2 | Optional
3 | Not Available

================================================================================
Table: [dbo].[RearVisibilityCamera]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[RearVisibilityCamera]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[SeatBeltsAll]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[SeatBeltsAll]:
Id | Name
---------
2 | Automatic
1 | Manual
3 | Manual and Automatic

================================================================================
Table: [dbo].[SemiautomaticHeadlampBeamSwitching]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[SemiautomaticHeadlampBeamSwitching]:
Id | Name
---------
1 | Standard
2 | Not Available
3 | Optional

================================================================================
Table: [dbo].[Steering]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[Steering]:
Id | Name
---------
1 | Left-Hand Drive (LHD)
2 | Right-Hand Drive (RHD)

================================================================================
Table: [dbo].[TPMS]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[TPMS]:
Id | Name
---------
1 | Direct
2 | Indirect

================================================================================
Table: [dbo].[TractionControl]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[TractionControl]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[TrailerBodyType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[TrailerBodyType]:
Id | Name
---------
136 | Agricultural Trailer
58 | Auto Transporter
2 | Boat Trailer
5 | Box or Van Enclosed Trailer
10 | Camping or Travel Trailer
3 | Car Hauler Trailer
162 | Concession Trailer
154 | Construction Trailer
45 | Dolly
4 | Dump Trailer

================================================================================
Table: [dbo].[TrailerType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[TrailerType]:
Id | Name
---------
31 | Ball Hitch
1 | Ball Type Pull
14 | Bumper Pull
5 | Fifth Wheel
3 | Gooseneck
6 | Kingpin
30 | Other
2 | Pintle Hitch/Hook
4 | Straight Semi/Semi Trailer

================================================================================
Table: [dbo].[Transmission]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[Transmission]:
Id | Name
---------
8 | Automated Manual Transmission (AMT)
2 | Automatic
7 | Continuously Variable Transmission (CVT)
15 | Direct Drive
14 | Dual-Clutch Transmission (DCT)
4 | Electronic Continuously Variable (e-CVT)
3 | Manual/Standard
10 | Motorcycle - Chain Drive
13 | Motorcycle - Chain Drive Off-Road
12 | Motorcycle - CVT Belt Drive

================================================================================
Table: [dbo].[Turbo]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[Turbo]:
Id | Name
---------
2 | No
1 | Yes

================================================================================
Table: [dbo].[ValvetrainDesign]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[ValvetrainDesign]:
Id | Name
---------
1 | Camless Valve Actuation (CVA)
2 | Dual Overhead Cam (DOHC)
3 | Overhead Valve (OHV)
4 | Single Overhead Cam (SOHC)

================================================================================
Table: [dbo].[VehicleSpecPattern]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
VSpecSchemaPatternId           int                  No                                                 
IsKey                          bit                  No                                                 
ElementId                      int                  No                                                 
AttributeId                    varchar              No                                                 
CreatedOn                      datetime             Yes                                                
UpdatedOn                      datetime             Yes                                                

First 10 rows from [dbo].[VehicleSpecPattern]:
Id | VSpecSchemaPatternId | IsKey | ElementId | AttributeId | CreatedOn | UpdatedOn
-----------------------------------------------------------------------------------
1 | 1 | False | 86 | 1 | 2016-05-16 11:21:12.197000 | 2023-01-05 14:31:32.247000
2 | 1 | False | 87 | 1 | 2016-05-16 11:21:12.200000 | 2023-01-05 14:31:32.260000
3 | 1 | False | 99 | 1 | 2016-05-16 11:21:12.200000 | 2023-01-05 14:31:32.273000
4 | 1 | False | 104 | 1 | 2016-05-16 11:21:12.200000 | 2023-01-05 14:31:32.297000
5 | 2 | False | 55 | 4 | 2016-05-16 15:31:44.097000 | 2023-01-05 14:32:42.783000
6 | 2 | False | 65 | 3 | 2016-05-16 15:31:44.123000 | 2023-01-05 14:32:42.800000
7 | 2 | False | 69 | 3 | 2016-05-16 15:31:44.123000 | 2023-01-05 14:32:42.813000
8 | 2 | False | 78 | 1 | 2016-05-16 15:31:44.127000 | 2023-01-05 14:32:42.830000
9 | 2 | False | 107 | 4 | 2016-05-16 15:31:44.130000 | 2023-01-05 14:32:42.847000
11 | 3 | True | 14 | 2 | 2016-05-23 18:42:22.937000 | 2018-06-27 11:52:56.110000

================================================================================
Table: [dbo].[VehicleSpecSchema]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
MakeId                         int                  No                                                 
Description                    varchar              Yes                                                
CreatedOn                      datetime             No                                                 
UpdatedOn                      datetime             Yes                                                
VehicleTypeId                  int                  Yes                                                
Source                         varchar              Yes                                                
SourceDate                     datetime             Yes                                                
URL                            varchar              Yes                                                
TobeQCed                       bit                  Yes                                                

First 10 rows from [dbo].[VehicleSpecSchema]:
Id | MakeId | Description | CreatedOn | UpdatedOn | VehicleTypeId | Source | SourceDate | URL | TobeQCed
--------------------------------------------------------------------------------------------------------
1 | 448 | Sales brochure for the Toyota Corolla model line for 2016 | 2016-05-16 11:16:06.333000 | 2023-01-05 14:31:32.300000 | 2 | Toyota Sales Brochure - 2016 | 2016-01-01 00:00:00 | http://www.toyota.com/content/ebrochure/2016/corolla_ebrochure.pdf | None
2 | 448 | Toyota Camry Airbag Information for 2015 and 2016 | 2016-05-16 15:25:31.957000 | 2023-01-05 14:32:42.847000 | 2 | Cars.com Research | 2016-05-16 00:00:00 | http://www.cars.com/toyota/camry/2016/specifications/ | None
3 | 468 | None | 2016-05-23 18:36:04.927000 | 2023-01-05 15:06:09.767000 | 2 | cars.com | 2016-05-23 00:00:00 | http://www.cars.com/buick/cascada/2016/standard-equipment/ | None
6 | 582 | None | 2017-08-29 13:49:48.587000 | 2023-01-24 15:15:23.887000 | 2 | None | None | None | None
7 | 582 | None | 2017-08-29 15:00:38.720000 | None | 2 | None | None | None | None
9 | 582 | TPMS Type | 2017-08-30 06:36:05.637000 | 2023-02-23 09:22:17.257000 | 2 | None | None | None | None
10 | 582 | None | 2017-08-30 06:41:22.567000 | None | 2 | None | None | None | None
11 | 582 | TPMS Type | 2017-08-30 06:51:31.360000 | 2023-02-23 09:40:18.277000 | 2 | None | None | None | None
12 | 582 | None | 2017-08-30 10:10:41.137000 | 2018-07-23 14:51:08.973000 | 2 | None | None | None | None
13 | 582 | None | 2017-08-30 10:14:26.323000 | 2022-12-20 08:54:28.450000 | 2 | None | None | None | None

================================================================================
Table: [dbo].[VehicleSpecSchema_Model]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
VehicleSpecSchemaId            int                  No                                                 
ModelId                        int                  No                                                 

First 10 rows from [dbo].[VehicleSpecSchema_Model]:
Id | VehicleSpecSchemaId | ModelId
----------------------------------
1 | 1 | 2208
2 | 2 | 2469
3 | 3 | 10290
12 | 7 | 3148
17 | 10 | 4014
49 | 29 | 2074
51 | 31 | 2128
58 | 36 | 1959
59 | 36 | 1960
60 | 36 | 1961

================================================================================
Table: [dbo].[VehicleSpecSchema_Year]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
VehicleSpecSchemaId            int                  No                                                 
Year                           int                  No                                                 

First 10 rows from [dbo].[VehicleSpecSchema_Year]:
Id | VehicleSpecSchemaId | Year
-------------------------------
1 | 1 | 2016
2 | 2 | 2016
3 | 2 | 2015
4 | 3 | 2016
17 | 7 | 2012
26 | 10 | 2015
27 | 10 | 2014
119 | 29 | 2016
120 | 29 | 2015
123 | 31 | 2016

================================================================================
Table: [dbo].[VehicleType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 
DisplayOrder                   int                  Yes                                                
FormType                       int                  Yes                                                
Description                    varchar              Yes                                                
IncludeInEquipPlant            bit                  Yes                                                

First 10 rows from [dbo].[VehicleType]:
Id | Name | DisplayOrder | FormType | Description | IncludeInEquipPlant
-----------------------------------------------------------------------
1 | Motorcycle | None | None | None | True
2 | Passenger Car | None | None | None | True
3 | Truck | None | None | None | True
5 | Bus | None | None | None | True
6 | Trailer | None | None | None | True
7 | Multipurpose Passenger Vehicle (MPV) | None | None | None | True
9 | Low Speed Vehicle (LSV) | None | None | None | True
10 | Incomplete Vehicle | None | None | None | None
13 | Off Road Vehicle | None | None | None | None

================================================================================
Table: [dbo].[VinDescriptor]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Descriptor                     varchar              No                                                 
ModelYear                      int                  No                                                 
CreatedOn                      datetime             Yes                                                
UpdatedOn                      datetime             Yes                                                

First 10 rows from [dbo].[VinDescriptor]:
Id | Descriptor | ModelYear | CreatedOn | UpdatedOn
---------------------------------------------------
9 | YV40621A*P1 | 2023 | 2023-01-18 10:34:44.157000 | None
10 | YV4BR00K*L1 | 2020 | 2023-01-18 10:34:44.157000 | None
11 | YV4H600L*N1 | 2022 | 2023-01-18 10:34:44.157000 | None
12 | YV40621N*P1 | 2023 | 2023-01-18 10:34:44.157000 | None
13 | YV4BR00K*M1 | 2021 | 2023-01-18 10:34:44.157000 | None
14 | YV4H600N*P1 | 2023 | 2023-01-18 10:34:44.157000 | None
15 | YV4A221K*L1 | 2020 | 2023-01-18 10:34:44.157000 | None
16 | YV4BR00K*N1 | 2022 | 2023-01-18 10:34:44.157000 | None
17 | YV4H600Z*N1 | 2022 | 2023-01-18 10:34:44.157000 | None
18 | YV4A221K*M1 | 2021 | 2023-01-18 10:34:44.157000 | None

================================================================================
Table: [dbo].[VinException]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
VIN                            varchar              No                                                 
CheckDigit                     bit                  No                                                 
CreatedOn                      datetime             Yes                                                
UpdatedOn                      datetime             Yes                                                

First 10 rows from [dbo].[VinException]:
Id | VIN | CheckDigit | CreatedOn | UpdatedOn
---------------------------------------------
1 | KMTGE4S1PRU008144 | True | 2024-02-13 19:08:40.140000 | None
2 | KMTGE4S1PRU008174 | True | 2024-02-13 19:08:40.147000 | None
3 | KMTGE4S1PRU008173 | True | 2024-02-13 19:08:40.153000 | None
4 | KMTGE4S1PRU008143 | True | 2024-02-13 19:08:40.157000 | None
5 | KMTGE4S1PRU008175 | True | 2024-02-13 19:08:40.160000 | None
6 | KMTGE4S1PRU008186 | True | 2024-02-13 19:08:40.163000 | None
7 | KMTGE4S1PRU008184 | True | 2024-02-13 19:08:40.167000 | None
8 | KMTGE4S1PRU008188 | True | 2024-02-13 19:08:40.170000 | None
9 | KMTGE4S1PRU008187 | True | 2024-02-13 19:08:40.170000 | None
10 | KMTGE4S1PRU008185 | True | 2024-02-13 19:08:40.173000 | None

================================================================================
Table: [dbo].[VinSchema]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 
sourcewmi                      varchar              Yes                                                
CreatedOn                      datetime             Yes                                                
UpdatedOn                      datetime             Yes                                                
Notes                          varchar              Yes                                                
TobeQCed                       bit                  Yes                                                

First 10 rows from [dbo].[VinSchema]:
Id | Name | sourcewmi | CreatedOn | UpdatedOn | Notes | TobeQCed
----------------------------------------------------------------
2225 |  Aston Martin Schema for SCF - 2010 | None | 2015-03-03 19:36:03 | 2023-01-10 16:47:32.920000 | None | False
2226 | Tesla Schema for 5YJ (2012-2013) (for Model S) | None | 2015-03-04 13:20:26 | 2023-01-12 13:42:47.750000 | None | False
2227 |  Aston Martin Schema for SCF - 2011 | None | None | 2023-01-12 09:37:09.937000 | None | False
2230 | Maserati Schema for ZAM (2013) | None | 2015-03-05 10:15:35 | 2015-03-05 11:04:26.333000 | None | None
2231 |  Aston Martin Schema for SCF - 2012 | None | None | 2023-01-11 15:38:10.243000 | None | False
2232 | Jialing Schema for LAA (2008 - 2009) - Scooter | None | 2015-03-05 13:10:22 | 2015-06-15 13:11:48.407000 | None | None
2233 | Jialing Schema for LAA (2010) - Scooter | None | None | None | None | None
2234 | Tesla Model S Schema for 5YJ (2014) | None | None | 2024-08-26 07:17:39.347000 | None | False
2236 | Rolls Royce schema for SCA - 2013 | None | 2015-03-05 14:28:45 | 2015-12-08 15:54:14.787000 | None | None
2237 | Aston Martin Schema for SCF - 2013 | None | 2015-03-05 14:54:08.677000 | 2023-01-12 09:56:30.630000 | None | False

================================================================================
Table: [dbo].[VSpecSchemaPattern]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
SchemaId                       int                  No                                                 

First 10 rows from [dbo].[VSpecSchemaPattern]:
Id | SchemaId
-------------
1 | 1
2 | 2
3 | 3
8 | 7
9 | 9
10 | 10
11 | 11
12 | 12
13 | 13
14 | 14

================================================================================
Table: [dbo].[WheelBaseType]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[WheelBaseType]:
Id | Name
---------
4 | Extra Long
1 | Long
6 | Medium
2 | Short
5 | Standard
3 | Super Long

================================================================================
Table: [dbo].[WheelieMitigation]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Name                           varchar              No                                                 

First 10 rows from [dbo].[WheelieMitigation]:
Id | Name
---------
2 | Not Available
3 | Optional
1 | Standard

================================================================================
Table: [dbo].[Wmi]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
Wmi                            varchar              No                                                 
ManufacturerId                 int                  Yes                                                
MakeId                         int                  Yes                                                
VehicleTypeId                  int                  Yes                                                
CreatedOn                      datetime             Yes                                                
UpdatedOn                      datetime             Yes                                                
CountryId                      int                  Yes                                                
PublicAvailabilityDate         datetime             Yes                                                
TruckTypeId                    int                  Yes                                                
ProcessedOn                    datetime             Yes                                                
NonCompliant                   bit                  Yes                                                
NonCompliantReason             varchar              Yes                                                
NonCompliantSetByOVSC          bit                  Yes                                                

First 10 rows from [dbo].[Wmi]:
Id | Wmi | ManufacturerId | MakeId | VehicleTypeId | CreatedOn | UpdatedOn | CountryId | PublicAvailabilityDate | TruckTypeId | ProcessedOn | NonCompliant | NonCompliantReason | NonCompliantSetByOVSC
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
1995 | SCF | 956 | 440 | 2 | 2015-03-03 19:29:57 | 2018-01-26 11:54:50.870000 | 5 | 2015-01-01 00:00:00 | None | 2025-09-08 23:15:02.090000 | None | None | None
1996 | SAJ | 1079 | 442 | 2 | 2015-03-04 09:34:13 | 2015-05-10 22:30:57.720000 | 5 | 2015-01-01 00:00:00 | None | 2025-09-07 19:15:01.400000 | None | None | None
1997 | SAL | 1079 | 444 | 7 | 2015-03-04 09:41:10 | 2015-05-10 11:45:58.983000 | 5 | 2015-01-01 00:00:00 | None | 2025-09-08 20:25:30.850000 | None | None | None
1998 | 5YJ | 955 | 441 | 2 | 2015-03-04 12:48:16.543000 | None | 6 | 2015-01-01 00:00:00 | None | 2025-09-05 23:05:01.517000 | None | None | None
1999 | 546 | 961 | 446 | 1 | 2015-03-05 08:39:50 | 2024-10-31 13:07:29.717000 | 6 | 2015-01-01 00:00:00 | None | 2025-09-06 12:30:06.900000 | False | None | False
2000 | ZAM | 15956 | 443 | 2 | 2015-03-05 10:03:45 | 2021-09-13 12:35:26.447000 | 9 | 2015-01-01 00:00:00 | None | 2025-09-06 21:25:01.753000 | None | None | None
2001 | LAA | 14273 | 447 | 1 | 2015-03-05 13:09:32 | 2020-06-09 14:42:04.843000 | 8 | 2015-01-01 00:00:00 | None | 2025-09-09 21:25:04.810000 | None | None | None
2002 | SCA | 960 | 445 | 2 | 2015-03-05 14:24:52.863000 | None | 5 | 2015-01-01 00:00:00 | None | 2025-09-06 23:35:07.950000 | None | None | None
2003 | WDZ | 964 | 449 | 5 | 2015-03-09 12:23:33.157000 | None | 2 | 2015-01-01 00:00:00 | None | 2025-09-09 20:15:06.260000 | None | None | None
2004 | WCD | 1146 | 450 | 5 | 2015-03-09 12:24:46 | 2021-02-10 11:34:20.710000 | 2 | 2015-01-01 00:00:00 | None | 2025-09-09 22:05:00.993000 | None | None | None

================================================================================
Table: [dbo].[Wmi_Make]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
WmiId                          int                  No                                                 
MakeId                         int                  No                                                 

First 10 rows from [dbo].[Wmi_Make]:
WmiId | MakeId
--------------
1995 | 440
12797 | 440
1998 | 441
2205 | 441
12871 | 441
13374 | 441
1996 | 442
6799 | 442
2000 | 443
6800 | 443

================================================================================
Table: [dbo].[Wmi_VinSchema]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
Id                             int                  No                                                 
WmiId                          int                  No                                                 
VinSchemaId                    int                  No                                                 
YearFrom                       int                  No                                                 
YearTo                         int                  Yes                                                
OrgId                          int                  Yes                                                

First 10 rows from [dbo].[Wmi_VinSchema]:
Id | WmiId | VinSchemaId | YearFrom | YearTo | OrgId
----------------------------------------------------
1891 | 1995 | 2225 | 2010 | 2010 | 4
1894 | 1995 | 2227 | 2011 | 2011 | 5
1898 | 2000 | 2230 | 2013 | 2013 | 10
1899 | 1995 | 2231 | 2012 | 2012 | 7
1900 | 2001 | 2232 | 2008 | 2009 | 17
1902 | 2001 | 2233 | 2010 | None | 18
1904 | 1998 | 2226 | 2012 | 2013 | 3
1905 | 1998 | 2234 | 2014 | 2014 | 48029
1908 | 1995 | 2237 | 2013 | 2013 | 8
1909 | 1995 | 2238 | 2014 | 2014 | 20

================================================================================
Table: [dbo].[WMIYearValidChars]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
id                             int                  No                                                 
WMI                            varchar              No                                                 
Year                           int                  No                                                 
Position                       int                  Yes                                                
Char                           varchar              Yes                                                

First 10 rows from [dbo].[WMIYearValidChars]:
id | WMI | Year | Position | Char
---------------------------------
1936457338 | 101 | 1980 | 4 | B
1936457339 | 101 | 1980 | 4 | F
1936457340 | 101 | 1980 | 4 | G
1936457341 | 101 | 1980 | 4 | S
1936457342 | 101 | 1980 | 5 | B
1936457343 | 101 | 1980 | 5 | F
1936457344 | 101 | 1980 | 5 | K
1936457345 | 101 | 1980 | 5 | R
1936457346 | 101 | 1980 | 5 | S
1936457347 | 101 | 1980 | 5 | T

================================================================================
Table: [dbo].[WMIYearValidChars_CacheExceptions]
--------------------------------------------------------------------------------
Columns:
Column Name                    Data Type            Nullable   Description
------------------------------ -------------------- ---------- ----------------------------------------
WMI                            varchar              No                                                 
CreatedOn                      datetime             No                                                 
Id                             int                  No                                                 

First 10 rows from [dbo].[WMIYearValidChars_CacheExceptions]:
...table is empty...
"""
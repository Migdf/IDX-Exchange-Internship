import pandas as pd
import os


def clean_week4_dataset(input_path, output_path, dataset_name):
    ### Load dataset ###

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    data = pd.read_csv(input_path, low_memory=False)

    print("\n==================================================")
    print(f"{dataset_name.upper()} DATASET LOADED")
    print("==================================================")
    print("Dataset loaded successfully.")
    print(f"Input path: {input_path}")
    print(f"Original dataset shape: {data.shape}")
    print(f"Original row count: {data.shape[0]}")
    print(f"Original column count: {data.shape[1]}")

    rows_before_cleaning = data.shape[0]

    ### Convert to Datetime Format ###
    print("\n----- Date Field Conversion -----")

    date_fields = [
        "CloseDate",
        "PurchaseContractDate",
        "ListingContractDate",
        "ContractStatusChangeDate"
    ]

    date_fields_existing = [
        col for col in date_fields
        if col in data.columns
    ]

    date_fields_missing = [
        col for col in date_fields
        if col not in data.columns
    ]

    print("Date fields found:")
    print(date_fields_existing)

    print("\nDate fields missing:")
    print(date_fields_missing)

    for col in date_fields_existing:
        data[col] = pd.to_datetime(data[col], errors="coerce")
        print(f"{col} converted to: {data[col].dtype}")

    ### Check Numeric Fields are Properly Typed ###
    print("\n----- Numeric Field Conversion -----")

    numeric_fields = [
        "ClosePrice",
        "ListPrice",
        "OriginalListPrice",
        "LivingArea",
        "LotSizeAcres",
        "BedroomsTotal",
        "BathroomsTotalInteger",
        "DaysOnMarket",
        "YearBuilt",
        "Latitude",
        "Longitude",
        "rate_30yr_fixed"
    ]

    numeric_fields_existing = [
        col for col in numeric_fields
        if col in data.columns
    ]

    numeric_fields_missing = [
        col for col in numeric_fields
        if col not in data.columns
    ]

    print("Numeric fields found:")
    print(numeric_fields_existing)

    print("\nNumeric fields missing:")
    print(numeric_fields_missing)

    for col in numeric_fields_existing:
        data[col] = pd.to_numeric(data[col], errors="coerce")
        print(f"{col} converted to: {data[col].dtype}")

    ### Remove Unecessary/Redundant Columns ###
    print("\n----- Removing Unnecessary or Redundant Columns -----")

    columns_to_remove = [
        "latfilled",
        "lonfilled"
    ]

    existing_columns_to_remove = [
        col for col in columns_to_remove
        if col in data.columns
    ]

    print("Columns selected for removal:")
    print(existing_columns_to_remove)

    columns_before_removal = data.shape[1]

    data = data.drop(columns=columns_to_remove, errors="ignore")

    columns_after_removal = data.shape[1]

    print(f"Columns before removal: {columns_before_removal}")
    print(f"Columns after removal: {columns_after_removal}")
    print(f"Columns removed: {columns_before_removal - columns_after_removal}")

    ### Handle Missing Values ###
    print("\n----- Missing Value Check -----")

    missing_counts = data.isnull().sum()
    missing_percentages = (missing_counts / len(data)) * 100

    missing_summary = pd.DataFrame({
        "Column": missing_counts.index,
        "MissingCount": missing_counts.values,
        "MissingPercentage": missing_percentages.values
    }).sort_values(by="MissingPercentage", ascending=False)

    print("\nMissing value summary:")
    print(missing_summary.to_string(index=False))

    ### Flag Invalid Values ###
    print("\n----- Invalid Numeric Value Flags -----")

    # Invalid values are flagged instead of removed.
    # This preserves the data while documenting which records may need review.

    if "ClosePrice" in data.columns:
        data["invalid_closeprice_flag"] = data["ClosePrice"] <= 0
    else:
        data["invalid_closeprice_flag"] = False

    if "LivingArea" in data.columns:
        data["invalid_livingarea_flag"] = data["LivingArea"] <= 0
    else:
        data["invalid_livingarea_flag"] = False

    if "DaysOnMarket" in data.columns:
        data["invalid_daysonmarket_flag"] = data["DaysOnMarket"] < 0
    else:
        data["invalid_daysonmarket_flag"] = False

    if "BedroomsTotal" in data.columns:
        data["invalid_bedrooms_flag"] = data["BedroomsTotal"] < 0
    else:
        data["invalid_bedrooms_flag"] = False

    if "BathroomsTotalInteger" in data.columns:
        data["invalid_bathrooms_flag"] = data["BathroomsTotalInteger"] < 0
    else:
        data["invalid_bathrooms_flag"] = False

    invalid_numeric_flags = [
        "invalid_closeprice_flag",
        "invalid_livingarea_flag",
        "invalid_daysonmarket_flag",
        "invalid_bedrooms_flag",
        "invalid_bathrooms_flag"
    ]

    for flag in invalid_numeric_flags:
        print(f"{flag}: {data[flag].sum()} records flagged")

    ### Date Consistency Check ###
    print("\n----- Date Consistency Checks -----")

    # Required logical order:
    # ListingContractDate should be before PurchaseContractDate,
    # and PurchaseContractDate should be before CloseDate.
    #
    # Listings may not have CloseDate or PurchaseContractDate.
    # If a field is missing, the related flag is set to False.

    if "ListingContractDate" in data.columns and "CloseDate" in data.columns:
        data["listing_after_close_flag"] = data["ListingContractDate"] > data["CloseDate"]
    else:
        data["listing_after_close_flag"] = False

    if "PurchaseContractDate" in data.columns and "CloseDate" in data.columns:
        data["purchase_after_close_flag"] = data["PurchaseContractDate"] > data["CloseDate"]
    else:
        data["purchase_after_close_flag"] = False

    if "ListingContractDate" in data.columns and "PurchaseContractDate" in data.columns:
        data["negative_timeline_flag"] = data["ListingContractDate"] > data["PurchaseContractDate"]
    else:
        data["negative_timeline_flag"] = False

    date_flags = [
        "listing_after_close_flag",
        "purchase_after_close_flag",
        "negative_timeline_flag"
    ]

    for flag in date_flags:
        print(f"{flag}: {data[flag].sum()} records flagged")

    ### Geographic Data Check ###
    print("\n----- Geographic Data Checks -----")

    # California latitude is usually around 32 to 42.
    # California longitude is usually around -125 to -114.
    # These bounds are used to flag clearly implausible coordinates.

    if "Latitude" in data.columns and "Longitude" in data.columns:
        data["missing_coordinates_flag"] = data["Latitude"].isnull() | data["Longitude"].isnull()

        data["zero_coordinates_flag"] = (
            (data["Latitude"] == 0) |
            (data["Longitude"] == 0)
        )

        data["positive_longitude_flag"] = data["Longitude"] > 0

        data["implausible_coordinates_flag"] = (
            (data["Latitude"] < 32) |
            (data["Latitude"] > 42.5) |
            (data["Longitude"] < -125) |
            (data["Longitude"] > -114)
        )

    else:
        data["missing_coordinates_flag"] = False
        data["zero_coordinates_flag"] = False
        data["positive_longitude_flag"] = False
        data["implausible_coordinates_flag"] = False

    geo_flags = [
        "missing_coordinates_flag",
        "zero_coordinates_flag",
        "positive_longitude_flag",
        "implausible_coordinates_flag"
    ]

    for flag in geo_flags:
        print(f"{flag}: {data[flag].sum()} records flagged")

    ### Combined Data Quality Check ###
    print("\n----- Combined Data Quality Flags -----")

    quality_flag_columns = invalid_numeric_flags + date_flags + geo_flags

    data["any_quality_issue_flag"] = data[quality_flag_columns].any(axis=1)

    print(f"Records with at least one quality issue: {data['any_quality_issue_flag'].sum()}")
    print(f"Records with no quality issue flags: {(~data['any_quality_issue_flag']).sum()}")

    ### Before/After Row Counts ###
    print("\n----- Before/After Row Counts -----")

    print(f"Rows before cleaning: {rows_before_cleaning}")
    print(f"Rows after cleaning: {data.shape[0]}")
    print(f"Columns after cleaning and flag creation: {data.shape[1]}")

    ### Data Type Confirmation ###

    print("\n----- Final Data Type Confirmation -----")

    print("\nDate field data types:")
    for col in date_fields_existing:
        print(f"{col}: {data[col].dtype}")

    print("\nNumeric field data types:")
    for col in numeric_fields_existing:
        print(f"{col}: {data[col].dtype}")

    print("\nFlag column data types:")
    for col in quality_flag_columns + ["any_quality_issue_flag"]:
        print(f"{col}: {data[col].dtype}")

    ### Save CSV ###
    data.to_csv(output_path, index=False)

    print("\n----- Final Output -----")
    print("Cleaned analysis-ready CSV saved.")
    print(f"Output path: {output_path}")
    print(f"Final row count: {data.shape[0]}")
    print(f"Final column count: {data.shape[1]}")


### File Paths ###

output_folder = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 4 Output"

listings_input_path = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 3 Output/listings_with_mortgage_rates.csv"
sold_input_path = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 3 Output/sold_with_mortgage_rates.csv"

listings_output_path = os.path.join(output_folder, "listings_week4_cleaned.csv")
sold_output_path = os.path.join(output_folder, "sold_week4_cleaned.csv")


### Clean Listings ###

clean_week4_dataset(
    input_path=listings_input_path,
    output_path=listings_output_path,
    dataset_name="Listings"
)


### Clean Sold ###

clean_week4_dataset(
    input_path=sold_input_path,
    output_path=sold_output_path,
    dataset_name="Sold"
)
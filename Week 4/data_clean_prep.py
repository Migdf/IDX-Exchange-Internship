import pandas as pd
import os

### Load dataset ###

input_path = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 3 Output/sold_week3.csv"
output_folder = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 4 Output"
output_path = os.path.join(output_folder, "sold_week4_cleaned.csv")

os.makedirs(output_folder, exist_ok=True)

sold = pd.read_csv(input_path, low_memory=False)

print("Dataset loaded successfully.")
print(f"Input path: {input_path}")
print(f"Original dataset shape: {sold.shape}")
print(f"Original row count: {sold.shape[0]}")
print(f"Original column count: {sold.shape[1]}")

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
    if col in sold.columns
]

date_fields_missing = [
    col for col in date_fields
    if col not in sold.columns
]

print("Date fields found:")
print(date_fields_existing)

print("\nDate fields missing:")
print(date_fields_missing)

for col in date_fields_existing:
    sold[col] = pd.to_datetime(sold[col], errors="coerce")
    print(f"{col} converted to: {sold[col].dtype}")

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
    "Longitude"
]

numeric_fields_existing = [
    col for col in numeric_fields
    if col in sold.columns
]

numeric_fields_missing = [
    col for col in numeric_fields
    if col not in sold.columns
]

print("Numeric fields found:")
print(numeric_fields_existing)

print("\nNumeric fields missing:")
print(numeric_fields_missing)

for col in numeric_fields_existing:
    sold[col] = pd.to_numeric(sold[col], errors="coerce")
    print(f"{col} converted to: {sold[col].dtype}")

### Remove Unecessary/Redundant Columns ###
print("\n----- Removing Unnecessary or Redundant Columns -----")

columns_to_remove = [
    "latfilled",
    "lonfilled"
]

existing_columns_to_remove = [
    col for col in columns_to_remove
    if col in sold.columns
]

print("Columns selected for removal:")
print(existing_columns_to_remove)

columns_before_removal = sold.shape[1]

sold = sold.drop(columns=columns_to_remove, errors="ignore")

columns_after_removal = sold.shape[1]

print(f"Columns before removal: {columns_before_removal}")
print(f"Columns after removal: {columns_after_removal}")
print(f"Columns removed: {columns_before_removal - columns_after_removal}")

### Handle Missing Values ###
print("\n----- Missing Value Check -----")

missing_counts = sold.isnull().sum()
missing_percentages = (missing_counts / len(sold)) * 100

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

if "ClosePrice" in sold.columns:
    sold["invalid_closeprice_flag"] = sold["ClosePrice"] <= 0
else:
    sold["invalid_closeprice_flag"] = False

if "LivingArea" in sold.columns:
    sold["invalid_livingarea_flag"] = sold["LivingArea"] <= 0
else:
    sold["invalid_livingarea_flag"] = False

if "DaysOnMarket" in sold.columns:
    sold["invalid_daysonmarket_flag"] = sold["DaysOnMarket"] < 0
else:
    sold["invalid_daysonmarket_flag"] = False

if "BedroomsTotal" in sold.columns:
    sold["invalid_bedrooms_flag"] = sold["BedroomsTotal"] < 0
else:
    sold["invalid_bedrooms_flag"] = False

if "BathroomsTotalInteger" in sold.columns:
    sold["invalid_bathrooms_flag"] = sold["BathroomsTotalInteger"] < 0
else:
    sold["invalid_bathrooms_flag"] = False

invalid_numeric_flags = [
    "invalid_closeprice_flag",
    "invalid_livingarea_flag",
    "invalid_daysonmarket_flag",
    "invalid_bedrooms_flag",
    "invalid_bathrooms_flag"
]

for flag in invalid_numeric_flags:
    print(f"{flag}: {sold[flag].sum()} records flagged")

### Date Consistency Check ###
print("\n----- Date Consistency Checks -----")

# Required logical order:
# ListingContractDate should be before PurchaseContractDate,
# and PurchaseContractDate should be before CloseDate.

if "ListingContractDate" in sold.columns and "CloseDate" in sold.columns:
    sold["listing_after_close_flag"] = sold["ListingContractDate"] > sold["CloseDate"]
else:
    sold["listing_after_close_flag"] = False

if "PurchaseContractDate" in sold.columns and "CloseDate" in sold.columns:
    sold["purchase_after_close_flag"] = sold["PurchaseContractDate"] > sold["CloseDate"]
else:
    sold["purchase_after_close_flag"] = False

if "ListingContractDate" in sold.columns and "PurchaseContractDate" in sold.columns:
    sold["negative_timeline_flag"] = sold["ListingContractDate"] > sold["PurchaseContractDate"]
else:
    sold["negative_timeline_flag"] = False

date_flags = [
    "listing_after_close_flag",
    "purchase_after_close_flag",
    "negative_timeline_flag"
]

for flag in date_flags:
    print(f"{flag}: {sold[flag].sum()} records flagged")

### Geographic Data Check ###
print("\n----- Geographic Data Checks -----")

# California latitude is usually around 32 to 42.
# California longitude is usually around -125 to -114.
# These bounds are used to flag clearly implausible coordinates.

if "Latitude" in sold.columns and "Longitude" in sold.columns:
    sold["missing_coordinates_flag"] = sold["Latitude"].isnull() | sold["Longitude"].isnull()

    sold["zero_coordinates_flag"] = (
        (sold["Latitude"] == 0) |
        (sold["Longitude"] == 0)
    )

    sold["positive_longitude_flag"] = sold["Longitude"] > 0

    sold["implausible_coordinates_flag"] = (
        (sold["Latitude"] < 32) |
        (sold["Latitude"] > 42.5) |
        (sold["Longitude"] < -125) |
        (sold["Longitude"] > -114)
    )

else:
    sold["missing_coordinates_flag"] = False
    sold["zero_coordinates_flag"] = False
    sold["positive_longitude_flag"] = False
    sold["implausible_coordinates_flag"] = False

geo_flags = [
    "missing_coordinates_flag",
    "zero_coordinates_flag",
    "positive_longitude_flag",
    "implausible_coordinates_flag"
]

for flag in geo_flags:
    print(f"{flag}: {sold[flag].sum()} records flagged")

### Combined Data Quality Check ###
print("\n----- Combined Data Quality Flags -----")

quality_flag_columns = invalid_numeric_flags + date_flags + geo_flags

sold["any_quality_issue_flag"] = sold[quality_flag_columns].any(axis=1)

print(f"Records with at least one quality issue: {sold['any_quality_issue_flag'].sum()}")
print(f"Records with no quality issue flags: {(~sold['any_quality_issue_flag']).sum()}")

### Before/After Row Counts ###
print("\n----- Before/After Row Counts -----")

print(f"Rows before cleaning: {pd.read_csv(input_path, low_memory=False).shape[0]}")
print(f"Rows after cleaning: {sold.shape[0]}")
print(f"Columns after cleaning and flag creation: {sold.shape[1]}")

### Data Type Confirmation ###

print("\n----- Final Data Type Confirmation -----")

print("\nDate field data types:")
for col in date_fields_existing:
    print(f"{col}: {sold[col].dtype}")

print("\nNumeric field data types:")
for col in numeric_fields_existing:
    print(f"{col}: {sold[col].dtype}")

print("\nFlag column data types:")
for col in quality_flag_columns + ["any_quality_issue_flag"]:
    print(f"{col}: {sold[col].dtype}")

### Save CSV ###
sold.to_csv(output_path, index=False)

print("\n----- Final Output -----")
print("Cleaned analysis-ready CSV saved.")
print(f"Output path: {output_path}")
print(f"Final row count: {sold.shape[0]}")
print(f"Final column count: {sold.shape[1]}")
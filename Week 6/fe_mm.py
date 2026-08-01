import pandas as pd
import os
import geopandas as gpd
from shapely.geometry import Point


### Load dataset ###

input_path = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 4 Output/sold_week4_cleaned.csv"
output_folder = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 6 Output"
output_path = os.path.join(output_folder, "sold_week6_features.csv")

school_district_file = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 6 Output/DistrictAreas2526_-284845464123469011.geojson"

os.makedirs(output_folder, exist_ok=True)

sold = pd.read_csv(input_path, low_memory=False)

print("Dataset loaded successfully.")
print(f"Input path: {input_path}")
print(f"Original dataset shape: {sold.shape}")
print(f"Original row count: {sold.shape[0]}")
print(f"Original column count: {sold.shape[1]}")


### Convert Date Fields ###

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


### Convert Numeric Fields ###

print("\n----- Numeric Field Conversion -----")

numeric_fields = [
    "ClosePrice",
    "OriginalListPrice",
    "ListPrice",
    "LivingArea",
    "DaysOnMarket",
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


### Feature Engineering ###

print("\n----- Feature Engineering -----")

# Price Ratio = ClosePrice / OriginalListPrice
if "ClosePrice" in sold.columns and "OriginalListPrice" in sold.columns:
    sold["price_ratio"] = sold["ClosePrice"] / sold["OriginalListPrice"]
else:
    sold["price_ratio"] = pd.NA

# Close to Original List Ratio = ClosePrice / OriginalListPrice
if "ClosePrice" in sold.columns and "OriginalListPrice" in sold.columns:
    sold["close_to_original_list_ratio"] = sold["ClosePrice"] / sold["OriginalListPrice"]
else:
    sold["close_to_original_list_ratio"] = pd.NA

# Price Per Sq Ft = ClosePrice / LivingArea
if "ClosePrice" in sold.columns and "LivingArea" in sold.columns:
    sold["price_per_sqft"] = sold["ClosePrice"] / sold["LivingArea"]
else:
    sold["price_per_sqft"] = pd.NA

# Days on Market = raw DaysOnMarket field
if "DaysOnMarket" in sold.columns:
    sold["days_on_market_metric"] = sold["DaysOnMarket"]
else:
    sold["days_on_market_metric"] = pd.NA

# Year / Month / YrMo from CloseDate
if "CloseDate" in sold.columns:
    sold["close_year"] = sold["CloseDate"].dt.year
    sold["close_month"] = sold["CloseDate"].dt.month
    sold["YrMo"] = sold["CloseDate"].dt.to_period("M").astype(str)
else:
    sold["close_year"] = pd.NA
    sold["close_month"] = pd.NA
    sold["YrMo"] = pd.NA

# Listing to Contract Days = PurchaseContractDate - ListingContractDate
if "PurchaseContractDate" in sold.columns and "ListingContractDate" in sold.columns:
    sold["listing_to_contract_days"] = (
        sold["PurchaseContractDate"] - sold["ListingContractDate"]
    ).dt.days
else:
    sold["listing_to_contract_days"] = pd.NA

# Contract to Close Days = CloseDate - PurchaseContractDate
if "CloseDate" in sold.columns and "PurchaseContractDate" in sold.columns:
    sold["contract_to_close_days"] = (
        sold["CloseDate"] - sold["PurchaseContractDate"]
    ).dt.days
else:
    sold["contract_to_close_days"] = pd.NA

engineered_columns = [
    "price_ratio",
    "close_to_original_list_ratio",
    "price_per_sqft",
    "days_on_market_metric",
    "close_year",
    "close_month",
    "YrMo",
    "listing_to_contract_days",
    "contract_to_close_days"
]

print("Engineered metrics created:")
print(engineered_columns)


### Clean Invalid Engineered Values ###

print("\n----- Cleaning Invalid Engineered Values -----")

for col in [
    "price_ratio",
    "close_to_original_list_ratio",
    "price_per_sqft"
]:
    if col in sold.columns:
        sold[col] = sold[col].replace([float("inf"), float("-inf")], pd.NA)
        print(f"{col}: infinite values replaced with NA")


### Add School Districts Using Latitude and Longitude ###

print("\n----- School District Mapping -----")

# Aidan's instructions:
# 1. Download the California School District boundary GeoJSON
# 2. Install GeoPandas
# 3. Read the school district GeoJSON into a GeoDataFrame
# 4. Filter the school district dataset to only include DistrictType = "Unified"
# 5. Convert each property's Latitude and Longitude into a geographic point
# 6. Perform a spatial join to determine which Unified School District polygon contains each property
# 7. Add the resulting DistrictName as a new column in your dataset
# 8. Save the enriched dataset

if not os.path.exists(school_district_file):
    raise FileNotFoundError(f"School district GeoJSON not found at: {school_district_file}")

school_districts = gpd.read_file(school_district_file)

print("School district file loaded successfully.")
print(f"Original school district shape: {school_districts.shape}")

print("\nSchool district columns:")
print(school_districts.columns.tolist())

# Find DistrictType column safely
district_type_col = None

for col in school_districts.columns:
    cleaned_col = col.lower().replace(" ", "").replace("_", "")
    if cleaned_col == "districttype":
        district_type_col = col
        break

if district_type_col is None:
    raise KeyError(
        "Could not find a DistrictType column. "
        "Check the printed school district column names above."
    )

# Find DistrictName column safely
district_name_col = None

for col in school_districts.columns:
    cleaned_col = col.lower().replace(" ", "").replace("_", "")
    if cleaned_col == "districtname":
        district_name_col = col
        break

if district_name_col is None:
    raise KeyError(
        "Could not find a DistrictName column. "
        "Check the printed school district column names above."
    )

print(f"\nUsing district type column: {district_type_col}")
print(f"Using district name column: {district_name_col}")

# Filter school district dataset to only Unified districts
school_districts_unified = school_districts[
    school_districts[district_type_col] == "Unified"
].copy()

print(f"\nUnified school district shape: {school_districts_unified.shape}")

# Confirm Latitude and Longitude exist
if "Latitude" not in sold.columns or "Longitude" not in sold.columns:
    raise KeyError("Latitude and/or Longitude column was not found in sold dataset.")

# Drop rows with missing coordinates only for the spatial join.
# The original sold dataset is preserved.
sold_with_coords = sold.dropna(subset=["Latitude", "Longitude"]).copy()

print(f"\nRows with Latitude/Longitude available: {len(sold_with_coords)}")
print(f"Rows missing Latitude/Longitude: {len(sold) - len(sold_with_coords)}")

# Convert each property's Latitude and Longitude into a geographic point.
# Point uses x, y order, so Longitude comes first and Latitude comes second.
sold_with_coords["geometry"] = [
    Point(longitude, latitude)
    for longitude, latitude in zip(
        sold_with_coords["Longitude"],
        sold_with_coords["Latitude"]
    )
]

sold_geo = gpd.GeoDataFrame(
    sold_with_coords,
    geometry="geometry",
    crs="EPSG:4326"
)

# Make sure school district polygons use the same coordinate system
school_districts_unified = school_districts_unified.to_crs("EPSG:4326")

# Perform spatial join to find which Unified School District contains each property
sold_with_districts = gpd.sjoin(
    sold_geo,
    school_districts_unified[[district_name_col, "geometry"]],
    how="left",
    predicate="within"
)

# Create blank school_district column in original sold dataset
sold["school_district"] = pd.NA

# Add DistrictName as a new column in the original sold dataset
sold.loc[
    sold_with_districts.index,
    "school_district"
] = sold_with_districts[district_name_col]

print("\nSchool district mapping completed.")
print(f"Rows with school district matched: {sold['school_district'].notna().sum()}")
print(f"Rows without school district matched: {sold['school_district'].isna().sum()}")


### Sample Output Table ###

print("\n----- Sample Output Table Showing New Columns -----")

sample_columns = [
    "ClosePrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket",
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "price_ratio",
    "close_to_original_list_ratio",
    "price_per_sqft",
    "days_on_market_metric",
    "close_year",
    "close_month",
    "YrMo",
    "listing_to_contract_days",
    "contract_to_close_days",
    "school_district"
]

sample_columns_existing = [
    col for col in sample_columns
    if col in sold.columns
]

print(sold[sample_columns_existing].head(20).to_string(index=False))


### Segment Analysis by PropertyType ###

print("\n----- Segment Summary by PropertyType -----")

segment_metrics = [
    "ClosePrice",
    "price_ratio",
    "price_per_sqft",
    "DaysOnMarket",
    "listing_to_contract_days",
    "contract_to_close_days"
]

segment_metrics_existing = [
    col for col in segment_metrics
    if col in sold.columns
]

if "PropertyType" in sold.columns:
    property_type_summary = sold.groupby("PropertyType")[segment_metrics_existing].agg(
        ["count", "mean", "median", "min", "max"]
    )

    print(property_type_summary.to_string())
else:
    print("PropertyType column not found. Skipping PropertyType segment summary.")


### Segment Analysis by CountyOrParish ###

print("\n----- Segment Summary by CountyOrParish -----")

if "CountyOrParish" in sold.columns:
    county_summary = sold.groupby("CountyOrParish")[segment_metrics_existing].agg(
        ["count", "mean", "median", "min", "max"]
    )

    print(county_summary.to_string())
else:
    print("CountyOrParish column not found. Skipping CountyOrParish segment summary.")


### Segment Analysis by PropertySubType ###

print("\n----- Segment Summary by PropertySubType -----")

if "PropertySubType" in sold.columns:
    subtype_summary = sold.groupby("PropertySubType")[segment_metrics_existing].agg(
        ["count", "mean", "median", "min", "max"]
    )

    print(subtype_summary.to_string())
else:
    print("PropertySubType column not found. Skipping PropertySubType segment summary.")


### Segment Analysis by MLSAreaMajor ###

print("\n----- Segment Summary by MLSAreaMajor -----")

if "MLSAreaMajor" in sold.columns:
    area_summary = sold.groupby("MLSAreaMajor")[segment_metrics_existing].agg(
        ["count", "mean", "median", "min", "max"]
    )

    print(area_summary.to_string())
else:
    print("MLSAreaMajor column not found. Skipping MLSAreaMajor segment summary.")


### Competitive Intelligence: ListOfficeName ###

print("\n----- Segment Summary by ListOfficeName -----")

if "ListOfficeName" in sold.columns:
    list_office_summary = sold.groupby("ListOfficeName")[segment_metrics_existing].agg(
        ["count", "mean", "median"]
    )

    if "ClosePrice" in segment_metrics_existing:
        list_office_summary = list_office_summary.sort_values(
            by=("ClosePrice", "count"),
            ascending=False
        )

    print(list_office_summary.head(25).to_string())
else:
    print("ListOfficeName column not found. Skipping ListOfficeName segment summary.")


### Competitive Intelligence: BuyerOfficeName ###

print("\n----- Segment Summary by BuyerOfficeName -----")

if "BuyerOfficeName" in sold.columns:
    buyer_office_summary = sold.groupby("BuyerOfficeName")[segment_metrics_existing].agg(
        ["count", "mean", "median"]
    )

    if "ClosePrice" in segment_metrics_existing:
        buyer_office_summary = buyer_office_summary.sort_values(
            by=("ClosePrice", "count"),
            ascending=False
        )

    print(buyer_office_summary.head(25).to_string())
else:
    print("BuyerOfficeName column not found. Skipping BuyerOfficeName segment summary.")


### Time-Series Summary by YrMo ###

print("\n----- Time-Series Summary by YrMo -----")

if "YrMo" in sold.columns:
    yrmo_summary = sold.groupby("YrMo")[segment_metrics_existing].agg(
        ["count", "mean", "median"]
    )

    print(yrmo_summary.to_string())
else:
    print("YrMo column not found. Skipping YrMo summary.")


### Save CSV ###

sold.to_csv(output_path, index=False)

print("\n----- Final Output -----")
print("Week 6 feature-engineered and school-district-enriched CSV saved.")
print(f"Output path: {output_path}")
print(f"Final row count: {sold.shape[0]}")
print(f"Final column count: {sold.shape[1]}")
import geopandas as gpd
from shapely.geometry import Point

print("\n----- School District Mapping -----")

school_district_file = "'/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/DistrictAreas2526_7183497817009048579.csv'"

# Read the school district GeoJSON into a GeoDataFrame
school_districts = gpd.read_file(school_district_file)

print("School district file loaded successfully.")
print(f"Original school district shape: {school_districts.shape}")

# Filter to only Unified school districts
school_districts_unified = school_districts[
    school_districts["DistrictType"] == "Unified"
].copy()

print(f"Unified school district shape: {school_districts_unified.shape}")

# Convert each property's Latitude and Longitude into a geographic point
sold["geometry"] = [
    Point(longitude, latitude)
    for longitude, latitude in zip(sold["Longitude"], sold["Latitude"])
]

sold_geo = gpd.GeoDataFrame(
    sold,
    geometry="geometry",
    crs="EPSG:4326"
)

# Make sure school district polygons use the same coordinate system
school_districts_unified = school_districts_unified.to_crs("EPSG:4326")

# Perform spatial join to find which Unified School District contains each property
sold_with_districts = gpd.sjoin(
    sold_geo,
    school_districts_unified[["DistrictName", "geometry"]],
    how="left",
    predicate="within"
)

# Add DistrictName as a new column
sold_with_districts = sold_with_districts.rename(
    columns={"DistrictName": "school_district"}
)

# Drop geospatial helper columns before saving back to regular CSV
sold = pd.DataFrame(
    sold_with_districts.drop(columns=["geometry", "index_right"], errors="ignore")
)

print("School district mapping completed.")
print(f"Rows with school district matched: {sold['school_district'].notna().sum()}")
print(f"Rows without school district matched: {sold['school_district'].isna().sum()}")
import pandas as pd
import matplotlib.pyplot as plt
import os

### Load dataset ###
input_path = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 1 Output/sold.csv"
output_folder = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 2 Output"
output_path = os.path.join(output_folder, "sold_week2.csv")

os.makedirs(output_folder, exist_ok=True)

sold = pd.read_csv(input_path, low_memory=False)

print("Dataset loaded successfully.")
print(f"Original dataset shape: {sold.shape}")
print(f"Original row count: {sold.shape[0]}")
print(f"Original column count: {sold.shape[1]}")

### Inspect Structure ###
print("----- Dataset Structure -----")
print("\nColumn names:")
print(sold.columns.tolist())

print("\nFirst 5 rows:")
print(sold.head())

# print("\nColumn data types:") # Maybe delete? #
# print(sold.dtypes)

### Unique Property Types Analysis ###
uniques = sold['PropertyType'].unique()
print("Types of properties: ", uniques)

if "PropertyType" not in sold.columns:
    raise KeyError("PropertyType column was not found in the dataset.")

property_type_counts = sold["PropertyType"].value_counts(dropna=False)
property_type_percentages = sold["PropertyType"].value_counts(normalize=True, dropna=False) * 100

property_type_summary = pd.DataFrame({
    "Count": property_type_counts,
    "Percentage": property_type_percentages
})

print(property_type_summary)

### Filter - ONLY Residential ###
sold_residential = sold[sold.PropertyType == 'Residential']
print(f"Residential column count: {sold_residential.shape[1]}")
### Dropping Empty Columns ###
missing_counts = sold_residential.isnull().sum()
missing_percentages = (missing_counts / len(sold_residential)) * 100

missing_report = pd.DataFrame({
    "Column": missing_counts.index,
    "MissingCount": missing_counts.values,
    "MissingPercentage": missing_percentages.values
})

missing_report["Above90PercentMissing"] = missing_report["MissingPercentage"] > 90

missing_report = missing_report.sort_values(
    by="MissingPercentage",
    ascending=False
)

print("\nNull-count summary table for Residential-only dataset:")
print(missing_report.to_string(index=False))

columns_above_90_missing = missing_report[
    missing_report["Above90PercentMissing"] == True
]["Column"].tolist()

print("\nColumns flagged above 90% missing in Residential-only dataset:")
print(columns_above_90_missing)

print(f"\nNumber of columns above 90% missing: {len(columns_above_90_missing)}")

### Drop Missing Columns ###
columns_before_drop = sold_residential.shape[1]

sold_residential_cleaned = sold_residential.drop(
    columns=columns_above_90_missing
)

columns_after_drop = sold_residential_cleaned.shape[1]

print(f"Columns before dropping >90% missing columns: {columns_before_drop}")
print(f"Columns after dropping >90% missing columns: {columns_after_drop}")
print(f"Columns dropped: {columns_before_drop - columns_after_drop}")

print("\nThe dataset used from this point forward is Residential-only and has columns above 90% missing removed.")

### Numerical Analysis ###
numeric_fields = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt"
]

numeric_fields_existing = [
    col for col in numeric_fields
    if col in sold_residential_cleaned.columns
]

missing_numeric_fields = [
    col for col in numeric_fields
    if col not in sold_residential_cleaned.columns
]

print("\nNumeric fields found:")
print(numeric_fields_existing)

print("\nNumeric fields missing or dropped:")
print(missing_numeric_fields)

for col in numeric_fields_existing:
    sold_residential_cleaned[col] = pd.to_numeric(
        sold_residential_cleaned[col],
        errors="coerce"
    )

numeric_summary = sold_residential_cleaned[numeric_fields_existing].describe(
    percentiles=[0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
).T

numeric_summary = numeric_summary.rename(columns={
    "count": "Count",
    "mean": "Mean",
    "std": "StdDev",
    "min": "Min",
    "1%": "P1",
    "5%": "P5",
    "10%": "P10",
    "25%": "P25",
    "50%": "Median",
    "75%": "P75",
    "90%": "P90",
    "95%": "P95",
    "99%": "P99",
    "max": "Max"
})

print(numeric_summary.to_string())

### Outliers Using IQR ###
for col in numeric_fields_existing:
    series = sold_residential_cleaned[col].dropna()

    if series.empty:
        print(f"\n{col}: No valid numeric values available.")
        continue

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = series[
        (series < lower_bound) |
        (series > upper_bound)
    ]

    print(f"\nColumn: {col}")
    print(f"Q1: {q1}")
    print(f"Q3: {q3}")
    print(f"IQR: {iqr}")
    print(f"Lower outlier bound: {lower_bound}")
    print(f"Upper outlier bound: {upper_bound}")
    print(f"Outlier count: {len(outliers)}")
    print(f"Outlier percentage: {(len(outliers) / len(series)) * 100:.2f}%")

    if len(outliers) > 0:
        print(f"Smallest outlier value: {outliers.min()}")
        print(f"Largest outlier value: {outliers.max()}")

### Plots ###
for col in numeric_fields_existing:
    series = sold_residential_cleaned[col].dropna()

    if series.empty:
        print(f"{col}: skipped because there are no valid numeric values.")
        continue

    print(f"Generating histogram and boxplot for: {col}")

    plt.figure(figsize=(8, 5))
    plt.hist(series, bins=50)
    plt.title(f"Histogram of {col}")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(8, 5))
    plt.boxplot(series, vert=False,flierprops={
        "marker": ".",
        "markersize": 5
    })
    plt.title(f"Boxplot of {col}")
    plt.xlabel(col)
    plt.tight_layout()
    plt.show()

### Save CSV ###
sold_residential_cleaned.to_csv(output_path, index=False)

print("Final CSV saved.")
print(f"Output path: {output_path}")
print(f"Final rows: {sold_residential_cleaned.shape[0]}")
print(f"Final columns: {sold_residential_cleaned.shape[1]}")
import pandas as pd
import os


### Load dataset ###

input_path = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 6 Output/sold_week6_features.csv"
output_folder = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 7 Output"

flagged_output_path = os.path.join(output_folder, "sold_week7_flagged.csv")
filtered_output_path = os.path.join(output_folder, "sold_week7_filtered.csv")

os.makedirs(output_folder, exist_ok=True)

sold = pd.read_csv(input_path, low_memory=False)

print("Dataset loaded successfully.")
print(f"Input path: {input_path}")
print(f"Original dataset shape: {sold.shape}")
print(f"Original row count: {sold.shape[0]}")
print(f"Original column count: {sold.shape[1]}")


### Convert Numeric Fields ###

print("\n----- Numeric Field Conversion -----")

numeric_fields = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
    "price_per_sqft",
    "price_ratio",
    "close_to_original_list_ratio"
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


### Business Rule Flags ###

print("\n----- Business Rule Flags -----")

# These values are invalid based on basic real estate logic.
# They are flagged separately from statistical IQR outliers.

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

if "price_per_sqft" in sold.columns:
    sold["invalid_price_per_sqft_flag"] = sold["price_per_sqft"] <= 0
else:
    sold["invalid_price_per_sqft_flag"] = False

if "price_ratio" in sold.columns:
    sold["invalid_price_ratio_flag"] = sold["price_ratio"] <= 0
else:
    sold["invalid_price_ratio_flag"] = False

if "close_to_original_list_ratio" in sold.columns:
    sold["invalid_close_to_original_list_ratio_flag"] = sold["close_to_original_list_ratio"] <= 0
else:
    sold["invalid_close_to_original_list_ratio_flag"] = False

business_rule_flags = [
    "invalid_closeprice_flag",
    "invalid_livingarea_flag",
    "invalid_daysonmarket_flag",
    "invalid_price_per_sqft_flag",
    "invalid_price_ratio_flag",
    "invalid_close_to_original_list_ratio_flag"
]

for flag in business_rule_flags:
    print(f"{flag}: {sold[flag].sum()} records flagged")


### IQR Outlier Flagging Function ###

def add_iqr_outlier_flag(data, column):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    flag_column = f"{column}_iqr_outlier_flag"

    data[flag_column] = (
        (data[column] < lower) |
        (data[column] > upper)
    )

    print(f"\n{column} IQR Summary")
    print(f"Q1: {Q1}")
    print(f"Q3: {Q3}")
    print(f"IQR: {IQR}")
    print(f"Lower bound: {lower}")
    print(f"Upper bound: {upper}")
    print(f"Outliers flagged: {data[flag_column].sum()}")

    return data, flag_column


### Apply IQR Outlier Detection ###

print("\n----- IQR Outlier Detection -----")

iqr_fields = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
    "price_per_sqft",
    "price_ratio",
    "close_to_original_list_ratio"
]

iqr_flag_columns = []

for col in iqr_fields:
    if col in sold.columns:
        sold, flag_col = add_iqr_outlier_flag(sold, col)
        iqr_flag_columns.append(flag_col)
    else:
        print(f"{col} not found. Skipping IQR flag.")


### Percentile Summary ###

print("\n----- Percentile Summary -----")

percentile_fields_existing = [
    col for col in iqr_fields
    if col in sold.columns
]

percentile_summary = sold[percentile_fields_existing].describe(
    percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
)

print(percentile_summary.to_string())


### Combined Outlier Flag ###

print("\n----- Combined Outlier Flags -----")

all_flag_columns = business_rule_flags + iqr_flag_columns

sold["any_outlier_or_invalid_flag"] = sold[all_flag_columns].any(axis=1)

print(f"Total records: {len(sold)}")
print(f"Records flagged with at least one issue: {sold['any_outlier_or_invalid_flag'].sum()}")
print(f"Records not flagged: {(~sold['any_outlier_or_invalid_flag']).sum()}")


### Before Filtering Summary ###

print("\n----- Before Filtering Median Values -----")

summary_fields = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
    "price_per_sqft",
    "price_ratio",
    "close_to_original_list_ratio"
]

summary_fields_existing = [
    col for col in summary_fields
    if col in sold.columns
]

before_medians = sold[summary_fields_existing].median(numeric_only=True)

print("Median values before filtering:")
print(before_medians)


### Create Filtered Analysis Dataset ###

print("\n----- Creating Filtered Analysis Dataset -----")

sold_filtered = sold[
    sold["any_outlier_or_invalid_flag"] == False
].copy()

print(f"Rows before filtering: {sold.shape[0]}")
print(f"Rows after filtering: {sold_filtered.shape[0]}")
print(f"Rows removed from filtered analysis dataset: {sold.shape[0] - sold_filtered.shape[0]}")


### Cleaned Mean Values ###

print("\n----- Cleaned Mean Values After Filtering -----")

cleaned_means = sold_filtered[summary_fields_existing].mean(numeric_only=True)

print("Cleaned mean values after filtering:")
print(cleaned_means)


### After Filtering Summary ###

print("\n----- After Filtering Median Values -----")

after_medians = sold_filtered[summary_fields_existing].median(numeric_only=True)

print("Median values after filtering:")
print(after_medians)


### Before/After Mean and Median Comparison ###

print("\n----- Before/After Mean and Median Comparison -----")

comparison_summary = pd.DataFrame({
    "MeanBeforeFiltering": sold[summary_fields_existing].mean(numeric_only=True),
    "MeanAfterFiltering": sold_filtered[summary_fields_existing].mean(numeric_only=True),
    "MedianBeforeFiltering": sold[summary_fields_existing].median(numeric_only=True),
    "MedianAfterFiltering": sold_filtered[summary_fields_existing].median(numeric_only=True)
})

comparison_summary["MeanChange"] = (
    comparison_summary["MeanAfterFiltering"] -
    comparison_summary["MeanBeforeFiltering"]
)

comparison_summary["MedianChange"] = (
    comparison_summary["MedianAfterFiltering"] -
    comparison_summary["MedianBeforeFiltering"]
)

comparison_summary["MeanPercentChange"] = (
    comparison_summary["MeanChange"] /
    comparison_summary["MeanBeforeFiltering"]
) * 100

comparison_summary["MedianPercentChange"] = (
    comparison_summary["MedianChange"] /
    comparison_summary["MedianBeforeFiltering"]
) * 100

print(comparison_summary.to_string())


### Dataset Size Comparison ###

print("\n----- Dataset Size Comparison -----")

size_comparison = pd.DataFrame({
    "Dataset": [
        "Full flagged dataset",
        "Clean filtered dataset"
    ],
    "RowCount": [
        sold.shape[0],
        sold_filtered.shape[0]
    ],
    "ColumnCount": [
        sold.shape[1],
        sold_filtered.shape[1]
    ]
})

size_comparison["RowsRemoved"] = [
    0,
    sold.shape[0] - sold_filtered.shape[0]
]

size_comparison["PercentRowsRemoved"] = [
    0,
    ((sold.shape[0] - sold_filtered.shape[0]) / sold.shape[0]) * 100
]

print(size_comparison.to_string(index=False))


### Save Output Files ###

sold.to_csv(flagged_output_path, index=False)
sold_filtered.to_csv(filtered_output_path, index=False)

print("\n----- Final Output -----")
print("Week 7 full flagged dataset saved.")
print(f"Flagged output path: {flagged_output_path}")
print(f"Flagged dataset shape: {sold.shape}")

print("\nWeek 7 clean filtered dataset saved.")
print(f"Filtered output path: {filtered_output_path}")
print(f"Filtered dataset shape: {sold_filtered.shape}")
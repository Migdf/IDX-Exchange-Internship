Objective: Clean and validate the Week 4 sold and listings MLS datasets for analysis-ready use.

Taking the Week 3 mortgage-enriched sold and listings datasets as input, the Week 4 script applies the same cleaning process to both files using a reusable function. It loads each dataset, prints the original row and column counts, and converts key date fields, such as CloseDate, PurchaseContractDate, ListingContractDate, and ContractStatusChangeDate, into datetime format. It also converts important numeric fields, including prices, living area, lot size, bedrooms, bathrooms, DaysOnMarket, coordinates, year built, and mortgage rate, into numeric format.

The script removes redundant coordinate-fill columns when present and performs a missing value summary for every column. Instead of removing questionable records, it creates data quality flags for invalid numeric values, inconsistent date timelines, and geographic issues such as missing, zero, positive, or implausible California coordinates.

Finally, the script combines all issue flags into an any_quality_issue_flag column, prints the number of records with and without quality issues, confirms final data types, and saves the cleaned outputs as listings_week4_cleaned.csv and sold_week4_cleaned.csv for future analysis.

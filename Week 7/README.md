Objective: Identify, flag, and filter out invalid or extreme values in the Week 7 sold MLS dataset.

Taking the Week 6 feature-engineered sold dataset as input, the Week 7 script loads the data, prints the original row and column counts, and converts key numeric fields such as ClosePrice, LivingArea, DaysOnMarket, price_per_sqft, price_ratio, and close_to_original_list_ratio into numeric format. It then applies business rule checks to flag clearly invalid values, including nonpositive prices, nonpositive living area, negative DaysOnMarket, and invalid price ratio fields.

After the basic validation checks, the script uses the Interquartile Range method to identify statistical outliers in the main numeric fields. For each field, it calculates Q1, Q3, IQR, lower bound, and upper bound, then creates an outlier flag for records that fall outside the acceptable range. The script also prints percentile summaries to help review the spread of the data.

The script combines all business rule and IQR outlier flags into one any_outlier_or_invalid_flag column. It then creates a filtered analysis dataset by removing records with any invalid or outlier flag. Before and after filtering, the script compares median and mean values to show how removing extreme records changes the dataset. It also prints a dataset size comparison showing how many rows were removed and what percentage of the dataset was filtered out.

Finally, the script saves two outputs: sold_week7_flagged.csv, which keeps the full dataset with all flags added, and sold_week7_filtered.csv, which contains only the cleaned records for analysis.

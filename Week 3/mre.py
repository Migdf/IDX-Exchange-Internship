import pandas as pd
import os

input_folder = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 1 Output"
output_folder = "/Users/michael/Downloads/IDX Exchange Internship/IDX Exchange DA28 Repo/Week 3 Output"

sold_input = os.path.join(input_folder, "sold.csv")
listings_input = os.path.join(input_folder, "listings.csv")

sold_output = os.path.join(output_folder, "sold_with_mortgage_rates.csv")
listings_output = os.path.join(output_folder, "listings_with_mortgage_rates.csv")

os.makedirs(output_folder, exist_ok=True)

### Load and Fetch Data ###
sold = pd.read_csv(sold_input)
listings = pd.read_csv(listings_input)

url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=["observation_date"])
mortgage.columns = ["date", "rate_30yr_fixed"]

# Resample from weekly rates to monthly averages
mortgage["year_month"] = mortgage["date"].dt.to_period("M")
mortgage_monthly = (
    mortgage.groupby("year_month")["rate_30yr_fixed"]
    .mean()
    .reset_index()
)

### Create matching year_month key on MLS datasets ###

# Sold dataset uses CloseDate
sold["CloseDate"] = pd.to_datetime(sold["CloseDate"], errors="coerce")
sold["year_month"] = sold["CloseDate"].dt.to_period("M")

# Listings dataset uses ListingContractDate
listings["ListingContractDate"] = pd.to_datetime(
    listings["ListingContractDate"],
    errors="coerce"
)
listings["year_month"] = listings["ListingContractDate"].dt.to_period("M")

### Merge ###
sold_with_rates = sold.merge(
    mortgage_monthly,
    on="year_month",
    how="left"
)

listings_with_rates = listings.merge(
    mortgage_monthly,
    on="year_month",
    how="left"
)

### Validate the Merge ###
sold_null_rates = sold_with_rates["rate_30yr_fixed"].isnull().sum()
listings_null_rates = listings_with_rates["rate_30yr_fixed"].isnull().sum()

print("Sold rows missing mortgage rate:", sold_null_rates)
print("Listings rows missing mortgage rate:", listings_null_rates)

if sold_null_rates == 0 and listings_null_rates == 0:
    print("Validation passed: no null mortgage rate values.")
else:
    print("Validation warning: some rows are missing mortgage rates.")

# Previews
print("\nSold preview:")
print(
    sold_with_rates[
        ["CloseDate", "year_month", "ClosePrice", "rate_30yr_fixed"]
    ].head()
)

print("\nListings preview:")
print(
    listings_with_rates[
        ["ListingContractDate", "year_month", "ListPrice", "rate_30yr_fixed"]
    ].head()
)

### Save ###
# Convert year_month to string
sold_with_rates["year_month"] = sold_with_rates["year_month"].astype(str)
listings_with_rates["year_month"] = listings_with_rates["year_month"].astype(str)

sold_with_rates.to_csv(sold_output, index=False)
listings_with_rates.to_csv(listings_output, index=False)

print(f"\nSaved enriched sold dataset to: {sold_output}")
print(f"Saved enriched listings dataset to: {listings_output}")
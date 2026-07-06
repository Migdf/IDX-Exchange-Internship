import pandas as pd
import glob
import os
import re


def extract_number(file_path):
    """
    Gets the numbers from the file name
    """
    filename = os.path.basename(file_path)      # Extracts only file name from full path
    match = re.search(r"\d+", filename)         # Finds the numbers from filename using regular expressions
    return int(match.group()) if match else -1  # Returns the number using .group()


def is_filled(file_path):
    """ 
    Determines if the file name has '_filled'
    """
    filename = os.path.basename(file_path)
    return "_filled" in filename


def choose_files_prefer_filled(csv_files):
    """
    If two files have the same number, keep the _filled version
    """

    files_by_number = {}

    for file in csv_files:                                          # For every file, get the number
        number = extract_number(file)

        if number not in files_by_number:                           # If the number is not in the dictionary, add it with the number as the key
            files_by_number[number] = file
        else:
            existing_file = files_by_number[number]                 # If there is a duplicate number, extract the already processed filename

            if is_filled(file) and not is_filled(existing_file):    # If current file has _filled then replace exisiting filepath with new path
                files_by_number[number] = file

    return sorted(files_by_number.values(), key=extract_number)     # Sort dictionary in ascending order


def read_csv_clean(file):
    df = pd.read_csv(file, low_memory=False)                        # low_memory-False so column type is correct

    if is_filled(file):                                             # If the file is a _filled file, remove the two extra columns - if they don't exist just ignore
        df = df.drop(columns=["latfilled", "lonfilled"], errors="ignore")

    return df


def combine_and_filter_residential(folder_path, output_path, dataset_name):
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))           # Finds all *.csv files in selected folder

    csv_files = choose_files_prefer_filled(csv_files)                   # Filter .csv files to prefer '_filled' for duplicates

    print(f"\n{dataset_name} files that will be combined:\n")           # Print the numerically sorted .csv files that will be concatenated
    for file in csv_files:
        print(os.path.basename(file))

    dataframes = []

    # Row count before concatenation
    total_rows_before_concat = 0

    for file in csv_files:                                              # For each file in sorted dictionary turn into pandas dataframe and add to list
        df = read_csv_clean(file)
        total_rows_before_concat += len(df)
        dataframes.append(df)

    print(f"\n{dataset_name} row count before concatenation: {total_rows_before_concat}")

    # Concatenate the list and makes sure index is reset
    combined = pd.concat(dataframes, ignore_index=True)

    # Row count after concatenation
    print(f"{dataset_name} row count after concatenation: {len(combined)}")

    # Row count before Residential filter
    rows_before_filter = len(combined)
    print(f"{dataset_name} row count before Residential filter: {rows_before_filter}")

    # Filter to only keep PropertyType == Residential
    residential = combined[combined["PropertyType"] == "Residential"] # Comment out for non-filtered concatenation
    # residential = combined # Comment in for no filter

    # Row count after Residential filter
    rows_after_filter = len(residential)
    print(f"{dataset_name} row count after Residential filter: {rows_after_filter}")

    # Write to csv
    residential.to_csv(output_path, index=False)

    print(f"{dataset_name} Residential CSV saved to: {output_path}")


### Listings ###
listings_folder = "/Users/michael/Downloads/IDX Exchange Internship/CRMLSL IDX Exchange CSVs/CRMLSListing"
listings_output = "/Users/michael/Downloads/Listings_Residential.csv"

combine_and_filter_residential(
    folder_path=listings_folder,
    output_path=listings_output,
    dataset_name="Listings"
)


### Sold ###
sold_folder = "/Users/michael/Downloads/IDX Exchange Internship/CRMLSL IDX Exchange CSVs/CRMLSSold"
sold_output = "/Users/michael/Downloads/Sold_Residential.csv"

combine_and_filter_residential(
    folder_path=sold_folder,
    output_path=sold_output,
    dataset_name="Sold"
)
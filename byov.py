# Copyright 2024 David Bower, Koales Ltd
# Demonstrator project for vector search with bring-your-own vectors
# Utilising Kaggle for datasource and Weaviate for vector search
# Please report bugs, comments and ask help of the author
# Distributed under the MIT License - see LICENSE file for details

import argparse
import random
import kagglehub
import pandas as pd
import weaviate
import weaviate.classes as wvc
from weaviate.classes.query import MetadataQuery

# Constants
SCRIPT_DESCRIPTION = "Demonstrator project:  Bring-your-own vector store and seach;  Load Kaggle CSV numeric dataset into Weaviate with self-generated vectors and query with nearest vector search"

# Default values
KAGGLE_DATASET = "atharvaingle/crop-recommendation-dataset"
KAGGLE_DATA_FILE = "Crop_recommendation.csv"
DATASET_LABEL_COLUMN = "label"
WEAVIATE_COLLECTION = "CropRecommendations"

# The default dataset contains sensor readings for soil and environmental conditions
# and a recommended crop to grow based on these conditions, see
# https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset

# The default dataset is a CSV file with the following columns:
'''
N - ratio of Nitrogen content in soil
P - ratio of Phosphorous content in soil
K - ratio of Potassium content in soil
temperature - temperature in degree Celsius
humidity - relative humidity in %
ph - ph value of the soil
rainfall - rainfall in mm
label - the recommended crop to grow
'''

# Any freely-accessible Kaggle dataset stored as CSV with numeric values and a
# label column could be used directly with this script - see the command line options



def parse_cli_arguments():
    # Parse command line options
    # Display help message if --help flag is specified
    global KAGGLE_DATASET, KAGGLE_DATA_FILE, DATASET_LABEL_COLUMN, WEAVIATE_COLLECTION

    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--delete-collection", action="store_true", help="Delete Weaviate collection, if it previously exists, before loading data")
    group.add_argument("--append-collection", action="store_true", help="Append to previously existing Weaviate collection, if it already exists")

    parser.add_argument("--kaggle-dataset", type=str, default=KAGGLE_DATASET, help="Kaggle dataset name (default: %(default)s)")
    parser.add_argument("--kaggle-datafile", type=str, default=KAGGLE_DATA_FILE, help="Data filename within Kaggle dataset (default: %(default)s)")
    parser.add_argument("--dataset-label-column", type=str, default=DATASET_LABEL_COLUMN, help="Column name for label column (default: %(default)s)")

    parser.add_argument("--weaviate-collection", type=str, default=WEAVIATE_COLLECTION, help="Weaviate collection name (default: %(default)s)")

    args = parser.parse_args()

    # Update default values with command line options (will use default values if not specified))
    KAGGLE_DATASET = args.kaggle_dataset
    KAGGLE_DATA_FILE = args.kaggle_datafile
    DATASET_LABEL_COLUMN = args.dataset_label_column
    WEAVIATE_COLLECTION = args.weaviate_collection

    return args


def display_intro_message():
    # Name of this script
    script_name = "byov.py"

    # Display introduction message
    print(f"{SCRIPT_DESCRIPTION}\n")
    print(f"For command line options, run as: {script_name} --help\n")


def download_kaggle_dataset(dataset, path):
    # Download dataset from Kaggle
    print(f"Download Kaggle dataset: {dataset} file path: {path}")

    # Download latest version
    local_path = kagglehub.dataset_download(
        dataset,
        path=path
    )

    print(f"Local path to downloaded Kaggle data file: {local_path}")

    return local_path


def read_csv_to_dataframe(path):
    # Use Pandas to read CSV file into Pandas DataFrame
    print("Read CSV file into pandas DataFrame")
    print(f"CSV file path: {path}")

    df = pd.read_csv(path)
    print("")

    # Print summary information about the dataset
    print("DataFrame summary information")
    print(df.info())

    return df


def get_dataframe_value_column_names_as_list(df, label_column):
    # Generate a list of the dataframe's column names
    # Exclude the label column
    column_names = df.columns.tolist()
    column_names.remove(label_column)

    return column_names


def weaviate_connect():
    # Create a Weaviate client instance
    # Weaviate must be running locally

    print("Weaviate must be running locally")
    print("Connect to Weaviate")
    weaviate_client = weaviate.connect_to_local()

    return weaviate_client


def weaviate_close_client(weaviate_client):
    # Close Weaviate client
    print("Close Weaviate client")
    weaviate_client.close()


def weaviate_collection_exists(weaviate_client, collection_name):
    # Check if Weaviate collection exists
    print(f"Check if Weaviate collection {collection_name} exists")
    collection_exists = weaviate_client.collections.exists(collection_name)

    return collection_exists


def weaviate_delete_collection(weaviate_client, collection_name):
    # Delete a Weaviate collection
    print(f"Delete Weaviate collection {collection_name}")
    weaviate_client.collections.delete(collection_name)


def weaviate_create_collection(weaviate_client, collection_name):
    # Create Weaviate collection
    # We will provide our own vector values for each row
    # We are not using a vectoriser, so we specify none
    # The properties will be the column names and values from the dataset
    # The vector will be the values from the columns in the dataset
    print(f"Create Weaviate collection {collection_name}")
    weaviate_client.collections.create(
        name=collection_name,
        vectorizer_config=wvc.config.Configure.Vectorizer.none()
    )


def weaviate_get_collection(weaviate_client, collection_name):
    # Get the Weaviate collection object
    print(f"Get a reference for the Weaviate collection {collection_name}")
    collection = weaviate_client.collections.get(collection_name)

    return collection


def make_vector_from_dataframe_row(row, value_column_names):
    # Make a vector with values from a row taken from the source dataset
    # The vector will be the values from the columns in the dataset, excluding the label column
    vector = [row[column] for column in value_column_names]

    return vector


def weaviate_insert_dataframe(collection, df, value_column_names):
    # Loop over the pandas dataframe and add all rows to Weaviate
    # Because we are specifiyng our own vector, we must create a
    # weaviate.classes.data.DataObject object instance for each row, this enables us to
    # specify the row properties and also the vector value itself

    print("Insert Pandas dataframe into Weaviate collection")
    print("Generate Weaviate DataObject instances for each row in the dataset")
    row_objs = list()
    for index, row in df.iterrows():    # index is the row number but unused for our purposes
        # Using the column names for the dataset, create a list of values for the vector
        vector = make_vector_from_dataframe_row(row, value_column_names)

        # Create a DataObject instance for the row
        row_objs.append(wvc.data.DataObject(
            properties=row,
            vector=vector
        ))

    print("Insert all DataObject instances into Weaviate")
    collection.data.insert_many(row_objs)
    print("Dataframe inserted into Weaviate\n")


def weaviate_count_collection_objects(collection):
    # Count the number of items in a collection
    print("Count objects in Weaviate collection")
    response = collection.aggregate.over_all(
        total_count=True,
    )

    object_count = response.total_count
    return object_count


def count_dataframe_items(df):
    # Count the number of items in a Pandas DataFrame
    return len(df)


def weaviate_query_nearest_vector(collection, vector, limit=1):
    print("Query Weaviate collection with nearest vector search")
    print(f"Search vector:\n{vector}")
    response = collection.query.near_vector(
        near_vector=vector,
        limit=limit,
        return_metadata=MetadataQuery(distance=True)
    )

    return response


def get_random_vector_label_pair_from_dataframe(df, value_column_names, label_column):
    # Choose a random row from the dataframe
    row_num = random.randint(0, dataset_row_count - 1)
    row = df.iloc[row_num]

    vector = make_vector_from_dataframe_row(row, value_column_names)
    label = row[label_column]

    return vector, label


def perform_vector_search(collection, vector, label_column):
    # Query Weaviate with nearest vector search
    response = weaviate_query_nearest_vector(collection, vector)

    # Get first result, result set is limited to 1 object
    print("Get first result from response from Weaviate")
    reponse_obj = response.objects[0]

    row = reponse_obj.properties
    label = row[label_column]
    vector_distance = reponse_obj.metadata.distance

    return row, label, vector_distance


def verify_vector_search_label_matches(collection, vector, label, label_column):
    # Query Weaviate with nearest vector search for a known vector and its associated label
    row, obtained_label, vector_distance = perform_vector_search(collection, vector, label_column)    

    print(f"Expected label: {label}")
    print(f"Label obtained from Weaviate search: {obtained_label}")

    print(f"Vector distance of search vector to matched vector: {vector_distance}")

    if label == obtained_label:
        print("Expected label matches label obtained from Weaviate search")
        return True
    else:
        print("Expected label does not match label obtained from Weaviate search")
        return False
    print("")


def get_dataframe_column_ranges(df, value_column_names):
    # Calculate the range of values for each column, excluding the label column
    print("Calculate value ranges for each column in the dataset")
    
    # Make a list of vaule column names and the associated min and max values
    value_ranges = {column: {"min": df[column].min(), "max": df[column].max()} for column in value_column_names}

    print(f"Value ranges: \n{value_ranges}\n")

    return value_ranges


def generate_random_vector_from_property_ranges(value_ranges):
    # Generate a random vector from the range of values for each column
    # Respect the variable type of each column
    print("Generate a random vector using the value ranges for each column")

    random_vector = [
        random.randint(value_ranges[column]["min"], value_ranges[column]["max"]) if df[column].dtype == int 
        else random.uniform(value_ranges[column]["min"], value_ranges[column]["max"]) if df[column].dtype == float 
        else random.choice(df[column].unique()) 
        for column in value_ranges
    ]

    print(f"Random vector: \n{random_vector}\n")

    return random_vector


# Main script begins here

print("Step 1. Parse command line options")
# Parse command line options - will display help message and exit if help flag specified
args = parse_cli_arguments()
print("")


print("Step 2. Display script introduction message")
# Display script introduction message
display_intro_message()


print("Step 3. Output configuration options specified in command line parameters")
# Display configuration from command line options
print("Configuration from command line options:")

# Has delete been specified for the Weaviate collection in the command line arguments?
delete_collection = args.delete_collection
print(f"Delete Weaviate collection flag set: {delete_collection}")

# Has append to the Weaviate collection been specified in the command line arguments?
append_collection = args.append_collection
print(f"Append to Weaviate collection flag set: {append_collection}")
print("")


print("Step 4. Download the dataset from Kaggle")
# Download the Kaggle dataset
path = download_kaggle_dataset(KAGGLE_DATASET, KAGGLE_DATA_FILE)
print("")


print("Step 5. Read the CSV file into a Pandas DataFrame")
# Read the CSV file into a Pandas DataFrame
df = read_csv_to_dataframe(path)
print("")


print("Step 6. Get the column names from the dataset - we need them to specify the object properties for the Weaviate collection and to generate the vector")
# We need a list of the column names from the dataset
# These column names are used to specify the object properties when inserting into Weaviate
# and to generate the vector for each row
# We need to exclude the label column from the list of column names
value_column_names = get_dataframe_value_column_names_as_list(df, DATASET_LABEL_COLUMN)
print("")


# Perform all Weaviate operations within a try block since we need to
# close the Weaviate client at the end, regardless of whether an exception is raised
try:
    print("Step 7. Connect to Weaviate")
    weaviate_client = weaviate_connect()
    print(f"Weaviate client is ready? {weaviate_client.is_ready()}\n")  # Should print: `True`


    print("Step 8. Create Weaviate collection, delete pre-existing collection if specified")
    # Determine if we need to create the collection, or not
    # Check if collection exists, delete if it does and if flag set,
    # otherwise check if append flag set
    create_collection = True   # Assume we need to create the collection
    collection_exists = weaviate_collection_exists(weaviate_client, WEAVIATE_COLLECTION)

    if collection_exists:
        print(f"Collection {WEAVIATE_COLLECTION} exists")

        if delete_collection:
            print(f"Delete collection CLI option set")
            # Empty the collection by deleting it
            weaviate_delete_collection(weaviate_client, WEAVIATE_COLLECTION)
        else:
            if append_collection:
                print(f"Append CLI option set, retain Weaviate collection {WEAVIATE_COLLECTION}")
                create_collection = False
            else:
                raise RuntimeError(f"Collection {WEAVIATE_COLLECTION} exists, and no CLI option specified to delete it or append to it")
    else:
        print(f"Collection {WEAVIATE_COLLECTION} does not exist")
    print("")

    if create_collection:
        # Create the collection
        weaviate_create_collection(weaviate_client, WEAVIATE_COLLECTION)
    print("")


    print("Step 9. Get a reference to the Weaviate collection")
    # Get Weaviate collection object
    collection = weaviate_get_collection(weaviate_client, WEAVIATE_COLLECTION)
    print("")


    print("Step 10. Insert the Pandas DataFrame into the Weaviate collection")
    # Insert the dataset into Weaviate
    weaviate_insert_dataframe(collection, df, value_column_names)


    print("Step 11. Count the number of rows in the original dataset and Weaviate collection as a sanity check - not if append has been specified (as prev-existing rows may have been present)")
    # Count the number of rows in the original dataset and in the Weaviate collection
    dataset_row_count = count_dataframe_items(df)
    weaviate_collection_count = weaviate_count_collection_objects(collection)

    print(f"Number of rows in original dataset: {dataset_row_count}")
    print(f"Number of rows in Weaviate collection: {weaviate_collection_count}")

    # If the collection as been created from scratch, we can perform a sanity check,
    # otherwise just output row totals
    if create_collection:
        if dataset_row_count == weaviate_collection_count:
            print("Number of rows in original dataset matches number of objects in Weaviate collection")
        else:
            print("Number of rows in original dataset does not match number of objects in Weaviate collection")
    print("")


    print("Step 12. Sanity check - query Weaviate using nearest vector search with a known sample row from the dataset")
    # Sanity check - query Weaviate using a vector search with data from the
    # CSV dataset and compare returned label value with expected label value
    print("Query Weaviate with known sample row from dataset")

    # Get vector and label for a random row from the dataset
    test_vector, test_expected_label = get_random_vector_label_pair_from_dataframe(df, value_column_names, DATASET_LABEL_COLUMN)

    # Perform Weeaviate vector search and Verify that the result matches the expected label
    verify_vector_search_label_matches(collection, test_vector, test_expected_label, DATASET_LABEL_COLUMN)
    print("")


    # Test querying Weaviate by nearest vector search with a random set of values
    # to get a recommendaed label value for a test vector value

    print("Step 13. Calculate the range of values for each column in the original dataset - we need this so we can generate a random vector that has values within the range for each column")
    # Calculate the range of values for each column, excluding label
    dataset_value_ranges = get_dataframe_column_ranges(df, value_column_names)


    print("Step 14. Generate a random vector from the range of values for each column")
    # Generate a random vector from the range of values for each column
    random_vector = generate_random_vector_from_property_ranges(dataset_value_ranges)


    print("Step 15. Test query - generate a random vector and query Weaviate with nearest vector search to obtain a recommended label value")
    row, obtained_label, vector_distance = perform_vector_search(collection, random_vector, DATASET_LABEL_COLUMN)    

    print(f"Label obtained from nearest vector search from Weaviate with random vector values: {obtained_label}")
    print(f"Vector distance between random vector values and matched vector: {vector_distance}")
    print("")
except Exception as e:
    print(f"Error: {e}\n")
finally:
    print("Final Step. We always need to close the Weaviate client, otherwise there is a risk of memory leaks")
    # We always need to close the Weaviate client, otherwise there is a risk of memory leaks
    weaviate_close_client(weaviate_client)

print("")
print("Done\n")

# Bring-Your-Own-Vector Demonstration Project

## Overview

This project demonstrates a "bring-your-own vector" approach to creating, storing, and searching vectors in a vector database. It serves as a practical example of how to:
- Load a dataset from [Kaggle](https://www.kaggle.com) (an excellent platform for diverse, accessible datasets)
- Generate vectors from dataset features
- Store vectors in a vector database [Weaviate](https://weaviate.io) (a powerful open-source vector database)
- Perform nearest vector searches

**Note**: Both Kaggle and Weaviate are used as examples in this demonstrator. Developers are encouraged (and expected) to replace these with their preferred alternatives if and as required.

### Key Concepts

- **Flexible Vector Generation**: Create vectors directly from numeric dataset features
- **Vector Database Integration**: Demonstrate vector storage and search, with Weaviate but principle should extend to other vector databses
- **Extensible Approach**: Easily adaptable to different datasets and use cases

## Dataset

The project uses a crop recommendation dataset as an illustrative example. This dataset is:
- Publicly accessible
- Entirely numeric with a single textual label column
- Small enough for quick demonstration

The dataset columns are:
- soil data (e.g. pH level, etc)
- local environmental data (e.g. rainfall, etc)
- recommended crop to grow given the soil and environmental observations

**Important**: This dataset is just an example. The script is designed to work with any similar numeric CSV dataset with a label column.

## Prerequisites

- Python 3.8+
- Weaviate running locally (see [Weaviate Local Installation Docs](https://weaviate.io/developers/weaviate/quickstart/local))

## Installation

1. Open the folder containg the files in this project and create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, replace this while line just with `venv\Scripts\activate`  (i.e. no `source` part and reverse path slashes)
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Weaviate is running locally

## Usage

Run the script with default settings:
```bash
python byov.py
```

### Command Line Options

- `--delete-collection`: Delete existing Weaviate collection before loading
- `--append-collection`: Append to existing collection
- `--kaggle-dataset`: Specify a different Kaggle dataset
- `--kaggle-datafile`: Specify a different data file
- `--dataset-label-column`: Specify a different label column
- `--weaviate-collection`: Specify a different Weaviate collection name

Example:
```bash
python byov.py --kaggle-dataset your-dataset --delete-collection
```

## Warnings

**IMPORTANT**  This script is capable of deleting database collections.

Care must be exercised only to run this script in development, and only with database collections that are safe to delete - you will loose all data from collections that are deleted.

This project is a demonstrator - it should not be used on production data and all operations should be carefully considered before performing.

Data will be loaded into a database - the database collection where the data is stored is created by the script after inspecting the source dataset.

To allow the developer to re-run the script, there is a command-line option to delete the database collection (start from a blank page) before importing the new data.  Alternatively the dataset can be appended (load multiple datasets into the same collection, maybe the dataset has been chunked into separate files) to a pre-existing database collection (assuming that it already exists and has the expected confirguration).

## Workflow Demonstration

The script is split into the following numbered steps (matching with debugging statements in the code):

**Step 1 & 2: Configuration and Introduction**
- Parse command line options
- Display script introduction message

**Step 3: Configuration Output**
- Display configuration options specified in command line parameters
- Show deletion and append flags for Weaviate collection

**Step 4 & 5: Data Acquisition and Loading**
- Download the dataset from Kaggle
- Read the CSV file into a Pandas DataFrame
- Inspect and summarize dataset characteristics

**Step 6: Prepare Column Names**
- Extract column names for use in Weaviate collection
- Separate value columns from label column

**Step 7 & 8: Weaviate Collection Preparation**
- Connect to Weaviate
- Check for existing collection
- Delete or prepare collection based on command line options

**Step 9 & 10: Data Insertion**
- Get a reference to the Weaviate collection
- Insert the Pandas DataFrame into Weaviate
- Create vector representations for each row

**Step 11: Data Verification**
- Count and verify number of rows in original dataset and Weaviate collection

**Step 12: Vector Search Sanity Check**
- Perform a vector search with a known sample row
- Verify that the search returns the expected label

**Step 13 & 14: Random Vector Generation**
- Calculate value ranges for each column
- Generate a random vector using these ranges

**Step 15: Random Vector Search**
- Query Weaviate with the randomly generated vector
- Obtain a recommended label based on nearest vector search

## How to Use in Your Own Project

This script is intentionally modular. Developers are encouraged to:
- Extract individual functions for their own use
- Adapt the vector generation approach
- Replace components (e.g., data source, vector database) as needed

## Experiment and Contribute

We encourage developers to:
- Experiment with different datasets
- Try alternative vector generation techniques
- Share their modifications and results

## Limitations

As a demonstrator project, this implementation has several known limitations:

1. **Memory Constraints**
   - The entire CSV file is processed in-memory using pandas
   - Potentially problematic for very large datasets
   - Alternative approaches for large datasets might include:
     * Streaming data processing
     * Chunk-based loading
     * Using more memory-efficient data loading techniques

2. **Vector Generation**
   - Current approach uses raw numeric values directly as vectors
   - May not be optimal for all use cases
   - Lacks sophisticated feature engineering or normalization
   - All dimensions (or vector values, i.e. soil and environmental conditions in this example dataset) are considered equal.  In real life, this is unlikely to be the case, or example, a given crop may not tollerate relatively small changes in soil pH or may not survive if the amount of rainfall is too high, etc.

3. **Error Handling**
   - Basic error handling implemented
   - May require more robust error management in production scenarios

4. **Performance Considerations**
   - Designed for demonstration, not optimized for high-performance scenarios
   - Vector generation and search methods are simplistic
   - May not scale efficiently with complex or large datasets

5. **Dependency Specifics**
   - Relies on specific versions of Weaviate, Kaggle, and other libraries
   - Potential compatibility issues with future library updates

6. **Configuration Limitations**
   - Command-line options provide basic configurability
   - Advanced use cases may require more extensive configuration methods

**Note**: These limitations are intentional. As a demonstrator project, the goal is to provide a clear, understandable example that developers can easily learn from and adapt to their specific needs.

## Ask for Help

This project is a learning demonstrator, and questions are not just welcome—they're expected! 

As a demonstrative project, our goal is to help developers understand:
- Vector generation techniques
- Vector database integration
- Data processing workflows

If you:
- Are unsure about any part of the code
- Want to understand a specific implementation detail
- Have ideas for improvements
- Encounter challenges while adapting the script

Please don't hesitate to reach out! This project is a learning tool, and your questions help improve it for the entire community.

## License

Distributed under the MIT License. See LICENSE file for details.

## Contact

For bugs, comments, or contributions, please contact the original author.

Copyright 2024 David Bower, Koales Ltd

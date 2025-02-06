# Remove Host Tags Script

This script is designed to remove tags from hosts using a CSV file and credentials provided by the user. The script reads the credentials and CSV file, retrieves the tags for each host, and removes the specified tags.

![2025-02-06 12 21 29](https://github.com/user-attachments/assets/bbfe49ab-e057-4485-9640-3a66bc00c966)


## Prerequisites

- Python 3.x
- Required Python packages:
  - `argparse`
  - `colorama`
  - `requests`
  - `pandas`
  - `jwt`

You can install the required packages using the following command:

```sh
pip install argparse colorama requests pandas pyjwt
```

## Usage

To run the script, use the following command:

```sh
python remove_host_tags.py -creds_file <path_to_credentials_file> -csv_file <path_to_csv_file>
```

### Arguments

- `-creds_file` or `--credentials_file`: Path to the credentials file (required).
- `-csv_file` or `--csv_file`: Path to the CSV file containing columns `asset_id` and `tag_name` (required).

### Example

```sh
python remove_host_tags.py -creds_file credentials.json -csv_file tags.csv
```

## Credential File Format (JSON)

Credential file should contain following values:

- `customerId`: The unique ID of the uptycs tenant
- `key`: API KEY
- `secret`: API SECRET
- `domain`: domain name of uptycs tenant
- `domainSuffix`: domainSuffix of the uptycs tenant (eg: uptycs.io)

Example JSON File:

```json
{
  "id": "90ec4f1a-e764-4f90-b3b8-cbf0ee295fd9",
  "userId": "751c8192-e99e-442b-ba80-9ee5bc28a9d5",
  "customerId": "049dad7d-94fc-4d78-9740-f98d81e0a3f1",
  "active": true,
  "isInternal": false,
  "key": "HRYDDCKMJCEI6OLZLBMNBJH7L0XIAFCI",
  "secret": "pyi60bcqgMKsLsf78Ko0tR9TRON9/qclZJyzg3kK7+dHO4M53b+I88DNSyN/V2Gf",
  "expiry": null,
  "updatedAt": "2024-08-28T17:05:24.312Z",
  "createdAt": "2024-08-28T17:05:24.312Z",
  "domainSuffix": ".uptycs.io",
  "domain": "sparrow"
}
```

## CSV File Format

The CSV file should contain the following columns:

- `asset_id`: The ID of the asset.
- `tag_name`: The name of the tag to be removed.

Example CSV file:

```csv
asset_id,tag_name
7bd784f7-0d2b-4e48-b79b-9e8674218625,tag1
1a1557fc-6134-450d-b309-416734b70a80,tag1
1a1557fc-6134-450d-b309-416734b70a80,tag2
```

## Script Details

### Functions

- `new_line()`: Prints a new line.
- `wait_a_second()`: Pauses the script for 1 second.
- `parse_args()`: Parses command-line arguments.
- `get_full_path(file_path)`: Returns the full path of the given file.
- `read_csv_file(file_path)`: Reads the CSV file and returns a dictionary of asset_id and tags to be removed from that asset.
- `read_credentials(file_path, expiry)`: Reads the credentials file and generates an bearer authorization token.
- `get_base_url(credentials)`: Constructs the base URL using the credentials.
- `get_tags(credentials, asset_id)`: Retrieves the tags for the given asset ID.
- `update_tags(credentials, new_tags, asset_id)`: Updates (removes) the tags for the given asset ID.
- `showError(data)`: Displays error context if the user opts to see more details.
- `remove_tags(credentials, host_tag_dict)`: Removes the specified tags from the hosts.
- `main()`: Main function that orchestrates the script execution.

### Main Execution Flow

1. Parse command-line arguments.
2. Get the full paths of the credentials and CSV files.
3. Read the credentials and CSV file.
4. Retrieve and remove the specified tags from the hosts.

## License

This project is licensed under the MIT License.

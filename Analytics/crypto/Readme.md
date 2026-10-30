# Gate.io Data Processing Toolkit

This toolkit consists of three scripts designed to download, process, and parse cryptocurrency trading data from Gate.io. The toolkit includes two Bash scripts for data downloading and processing control, and one Python script for data parsing and transformation.

## Scripts Overview

1. **Download Script (Bash)**: Downloads trading data from Gate.io for specified date ranges and market parameters.
2. **Processing Script (Bash)**: Runs the Python script to process the downloaded data, taking input and output paths as arguments.
3. **Parser Script (Python)**: Parses the downloaded data, processes it according to specific rules, and outputs the transformed data.

## Requirements

- Python 3
- Bash Shell
- Python libraries: pandas, numpy
- Internet connection for downloading data

## Setup

1. **Python Environment**: Ensure Python 3 is installed on your system. Optionally, set up a virtual environment and install required Python libraries (`pandas`, `numpy`).

   ```bash
   pip install pandas numpy
```

2. **Script Files**: Place all three script files (`download_data.sh`, `process_data.sh`, and `gateio_data_parser.py`) in the same directory.

## Usage

### 1. Downloading Data

The download script fetches trading data from Gate.io. Customize the download parameters as needed.

#### Parameters:

- **Start date (`start_date`)**: Start date of the range in `YYYY-MM-DD` format.
- **End date (`end_date`)**: End date of the range in `YYYY-MM-DD` format.
- **Business type (`biz`)**: Type of business data to download, e.g., `spot`.
- **Types (`types`)**: Types of data to download, e.g., `orderbooks`.
- **Market (`market`)**: Market identifier, e.g., `BTC_USDT`.
- **Merge control (`no-merge`)**: If provided, disables merging of hourly files into daily files.

#### Usage:

```bash
gateio_l2_data_script.sh [start_date] [end_date] [biz] [types] [market] [no-merge]
```
```bash
gateio_l2_data_script.sh 2022-01-01 2022-01-31 spot orderbooks BTC_USDT
```
### 2. Processing and Data parsing

The bash script `gateio_l2_data_parser.sh` runs the Python script `gateio_l2_data_parser.py` to process the downloaded data.

#### Parameters:

- `--input_path`: Path to the input directory containing downloaded data.
- `--output_path`: Path to the output directory for processed data.

#### Usage:

```bash
gateio_l2_data_parser.sh --input_path "path/to/input" --output_path "path/to/output"
```
```bash 
gateio_l2_data_parser.sh --input_path "downloaded_files" --output_path "processed_files"
```
## Additional Information

- Ensure all scripts are executable. Use `chmod +x script_name.sh` for Bash scripts. For example:
- The Python script should be in the same directory as the Bash scripts, or modify the Bash script to include the correct path to the Python script.
- For detailed information on each script, refer to the script's internal documentation or help command. Each bash script has help command and python script has a docstring expalining how each function works.





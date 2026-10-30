#!/bin/bash

# Variable for the historical quotes URL
hist="https://www.gate.io/developer/historical_quotes"

# Default behavior is to merge files
merge_files=1

# Function to display help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Download data files for a given date range and market parameters."
    echo
    echo "Options:"
    echo "  --start_date=DATE   Start date of the range in YYYY-MM-DD format (default: 2022-01-01)"
    echo "  --end_date=DATE     End date of the range in YYYY-MM-DD format (default: 2022-12-31)"
    echo "  --biz=BIZ           Business type (default: spot)"
    echo "  --types=TYPES       Types of data to download (default: orderbooks)"
    echo "  --market=MARKET     Market identifier (default: BTC_USDT)"
    echo "  --no-merge          If provided, disables merging of hourly files into daily files."
    echo "  --help, -h          Show this help message and exit"
    echo
    echo "For more information on the possible markets for different business types, please visit:"
    echo "$hist"
}

# Check for -h or --help
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  show_help
  exit 0
fi

# Initialize default values
start_date="2022-01-01"
end_date="2022-12-31"
biz="spot"
types="orderbooks"
market="BTC_USDT"
merge_files=1  # Default behavior is to merge files

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --start_date=*)
            start_date="${1#*=}"
            shift
            ;;
        --end_date=*)
            end_date="${1#*=}"
            shift
            ;;
        --biz=*)
            biz="${1#*=}"
            shift
            ;;
        --types=*)
            types="${1#*=}"
            shift
            ;;
        --market=*)
            market="${1#*=}"
            shift
            ;;
        --no-merge)
            merge_files=0
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Disable merging if the last argument is 'no-merge'
if [ "$merge_option" == "no-merge" ]; then
  merge_files=0
fi

hours=($(printf "%02d " {0..23}))

# Base directory for downloaded files
base_directory="./downloaded_files"

# Check if the "downloaded_files" directory exists and create it if not
if [ ! -d "$base_directory" ]; then
  mkdir "$base_directory"
fi

# Specify the base URL
base_url="https://download.gatedata.org/${biz}/${types}/"

# Finding total number of cores
total_cores=$(nproc)
max_processes=$((total_cores - 4))

# Ensure max_processes is at least 1
max_processes=$((max_processes > 1 ? max_processes : 1))

# Use max_processes for both downloading and merging processes
max_concurrent_downloads=$max_processes
max_concurrent_merges=$max_processes

# Loop through the range of dates
current_date="$start_date"
while [ "$(date -d "$current_date" '+%Y%m%d')" -le "$(date -d "$end_date" '+%Y%m%d')" ]; do
    year=$(date -d "$current_date" '+%Y')
    month=$(date -d "$current_date" '+%m')
    day=$(date -d "$current_date" '+%d')
    
    # Correctly define year_dir and month_dir
    year_dir="${base_directory}/${market}/${year}"
    month_dir="${base_directory}/${market}/${year}/${month}"

    # Output file for the merged data
    daily_output_file="${month_dir}/${market}-${year}${month}${day}.csv.gz"

    # Check if the daily merged file already exists
    if [ -f "$daily_output_file" ]; then
        echo "Daily file for ${year}-${month}-${day} already exists. Skipping download."
    else
        # Create year and month directories if they don't exist
        if [ ! -d "$year_dir" ]; then
            mkdir -p "$year_dir"
        fi
        if [ ! -d "$month_dir" ]; then
            mkdir -p "$month_dir"
        fi

	  # Function for downloading and processing a file
	download_and_process() {
	    local url="$1"
	    local output_file="$2"

	    curl -o "$output_file" "$url"
	    local status=$?

	    if [ $status -eq 0 ]; then
		echo "Downloaded: $url"

		# Check if the downloaded file is not in .csv.gz format
		if [[ "$output_file" != *.csv.gz ]]; then
		    echo "Converting $output_file to .csv.gz format"
		    gzip "$output_file"
		    mv "$output_file.gz" "${output_file%.*}.csv.gz"
		fi
	    else
		echo "Failed to download: $url"
	    fi
	}

	#current number of downloads
	current_downloads=0

	for hour in "${hours[@]}"; do
	    url="${base_url}${year}${month}/${market}-${year}${month}${day}${hour}.csv.gz"
	    output_file="${month_dir}/${market}-${year}${month}${day}${hour}.csv.gz"

	    # Call the download function in the background
	    download_and_process "$url" "$output_file" &
	    ((current_downloads++))

	    # Check if the number of current downloads reached the maximum
	    if [[ $current_downloads -ge $max_concurrent_downloads ]]; then
		wait # Wait for all background processes to finish
		current_downloads=0
	    fi
	done

	# Wait for the last batch of downloads to finish
	wait
    fi

    # Increment the current_date by one day
    current_date=$(date -d "$current_date + 1 day" '+%Y-%m-%d')
done
# Function for merging files for a specific day
merge_files_for_day() {
    local year=$1
    local month=$2
    local day=$3
    local day_dir=$4
    local output_file=$5
    
    # Check if the daily merged file already exists
    if [ -f "$output_file" ]; then
        echo "Merged file for ${year}-${month}-${day} already exists. Skipping merge."
    else
        # Find and concatenate all files for the day, then gzip the result
        find "$day_dir" -name "${market}-${year}${month}${day}*.csv.gz" -exec gzip -dc {} + | gzip > "$output_file.tmp"
	mv -fv "$output_file.tmp" "$output_file"
	#zcat ${day_dir}/${market}-${year}${month}${day}*.csv.gz > $output_file
	#gzip $output_file

        # Delete the hourly files after merging
        find ${day_dir} -type f -name "${market}-${year}${month}${day}*.csv.gz" ! -name "${market}-${year}${month}${day}.csv.gz" -exec rm {} \;
        
    fi
}

merge_daily_files() {
  local start_date=$1
  local end_date=$2

  local current_date="$start_date"
  local current_merges=0

  while [ "$(date -d "$current_date" '+%Y%m%d')" -le "$(date -d "$end_date" '+%Y%m%d')" ]; do
    year=$(date -d "$current_date" '+%Y')
    month=$(date -d "$current_date" '+%m')
    day=$(date -d "$current_date" '+%d')

    local day_dir="${base_directory}/${market}/${year}/${month}"
    local output_file="${day_dir}/${market}-${year}${month}${day}.csv.gz"

    # Call the merge function in the background
    merge_files_for_day "$year" "$month" "$day" "$day_dir" "$output_file" &
    ((current_merges++))

    # Check if the number of current merges reached the maximum
    if [[ $current_merges -ge $max_concurrent_merges ]]; then
        wait # Wait for all background processes to finish
        echo $current_merges
        current_merges=0
    fi

    # Increment the current_date by one day
    current_date=$(date -d "$current_date + 1 day" '+%Y-%m-%d')
  done

  # Wait for the last batch of merges to finish
  wait
}

# Call the merge function if merging is enabled
if [[ $merge_files -eq 1 ]]; then
  merge_daily_files "$start_date" "$end_date"
fi




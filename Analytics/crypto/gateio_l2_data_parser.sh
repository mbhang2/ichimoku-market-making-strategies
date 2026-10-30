#!/bin/bash

# Initialize variables
input_path=""
output_path=""
symbol=""
parallel=""

# Function to display help message
show_help() {
    echo "Usage: $0 --input_path [path] --output_path [path] [--symbol [symbol]] [--parallel [parallel]]"
    echo ""
    echo "Options:"
    echo "  --input_path    Specify the input directory path"
    echo "  --output_path   Specify the output directory path"
    echo "  --symbol        Specify the trading pair symbol (e.g. BTC_USDT)"
    echo "  --parallel      Specify whether to run scripts in parallel"
    echo "  --help          Display this help message"
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --input_path)
            input_path="$2"
            shift # past argument
            shift # past value
            ;;
        --output_path)
            output_path="$2"
            shift # past argument
            shift # past value
            ;;
        --symbol)
            symbol="$2"
            shift # past argument
            shift # past value
            ;;
        --parallel)
            parallel="$2"
            shift # past argument
            shift # past value
            ;;
        --help)
            show_help
            exit 0
            ;;
        *) # unknown option
            show_help
            exit 1
            ;;
    esac
done

# Check if input_path and output_path are provided
if [ -z "$input_path" ] || [ -z "$output_path" ]; then
    echo "Error: input_path and output_path are required."
    show_help
    exit 1
fi

# Construct the command to execute the Python script
command="python gateio_l2_data_parser.py --input_path \"$input_path\" --output_path \"$output_path\""

# Add optional arguments if provided
if [ -n "$symbol" ]; then
    command+=" --symbol \"$symbol\""
fi
if [ -n "$parallel" ]; then
    command+=" --parallel \"$parallel\""
fi

# Execute the Python script with the provided paths and optional arguments
eval $command


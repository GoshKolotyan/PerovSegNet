#!/bin/bash

output_dir="predictions"

while getopts "o:" opt; do
    case $opt in
        o)
            output_dir=$OPTARG
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            exit 1
            ;;
    esac
done

streamlit run app/main.py #-- --output_dir "$output_dir"
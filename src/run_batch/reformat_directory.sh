#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <source_base_directory>"
    exit 1
fi

SOURCE_BASE="$1"
DEST_DIR="$SOURCE_BASE"

# Ensure destination directory exists
if [ ! -d "$DEST_DIR" ]; then
    mkdir -p "$DEST_DIR"
    echo "Created destination directory: $DEST_DIR"
fi

# Find and move all subfolders under the source base directory to the destination
find "$SOURCE_BASE" -mindepth 2 -type d -exec mv {} "$DEST_DIR" \;

echo "All subfolders moved to $DEST_DIR."

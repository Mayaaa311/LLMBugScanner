#!/bin/bash

SOURCE_BASE="/home/hice1/yyuan394/scratch/LLMBugScanner/run2_cleaned"
DEST_DIR="/home/hice1/yyuan394/scratch/LLMBugScanner/run2_cleaned"

# Ensure destination directory exists
if [ ! -d "$DEST_DIR" ]; then
    mkdir -p "$DEST_DIR"
    echo "Created destination directory: $DEST_DIR"
fi

# Find and move all subfolders under the source base directory to the destination
find "$SOURCE_BASE" -mindepth 2 -type d -exec mv {} "$DEST_DIR" \;

echo "All subfolders moved to $DEST_DIR."

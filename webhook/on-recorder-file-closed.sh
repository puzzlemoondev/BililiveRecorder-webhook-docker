#!/bin/sh

record_dir=$(echo "$1" | awk -F/ '{print $1}')
echo "new record: $1"
echo "record directory: $record_dir"

uid=$(baidupcs-go who | cut -d ',' -f 1 | grep -oE '[0-9]+')
if [ "$uid" = 0 ]; then
    echo "not logged in to baidupcs. attempting login..."
    baidupcs-go login -bduss="$BAIDUPCS_BDUSS" -stoken="$BAIDUPCS_STOKEN"
fi

echo "uploading directory $record_dir"
baidupcs-go upload "$record_dir" "$record_dir" && rm -rf "$record_dir"
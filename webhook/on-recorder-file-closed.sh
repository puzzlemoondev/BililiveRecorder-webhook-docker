#!/bin/sh

record_file=$(echo "$1" | jq -r ".EventData.RelativePath")
record_dir=$(dirname "$record_file")
echo "new record: $record_file"

event_json_file="${record_file%.*}.json"
echo "writing event to file $event_json_file"
echo "$1" | jq > "$event_json_file"

uid=$(baidupcs-go who | cut -d ',' -f 1 | grep -oE '[0-9]+')
if [ "$uid" = 0 ]; then
    echo "not logged in to baidupcs. attempting login..."
    baidupcs-go login -bduss="$BAIDUPCS_BDUSS" -stoken="$BAIDUPCS_STOKEN"
fi

echo "uploading directory $record_dir"
baidupcs-go upload "$record_dir" / && rm -rf "$record_dir"
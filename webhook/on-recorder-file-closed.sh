#!/bin/sh

set -eu

record_file=$(echo "$1" | jq -r ".EventData.RelativePath")
record_dir=$(dirname "$record_file")
echo "new record: $record_file"

event_json_file="${record_file%.*}.json"
echo "writing event to file $event_json_file"
echo "$1" | jq > "$event_json_file"

upload_baidupcs() {
    if [ ! "${BAIDUPCS_BDUSS+1}" ] || [ ! "${BAIDUPCS_STOKEN+1}" ]; then
        exit
    fi

    loglist_length=$(baidupcs-go loglist | grep . | wc -l)
    if [ "$loglist_length" -le 1 ]; then
        echo "baidupcs not logged in. attempting login..."
        baidupcs-go login -bduss="$BAIDUPCS_BDUSS" -stoken="$BAIDUPCS_STOKEN"
    fi

    echo "baidupcs uploading directory $record_dir"
    baidupcs-go upload "$record_dir" /
}

upload_aliyunpan() {
    if [ ! "${ALIYUNPAN_RTOKEN+1}" ]; then
        exit
    fi

    loglist_length=$(aliyunpan loglist | grep . | wc -l)
    if [ "$loglist_length" -le 1 ]; then
        echo "aliyunpan not logged in. attempting login..."
        aliyunpan login -RefreshToken="$ALIYUNPAN_RTOKEN"
    fi

    echo "aliyunpan uploading directory $record_dir"
    aliyunpan upload "$record_dir" / 
}

upload_baidupcs &
pid_baidupcs=$!

upload_aliyunpan &
pid_aliyunpan=$!

wait $pid_baidupcs $pid_aliyunpan

rm -rf "$record_dir"
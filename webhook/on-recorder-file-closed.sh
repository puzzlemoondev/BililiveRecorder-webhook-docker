#!/bin/sh

record_file=$(echo "$1" | jq -r ".EventData.RelativePath")
record_dir=$(dirname "$record_file")
echo "new record: $record_file"

event_json_file="${record_file%.*}.json"
echo "writing event to file $event_json_file"
echo "$1" | jq > "$event_json_file"

has_baidupcs=false
if [ -n "$BAIDUPCS_BDUSS" ] && [ -n "$BAIDUPCS_STOKEN" ]; then
    has_baidupcs=true
fi

has_aliyunpan=false
if [ -n "$ALIYUNPAN_RTOKEN" ]; then
    has_aliyunpan=true
fi

contain_records() {
    output=true
    find "$record_dir" -type f \( -iname \*.flv -o -iname \*.json \) -mindepth 1 -printf '%P\n' > tmp
    while IFS= read -r file; do
        if [ -n "${1##*"$file"*}" ]; then
            output=false
            break
        fi
    done < tmp
    rm tmp
    echo "$output"
}

upload_baidupcs() {
    if [ "$has_baidupcs" = false ]; then
        exit
    fi

    loglist_length=$(baidupcs-go loglist | grep -c .)
    if [ "$loglist_length" -le 1 ]; then
        echo "baidupcs not logged in. attempting login..."
        baidupcs-go login -bduss="$BAIDUPCS_BDUSS" -stoken="$BAIDUPCS_STOKEN"
    fi

    echo "baidupcs uploading directory $record_dir"
    baidupcs-go upload "$record_dir" /
}

upload_aliyunpan() {
    if [ "$has_aliyunpan" = false ]; then
        exit
    fi

    loglist_length=$(aliyunpan loglist | grep -c .)
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

is_baidupcs_completed=true
if [ "$has_baidupcs" = true ]; then
    baidupcs_content=$(baidupcs-go ls "$record_dir")
    is_baidupcs_completed=$(contain_records "$baidupcs_content")
fi

is_aliyunpan_completed=true
if [ "$has_aliyunpan" = true ]; then
    aliyunpan_content=$(aliyunpan ls "$record_dir")
    is_aliyunpan_completed=$(contain_records "$aliyunpan_content")
fi

if [ "$is_baidupcs_completed" = true ] && [ "$is_aliyunpan_completed" = true ]; then 
    echo "directory uploaded. removing local..."
    rm -rf "$record_dir"
fi
#!/bin/bash
input="/storage/emulated/0/Download/YT Music/temp.txt"
while IFS= read -r line || [[ -n "$line" ]]; do
    str="a"
	newname="$line$str"
	mv "$line" "$newname"
	echo "Text read from file: $line"
done < "$input"

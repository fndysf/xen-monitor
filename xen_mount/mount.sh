#!/bin/sh
if [ $# != 2 ];then
    echo "usage : mount.sh img dir"
    exit 1;
fi
kpartx -av "$1"
cnt=1
for f in /dev/mapper/loop*;do
    mkdir "$2"/$cnt 1>/dev/null 2>&1
    mount $f "$2"/$cnt 1>/dev/null 2>&1
    cnt=$((cnt+1))
done

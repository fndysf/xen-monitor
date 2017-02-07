#!/bin/sh
if [ $# != 2 ];then
    echo "usage : mount.sh img dir"
    exit 1;
fi
cnt=1
for f in /dev/mapper/loop*;do
    umount "$2"/$cnt 1>/dev/null 2>&1
    cnt=$((cnt+1))
done
for f in "$2"/*;do
    rm -r $f
done
kpartx -dv "$1"

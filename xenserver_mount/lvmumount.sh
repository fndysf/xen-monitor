#! /bin/sh

# STEPS:
# 1. Unmount the logical volume
# 2. Deactivate the volume group
# 3. Remove the device mapping
# 4. Unplug and destroy the VBD

help () {
	echo "./unmount [vm-name] [mount-path]\n"
}

# check for user is root
if [ $UID -ne 0 ]; then
	echo "You need to login in as root"
	exit 1
fi

# check for "xe" tool
xe_tool_path=`which xe`
if [ "$?" -ne 0 ]; then
	echo "xapi-xe not found!"
	exit 1
fi

# check for parameters
if [ "$#" -ne 2 ]; then
	help
	exit 1
fi

# check for file "new_vbd_uuid"
if [ ! -f new_vbd_uuid ]; then
	echo "file new_vbd_uuid not existed!"
	exit 1
fi

vm_name=$1
mount_dir=$2


# 1
umount ${mount_dir}

# 2
vm_vdis=`xe vbd-list vm-name-label="${vm_name}" params=vdi-uuid --minimal`
vm_arr=(${vm_vdis//,/ })

if [ ${#vm_arr[@]} -eq 0 ]; then
	echo "${vm_name} not exist!"
	exit 1
fi
cnt=${#vm_arr[@]}
cnt=$((cnt-1))
vm_vdi=${vm_arr[$cnt]}

volumn_name=`pvscan | grep $vm_vdi | awk '{print $4}'`
vgchange -an ${volumn_name}

# 3
vbd_device=`xe vbd-list | grep device | grep $vm_vdi | head -1 | awk '{print $4}'`
vbd_device_path="/dev/"${vbd_device}
kpartx -d ${vbd_device_path}

#4
vbd_uuid=`cat new_vbd_uuid`
xe vbd-unplug uuid=${vbd_uuid}
xe vbd-destroy uuid=${vbd_uuid}


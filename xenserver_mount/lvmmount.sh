#!/bin/sh

# STEPS:
# 1. Find VDI of the VM
# 2. Find UUID of Dom0
# 3. Create a VBD for the VDI and Dom0, plug the VBD
# 4. Using kpartx to add device mapping
# 5. Using vgchange to active the volume
# 6. Mount the logical volume

help () {
	echo "./mount [vm-name] [mount-path]\n"
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

vm_name=$1
mount_dir=$2

# 1
vm_vdis=`xe vbd-list vm-name-label="${vm_name}" params=vdi-uuid --minimal`
#echo vm_vdis: $vm_vdis
vm_arr=(${vm_vdis//,/ })

if [ ${#vm_arr[@]} -eq 0 ]; then
	echo "${vm_name} not exist!"
	exit 1
fi
cnt=${#vm_arr[@]}
cnt=$((cnt-1))
#echo $cnt 
vm_vdi=${vm_arr[$cnt]}
#echo vm_vdi: $vm_vdi
# 2
dom0_uuid=`xe vm-list | grep -B 1 -e Control | grep uuid | awk '{print $5}'`
#echo dom0_uuid: $dom0_uuid
# 3
vbd_uuid=`xe vbd-create vm-uuid=$dom0_uuid vdi-uuid=$vm_vdi device=autodetect`
#echo vbd_uuid : $vbd_uuid
if [ $? -ne 0 ]; then
	echo "xe vbd-create failed!"
	exit 1
fi
xe vbd-plug uuid=$vbd_uuid
echo "$vbd_uuid" > new_vbd_uuid

# 4
#echo start
vbd_device=`xe vbd-list | grep device | grep $vm_vdi`
#echo vbd_device : $vbd_device
vbd_device=`xe vbd-list | grep device | grep $vm_vdi | head -1 | awk '{print $4}'`
vbd_device_path="/dev/"${vbd_device}
#echo vbd_device : $vbd_device   vbd_path: $vbd_device_path
kpartx -av ${vbd_device_path} 
# 5
volumn_name=`pvscan | grep $vm_vdi | awk '{print $4}'`
#echo volumn_name: $volumn_name
vgchange -ay ${volumn_name}

# 6
if [ ! -d "${mount_dir}" ]; then
	mkdir "${mount_dir}"
fi
echo mount /dev/${volumn_name}/root "$mount_dir"
mount /dev/${volumn_name}/root "$mount_dir"

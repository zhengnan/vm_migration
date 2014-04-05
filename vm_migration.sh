#!/bin/bash

vm_num=`virsh list | grep -c '[0-9]'`
if [[ -z $vm_num ]]; then
	echo "Failed to get vm number!"
else
	echo "There are $vm_num vms!"
fi

echo "==========Now we start migration========== "
sleep 2
for((i=3;i<=$[$vm_num+2];i++));do
	vm_name=`virsh list | awk 'NR=='$i' {print $2}'`
	if [[ -z $vm_name ]]; then
		echo "Failed to get NO.$[$i-2]'s name!"
	else
		if [[ `echo $vm_name | grep -e i-[0-9]-[0-9]-VM` ]]; then
			s_file=`virsh dumpxml $vm_name | awk -F"'" '/source file/ {print $2}' | awk 'NR==1'`
			b_file=`qemu-img info $s_file | awk -F' ' '/backing file/ {print $3}'`
			if [[ -z $b_file ]]; then
				echo "NO.$[$i-2] vm is ISO vm!"
			else
				echo $s_file
				echo $b_file
				success=$[$success+1]
			fi
		elif [[ `echo $vm_name | grep -e [a-z]-[0-9]-VM` ]]; then
			echo "NO.$[$i-2] vm is ssvm!"
		else
			echo "NO.$[$i-2] vm is openstack's vm!"
		fi
	fi
done
echo "Succeed to migrate $success vms!"
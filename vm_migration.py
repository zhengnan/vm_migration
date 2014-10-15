#!/usr/bin/env python
import os
import os.path
import time
import commands
import shutil

before='source ./OPENRC && '
command='virsh list | awk \'NR>2 {print $2}\''
status, output=commands.getstatusoutput(command)

class GetSourceMap():
        def __init__(self, str):
                self.vm_list=str.split()
                self.vm_map={}

        def get_source_map(self):
                for vm in self.vm_list:
                        self.vm_map[vm]=[]
                        find_source='virsh dumpxml '+vm+'|awk -F"\'" \'/source file/ {print $2}\'|awk \'NR==1\''
                        s_status, s_file=commands.getstatusoutput(find_source)
                        find_backing='qemu-img info '+s_file+'|awk \'/backing file/ {print $3}\''
                        b_status, b_file=commands.getstatusoutput(find_backing)
                        self.vm_map[vm].append(s_file)
                        self.vm_map[vm].append(b_file)
                return self.vm_map

class StartMachine():
        def __init__(self, map):
                self.source_map=map
                self.base_file_map={}

        def start_base_machine(self):
                map_add_instance=self.create_base_img()
                count=0
                for vm in map_add_instance:
                        start_base_vm=before+'nova boot --flavor m1.tiny --image '+map_add_instance[vm][2]+' --nic net-id=5c9d3ae0-192f-4773-bcb1-88b3e94a4235 --security-group default --key-name demo-key '+'CloudStack_migration'+str(count)
                        print start_base_vm
                        start_base_vm_status, start_base_vm_output=commands.getstatusoutput(start_base_vm)
                        print start_base_vm_status
                        print map_add_instance
                        find_vm_openstack=before+'nova show CloudStack_migration'+str(count)+'|grep OS-EXT-SRV-ATTR:instance_name|awk \'{print $4}\''
                        find_vm_openstack_status, find_vm_openstack_output=commands.getstatusoutput(find_vm_openstack)
                        map_add_instance[vm].append('CloudStack_migration'+str(count))
                        map_add_instance[vm].append(find_vm_openstack_output)
                        print map_add_instance
                        time.sleep(60)
                        temp_container=self.get_src_back_file(map_add_instance[vm][4])
                        map_add_instance[vm].append(temp_container)
                        print map_add_instance
                        

        def get_network_id(self):
                pass

        def get_sec_grp(self):
                pass

        def get_src_back_file(self, instance):
                res=[]
                find_source='virsh dumpxml '+instance+'|awk -F"\'" \'/source file/ {print $2}\'|awk \'NR==1\''
                s_status, s_file=commands.getstatusoutput(find_source)
                find_back='qemu-img info '+s_file+'|awk \'/backing file/ {print $3}\''
                b_status, b_file=commands.getstatusoutput(find_back)
                res.append(s_file)
                res.append(b_file)
                return res

        def create_base_img(self):
                map_add_img=self.source_map
                count=0
                for vm in self.source_map:
                        index=self.source_map[vm][1]
                        if  index not in self.base_file_map.keys():
                                create_img=before+'glance image-create --name "mytest"'+str(count)+' --disk-format qcow2 --container-format bare --is-public True --progress < '+index
                                img_status, img_output=commands.getstatusoutput(create_img)
                                if img_status==0:
                                        map_add_img[vm].append('mytest'+str(count))
                                        self.base_file_map[index]='mytest'+str(count)
                                        count=count+1
                                else:
                                        print "ERROR!!!"+img_status
                        else:
                                map_add_img[vm].append(self.base_file_map[index])
                return map_add_img
				
	def change_backing_file(self, src_file, openstack_bac_file):
		rebase_str='qemu-img rebase -u '+src_file+' -b '+openstack_bac_file
		rebase_status, rebase_output=commands.getstatusoutput(rebase_str)
		if rebase_status != 0:
			print "ERROR!!!"
				
	def change_openstack_disk(self, openstack_disk, src_file):
		cp_dest=openstack_disk[:-4]
		cp_name='disk'
		after_cp_src=cp_dest+src_file.split('/')[-1]
		if os.path.exists(openstack_disk):
			os.remove(openstack_disk)
			shutil.copy(src_file, cp_dest)
			if os.path.exists(after_cp_src):
				os.rename(after_cp_src, openstack_disk)
			else:
				print "ERROR!!!"
						
		else:
			print "ERROR!!!"
                        

if __name__=='__main__':
        example=GetSourceMap(output)
        temp=example.get_source_map()
        test=StartMachine(temp)
        test.start_base_machine()

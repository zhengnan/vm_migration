#!/usr/bin/env python
import os
import commands

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
                map_add_instance=create_base_img()
                count=0
                for vm in map_add_instance:
                        start_base_vm=before+'nova boot --flavor m1.tiny --image '+map_add_instance[vm][2]' --nic net-id=5c9d3ae0-192f-4773-bcb1-88b3e94a4235 --security-group default --key-name demo-key '+'CloudStack_migration'+count
                        

        def get_network_id(self):
                pass

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
                print self.base_file_map
                return map_add_img
                        

if __name__=='__main__':
        example=GetSourceMap(output)
        temp=example.get_source_map()
        test=StartMachine(temp)
        s=test.create_base_img()
        print s

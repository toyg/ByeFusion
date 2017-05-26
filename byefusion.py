#!/usr/bin/python3

import sys
import hashlib

from pathlib import Path
from subprocess import Popen, PIPE, STDOUT
from xml.dom import minidom
from shutil import copy2
from time import sleep


OVFTOOL="/Applications/VMware Fusion.app/Contents/Library/VMware OVF Tool/ovftool"
def fix_scsi(ovf_file_path):
        # first, let's backup the original file...
        f = Path(ovf_file_path)
        copy2(f, f.with_suffix(".ovf.BACKUP"))
        # ok let's work
        ovf_dom = None
        with open(f, "r", encoding="utf-8") as fo:
            ovf_dom = minidom.parse(fo)
        items = ovf_dom.getElementsByTagName('Item')
        # first remove scsi controllers and find ide controller
        purged = []
        ides = {}
        for item in items:
            # resource type is compulsory
            resType = item.getElementsByTagName('rasd:ResourceType')[0].firstChild.nodeValue
            if resType == '6':  # scsi controller! Purge!
                print("Detected scsi")
                iid = item.getElementsByTagName('rasd:InstanceID')[0].firstChild.nodeValue
                purged.append(iid)
                item.parentNode.removeChild(item)
            elif resType == '5':  # ide controller, remember!
                print("Detected ide")
                iid = item.getElementsByTagName('rasd:InstanceID')[0].firstChild.nodeValue
                if iid not in ides:
                    ides[iid] = [] 
                
        # then remap disks
        for good_item in ovf_dom.getElementsByTagName('Item'):
            resType = good_item.getElementsByTagName('rasd:ResourceType')[0].firstChild.nodeValue
            if resType == '17':
                # disk!
                print("Detected disk {}".format(
                    good_item.getElementsByTagName('rasd:ElementName')[0].firstChild.nodeValue))
                disk_parent_node = good_item.getElementsByTagName('rasd:Parent')[0].firstChild
                if disk_parent_node.nodeValue in purged:
                    print("Remapping disk...")
                    #remap to available ide
                    remapped = False
                    for ide in ides:
                        # we allow a maximum of two disks on each IDE controller
                        # tbh I'm not sure this is required. Feedback welcome
                        if len(ides[ide]) < 2:
                            disk_parent_node.nodeValue = ide
                            remapped = True
                            break
                    if remapped == False:
                        raise Exception("Too many disks, you need more IDE controllers.\n" + 
                        "It's probably better to create a blank VM and just add the disks.")
        # ok, let's write it down
        print("Saving result...")
        with open(f, "w", encoding="utf-8") as fo:        
            ovf_dom.writexml(fo)
        
def fix_sha(ovf_file_path):
    ovf_path = Path(ovf_file_path)
    mf_path = ovf_path.with_suffix(".mf")
    # backup first
    copy2(mf_path, mf_path.with_suffix(".mf.BACKUP"))
        
    sha = None
    print("Recalculating hash...")
    with open(ovf_path, "rb") as ovf:
        sha = hashlib.sha1(ovf.read()).hexdigest()
    with open(mf_path, "r", encoding="utf-8") as mf:
        lines = mf.readlines()
        outlines = []
        for l in lines:
            key, val = l.split("= ")
            if key == f'SHA1({ovf_path.name})':
                outlines.append(f'{key}= {sha}\n')
            else:
                outlines.append(l)
    print("Correcting MF...")
    with open(mf_path, "w", encoding="utf-8") as mf:
        mf.writelines(outlines)

def to_ovf(vmw_path, out_dir="/tmp"):
    source_p = Path(vmw_path).resolve()
    target_p = (Path(out_dir) / Path(source_p.name).with_suffix(".ovf")).resolve()
    for p in [source_p, Path(target_p.parent)]:
        if not p.exists():
            raise Exception("Path does not exist: {}".format(p))
    
    vmx = list(source_p.glob('*.vmx'))[0]
    
    print(f'Converting {vmx} (this will take a while)...')
    print('While it runs, you should get a .tmp file in ' + out_dir)
    try:
        result = Popen([OVFTOOL,'--acceptAllEulas','--machineOutput', vmx,target_p], 
                        stdout=PIPE, 
                        stderr=STDOUT)
        message = result.communicate()
        if not b'SUCCESS' in message[0]:
            raise(Exception(message[0]))
        print('DONE! Phew.')
        return  target_p
        
    except OSError as e:
        raise

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Parameters: /path/to/image.vmwarevm [/path/to/out_dir]")
        sys.exit(1)
    in_vm = sys.argv[1]
    out_dir = "/tmp"
    if len(sys.argv) > 2:
        out_dir = sys.argv[2]
    try:
        print(">> Source VM  : " + in_vm)
        print(">> Output Dir : " + out_dir)
    
        ovf = to_ovf(in_vm, out_dir)
        fix_scsi(ovf)
        fix_sha(ovf)
        print("Conversion completed. Import appliance in VirtualBox now (you will have to disable network cards)")
    except Exception as e:
        print(e)
        raise

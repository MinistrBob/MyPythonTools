#!/usr/bin/env python
# VMware vSphere Python SDK
# Copyright (c) 2008-2015 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Python program for listing the vms on an ESX / vCenter host
"""

from __future__ import print_function

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

import argparse
import atexit
import getpass
import ssl


def GetArgs():
    """
   Supports the command-line arguments listed below.
   """
    parser = argparse.ArgumentParser(
        description='Process args for retrieving all the Virtual Machines')
    parser.add_argument('-s', '--host', required=True, action='store',
                        help='Remote host to connect to')
    parser.add_argument('-o', '--port', type=int, default=443, action='store',
                        help='Port to connect on')
    parser.add_argument('-u', '--user', required=True, action='store',
                        help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False, action='store',
                        help='Password to use when connecting to host')
    args = parser.parse_args()
    # print(args)
    return args


def PrintVmInfo(vm, depth=1, report_type='report'):
    """
   Print information for a particular virtual machine or recurse into a folder
   or vApp with depth protection
   """
    maxdepth = 10

    # if this is a group it will have children. if it does, recurse into them
    # and then return
    if hasattr(vm, 'childEntity'):
        if depth > maxdepth:
            return
        vmList = vm.childEntity
        for c in vmList:
            PrintVmInfo(c, depth + 1, report_type=report_type)
        return

    # if this is a vApp, it likely contains child VMs
    # (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
    if isinstance(vm, vim.VirtualApp):
        vmList = vm.vm
        for c in vmList:
            PrintVmInfo(c, depth + 1, report_type=report_type)
        return

    # Collect data
    vm_dict = {
        'vm_host': vm.summary.runtime.host.name,  # 172.26.12.8
        'vm_ip': str(vm.summary.guest.ipAddress),  # 172.26.12.171
        'vm_name': vm.summary.config.name,  # ic-dp-and-app
        # 'vm_path': vm.summary.config.vmPathName,  # [datastore8] ic-dp-and-app/ic-dp-and-app.vmx
        'vm_guest_fullname': vm.summary.config.guestFullName,  # Microsoft Windows Server 2016 or later (64-bit)
        'vm_guest_id': str(vm.summary.guest.guestId),
        'vm_guest_family': str(vm.guest.guestFamily),
        'vm_guest_state': vm.guest.guestState,
        # 'vm_annotation': vm.summary.config.annotation,  ### notes can be very long
        'vm_state': vm.summary.runtime.powerState,  # poweredOn
        'vm_question': str(vm.summary.runtime.question)
    }

    match report_type:
        case 'report':
            print("Name       : ", vm_dict['vm_name'])
            print("Path       : ", vm_dict['vm_path'])
            print("Guest      : ", vm_dict['vm_guest_fullname'])
            print("Annotation : ", vm_dict['vm_annotation'])
            print("State      : ", vm_dict['vm_state'])
            print("IP         : ", vm_dict['vm_ip'])
            print("Question   : ", vm_dict['vm_question'])
            print("Host       : ", vm_dict['vm_host'])
            print("")
        case 'tab':
            print('\t'.join(vm_dict.values()))

    # exit(0)  # DEBUG


def main():
    """
   Simple command-line program for listing the virtual machines on a system.
   """

    args = GetArgs()
    if args.password:
        password = args.password
    else:
        password = getpass.getpass(prompt='Enter password for host %s and '
                                          'user %s: ' % (args.host, args.user))

    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    si = SmartConnect(host=args.host,
                      user=args.user,
                      pwd=password,
                      port=int(args.port),
                      sslContext=context)
    if not si:
        print("Could not connect to the specified host using specified "
              "username and password")
        return -1

    atexit.register(Disconnect, si)

    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vm_folder = datacenter.vmFolder
            vm_list = vm_folder.childEntity
            for vm in vm_list:
                PrintVmInfo(vm, report_type='tab')
    return 0


# Start program
if __name__ == "__main__":
    main()

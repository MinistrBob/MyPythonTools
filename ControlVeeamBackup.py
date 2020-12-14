import os
import ssl
import atexit
import pprint
import traceback

import custom_logger
import SETTINGS
from datetime import datetime
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from alert_to_mail import send_email

program_file = os.path.realpath(__file__)
logger = custom_logger.get_logger(program_file=program_file)


def get_vm_name(vm, depth=1):
    """ Print information for a particular virtual machine or recurse into a folder or vApp with depth protection """
    maxdepth = 10

    # if this is a group it will have children. if it does, recurse into them
    # and then return
    if hasattr(vm, 'childEntity'):
        if depth > maxdepth:
            return
        vmList = vm.childEntity
        for c in vmList:
            get_vm_name(c, depth + 1)
        return

    # if this is a vApp, it likely contains child VMs
    # (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
    if isinstance(vm, vim.VirtualApp):
        vmList = vm.vm
        for c in vmList:
            get_vm_name(c, depth + 1)
        return

    # summary = vm.summary
    # print("Name       : ", summary.config.name)
    return vm.summary.config.name


def get_list_current_vbk():
    (_, _, filenames) = next(os.walk(SETTINGS.settings['backup_dir']))
    logger.debug(f"filenames=\n{filenames}")
    logger.info("VBK list processing")
    # _list_current_vbk = [filename[:-16][:-11] for filename in filenames]
    # logger.debug(_list_current_vbk)
    _dict_current_vbk_with_date = {filename[:-16][:-11]: datetime.strptime(filename[:-16][-10:], '%Y-%m-%d') for
                                   filename
                                   in filenames if filename.endswith('.vbk')}
    logger.debug(f"_dict_current_vbk_with_date=\n{_dict_current_vbk_with_date}")
    return _dict_current_vbk_with_date


def get_list_current_vms():
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    si = SmartConnect(host=SETTINGS.settings['vmware_host'],
                      user=SETTINGS.settings['vmware_user'],
                      pwd=SETTINGS.settings['vmware_password'],
                      port=SETTINGS.settings['vmware_port'],
                      sslContext=context)
    if not si:
        print("Could not connect to the vCenter using specified username and password")
        exit(1)
    logger.info("Connect to VMWare vCenter is OK")
    atexit.register(Disconnect, si)

    content = si.RetrieveContent()
    _list_current_vms = []
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vmFolder = datacenter.vmFolder
            vmList = vmFolder.childEntity
            for vm in vmList:
                _list_current_vms.append(get_vm_name(vm))
    # Filter None
    not_none_list = filter(None.__ne__, _list_current_vms)
    _list_current_vms = list(not_none_list)
    logger.debug(f"_list_current_vms=\n{_list_current_vms}")
    return _list_current_vms


if __name__ == "__main__":
    logger.info(">>>> BEGIN ControlVeeamBackup >>>>")

    # # DEBUG  Get dict current VMs
    # list_current_vms = get_list_current_vms()
    # d1 = {i: 365 for i in list_current_vms}
    # d1 = pprint.pformat(d1)
    # logger.info(f"d1=\n{d1}")
    # exit(0)

    # Get list current backup files from disk
    logger.info("Get list current backup files from disk")
    try:
        dict_current_vbk_with_date = get_list_current_vbk()
    except:
        logger.error(traceback.format_exc())
        exit(1)
    # Get list current VMs from ESXi
    logger.info("Get list current VMs from ESXi")
    try:
        list_current_vms = get_list_current_vms()
    except:
        logger.error(traceback.format_exc())
        exit(1)
    # Checking process
    logger.info("Checking process")
    list_no_backup = []  # Separate list of virtual machines that have not been backed up. For convenience.
    list_expired = []  # Seperate List of virtual machines whose backups are expired. For convenience.
    report = []  # Final complete list.
    for vm_name in list_current_vms:
        if vm_name in dict_current_vbk_with_date:
            # List of virtual machines whose backups are expired
            pass  # проверка древности
            if vm_name in SETTINGS.settings['vm_expires']:
                # compare date
                logger.debug(f"{vm_name}|{datetime.now()}|{dict_current_vbk_with_date[vm_name]}|{(datetime.now() - dict_current_vbk_with_date[vm_name]).days}|{SETTINGS.settings['vm_expires'][vm_name]}")
                if (datetime.now() - dict_current_vbk_with_date[vm_name]).days > SETTINGS.settings['vm_expires'][vm_name]:
                    list_expired.append(vm_name)
                    report.append(f"{vm_name} - !!! backup expired !!!")
                else:
                    report.append(vm_name)  # = OK
            else:
                report.append(f"{vm_name} - not set expired date")
        else:
            # List of virtual machines that have not been backed up
            list_no_backup.append(vm_name)
            report.append(f"{vm_name} - !!! not backup !!!")
    # Sort all lists
    list_no_backup.sort()
    list_expired.sort()
    report.sort()
    logger.debug(f"list_no_backup=\n{list_no_backup}")
    logger.debug(f"list_expired=\n{list_expired}")
    logger.debug(f"report=\n{report}")
    # Preparing of report
    list_no_backup = pprint.pformat(list_no_backup)
    list_expired = pprint.pformat(list_expired)
    report = pprint.pformat(report)
    text_of_report = "=" * 80 + \
                     "\nList of virtual machines that have not been backed up\n" + \
                     "=" * 80 + \
                     f"\n{list_no_backup}\n" + \
                     "=" * 80 + \
                     "\nList of virtual machines whose backups are expired\n" + \
                     "=" * 80 + \
                     f"\n{list_expired}\n" + \
                     "=" * 80 + \
                     "\nFinal complete list\n" + \
                     "=" * 80 + \
                     f"\n{report}\n"
    # Send report
    receiver_emails = SETTINGS.settings['recipient_emails']
    subject = "ControlVeeamBackup"
    attached_file = logger.handlers[0].baseFilename
    send_email(receiver_emails, subject, text_of_report, logger, attached_file)
    logger.info(">>>> END ControlVeeamBackup >>>>")

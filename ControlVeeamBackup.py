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


def get_vm_info(vm_name_, depth=1):
    """ Print information for a particular virtual machine or recurse into a folder or vApp with depth protection """
    maxdepth = 10

    # if this is a group it will have children. if it does, recurse into them
    # and then return
    if hasattr(vm_name_, 'childEntity'):
        if depth > maxdepth:
            return
        vmList = vm_name_.childEntity
        for c in vmList:
            get_vm_info(c, depth + 1)
        return

    # if this is a vApp, it likely contains child VMs
    # (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
    if isinstance(vm_name_, vim.VirtualApp):
        vmList = vm_name_.vm
        for c in vmList:
            get_vm_info(c, depth + 1)
        return

    summary = vm_name_.summary
    vm = {'name': summary.config.name,
          'power_state': summary.runtime.powerState.replace('poweredOn', 'ON')}
    if summary.guest is not None:
        if summary.guest.hostName is not None:
            vm['guest_name'] = summary.guest.hostName
        ip = summary.guest.ipAddress
        if ip is not None and ip != "":
            vm['guest_ip'] = ip

    return vm


def get_list_current_vbk(backup_dir_):
    if not os.path.exists(backup_dir_):
        msg = f"Path backup_dir={backup_dir_} does not exist"
        print(msg)
        logger.error(msg)
        exit(1)
    (_, _, vbk_files) = next(os.walk(backup_dir_))
    logger.debug(f"vbk_files=\n{vbk_files}")
    logger.info("VBK list processing")
    # _list_current_vbk = [vbk_file[:-16][:-11] for vbk_file in vbk_files]
    # logger.debug(_list_current_vbk)
    # _dict_current_vbk_with_date = {vbk_file[:-16][:-11]: datetime.strptime(vbk_file[:-16][-10:], '%Y-%m-%d') for
    #                                vbk_file
    #                                in vbk_files if vbk_file.endswith('.vbk')}
    _dict_current_vbk_with_date = {}
    for vbk_file in vbk_files:
        if vbk_file.endswith('.vbk'):  # обрабатываем только vbk файлы
            vbk_vm_name = vbk_file[:-16][:-11]  # type: str
            vbk_create_date = datetime.strptime(vbk_file[:-16][-10:], '%Y-%m-%d')  # type: datetime
            if vbk_vm_name in _dict_current_vbk_with_date:
                # такая резервная копия уже есть,
                # нужно обработать дату (остаётся самая последняя дата)
                # и увеличить счётчик копий
                if vbk_create_date > _dict_current_vbk_with_date[vbk_vm_name][0]:
                    _dict_current_vbk_with_date[vbk_vm_name][0] = vbk_create_date
                _dict_current_vbk_with_date[vbk_vm_name][1] = _dict_current_vbk_with_date[vbk_vm_name][1] + 1
            else:
                _dict_current_vbk_with_date[vbk_vm_name] = [vbk_create_date, 1]
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
    _list_current_vms = {}
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vmFolder = datacenter.vmFolder
            vmList = vmFolder.childEntity
            for real_vm in vmList:
                vm_ = get_vm_info(real_vm)
                if vm_ is not None:
                    # print(f"type={type(vm_)}|vm_={vm_}")
                    _list_current_vms[vm_['name']] = vm_
    # Filter None
    # not_none_list = filter(None.__ne__, _list_current_vms)
    # _list_current_vms = list(not_none_list)
    logger.debug(f"_list_current_vms=\n{_list_current_vms}")
    return _list_current_vms


def get_email_report(list_no_backup_, list_expired_, list_backup_vm_no_longer_exist_, report_):
    # Sort all lists
    list_no_backup_.sort()
    list_expired_.sort()
    list_backup_vm_no_longer_exist_.sort()
    report_.sort()
    logger.debug(f"list_no_backup=\n{list_no_backup_}")
    logger.debug(f"list_expired=\n{list_expired_}")
    logger.debug(f"list_backup_vm_no_longer_exist_=\n{list_backup_vm_no_longer_exist_}")
    logger.debug(f"report=\n{report_}")
    # Preparing of report
    list_no_backup_ = pprint.pformat(list_no_backup_)
    list_expired_ = pprint.pformat(list_expired_)
    list_backup_vm_no_longer_exist_ = pprint.pformat(list_backup_vm_no_longer_exist_)
    report_ = pprint.pformat(report_)
    _text_of_report = "=" * 80 + \
                      "\nList of virtual machines that have not been backed up\n" + \
                      "=" * 80 + \
                      f"\n{list_no_backup_}\n" + \
                      "=" * 80 + \
                      "\nList of virtual machines whose backups are expired\n" + \
                      "=" * 80 + \
                      f"\n{list_expired_}\n" + \
                      "=" * 80 + \
                      "\nList of backups of virtual machines that no longer exist\n" + \
                      "=" * 80 + \
                      f"\n{list_backup_vm_no_longer_exist_}\n" + \
                      "=" * 80 + \
                      "\nFinal complete list\n" + \
                      "=" * 80 + \
                      f"\n{report_}\n"
    return _text_of_report


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
    dict_current_vbk_with_date = {}
    try:
        dict_current_vbk_with_date = get_list_current_vbk(SETTINGS.settings['backup_dir'])
    except:
        logger.error(traceback.format_exc())
        exit(1)

    # Get list current VMs from ESXi
    logger.info("Get list current VMs from ESXi")
    list_current_vms = []
    try:
        list_current_vms = get_list_current_vms()
    except:
        logger.error(traceback.format_exc())
        exit(1)

    # Get list of backups of virtual machines that no longer exist
    list_backup_vm_no_longer_exist = list(set(dict_current_vbk_with_date) - set(list_current_vms))
    logger.debug(f"list_backup_vm_no_longer_exist=\n{list_backup_vm_no_longer_exist}")

    # Checking process
    logger.info("Checking process")
    list_no_backup = []  # Separate list of virtual machines that have not been backed up. For convenience.
    list_expired = []  # Separate List of virtual machines whose backups are expired. For convenience.
    report = []  # Final complete table. type: str
    for vm_name in list_current_vms:  # type: str, list
        # exclude vm from vm_exclude_list
        if vm_name not in SETTINGS.settings['vm_exclude_list']:
            if vm_name in dict_current_vbk_with_date:
                # List of virtual machines whose backups are expired
                if vm_name in SETTINGS.settings['vm_expires']:
                    # compare date
                    backup_date = dict_current_vbk_with_date[vm_name][0]  # type: datetime
                    logger.debug(
                        f"{vm_name}|"
                        f"{datetime.now()}|"
                        f"{backup_date}|"
                        f"{(datetime.now() - backup_date).days}|"
                        f"{SETTINGS.settings['vm_expires'][vm_name]}")
                    if (datetime.now() - backup_date).days > \
                            SETTINGS.settings['vm_expires'][vm_name]:
                        list_expired.append(vm_name)
                        report.append(f"{vm_name} - !!! backup expired !!!")
                    else:
                        report.append(vm_name)  # = OK
                else:
                    report.append(f"{vm_name} - _you_need_set_expired_date_setting_")
            else:
                # List of virtual machines that have not been backed up
                list_no_backup.append(vm_name)
                report.append(f"{vm_name} - !!! no backup !!!")

    # Report to email
    if not list_no_backup and not list_expired and not list_backup_vm_no_longer_exist:
        logger.info("All lists empty.")
    else:
        text_of_report = get_email_report(list_no_backup, list_expired, list_backup_vm_no_longer_exist, report)
        # Send report
        receiver_emails = SETTINGS.settings['recipient_emails']
        subject = "ControlVeeamBackup"
        attached_file = logger.handlers[0].baseFilename
        send_email(receiver_emails, subject, text_of_report, logger, attached_file)

    logger.info(">>>> END ControlVeeamBackup >>>>")

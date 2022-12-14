import xml.dom.minidom


def main():
    doc = xml.dom.minidom.parse(r"c:\!SAVE\СП\zbx_export_hosts.xml")
    hosts = doc.getElementsByTagName("host")
    for item in hosts:
        print(item.childNodes[0].nodeValue)
        name = item.childNodes[0].nodeValue
        ips = item.getElementsByTagName("ip")
        for i in ips:
            # print(i.childNodes[0].nodeValue)
            ip = i.childNodes[0].nodeValue
            print(f"{name}\t{ip}")
        print("------------------------------")


if __name__ == '__main__':
    main()

# pip install wifi_qrcode_generator
import wifi_qrcode_generator as qr

qrCode = qr.wifi_qrcode('Givin_TP', False, 'WPA', 'givinschool')
qrCode.show()
qrCode.save(r'c:\!SAVE\wifi.png')

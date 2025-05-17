from onvif import ONVIFCamera

def discover_onvif_cameras(ip_range='192.168.1.0/24'):
    cameras = []
    for i in range(1, 255):
        ip = f"192.168.1.{i}"
        try:
            cam = ONVIFCamera(ip, 80, 'admin', '12345')
            dev_info = cam.devicemgmt.GetDeviceInformation()
            cameras.append({
                'ip': ip,
                'model': dev_info.Model,
                'protocol': 'ONVIF'
            })
        except:
            continue
    return cameras
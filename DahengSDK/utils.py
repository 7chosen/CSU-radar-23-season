import numpy as np
import DahengSDK.gxipy as gx
import cv2
device = gx.DeviceManager()
dev_num, dev_info = device.update_device_list()



def openByIndex(num):
    idx=dev_info[num].get("index")
    cam=device.open_device_by_index(idx)
    cam.stream_on()
    return cam
    

if dev_num != 0:
    cam1=openByIndex(0)
    cam1.ExposureTime.set(10000)
    cam2=openByIndex(1)
    cam2.ExposureTime.set(10000)

    
# source img to numpy format  
def openImg(src):
    raw_image=src.data_stream[0].get_image()
    rgb_image = raw_image.convert('RGB')
    numpy_image = rgb_image.get_numpy_array()
    numpy_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
    return numpy_image
    

# def setExposureTime(tm):
#     for i in [cam1,cam2]:
#         i.ExposureTime.set(tm)
    

#  composite two image then send to the main prog
def openDaheng():    
    img1=openImg(cam1)
    img2=openImg(cam2)
    img=np.hstack((img2,img1))
    img=cv2.resize(img,(0,0),fx=0.5,fy=0.5)
    return img
    
# functional
def closeDaheng(src=[cam1,cam2]):
    for s in src:
        s.stream_off()
        s.close_device()

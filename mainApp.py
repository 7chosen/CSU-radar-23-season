import argparse
import time
import cv2 as cv
import numpy as np
import os
import threading
from DahengSDK.utils import closeDaheng, openDaheng
from yolov7.general import xyxy2xywh
from yolov7.detect import detect,initial_check
from Serial.mainSei import Referee_Transmit_Map,srlInit

# check if location.txt exists
assert os.path.getsize('sources/location.txt') != 0,'No Matrix Found. Please Run adjustAngle.py in Terminal First'
Mat=np.loadtxt('sources/location.txt')
names=['blue1', 'blue2', 'blue3', 'blue4', 'blue5', 'car', 'grey1', 'grey2', 'grey3', 'grey4', 'grey5', 'red1', 'red2', 'red3', 'red4', 'red5']

sendLocInfo=[None]*6
clr=''
# srl=''
fixedwidth=0.02
fixedheight=0.02

def serialSendThread(arg1):
    i=1
    while 1:
        if sendLocInfo[i] is not None :
            carID=sendLocInfo[i][-1]
            x=sendLocInfo[i][0]
            y=sendLocInfo[i][1]
            Referee_Transmit_Map(0x0305,14,carID,x,y,arg1)

# DEBUG  print to the terminal
            # print('===')
            # print(carID,x,y)
            # print('===')
            
            time.sleep(0.1)
        else:
            with open ('sources/cache.txt','r') as f:
                f.close()
        i+=1
        if i>5:
            sendLocInfo.clear()
            i=1


# def serialReadThread():
#     read(srl)
    

def main(Map,stream,srl):
    
    global sendLocInfo,clr

    t1=threading.Thread(target=serialSendThread,kwargs={'arg1':srl})
    t1.start()
    
    # t2=threading.Thread(target=serialReadThread)
    # t2.start()
    
    if stream=='Daheng':
        streamFlag=1
    else:
        cap = cv.VideoCapture(stream)
        assert cap.isOpened(),f'Can\'t Open The Video'
        streamFlag=2

 
    while 1:
        map=cv.imread(Map)
        if streamFlag==2:
            ret, srcImg = cap.read()
        else:
            srcImg=openDaheng()
        
#DEBUG tag1 show source image
        cv.namedWindow('source',cv.WINDOW_NORMAL)
        cv.imshow('source', srcImg)
        k = cv.waitKey(1)
        if k & 0xff == 27:
            break
        
        # a container which store cars with exact label
        Car=detect(srcImg)

        if not len(Car):
            print('[INFO] No car detected in this frame')
            continue
        
        CarCentralPoint=[]
        # 
        for car in Car:    
            rectZone=car[:4]
            pt=xyxy2xywh(rectZone)[:2]
            
            # coordinates transformation
            newpt=np.array(pt,dtype=np.float32)
            
            # get the label  eg. 0,1,2...15 etc
            label=int(car[-1])
            label=names[label][-1]
            sendLabel=label
            if clr == 'RED':
                sendLabel = '10' + label
            
            
            newpt=newpt.reshape(1,-1,2)
            updatePts=cv.perspectiveTransform(newpt,Mat)
            
            updatePts=updatePts.reshape(2).astype(int)
            CarCentralPoint.append(updatePts)   
            sendLabel=int(sendLabel)
            sendLocInfo[sendLabel]=([updatePts[0]*fixedwidth,updatePts[1]*fixedheight,sendLabel])
           

# DEBUG plot
        if clr=='RED':
            drawClr=[255,0,0]
        else:
            drawClr=[0,0,255]
        if CarCentralPoint:
            for x,y in CarCentralPoint:
                # print(x,y)
                cv.circle(map,(x,y),3,drawClr,-1)
        cv.imshow('map',map) 
        cv.waitKey(1)

#DEBUG tag1
    # cv.destroyAllWindows()
    
    
    if streamFlag==2:
        cap.release()
    else:
        closeDaheng()
    
        
    t1.join()
    # t2.join()

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--weight',type=str,help='path of the weight',default='radar.pt')
    parser.add_argument('--map',type=str,help='red or blue map',default='sources/blueMap.png')
    parser.add_argument('--stream',type=str,help='path of image stream, Daheng/video path')
    parser.add_argument('--ser',type=str,help='COM* ')
    opt=parser.parse_args()
    weight,map=opt.weight,opt.map
    stream=opt.stream
    if map.find('b')!=-1:
        clr='BLUE'
    else:
        clr='RED'
    srl=opt.ser
    initial_check(weight,clr)
    srl=srlInit(srl)
    main(map,stream,srl)
    

    
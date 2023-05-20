import argparse
import numpy as np
import cv2 as cv
from DahengSDK.utils import closeDaheng, openDaheng



# fixed 4 points that u already mark on the map
knownPts=np.array([[408,350],[510,585],[669,345],[803,111]],dtype=np.float32)

threshold=100 # a region allows u marking point accurately
flag=0 # decide window open or close
tmpArr=list() # store 4 points u mark on the frame


def imgProcess(marks,points):
    '''
    compute the affline matrix and save under the sources folder 
    
    @param marks fixed points that already known\n
    @param points points you choose to project
    '''
    afflineMaT=cv.getPerspectiveTransform(points,marks)
    np.savetxt('sources/location.txt',afflineMaT)
    

def printPoint(e,x,y,flags,param):
    '''
    mark points
    '''
    tmpImg=param.copy()
    
    cv.rectangle(tmpImg,(threshold,threshold),(tmpImg.shape[1]-threshold,tmpImg.shape[0]-threshold),(0,255,0),1)
    h,w=param.shape[:2] 
    
    # left x, top y, right x, bottom y
    lx,ty,rx,by=x-threshold,y-threshold,x+threshold,y+threshold
    
    #  first check the range of x
    if lx<0:
        rx=2*threshold
        lx=0
    elif rx>w:
        rx=w
        lx=w-2*threshold
    
    # on the base of correct range of x, then check the range of y
    if ty<0:
        ty=0
        by=2*threshold
    elif by>h:
        ty=h-2*threshold
        by=h
    
    # begin to enlarge
    cropImg=tmpImg[ty:by,lx:rx]
    adjustImg=cv.resize(cropImg,None,fx=2,fy=2)
    miniH,miniW=adjustImg.shape[:2]
    cv.circle(adjustImg,(int(miniH/2),int(miniW/2)),3,(255,255,255),-1)
    cv.imshow('enlarge',adjustImg)
    
    if e==cv.EVENT_LBUTTONDOWN and len(tmpArr)<4:
        cv.circle(param,(x,y),5,(0,255,0),-1)
        tmpArr.append([x,y])
        cv.imshow('adjust',param)
        

def drawinvideo(pts,image):
    '''
    draw on the source image, while destroy the redundant windows
    '''
    global flag
    if flag!=1:
        cv.destroyWindow('adjust')
        cv.destroyWindow('enlarge')
    for i in range(4):
        cv.circle(image,(pts[i][0],pts[i][1]),5,(0,255,0),-1)


def main(stream):
    
    global flag,tmpArr
    
    streamFlag=0
    
    if stream == 'Daheng':
        streamFlag=1
    else:
        cap=cv.VideoCapture(stream)
        assert cap.isOpened(),f'Can\'t Open The Video'
        streamFlag=2
        
    # cv.namedWindow('video',cv.WINDOW_NORMAL) 
    while 1:
        if streamFlag==1:
            img=openDaheng()
        else:
            ret,img=cap.read()
        
        key = cv.waitKey(24) & 0xff 
        if key == 27:
            break
        elif key == ord('r'): # mark points while pressing 'r' on the keyboard
            flag=0
            tmpArr.clear()
            cv.imshow('adjust',img)
            cv.setMouseCallback('adjust',printPoint,img)
        
        # if already satisfy the condition, then draw on the frame and compute the matrix
        if len(tmpArr)==4 :
            drawinvideo(tmpArr,img)
            npArr=np.array(tmpArr,dtype=np.float32)
            imgProcess(knownPts,npArr)
            flag=1
        cv.namedWindow('video',cv.WINDOW_NORMAL)
        cv.imshow('video',img)
        
    # shutdown
    cv.destroyAllWindows()
    if streamFlag==2:
        cap.release()
    else:
        closeDaheng()

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--stream',type=str,help='path of the stream, Daheng/video path')
    # parser.add_argument('--map',type=str,default='sources/blueMap.png',help='which map to use')
    opt=parser.parse_args()
    # assert Path(opt.map).is_file(),f'File Not Found: {opt.map}'
    # src=opt.map
    stream=opt.stream
    main(stream=stream)
    
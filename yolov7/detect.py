'''
core detection function

'''
import torch
from collections import Counter
from numpy import random
import cv2
from models.yolo import attempt_load
from yolov7.general import LoadImages,check_img_size, non_max_suppression, \
    scale_coords, xyxy2xywh, time_synchronized,plot_one_box,check_file, check_centerPoint_zone

ourside=''
def initial_check(wts,side):
    '''
    inintially check the environment
    
    @param side which side u belongs to. Red/Blue
    
    '''
    
    
    global imgsz,device,stride,names,color,model
    global ourside
    
    # decide which side we belong to, RED or BlUE
    ourside=side.lower()
    print(f'[INFO] our side is {ourside}')
    
    # check cuda 
    if not torch.cuda.is_available():
        print('[WARN] cuda is not available!')
        exit()
    else:
        # set the default device
        device=torch.device('cuda:0')
        print(f'[INFO] Find {device}')
        
    # set the weight
    weight=check_file(wts)

    # model loading
    model=attempt_load(weights=weight,map_location=device)

    # declare the stride
    stride=int(model.stride.max())
        
    # declare the image size
    imgsz=check_img_size(960,s=stride)

    # ['blue1', 'blue2', 'blue3', 'blue4', 'blue5', 'car', 'grey1', 'grey2', 'grey3', 'grey4', 'grey5', 'red1', 'red2', 'red3', 'red4', 'red5']
    names=model.module.names if hasattr(model,'module') else model.names 

    color=[[random.randint(0,255) for _ in range(3)] for _ in names]  # double loop



def detect(srcImg):
    '''
    output a 2-dimen list, size n*(x1,y1,x2,y2,conf,label(int))
    '''
    
    
    dataset=LoadImages(srcImg,img_size=imgsz,stride=stride)
    
    for imgAdjust,imgSrc in dataset:
        imgAdjust=torch.from_numpy(imgAdjust).to(device)
        imgAdjust=imgAdjust.float()
        imgAdjust/=255.0  # normalization
        if imgAdjust.ndimension()==3:
            imgAdjust=imgAdjust.unsqueeze(0)

        t1=time_synchronized()
        pred=model(imgAdjust)[0]
        t2=time_synchronized()
        
        # change the threshold of confidence and iou
        pred=non_max_suppression(pred)   # pred [n,6]  n*[x1,y1,x2,y2,conf,classes(int)] 
        t3=time_synchronized()
        
        det=pred[0]
        imgTmp=imgSrc

        # scale the image to the origin size
        det[:,:4]=scale_coords(imgAdjust.shape[2:],det[:,:4],imgTmp.shape).round()
        det=det.cpu().detach().numpy() 
        
        # process and sift every prediction rectangle
        Car=[]
        Armor=[]
        for cls in det:
            nm=names[int(cls[5])]
            
            # sift label 'color about ourside' and 'grey' 
            jdg1=nm.find(ourside)
            jdg2=nm.find("grey")
            if jdg1!=-1 or jdg2!=-1:
                continue
            
            if nm=='car':
                Car.append(cls)
            else:
                Armor.append(cls)


        # change car's label, based on which armor has the largest propotion
        # after this procession, eg. if our side is red, then 
        # car's label is modified to [blue1-5 or car]
        for i in range(len(Car)-1,-1,-1):
            rectZone=Car[i][:4] # define the ROI of car 
            finalLabel=[]
            
            for armor in Armor:
                centralPt=xyxy2xywh(armor[:4])[:2]
                if check_centerPoint_zone(centralPt,rectZone):
                    finalLabel.append(armor[5])
            
            if len(finalLabel):
                counter=Counter(finalLabel)
                Car[i][-1]=counter.most_common(1)[0][0]
            
            # delete cars with no armor inside
            if Car[i][-1]==5.0:
                del Car[i]
                continue
            
                
#DEBUG plot on the copied source image and display it

        if len(Car):
            # print(len(Car))
            for *xyxy, conf, cls in reversed(Car):
                # label=f'{names[int(cls)]} {conf:.2f}'
                label=f'{names[int(cls)]}'
                # if label!='car':
                    # plot_one_box(xyxy,imgTmp,label=label,color=color[int(cls)],line_thickness=1)
                    # continue
                plot_one_box(xyxy,imgTmp,label=label,color=color[int(cls)],line_thickness=1)
        # else:
            # print('[INFO] No car detected in this frame.')
        
        cv2.namedWindow('realtimeDetection',cv2.WINDOW_NORMAL)
        cv2.imshow('realtimeDetection',imgTmp)

#DEBUG check every frame      
 
        # cv2.waitKey()
        
        t4=time_synchronized() 

#DEBUG COMMENT 
        print('-----')
        print(f'Done. ({(1E3 * (t2 - t1)):.1f}ms) Inference, ({(1E3 * (t3 - t2)):.1f}ms) NMS, ({(1E3 * (t4 - t3)):.1f}ms) Process')

        # prevent gradient explosion then ERR: OUT of MEMORY
        torch.set_grad_enabled(False)
        return Car

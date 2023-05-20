'''
refered to https://github.com/COMoER/LCR_sjtu
modified by 713
'''

import time
import numpy as np
import serial
from Serial.crc import *
from struct import pack


# ports_list = list(serials.comports())
# for comport in ports_list:
#     print(list(comport)[0], list(comport)[1])
def srlInit(portname):
    srl=serial.Serial(portname,115200)
    assert srl.is_open,'Can\'t Open this Serial, Please Check The Serial Name' 
    # debug
    return srl
    
# bufferCnt=0
# buffer=[0]
# buffer*=60
# cmdID=0
byte2int= lambda x:(0x0000|x[0]) | (x[1]<<8)


# def read(srl):
    # global bufferCnt
    # global buffer
    # global cmdID
    # while 1:
    #     s=srl.read(1)
    #     s=int.from_bytes(s,'big')
    #     # print(s)
        
    #     if bufferCnt>50:
    #         bufferCnt=0
        
    #     buffer[bufferCnt]=s
        
    #     if bufferCnt==0:
    #         if buffer[bufferCnt]!= 0xa5:
    #             bufferCnt=0
    #             continue
        
    #     if bufferCnt==5:
    #         # if 帧头CRC8校验未通过
    #         if Verify_CRC8(id(buffer),5)==0:
    #             bufferCnt=0
    #             if buffer[0] == 0xa5:
    #                 bufferCnt=1
    #             continue
               
    #     if bufferCnt==7:
    #         # print(buffer[5],buffer[6])
    #         cmdID= (0x0000|buffer[5]) | (buffer[6]<<8)
    #         print(hex(cmdID))
        
 
    #     # if bufferCnt ==37 and cmdID == 0x0003:
    #     #     if Verify_CRC16(id(buffer),37):
    #     #         Referee_Robot_HP(buffer)
    #     #         bufferCnt=0
    #     #         if buffer[bufferCnt]==0xa5:
    #     #             bufferCnt=1
    #     #         continue
                
        
    #     bufferCnt+=1
            


def Referee_Transmit_Map(cmdID, datalength, targetId, x, y, ser):
    '''
    send every car's loc info
    '''
    buffer = [0]
    buffer = buffer * 50

    buffer[0] = 0xA5  # 0xA5 refer to the Robomaster UART doc
    buffer[1] = (datalength) & 0x00ff  # length of data
    buffer[2] = ((datalength) & 0xff00) >> 8
    buffer[3] = 0x0  # package number
    buffer[4] = Check_CRC8(id(buffer), 5 - 1, 0xff)  # frame header verification
    buffer[5] = cmdID & 0x00ff
    buffer[6] = (cmdID & 0xff00) >> 8
    buffer[7] = 0xffff & targetId
    buffer[8] = 0
    x=pack('f',x)
    y=pack('f',y)
    buffer[9] = x[0]
    buffer[10] = x[1]
    buffer[11] = x[2]
    buffer[12] = x[3]
    buffer[13] = y[0]
    buffer[14] = y[1]
    buffer[15] = y[2]
    buffer[16] = y[3]
    buffer[17:20] = [0] * 4 ## a bug, need 4 bits to fill

    Append_CRC16(id(buffer), datalength + 9)  

    buffer_tmp_array = [0]
    buffer_tmp_array *= 9 + datalength

    for i in range(9 + datalength):
        buffer_tmp_array[i] = buffer[i]
 
    
    ser.write(bytearray(buffer_tmp_array))

    
def Referee_Transmit_BetweenCar(dataID, ReceiverId, data, ser):
    '''
    send info between car
    unused
    '''
    buffer = [0]
    buffer = buffer * 50

    buffer[0] = 0xA5  
    buffer[1] = 10  
    buffer[2] = 0
    buffer[3] = 0  
    buffer[4] = Check_CRC8(id(buffer), 5 - 1, 0xff)  
    buffer[5] = 0x01
    buffer[6] = 0x03
    # DIY ID
    buffer[7] = dataID & 0x00ff
    buffer[8] = (dataID & 0xff00) >> 8
    # if enemy:
        # buffer[9] = 9
    # else:
        # buffer[9] = 109
    buffer[10] = 0
    buffer[11] = ReceiverId
    buffer[12] = 0
    # DIY data
    buffer[13] = data[0]
    buffer[14] = data[1]
    buffer[15] = data[2]
    buffer[16] = data[3]

    Append_CRC16(id(buffer), 10 + 9)  

    buffer_tmp_array = [0]
    buffer_tmp_array *= 9 + 10

    for i in range(9 + 10):
        buffer_tmp_array[i] = buffer[i]
    ser.write(bytearray(buffer_tmp_array))



        
if __name__ == "__main__":
    # ports_list = list(serials.comports())
    # for comport in ports_list:
    #     print(list(comport)[0], list(comport)[1])
    srl=srlInit('COM5')
    x=np.array([8.2,11])
    while(1):
        Referee_Transmit_Map(0x0305,14,101,x[0],x[1],srl)
        time.sleep(1)

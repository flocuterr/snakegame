import math
import random

import cv2
import cvzone
import numpy as np
from cvzone.HandTrackingModule import HandDetector

cap=cv2.VideoCapture(0)
# if not cap.isOpened():
#     print("无法打开摄像头")
#     exit()
#
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("无法接收帧")
#         break
#
#     cv2.imshow('frame', frame)
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()
cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)

detector=HandDetector(detectionCon=0.8,maxHands=1)
'''detectionCon 是检测置信度阈值，用于控制检测的准确性。
设为 0.8 表示只有当手部检测置信度高于 0.8 时，才会认为检测到的手有效。
较高的置信度阈值有助于减少误检，但可能会略微影响检测的灵敏度。'''

class SnakeGameClass:
    def __init__(self,pathFood):
        self.points=[]# all point of the snake
        self.lengths=[]#distance between each points
        self.currentLength=0 # total length of the snake
        self.allowedLength=150# total allowed length
        self.previousHead=0,0# previous head point

        self.imgFood=cv2.imread(pathFood,cv2.IMREAD_UNCHANGED)
        self.hFood,self.wFood,_=self.imgFood.shape
        self.foodPoint=0,0
        self.randomFoodLocation()
        self.score=0
        self.GAMEOVER=False

    def randomFoodLocation(self):
            self.foodPoint = random.randint(100, 1000), random.randint(100, 600)

    def update(self,imgMain,CurrentHead):
        if self.GAMEOVER:
            cvzone.putTextRect(imgMain,"GAMEOVER",[300,300],scale=7,thickness=5,offset=20)
            cvzone.putTextRect(imgMain, f"Your score:{self.score}", [300, 500], scale=7, thickness=5, offset=20)
        else:
            px,py=self.previousHead
            cx,cy=CurrentHead


            self.points.append([cx,cy])
            distance=math.hypot(cx-px,cy-py)
            self.lengths.append(distance)
            self.currentLength+=distance
            self.previousHead=cx,cy

            #length reduction
            if self.currentLength>self.allowedLength:
                for i,length in enumerate(self.lengths):
                    self.currentLength-=length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength<self.allowedLength:
                        break

            #check if the snake eat the food
            rx,ry=self.foodPoint
            if rx-self.wFood//2<cx<rx+self.wFood//2 and ry-self.hFood//2<cy<ry+self.hFood//2:
                self.randomFoodLocation()
                self.allowedLength+=50
                self.score+=1
                print(self.score)

            #check for collision
            pts=np.array(self.points[:-2],np.int32)
            pts=pts.reshape((-1,1,2))
            cv2.polylines(imgMain,[pts],False,(0,200,0),3)

            #Draw snake
            if self.points:
                for i,point in enumerate(self.points):
                    '''enumerate(self.points)：返回一个枚举对象，其中每个元素是一个元组，
                    包含当前元素的索引 i 和元素本身 point。例如，self.points = [(x1, y1), (x2, y2)]，
                    则 enumerate(self.points) 将返回 (0, (x1, y1)), (1, (x2, y2))，依此类推。'''
                    if i!=0:
                        cv2.line(imgMain,self.points[i-1],self.points[i],(0,0,255),20)
                        cv2.circle(img, pointIndex, 20, (200, 0, 200), cv2.FILLED)
                cv2.circle(img,self.points[-1],20,(200,0,200),cv2.FILLED)#最后一个点是头
            #draw the donut
            cvzone.overlayPNG(imgMain, self.imgFood,(rx-self.wFood//2,ry-self.hFood//2))
            cvzone.putTextRect(imgMain, f"score:{self.score}", [100, 100], scale=3, thickness=3, offset=10)
            # check for collision
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(imgMain, [pts], False, (0, 200, 0), 3)
            minDist=cv2.pointPolygonTest(pts,(cx,cy),True)
            if -1<minDist<1:
                self.GAMEOVER=True
                self.points = []  # all point of the snake
                self.lengths = []  # distance between each points
                self.currentLength = 0  # total length of the snake
                self.allowedLength = 150  # total allowed length
                self.previousHead = 0, 0  # previous head point

        return imgMain




game=SnakeGameClass('Donut.png')

# def is_fist(lmlist):
#     tip=lmlist[8][0:2]
#     root=lmlist[0][0:2]
#     D=math.hypot(tip[0]-root[0],tip[1]-tip[1])
#     print(D)
#     # if D<50:
#     #     return True
#     return False


while True:
    sucess,img=cap.read()
    img=cv2.flip(img,1)
    hands,img=detector.findHands(img,flipType=False)

    if hands:
        lmlist=hands[0]["lmList"]#找到第一个手的索引坐标
        pointIndex=lmlist[8][0:2]#获取xy坐标
        cv2.circle(img,pointIndex,20,(200,0,200),cv2.FILLED)
        img=game.update(img,pointIndex)

        # if is_fist(lmlist):
        #     print("is fist")
        #     break
        '''img：要绘制圆的图像。
pointIndex：圆心的位置，通常是一个 (x, y) 坐标点。
20：圆的半径，单位是像素。
(200, 0, 200)：圆的颜色，以 BGR 格式表示。这里是紫色 (200, 0, 200)，对应 RGB 的 (200, 0, 200)。
cv2.FILLED：圆的填充方式。使用 cv2.FILLED 表示填充整个圆。'''
        '''0: 手腕
1-4: 拇指
1: 拇指根部（接近手腕）
2: 拇指的第一个关节
3: 拇指的第二个关节
4: 拇指指尖
5-8: 食指
5: 食指的第一个关节
6: 食指的第二个关节
7: 食指的第三个关节
8: 食指指尖
9-12: 中指
9: 中指的第一个关节
10: 中指的第二个关节
11: 中指的第三个关节
12: 中指指尖
13-16: 无名指
13: 无名指的第一个关节
14: 无名指的第二个关节
15: 无名指的第三个关节
16: 无名指指尖
17-20: 小指
17: 小指的第一个关节
18: 小指的第二个关节
19: 小指的第三个关节
20: 小指指尖'''

    cv2.imshow("Image",img)
    key=cv2.waitKey(1)
    if game.GAMEOVER==True and key==ord("r"):
        game.__init__("Donut.png")
        game.GAMEOVER=False

import cv2 
import os
import numpy as np
import math
import time

path = 'C:/Users/HS/Pictures/Image/'
MIN_MATCH_COUNT = 10
MAX_DIST = 50

class Test:
    def __init__(self, filename):
        self.cnt = 0
        self.dit = []
        file_list = filename.split(' ')
        self.image_list = []
        self.video = cv2.VideoCapture(path + 'test_video2.mp4') #테스트 동영상 
        #self.video = cv2.VideoCapture(0) #웹캠 사용시 
        self.detector = cv2.ORB_create()
        for i in file_list:
            self.image_list.append(self.binIMG(cv2.imread(path + i)))
            
        if self.video is None or len(self.image_list) == 0:
            print('Failed open File !')
            os.sys.exit()
            
        print('Start , ', self.cnt)
        self.start = time.time()
        
    def binIMG(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, bin_img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY_INV)
        
        return bin_img
    
    def countObj(self, dit):
        if self.cnt == 0:
            for i in dit:
                if i != 0:
                    self.cnt += 1
        else :
            #visited = [0 for i in range(len(self.dit))]
            for i in dit:
                min_dist = MAX_DIST
                for j in range(len(self.dit)):
                    if i != 0 and self.dit[j] != 0:
                        dist = math.sqrt((i[0]-self.dit[j][0])**2 + (i[1] - self.dit[j][1])**2)
                        if dist < min_dist:
                            min_dist = dist
                if min_dist == MAX_DIST and i != 0 :
                    self.cnt += 1
            
        self.dit = dit
        
    def Run(self):
        kp1, desc1 = self.detector.detectAndCompute(self.image_list[0], None)
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        while 1:
            ret, img = self.video.read()
            if not ret:
                print("Failed open Video!")
                break
     
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, img_bin = cv2.threshold(gray_img , 100, 255, cv2.THRESH_BINARY_INV)
            
            cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(img_bin)
            img_list = []
            pos_list = []
            cen_list = []
            for i in range(1, cnt):
                (x, y, w, h, area) = stats[i]
                
                if area < 10000:
                    continue
                
                img_list.append(img_bin[y:y+h, x:x+w])
                pos_list.append((x,y,w,h))
                cen_list.append((int(centroids[i][0]), int(centroids[i][1])))
                
            if len(img_list) > 0:
                ditect = [0 for i in range(len(img_list))]
                #matches = [0 for i in range(len(img_list))]
                
                for i in range(len(img_list)):
                    kp2, desc2 = self.detector.detectAndCompute(img_list[i], None)
                    if desc2 is None:
                        continue
                
                    matches = matcher.match(desc1, desc2)
                    matches = sorted(matches, key=lambda x:x.distance)
                        
                    src_pts = np.float32([ kp1[m.queryIdx].pt for m in matches ])
                    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in matches ])
                    if len(dst_pts) < 4:
                        continue
                    mtrx, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                    
                    accuracy=float(mask.sum()) / mask.size
                    #print(str(i+1) + "st image accuracy: %d/%d(%.2f%%)"% (mask.sum(), mask.size, accuracy*100))
                    if mask.sum() >= MIN_MATCH_COUNT or accuracy >= 0.2:        
                        ditect[i] = cen_list[i]
                        #cv2.circle(img, cen_list[i], 1, (255,0,255), 3)
                        cv2.rectangle(img, pos_list[i],(0,0,255),3)
                self.countObj(ditect)
                
            cv2.imshow('img', img)
            if cv2.waitKey(5) == 26:
                break
            
        cv2.destroyAllWindows()
        print('Result : ', self.cnt)
        print("time :", time.time() - self.start)
        
if __name__ == '__main__':
    obj = ('s3.jpg') # 찾을 물체 
    t = Test(obj)
    t.Run()
    
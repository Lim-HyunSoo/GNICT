import cv2 
import os
import numpy as np

path = 'C:/Users/HS/Pictures/Image/'

class CompareIMG:
    def __init__(self):
        print('Start')
        pass
    
    def binIMG(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, dst = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY) 
        
        if ret:
            return dst
        else:
            print("Failed read image!")
            exit()
    
    def diffIMG(self, img1, img2):
        img1 = self.binIMG(img1)
        detector = cv2.ORB_create()
        kp1, desc1 = detector.detectAndCompute(img1, None)
        #print(len(desc1))
        while 1:
            ret, img = img2.read()
            
            if not ret:
                print("Failed open Video!")
                break
            
            vid = self.binIMG(img)
            
            kp2, desc2 = detector.detectAndCompute(vid, None)
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = matcher.match(desc1, desc2)
            
            matches = sorted(matches, key=lambda x:x.distance)
             
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in matches ])
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in matches ])
            
            mtrx, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            
            h,w = img1.shape[:2]
            
            pts = np.float32([ [[0,0]],[[0,h-1]],[[w-1,h-1]],[[w-1,0]] ])
            dst = cv2.perspectiveTransform(pts,mtrx)
            img = cv2.polylines(img,[np.int32(dst)],True,255,3, cv2.LINE_AA)
            
            cv2.imshow('Result', img)
            
            if cv2.waitKey(55) == 27:
                break
            
        print("End")
        cv2.destroyAllWindows()
        
    def Run(self):
        #파일 경로
        filepath1 = path + 'n5.jpg' #찾고싶은대상
        filepath2 = path + 'n8.mp4' #비교 영상
        
        self.img1 = cv2.imread(filepath1) #찾고싶은대상
        self.img2 = cv2.VideoCapture(filepath2) #비교 영상
        
        if self.img1 is None or self.img2 is None:
            print('Image load failed!')
            os.sys.exit()
            
        self.diffIMG(self.img1, self.img2)

if __name__ == '__main__':
    cpimg = CompareIMG()
    cpimg.Run()


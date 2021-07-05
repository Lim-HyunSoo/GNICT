import cv2 
import math

MAX_DIST = 50 
P = 'C:/Users/HS/Pictures/Image/'

class Test:
    def __init__(self):
        print('Start')
        pass 
    
    def readIMG(self, path):
        if path[-3:] == 'jpg' or path[-3:] == 'png':
            img = cv2.imread(P + path)
            return img
        
        elif path[-3:] == 'mp4':
            video = cv2.VideoCapture(P + path)
            return video
        
    def binIMG(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, bin_img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY_INV)
        img_contours, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        return img_contours
    
    def count(self, cen, dis):
        visit = [0 for i in range(len(cen))]
           
        for i in range(len(self.center_list1)):
            min_dist = MAX_DIST
            index2 = 0
            for j in range(len(cen)):
                d = math.sqrt(((self.center_list1[i][0]-cen[j][0])**2) + ((self.center_list1[i][1]-cen[j][1])**2))
                if d < min_dist:
                    min_dist = d
                    index2 = j
                        
            if min_dist < MAX_DIST:
                visit[index2] = 1
                
                if self.ditect_list1[i][0] == dis[index2][0]: #case1 : 이전과 같은 경우 
                    continue
                elif (self.ditect_list1[i][0] != dis[index2][0]): #이전과 다른 경우 
                    if self.ditect_list1[i][0] == 'N': #case2 : n > 인식
                        #print('case2')
                        self.img_count[self.filelist.index(dis[index2][0])] += 1
                    else : 
                        if dis[index2][0] == 'N': #case3 : 인식 > n
                            #print('case3 : ', self.ditect_list1[i], " ", dis[index2])
                            dis[index2] = self.ditect_list1[i]
                        else : #case4 : 인식1 > 인식2 
                            if self.ditect_list1[i][1] > dis[index2][1]:
                                self.img_count[self.filelist.index(dis[index2][0])] += 1
                                self.img_count[self.filelist.index(self.ditect_list1[i][0])] -= 1
                            else: 
                                dis[index2] = self.ditect_list1[i]
                                
        for i in range(len(visit)):
            if visit[i] == 0 and dis[i][0] != 'N': #case5 새로운 객체 인식 
                self.img_count[self.filelist.index(dis[i][0])] += 1
          
        self.center_list1 = cen
        self.ditect_list1 = dis
            
    def Run(self, filename):
        self.filelist = filename.split(' ')
        #img_list = [0 for i in range(len(self.filelist))]
        img_contours = [0 for i in range(len(self.filelist))]
        self.img_count = [0 for i in range(len(img_contours))]
        cnt = 0
        
        self.center_list1 = []
        self.ditect_list1 = []
        
        for i in range(len(self.filelist)):
            #img_list[i] = self.readIMG(self.filelist[i])
            img_contours[i] = self.binIMG(self.readIMG(self.filelist[i]))[0]
        
        video = cv2.VideoCapture(P + 'test_video2.mp4')
        
        while 1:
            ret, v_img = video.read()
            
            if not ret:
                print('Failed open Video')
                break
                
            v_contours = self.binIMG(v_img)
            center_list2 = []
            ditect_list2 = []
            visited = [0 for i in range(len(v_contours))]
            
            for i in range(len(v_contours)):
                pts = v_contours[i]
                if cv2.contourArea(pts) < 1000:
                    continue
                
                rc = cv2.boundingRect(pts)
                
                M = cv2.moments(pts)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                
                if cnt == 0:
                    self.center_list1.append([cx,cy])
                else :
                    center_list2.append([cx,cy])
                
                cv2.drawContours(v_img,[pts],-1,(0,255,255),5)
                for j in range(len(img_contours)):
                    dist = cv2.matchShapes(img_contours[j], pts, cv2.CONTOURS_MATCH_I3, 0.0)
                    if dist < 0.5:
                        cv2.rectangle(v_img, rc, (0, 0, 255), 2)
                        cv2.circle(v_img, (cx, cy), 1, (0,0,255), 3)
                        #cv2.putText(v_img, self.filelist[j][:-4], (rc[0], rc[1]-3), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1, cv2.LINE_AA)
                        if cnt == 0:
                            if visited[i] == 1:
                                if dist < self.ditect_list1[-1][1]:
                                    self.ditect_list1[-1] = [self.filelist[j], dist]
                                    
                            elif visited[i] == 0:
                                self.ditect_list1.append([self.filelist[j], dist]) 
                                visited[i] = 1
                        else:
                            if visited[i] == 1:
                                if dist < ditect_list2[-1][1]:
                                    ditect_list2[-1] = [self.filelist[j], dist]
                         
                            elif visited[i] == 0:
                                ditect_list2.append([self.filelist[j], dist]) 
                                visited[i] = 1
                    else:
                        if cnt == 0:
                            self.ditect_list1.append(['N', dist])
                        else:
                            ditect_list2.append(['N', dist])
                    
            cv2.imshow('Result', v_img)
            
            if cnt == 0:
                cnt += 1
                for i in self.ditect_list1:
                    if i[0] != 'N':
                        self.img_count[self.filelist.index(i[0])] += 1
                print('First : ', self.img_count)
            else:
                self.count(center_list2, ditect_list2)
            
            if cv2.waitKey(40) == 26:
                print('CTRL Z')
                break 
        
        print('Result')
        for i in range(len(self.img_count)):
            print(self.filelist[i][:-4] + " : " + str(self.img_count[i]))
            
        print('End')
        cv2.destroyAllWindows()
            
if __name__ == '__main__':
    cpimg = Test()
    cpimg.Run('s3.jpg')


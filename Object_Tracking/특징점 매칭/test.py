
import cv2 
import os
from matplotlib import pyplot as plt
import numpy as np

MIN_MATCH_COUNT = 10
path = 'C:/Users/HS/Pictures/Image/'

obj = cv2.imread(path + 's3.jpg')
img = cv2.imread(path + 'sample.jpg')

if img is None or obj is None:
    print('Image load failed!')
    os.sys.exit()

obj2 = cv2.cvtColor(obj, cv2.COLOR_BGR2GRAY)
_, obj_bin = cv2.threshold(obj2, 100, 255, cv2.THRESH_BINARY_INV)

gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, img_bin = cv2.threshold(gray_img , 100, 255, cv2.THRESH_BINARY_INV)

cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(img_bin)
img_list = []
pos_list = []

for i in range(1, cnt): 
    (x, y, w, h, area) = stats[i]
    
    # 노이즈 제거
    if area < 10000:
        continue
    
    img_list.append(img_bin[y:y+h, x:x+w])
    pos_list.append((x,y,w,h))
    cv2.circle(img, (int(centroids[i][0]), int(centroids[i][1])), 1, (0,0,255), 3)
    
print('이미지 개수 : ' , len(img_list))

detector = cv2.ORB_create()
kp1, desc1 = detector.detectAndCompute(obj_bin, None)

print('Start')

matcher = [0 for i in range(len(img_list))]
matches = matcher
res1 = []
res2 = []
for i in range(len(img_list)):
    kp2, desc2 = detector.detectAndCompute(img_list[i], None)
    
    matcher[i] = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches[i] = matcher[i].match(desc1, desc2)
    matches[i] = sorted(matches[i], key=lambda x:x.distance)
    
    res1.append(cv2.drawMatches(obj, kp1, img_list[i], kp2, matches[i], None, flags=cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS))
        
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in matches[i] ])
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in matches[i] ])
    
    mtrx, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    matchesMask = mask.ravel().tolist()
    res2.append(cv2.drawMatches(obj, kp1, img_list[i], kp2, matches[i], None, matchesMask = matchesMask, flags=cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS))
     
    accuracy=float(mask.sum()) / mask.size
    print(str(i+1) + "st image accuracy: %d/%d(%.2f%%)"% (mask.sum(), mask.size, accuracy*100))
    if mask.sum() >= MIN_MATCH_COUNT or accuracy >= 0.2:
        cv2.rectangle(img, pos_list[i],(0,0,255),2)
        cv2.putText(img, str(i+1), (pos_list[i][0], pos_list[i][1]-3), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1, cv2.LINE_AA)
    

cv2.imshow('OBJ', obj)
cv2.imshow('IMG', img)

cv2.waitKey()
print("CLOSE")
cv2.destroyAllWindows()

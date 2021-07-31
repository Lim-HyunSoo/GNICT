import open3d
import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt

CALI_PATH = 'Cali_Data/'

def Projection():
    #파일 로드
    img_file = filedialog.askopenfilename(initialdir="/", title="Select file",filetypes=(("jpeg files","*.jpg"), ("all files", "*.*")))
    
    if img_file != '':
        img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)
        pcd_file = filedialog.askopenfilename(initialdir="/", title="Select file",filetypes=(("pcd files","*.pcd"), ("ply files", "*.ply"),("all files", "*.*")))
    else:
        tk.messagebox.showerror("Error", "Fail Open IMG")
        exit()
        
    if pcd_file != '':
        pcd = open3d.io.read_point_cloud(pcd_file)
    else:
        tk.messagebox.showerror("Error", "Fail Open PCD")
        exit()
    
    print("Success Read pcd, img ...........")
    pc = np.asarray(pcd.points)
    points3d = pc
    max_intensity = np.max(points3d[:, -1])
    min_intensity = np.min(points3d[:, -1])
    
    cmap = plt.cm.get_cmap('hsv', 256)
    cmap = np.array([cmap(i) for i in range(256)])[:, :3] * 255
    
    points_num = int(pc.size/3)
    print("포인트 수 : {}".format(pcd.dimension))
    
    #저장된 파라미터 읽어오기 
    intrinsic = np.loadtxt(os.path.join(CALI_PATH, 'intrinsic_mat.txt'), delimiter = ',')
    dist = np.loadtxt(os.path.join(CALI_PATH, 'distortion_mat.txt'), delimiter = ',')
    rot = np.loadtxt(os.path.join(CALI_PATH, 'rot_vec.txt'), delimiter = ',')
    tr = np.loadtxt(os.path.join(CALI_PATH, 'tr_vec.txt'), delimiter = ',')

    extrinsic = np.loadtxt(os.path.join(CALI_PATH, 'extrinsic_mat.txt'), delimiter = ',')
    
    print("Projecting...")
    
    for i in range(points_num):
        if (pc[i,1] > -1) and (pc[i,2] != 0) and (pc[i,2] > 0.3)and (abs(pc[i,0]) < 3) :
            #p = pc[i]
            #tr = tr.reshape(1,3)
            #dist = dist.reshape(1,3)
            
            #dot1 = (np.dot(extrinsic,p) + tr).reshape(-1,1)
            #result = (np.dot(intrinsic, dot1) + dist)
            
            result = cv2.projectPoints(pc[i], rot, tr, intrinsic, dist)[0].squeeze(1)
    
            x = round(result[0,0])
            y = round(result[0,1])
            
            #이미지 크기에 맞는 좌표만 이미지에 투영
            if x >= 0 and y >= 0 and x <= img.shape[1] and y <= img.shape[0]:
                color = cmap[int(pc[i,-1] / max_intensity), :]
                # 중심축을 기준으로 좌우를 확인하기 위해 색깔을 달리해서 융합 
                # 이후에 하나로 할 시 if 문을 없애고 
                # cv2.circle(img, (x,y), 1, color=tuple(color), thickness=-1) 한 줄로 실행시키면 된다. 
                if pc[i,0] <= 0 and pc[i,1] > 3:
                    cv2.circle(img, (x,y), 1, color=tuple(color), thickness = 1)
                    #continue
                elif pc[i,0] > 0 and pc[i,1] > 3:
                    cv2.circle(img, (x,y), 1, color=tuple(color), thickness = 1)
                    #continue
                else :
                    cv2.circle(img, (x,y), 1, color=tuple(color), thickness = 2)              
                   
    print("Projection End...")
    
    
    cv2.imshow('IMG', img)
    cv2.waitKey()
    cv2.destroyAllWindows()

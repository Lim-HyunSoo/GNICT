# Import required modules
import os
import cv2
import numpy as np
import glob

import tkinter as tk

import matplotlib.pyplot as plt
import open3d as o3d

OUSTER_LIDAR = False
PKG_PATH = os.path.dirname(os.path.realpath(__file__))
CALI_PATH = 'Cali_Data/'
        
def isFile(path):
    return os.path.isfile(path)

def save_data(data, filename, folder, is_image = False):
    # Empty data
    if not len(data): return
        
    if not os.path.isdir(folder):
        os.makedirs(os.path.join(PKG_PATH, folder))
        
    # Handle filename
    filename = os.path.join(PKG_PATH, os.path.join(folder, filename))
    
    if is_image:
        cv2.imwrite(filename, data)
        print('Save IMG')    
        return

    #np.save(filename, data)
    np.savetxt(filename, data, fmt = "%.12f", delimiter = ',')

    print('Success Save File')
        
def intrinsic(width, height, size, dirPath, listbox):
    CHECKERBOARD = (width - 1, height - 1)
    
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, size, 0.001)
    
    # Vector for 3D points
    objpoints = []
    
    # Vector for 2D points
    imgpoints = []
    
    # 3D points real world coordinates
    objectp3d = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objectp3d[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    prev_img_shape = None

    jpg_images = glob.glob(os.path.join(dirPath,'*.jpg'))
    png_images = glob.glob(os.path.join(dirPath,'*.png'))
    gif_images = glob.glob(os.path.join(dirPath,'*.gif'))
    
    images = jpg_images + png_images + gif_images
    #print(images)
    
    cnt = 0
    for filename in images:
        image = cv2.imread(filename)
        grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
    	# Find the chess board corners
        try:
            ret, corners = cv2.findChessboardCorners(
        					grayColor, CHECKERBOARD,
        					cv2.CALIB_CB_ADAPTIVE_THRESH
        					+ cv2.CALIB_CB_FAST_CHECK +
        					cv2.CALIB_CB_NORMALIZE_IMAGE)
        except:
            continue
            
    	# If desired number of corners can be detected then,
    	# refine the pixel coordinates and display
    	# them on the images of checker board
        if ret == True:
            objpoints.append(objectp3d)
    
    		# Refining pixel coordinates
    		# for given 2d points.
            corners2 = cv2.cornerSubPix(grayColor, corners, (11, 11), (-1, -1), criteria)
    
            imgpoints.append(corners2)
    
    		# Draw and display the corners
            image = cv2.drawChessboardCorners(image, CHECKERBOARD, corners2, ret)
            
            listbox.delete(cnt,cnt)
            listbox.insert(cnt, str(cnt)+'.png')

            save_data(image, str(cnt)+'.png', CALI_PATH, True)
            
            cnt += 1
        
    h, w = image.shape[:2]
    print(cnt)
    # Perform camera calibration
    ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(
    	objpoints, imgpoints, grayColor.shape[::-1], None, None)
    
    
    distortion = np.array(distortion[0][:4])
    
    save_data(matrix, 'intrinsic_mat.txt', CALI_PATH)
    save_data(distortion, 'distortion_mat.txt', CALI_PATH)
    
    image_path = os.path.join(PKG_PATH, CALI_PATH)
    
    return matrix, distortion, image_path

#이미지에 대한 체커보드 모서리 좌표를 구하기 위한 함수 
def extract_points_2D(img_path, cor):
    print("")
    print("1) Press [left click] to do point picking ")
    print("2) Press [ctrl + z] to undo point picking ")
    print("3) Press [right click] to do save picked point ")
    
    corners = cor
    xdata, ydata = [], []

    img = cv2.imread(img_path) 
    disp = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGB)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('Select 2D Image Points')
    ax.set_axis_off()
    ax.imshow(disp)

    line, = ax.plot(xdata, ydata)

    def onclick(event):
        # button 1 : 마우스 왼쪽 클릭시 클릭한 위치 입력 및 저장 
        if event.button == 1:
            x = event.xdata
            y = event.ydata
                    
            xdata.append(x)
            ydata.append(y)
                        
            corners.append([x,y])
                    
            print("Picked : " , (x,y))
            if len(xdata) > 1:
                line.set_data(xdata,ydata)
                plt.draw()
                
        if event.button == 3:
            # button 3 : 마우스 오른쪽 클릭시 저장 확인 메세지 
            MsgBox = tk.messagebox.askquestion ('Save Corners','Save it?')
            if MsgBox == 'yes':
                print("Result Corners : " ,corners)
                save_data(corners, 'img_corners.txt', CALI_PATH)
                plt.close()
            else:
                print("No")
                    
            
    def onpress(event):
        #print('press', event.key)
        # ctrl + z 입력 시 이전 입력값 삭제
        if event.key == 'ctrl+z':
            xdata.pop()
            ydata.pop()
            line.set_data(xdata, ydata)
            plt.draw()
                    
            if len(corners) > 0:
                del corners[-1]
                print("Current Corners : " , corners)
            
    fig.canvas.mpl_connect('key_press_event', onpress)            
    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
        
#pcd 파일에서 체커보드 모서리를 구하기 위한 함수 
def picked_points_3D(pcd):
    vis = o3d.visualization.VisualizerWithEditing()
    vis.create_window(width = 1020, height = 500)
    vis.add_geometry(pcd)
    vis.run()
    vis.destroy_window()
    
    return vis.get_picked_points()

def extract_points_3D(velodyne, cor):
    if os.path.isfile(velodyne):
    # Extract points data
        pcd = o3d.io.read_point_cloud(velodyne)
    else:
        print("Fail Open PCD...")
        return
    
    print("")
    print("1) Press [shift + left click] to do point picking")
    print("2) Press [shift + right click] to undo point picking")
    print("3) After picking points, press 'Q' to close the window.")
    
    pcd = np.asarray(pcd.points)
    
    #pcd 범위 설정. 단위 m , 0번 인덱스 x(좌우) , 1번 인덱스 y(앞뒤), 2번 인덱스 z(위아래)
    inrange = np.where((np.abs(pcd[:, 0]) < 3) &
                       ((pcd[:, 1]) < 3) &
                       (pcd[:, 1] > -1 ) &
                       (pcd[:, 2] != 0))
    
    pcd = pcd[inrange[0]]
    
    picked_points = cor
    
    pc = o3d.geometry.PointCloud()
    pc.points = o3d.utility.Vector3dVector(pcd)
    
    picked_list = picked_points_3D(pc)
    
    for i in picked_list:
        picked_points.append([pcd[i][0], pcd[i][1], pcd[i][2]])
    
    print(picked_points)
    save_data(picked_points, 'pcd_corners.txt', CALI_PATH)
    
#구해진 intrinsic, 꼭지점 좌표등을 이용해 extrinsic matrix를 계산하는 함수 
def cal_extrinsic():
    #extrinsic matrix를 계산하기 위한 저장된 파라미터 값 로
    cam_path = os.path.join(CALI_PATH, 'intrinsic_mat.txt')
    dist_path = os.path.join(CALI_PATH, 'distortion_mat.txt')
    p2d_path = os.path.join(CALI_PATH, 'img_corners.txt')
    p3d_path = os.path.join(CALI_PATH, 'pcd_corners.txt')
    
    if isFile(cam_path) and isFile(dist_path) and isFile(p2d_path) and isFile(p3d_path):    
        cam = np.loadtxt(cam_path, delimiter = ',')
        dist = np.loadtxt(dist_path, delimiter = ',')
        p_2d = np.loadtxt(p2d_path, delimiter = ',')
        p_3d = np.loadtxt(p3d_path, delimiter = ',')
    else: 
        return 0,0,0

    suc, rot, tr, inliers = cv2.solvePnPRansac(p_3d, p_2d, cam, dist, flags = cv2.SOLVEPNP_ITERATIVE)
    
    p_2d_reproj = cv2.projectPoints(p_3d,rot, tr, cam, dist)[0].squeeze(1)
    
    error = (p_2d_reproj - p_2d)[inliers]
    
    rmse = np.sqrt(np.mean(error[:,0][:,0]**2 + error[:,0][:,1]**2))
    
    cnt = 0
    rmse2 = 0

    while rmse > 1:
        rot2, tr2 = cv2.solvePnPRefineLM(p_3d, p_2d, cam, dist, rot, tr)
        p_2d_reproj2 = cv2.projectPoints(p_3d, rot2, tr2, cam, dist)[0].squeeze(1)
        
        error = (p_2d_reproj - p_2d)[inliers]
    
        rmse = np.sqrt(np.mean(error[:,0][:,0]**2 + error[:,0][:,1]**2))
        
        rot = rot2
        tr = tr2 
        
        if rmse2 == rmse:
            cnt += 1
        else:
            cnt = 0
            
        if cnt > 10:
            rot_mat = cv2.Rodrigues(rot2)[0]
            print('Result rmse : ', rmse)
            print('Result rot : ', rot2)
            print('Result tr : ', tr2)
            print('Result rot_mat : ', rot_mat)
            print('Result proj : ', p_2d_reproj2)
            break
        
        if rmse < 1:
            rot_mat = cv2.Rodrigues(rot2)[0]
            print('Result rmse : ', rmse)
            print('Result rot : ', rot2)
            print('Result tr : ', tr2)
            print('Result rot_mat : ', rot_mat)
            print('Result proj : ', p_2d_reproj2)
            break
        
        rmse2 = rmse
    
    save_data(rot2, 'rot_vec.txt', CALI_PATH)
    save_data(tr2, 'tr_vec.txt', CALI_PATH)
    save_data(rot_mat, 'extrinsic_mat.txt', CALI_PATH)
    
    return rot2, tr2, rot_mat

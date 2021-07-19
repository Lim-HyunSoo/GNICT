import open3d
import cv2
import os
import numpy as np

CALI_PATH = 'Cali_Data/'

def Projection(img_path = None, pcd_path = None):
    
    pcd = open3d.io.read_point_cloud("10.pcd")
    img = cv2.imread("10.jpg", cv2.IMREAD_UNCHANGED)
    
    print("Success Read pcd, img ...........")
    pc = np.asarray(pcd.points)
    points_num = int(pc.size/3)
    print("포인트 수 : {}".format(pcd.dimension))
    
    #cam = np.load(os.path.join(CALI_PATH, 'intrinsic_mat.npy'))
    #dist = np.load(os.path.join(CALI_PATH, 'distortion_mat.npy'))
    #rot = np.load(os.path.join(CALI_PATH, 'rot_vec.npy'))
    #tr = np.load(os.path.join(CALI_PATH, 'tr_vec.npy'))
    
    cam = np.matrix([(1342.49818, 0, 960.0), (0, 1351.351545, 540.0), (0, 0, 1)])
                    
    dist = np.array([-0.0038181, -0.001409, -0.000161, 0.001210])
    
    rot = np.array([(1.38140967e+00), (-4.53283005e-04), (4.77731969e-02)])
    tr = np.array([(-0.12462414), (1.10378111), (1.18725661)])
    
    """
    cam = np.matrix([(1068.057,  0,  911.481), (0,  1064.055,  653.414), (0,  0,  1)])

    dist = np.array([ -0.142020,  0.053378,  0.003663,  -0.011256 ])
    
    rot = np.array([(1.62365552), (0.55388034), (-0.49742148)])
    
    tr = np.array([(-0.07872811), (1.10276954), (0.86437174)])
    """
    coor = np.load(os.path.join(CALI_PATH, 'coor_mat.npy'))
    
    velo_to_cam = np.load(os.path.join(CALI_PATH, 'extrinsic_mat.npy'))
    
    print("Projecting.........")
    
    for i in range(points_num):
        if pc[i,1] > -1 and pc[i,2] > 0.5:
            #p = np.append(pc[i], 1.0)
            #dot1 = np.dot(velo_to_cam,p).reshape(-1,1)
            #dot2 = np.dot(coor, dot1)
            #result = np.dot(cam, dot2)
            result = cv2.projectPoints(pc[i], rot, tr, cam, dist)[0].squeeze(1)
    
            x = round(result[0,0])
            y = round(result[0,1])
            if x >= 0 and y >= 0 and x <= img.shape[1] and y <= img.shape[0]:
                if pc[i,0] <= 0 and pc[i,1] > 1 :
                    #cv2.circle(img, (x,y), 1, (0,200,0), 2)
                    continue
                elif pc[i,0] > 0 and pc[i,1] > 1:
                    #cv2.circle(img, (x,y), 1, (0,0,200), 2)
                    continue
                else :
                    cv2.circle(img, (x,y), 1, (0,200,200), 2)
                    
    print("Projection End")
    
    
    cv2.imshow('IMG', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


# Import required modules
import os
import cv2
import numpy as np
import glob
import matplotlib.cm
import matplotlib.pyplot as plt
import open3d as o3d

OUSTER_LIDAR = False
PKG_PATH = os.path.dirname(os.path.realpath(__file__))
CALI_PATH = 'Cali_Data/'

def save_data(data, filename, folder, is_image = False):
    # Empty data
    if not len(data): return
        
    # Handle filename
    filename = os.path.join(PKG_PATH, os.path.join(folder, filename))
        
    if not os.path.isdir(folder):
        os.makedirs(os.path.join(PKG_PATH, folder))
        
    if is_image:
        cv2.imwrite(filename, data)
        return
    
    """
    # Save points data
    if os.path.isfile(filename):
        data = np.vstack((np.load(filename), data))
    """
    np.save(filename, data)
        
    print('Success Save File')
        
def intrinsic(height, width, size):
    CHECKERBOARD = (height - 1, width - 1)
    
    # stop the iteration when specified
    # accuracy, epsilon, is reached or
    # specified number of iterations are completed.
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, size, 0.001)
    
    # Vector for 3D points
    threedpoints = []
    
    # Vector for 2D points
    twodpoints = []
    
    # 3D points real world coordinates
    objectp3d = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1],	3), np.float32)
    objectp3d[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    prev_img_shape = None
    
    # Extracting path of individual image stored
    # in a given directory. Since no path is
    # specified, it will take current directory
    # jpg files alone
    images = glob.glob('*.jpg')

    for filename in images:
        image = cv2.imread(filename)
        grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
    	# Find the chess board corners
    	# If desired number of corners are
    	# found in the image then ret = true
        ret, corners = cv2.findChessboardCorners(
    					grayColor, CHECKERBOARD,
    					cv2.CALIB_CB_ADAPTIVE_THRESH
    					+ cv2.CALIB_CB_FAST_CHECK +
    					cv2.CALIB_CB_NORMALIZE_IMAGE)
    
    	# If desired number of corners can be detected then,
    	# refine the pixel coordinates and display
    	# them on the images of checker board
        if ret == True:
            threedpoints.append(objectp3d)
    
    		# Refining pixel coordinates
    		# for given 2d points.
            corners2 = cv2.cornerSubPix(grayColor, corners, (11, 11), (-1, -1), criteria)
    
            twodpoints.append(corners2)
    
    		# Draw and display the corners
            image = cv2.drawChessboardCorners(image, CHECKERBOARD, corners2, ret)
            save_data(image, filename, CALI_PATH, True)
            
    h, w = image.shape[:2]
    
    # Perform camera calibration by
    # passing the value of above found out 3D points (threedpoints)
    # and its corresponding pixel coordinates of the
    # detected corners (twodpoints)
    ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(
    	threedpoints, twodpoints, grayColor.shape[::-1], None, None)
    
    
    distortion = np.array(distortion[0][:4])
    
    """
    # Displaying required output
    print(" Camera matrix:")
    print(matrix)
    
    print("\n Distortion coefficient:")
    print(distortion)

    print("\n Rotation Vectors:")
    print(r_vecs)
    
    print("\n Translation Vectors:")
    print(t_vecs)
    """
    save_data(matrix, 'intrinsic_mat.npy', CALI_PATH)
    save_data(distortion, 'distortion_mat.npy', CALI_PATH)
    #return matrix, distortion
    
def extract_points_2D(img_path, rectify=False):
        if os.path.isfile(img_path):
            img = cv2.imread(img_path)
        else:
            print("Fail open IMG")
            return 
        
        disp = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGB)
    
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('Select 2D Image Points')
        ax.set_axis_off()
        ax.imshow(disp)
    
        xdata, ydata, corners = [], [], []
        line, = ax.plot(xdata,ydata)
        
        def onclick(event):
        
            if event.button == 1:
                x = event.xdata
                y = event.ydata
                
                xdata.append(x)
                ydata.append(y)
                
                corners.append((x,y))
                
                print("Picked : " , (x,y))
                if len(xdata) > 1:
                    line.set_data(xdata,ydata)
                    plt.draw()
                    
            # button 3: 마우스 우클릭 시 이전 입력값 삭제
            if event.button == 3:
                xdata.pop()
                ydata.pop()
                line.set_data(xdata, ydata)
                plt.draw()
                
                if len(corners) > 0:
                    del corners[-1]
                    print("Current Corners : " , corners)
            
            if len(corners) > 4:
                print("Result Corners : " ,corners)
                save_data(corners, 'img_corners.npy', CALI_PATH)
                #save_data(disp, 'image_color.jpg', True)
                plt.close()
                
        fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()
        
def extract_points_3D(velodyne):
    if os.path.isfile(velodyne):
    # Extract points data
        pcd = o3d.io.read_point_cloud(velodyne)
    else:
        print("Fail Open PCD...")
        return
    #points = np.asarray(pcd.points)
    
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(pcd)
    vis.run()
    vis.destroy_window()

    """
    if OUSTER_LIDAR: points = points.reshape(-1, 9)[:, :4]
    
    inrange = np.where((abs(points[:, 1]) < 0.3) &
                       (points[:, 2] < 1.5))
    print(len(inrange[0]))
    points = points[inrange[0]]
    print(points[0])
    print(points[444])
    cmap = matplotlib.cm.get_cmap('hsv')
    colors = cmap(points[:, -1] / np.max(points[:, -1]))
    
    # Setup matplotlib GUI
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title('Select 3D LiDAR Points')
    ax.set_axis_off()
    ax.set_facecolor((0, 0, 0))
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], c = colors , s = 10, picker = 5)
    
    # Equalize display aspect ratio for all axes
    max_range = (np.array([points[:, 0].max() - points[:, 0].min(), 
        points[:, 1].max() - points[:, 1].min(),
        points[:, 2].max() - points[:, 2].min()]).max() / 2.0)
    mid_x = (points[:, 0].max() + points[:, 0].min()) * 0.5
    mid_y = (points[:, 1].max() + points[:, 1].min()) * 0.5
    mid_z = (points[:, 2].max() + points[:, 2].min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    # Pick points
    picked, corners = [], []
    def onpick(event):
        ind = event.ind[0]
        #ind = event.ind
        print(ind)
        x, y, z = event.artist._offsets3d
        print(x[0], y[0], z[0])
        print(x[444], y[444], z[444])
        # Ignore if same point selected again
        if picked and (x[ind] == picked[-1][0] and y[ind] == picked[-1][1] and z[ind] == picked[-1][2]):
            print('Return')
            return
        
        # Display picked point
        picked.append((x[ind], y[ind], z[ind]))
        corners.append((x[ind], y[ind], z[ind]))
        print('Picked : ', picked[-1])
        
        line, = ax.plot(x[ind], y[ind],z[ind])
        
        if len(picked) > 1:
            # Draw the line
            temp = np.array(picked)
            #print(temp[:, 0], temp[:, 1], temp[:, 2])
            ax.plot(temp[:, 0], temp[:, 1], temp[:, 2])
            
            #ax.plot(points[:, 0], points[:, 1], points[:, 2])
            ax.figure.canvas.draw_idle()

            # Reset list for future pick events
            del picked[0]
        
    # Display GUI
    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()
    """
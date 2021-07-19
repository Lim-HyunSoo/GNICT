import os
import cv2
import numpy as np
import matplotlib.cm
import matplotlib.pyplot as plt
import Calibration as Cal
import open3d
import tkinter as tk
from tkinter import filedialog
import Projection as Proj

OUSTER_LIDAR = False
PKG_PATH = os.path.dirname(os.path.realpath(__file__))
CALI_PATH = 'Cali_Data/'

class Ex():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GUI-Exam")
        self.root.geometry("720x480")
        
        menu = tk.Menu(self.root)
        
        menu_file = tk.Menu(menu, tearoff = 0)
        menu_file.add_command(label = "New Window")
        menu_file.add_separator()
        menu_file.add_command(label = "Open IMG...")
        menu_file.add_command(label = "Open PCD...")
        menu_file.add_separator()
        menu_file.add_command(label = "Exit")
        """
        menu_cal = tk.Menu(menu, tearoff = 0)
        menu_cal.add_command(label = "Intrinsic...", command = self.Intrinsic)
        menu_cal.add_separator()
        menu_cal.add_command(label = "Extrinsic...", command = self.Select_corners)
        
        menu_cal.add_separator()
        menu_cal.add_command(label = "Cali_Test", command = self.calibration)
        """
        menu.add_cascade(label = "File", menu = menu_file)
        #menu.add_cascade(label = "Calibration", menu = menu_cal)
        
        
        btn_int = tk.Button(self.root, text = "Intrinsic Calibration", command = self.Intrinsic)
        btn_ext = tk.Button(self.root, text = "Extrinsic Calibration", command = self.Extrinsic)
        btn_cali = tk.Button(self.root, text = "Calibration Test", command = self.Calibration)
        
        btn_int.pack()
        btn_ext.pack()
        btn_cali.pack()
        
        self.root.config(menu = menu)
        
        self.root.mainloop()
        
    def Load_IMG(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select file",filetypes=(("jpeg files","*.jpg"), ("all files", "*.*")))
        
        return filename
    
    def Load_PCD(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select file",filetypes=(("pcd files","*.pcd"), ("ply files", "*.ply"),("all files", "*.*")))
        
        return filename
    
    def Intrinsic(self):
        def Cali():
            h = eval(height_ent.get())
            w = eval(width_ent.get())
            s = eval(size_ent.get())
            
            Cal.intrinsic(h,w,s)
            
            root.destroy()
            
        root = tk.Tk()
        root.title("Checkerboard Info")
        root.geometry("300x250")
        
        fr = tk.LabelFrame(root, text = "Size")
        
        width = tk.Label(fr, text = "width")
        width_num = tk.IntVar()
        width_ent = tk.Entry(fr, textvariable = width_num)
        width_ent.insert(10, "7")
        #width_ent.bind("<Return>", calc_width)
        height = tk.Label(fr, text = "height")
        height_num = tk.IntVar()
        height_ent = tk.Entry(fr, textvariable = height_num)
        height_ent.insert(10, "5")
        size = tk.Label(fr, text = "size")
        size_num = tk.IntVar()
        size_ent = tk.Entry(fr, textvariable = size_num)
        size_ent.insert(10, "40")
        
        bt = tk.Button(fr, text = "OK", command = Cali)
        
        width.grid(row = 3, column = 0)
        width_ent.grid(row = 3, column = 1)
        height.grid(row = 4, column = 0)
        height_ent.grid(row = 4, column = 1)
        size.grid(row = 5, column = 0)
        size_ent.grid(row = 5, column = 1)
        
        bt.grid(row = 6, column = 0)
        """
        colors = ["black", "white"]
        for i in range(eval(height_ent.get())):
            for j in range(eval(width_ent.get())):
                checker = tk.Label(fr, width = 6, height = 3, bg = colors[(i+j)%2])
                checker.grid(row = i+1, column = j)
        """
        fr.pack(side = "left", fill = "both", expand = True)
        
        
        root.mainloop()
            
    def Extrinsic(self):
        img = self.Load_IMG()
        pcd = self.Load_PCD()
        
        if (img != None) and (pcd != None):
            Cal.extract_points_2D(img)
            Cal.extract_points_3D(pcd)
        else :
            print("Fail Open File")
            
    def save_data(self, data, filename, folder):
        # Empty data
        if not len(data): return
        
        # Handle filename
        filename = os.path.join(PKG_PATH, os.path.join(folder, filename))
        
        if not os.path.isdir(folder):
            os.makedirs(os.path.join(PKG_PATH, folder))
    
        """
        # Save points data
        if os.path.isfile(filename):
            data = np.vstack((np.load(filename), data))
        """
        np.save(filename, data)
        
        print('Success Save File')
    
    def Calibration(self, points2D=None, points3D=None):
        # Load corresponding points
        folder = os.path.join(PKG_PATH, CALI_PATH)
        if points2D is None: points2D = np.load(os.path.join(folder, 'img_corners.npy'))
        
        #print(points2D)
        #print(np.load(os.path.join(folder, 'intrinsic_mat.npy')))
        #print(np.load(os.path.join(folder, 'distortion_mat.npy')))
        #if points3D is None: points3D = np.load(os.path.join(folder, 'pcd_corners.npy'))
        Proj.Projection()
        
def extract_points_3D(pcd):
    # Extract points data
    points = np.asarray(pcd.points)
    
    if OUSTER_LIDAR: points = points.reshape(-1, 9)[:, :4]
    
    #inrange = np.where((abs(points[:,0]) < 0.2) & (abs(points[:, 1]) < 0.5) & (abs(points[:,2]) < 1.4) &(points[:,2] != 0))
    inrange = np.where((points[:,0] > -0.2) & (points[:,0] < 0.1) & (points[:,2] != 0) & (abs(points[:, 1]) < 0.5) & (points[:,2] > 1.1) & (points[:,2] < 1.3))
    points = points[inrange[0]]

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
        print(points[ind])
        x, y, z = event.artist._offsets3d
        
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


if __name__ == '__main__':
    #print(PKG_PATH)
    
    #ex = Ex()
    #Cal.intrinsic(5,7,40)
    
    pcd = open3d.io.read_point_cloud("test.pcd")
    extract_points_3D(pcd)

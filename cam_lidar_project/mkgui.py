import os
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import glob

import cv2
import open3d as o3d

import Calibration as cali
import Projection as proj 

OUSTER_LIDAR = False
PKG_PATH = os.path.dirname(os.path.realpath(__file__))
CALI_PATH = 'Cali_Data/'

class Cali_Tool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GUI-Exam")
        self.root.geometry("260x100")
        self.int_dirpath = ''
        self.ext_dirPath = ''
        self.img_corners = []
        self.pcd_corners = []
        
        menu = tk.Menu(self.root)
        
        menu_file = tk.Menu(menu, tearoff = 0)
        menu_file.add_command(label = "New Window")
        menu_file.add_separator()
        menu_file.add_command(label = "Open IMG...", command = self.img_visualize)
        menu_file.add_command(label = "Open PCD...", command = self.pcd_visualize)
        menu_file.add_separator()
        menu_file.add_command(label = "Exit", command = self.on_closing)

        menu.add_cascade(label = "File", menu = menu_file)
        
        btn_int = tk.Button(self.root, text = "Intrinsic Calibration", command = self.Intrinsic)
        btn_ext = tk.Button(self.root, text = "Extrinsic Calibration", command = self.Extrinsic)
        btn_proj = tk.Button(self.root, text = "Cam_LiDAR_Fusion Test", command = self.Fusion)
        
        btn_int.pack()
        btn_ext.pack()
        btn_proj.pack()
        
        self.root.config(menu = menu)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def __del__(self):
        print("DEL")
            
    def isFile(self, path):
        return os.path.isfile(path)

    def on_closing(self):
        print('Destroy')
        self.root.destroy()
        self.root.quit()
        
    def Load_IMG(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select file",filetypes=(("jpeg files","*.jpg"), ("all files", "*.*")))
        
        return filename
    
    def Load_PCD(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select file",filetypes=(("pcd files","*.pcd"), ("ply files", "*.ply"),("all files", "*.*")))
        
        return filename
    
    def Fail_Load(self, isIMG = False):
        if isIMG:
            tk.messagebox.showerror("Error", "Fail Open IMG")
            
        else :
            tk.messagebox.showerror("Error", "Fail Open PCD")
    
    def img_visualize(self):
        filename = self.Load_IMG()
        
        if filename != '':
            img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
            #print(img.shape)
            cv2.imshow("IMG", img)
            
            cv2.waitKey()
            cv2.destroyAllWindows()
        
    def pcd_visualize(self):
        filename = self.Load_PCD()
        
        if filename != '':
            pcd = o3d.io.read_point_cloud(filename)
            
            vis = o3d.visualization.VisualizerWithEditing()
            vis.create_window()
            vis.add_geometry(pcd)
            vis.run()
            vis.destroy_window()
        
    def Intrinsic(self):
        def on_closing():
            rt.destroy()
            rt.quit()
        
        def Load():
            root = tk.Tk() 
            root.withdraw() 
            self.int_dirPath = filedialog.askdirectory(parent=root, initialdir="/", title='폴더를 선택해주세요.')
            
            if self.int_dirPath != '':
                file_list = os.listdir(self.int_dirPath)
                
                if img_listbox.size() > 0:
                    for i in range(img_listbox.size()):
                        img_listbox.delete(0)
                        
                cnt = 0
                for i in file_list:
                    img_listbox.insert(cnt, i)
                    cnt += 1
            else:
                print('Fail open Folder...')
            
        def CurSelect(evt):
            value = str((img_listbox.get(img_listbox.curselection())))
            
            src = cv2.imread(os.path.join(self.int_dirPath, value))
            src = cv2.resize(src, (1000, 700))
            
            img = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            global imgtk
            imgtk = ImageTk.PhotoImage(image=img)
            
            label.config(image = imgtk)
            
            
        def Cali():
            if img_listbox.size() > 0:
                h = eval(h_ent.get())
                w = eval(w_ent.get())
                s = eval(size_ent.get())
                
                i_mat, d_mat, self.int_dirPath = cali.intrinsic(w,h,s, self.int_dirPath, img_listbox)
                
                win = tk.Tk()
                win.title("Result")
                
                tk.Label(win, text = " Camera Matrix(Intrinsic Matrix) ").pack()
                tk.Label(win, text = str(i_mat)).pack()
                tk.Label(win, text = " Distortion Matrix ").pack()
                tk.Label(win, text = str(d_mat)).pack()
            else: 
                tk.messagebox.showerror("Error", " Please Load IMG ")
                
        def create_checker():
            if (h_ent.get() != None) and (w_ent.get() != None):
                win = tk.Tk()
                win.title("Checker Board")
                
                colors = ["black", "white"]
                for i in range(eval(h_ent.get())):
                    for j in range(eval(w_ent.get())):
                        checker = tk.Label(win, width = 6, height = 3, bg = colors[(i+j)%2])
                        checker.grid(row = i+1, column = j)
                        
                    
        rt = tk.Toplevel()
        rt.title("Intrinsic Calibration")
        rt.geometry("1260x720")
        
        m_fr = tk.Frame(rt, width = 200, height = 700)
        m_fr.pack(side = "left", fill = "both")
        
        bt = tk.Button(m_fr, text = "Load IMG", command = Load)
        bt.grid(row = 1)
        
        img_listbox = tk.Listbox(m_fr, selectmode = "single", height = 0)
        img_listbox.bind('<Double-Button-1>', CurSelect)
        
        img_listbox.grid(row = 2)
        
        info_fr = tk.Frame(m_fr)
        info_fr.grid(row = 3)
        
        w = tk.Label(info_fr, text = "width")
        w.grid(row = 1, column = 0)
        w_num = tk.StringVar()
        w_ent = tk.Entry(info_fr, textvariable = w_num, width = 10)
        w_ent.insert(0, "7")
        w_ent.grid(row = 1, column = 1)
        
        h = tk.Label(info_fr, text = "height")
        h.grid(row = 2, column = 0)
        h_num = tk.StringVar()
        h_ent = tk.Entry(info_fr, textvariable = h_num, width = 10)
        h_ent.insert(0, "5")
        h_ent.grid(row = 2, column = 1)
        
        size = tk.Label(info_fr, text = "size")
        size.grid(row = 3, column = 0)
        size_num = tk.StringVar()
        size_ent = tk.Entry(info_fr, textvariable = size_num, width = 10)
        size_ent.insert(0, "40")
        size_ent.grid(row = 3, column = 1)
        
        view_ch = tk.Button(m_fr, text = "View CheckerBoard", command = create_checker)
        view_ch.grid(row = 4)
        
        cal_bt = tk.Button(m_fr, text = "Calculate", command = Cali)
        cal_bt.grid(row = 5)
        
        img_fr = tk.Frame(rt, width = 1000, height = 700)
        img_fr.config(bg = 'white')
        img_fr.pack(side = "right", fill = "both", expand = True)
        
        label = tk.Label(img_fr)
        label.pack(side = 'top')
        
        rt.protocol("WM_DELETE_WINDOW", on_closing)
        rt.mainloop()
        
    def Extrinsic(self):
        def on_closing():
            rt.destroy()
            rt.quit()
            
        def img_ext():
            if self.isFile(os.path.join(CALI_PATH,'img_corners.txt')):
                MsgBox = tk.messagebox.askquestion ('Already exists','img_corners Already exists, Do you want to save new?')
                if MsgBox == 'yes':
                    pass
                else:
                    self.img_corners = np.load(os.path.join(CALI_PATH,'img_corners.txt')).tolist()
                    print(self.img_corners)
                
            root = tk.Tk() 
            root.withdraw()
            self.ext_dirPath = filedialog.askdirectory(parent=root, initialdir="/", title='폴더를 선택해주세요.')
            
            if os.path.isdir(self.ext_dirPath):
                jpg_images = glob.glob(os.path.join(self.ext_dirPath,'*.jpg'))
                png_images = glob.glob(os.path.join(self.ext_dirPath,'*.png'))
                gif_images = glob.glob(os.path.join(self.ext_dirPath,'*.gif'))
    
                images_list = jpg_images + png_images + gif_images
                if img_listbox.size() > 0:
                    img_listbox.delete(0, img_listbox.size()-1)
                        
                cnt = 0
                for i in images_list:
                    img_listbox.insert(cnt, i)
                    cnt += 1
            else:
                print("Fail open IMG...")
                return 
    
                
        def pcd_ext():
            if self.isFile(os.path.join(CALI_PATH,'pcd_corners.txt')):
                MsgBox = tk.messagebox.askquestion ('Already exists','pcd_corners Already exists, Do you want to save new?')
                if MsgBox == 'yes':
                    pass
                else:
                    self.pcd_corners = np.load(os.path.join(CALI_PATH,'pcd_corners.txt')).tolist()
                    print(self.pcd_corners)
                
            root = tk.Tk() 
            root.withdraw()
            self.ext_dirPath = filedialog.askdirectory(parent=root, initialdir="/", title='폴더를 선택해주세요.')
            
            if os.path.isdir(self.ext_dirPath):
                pcds = glob.glob(os.path.join(self.ext_dirPath,'*.pcd'))

                if pcd_listbox.size() > 0:
                    pcd_listbox.delete(0, img_listbox.size()-1)
                    
                cnt = 0
                for i in pcds:
                    pcd_listbox.insert(cnt, i)
                    cnt += 1
            else:
                print("Fail open PCD...")
                return 
        
        def calculate():
            rot_vec, tr_vec, rot_mat = cali.cal_extrinsic()
            
            tk.Label(fr2, text = " Rotation Vector ").pack()
            tk.Label(fr2, text = str(rot_vec)).pack()
            tk.Label(fr2, text = "  Translation Vector ").pack()
            tk.Label(fr2, text = str(tr_vec)).pack()
            tk.Label(fr2, text = " Extrinsic Matrix ").pack()
            tk.Label(fr2, text = str(rot_mat)).pack()
        
        def imgSelect(evt):
            value = str((img_listbox.get(img_listbox.curselection())))
            cali.extract_points_2D(os.path.join(self.ext_dirPath, value), self.img_corners)
            
        def pcdSelect(evt):
            value = str((pcd_listbox.get(pcd_listbox.curselection())))
            cali.extract_points_3D(os.path.join(self.ext_dirPath, value), self.pcd_corners)
            
        rt = tk.Tk()
        rt.title("Extrinsic Calibration")
        rt.geometry("400x400")
        
        fr = tk.Frame(rt)
        fr.pack(side = 'left')
        
        bt = tk.Button(fr, text = "IMG", command = img_ext)
        bt2 = tk.Button(fr, text = "PCD", command = pcd_ext)
        bt3 = tk.Button(fr, text = "Calculate", command = calculate)
        
        img_listbox = tk.Listbox(fr, selectmode = "single", height = 0)
        img_listbox.bind('<Double-Button-1>', imgSelect)
        
        pcd_listbox = tk.Listbox(fr, selectmode = "single", height = 0)
        pcd_listbox.bind('<Double-Button-1>', pcdSelect)
        
        bt.pack()
        bt2.pack()
        bt3.pack()
        img_listbox.pack()
        pcd_listbox.pack()
        
        fr2 = tk.LabelFrame(rt, text = 'Result', height = 10)
        fr2.pack(side = 'right')
                
        rt.protocol("WM_DELETE_WINDOW", on_closing)
        rt.mainloop()
    
    def Fusion(self):
        proj.Projection()
        
def main():
    Cali_Tool()
    
    
    

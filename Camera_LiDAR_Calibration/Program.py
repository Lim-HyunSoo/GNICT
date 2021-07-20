import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk

import numpy as np
import matplotlib.cm
import matplotlib.pyplot as plt

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
        self.root.geometry("720x480")
        self.int_dirpath = ''
        
        menu = tk.Menu(self.root)
        
        menu_file = tk.Menu(menu, tearoff = 0)
        menu_file.add_command(label = "New Window")
        menu_file.add_separator()
        menu_file.add_command(label = "Open IMG...")
        menu_file.add_command(label = "Open PCD...", command = self.pcd_visualize)
        menu_file.add_separator()
        menu_file.add_command(label = "Exit", command = self.on_closing)

        menu.add_cascade(label = "File", menu = menu_file)
        
        btn_int = tk.Button(self.root, text = "Intrinsic Calibration", command = self.Intrinsic)
        btn_ext = tk.Button(self.root, text = "Extrinsic Calibration", command = self.Extrinsic)
        #btn_cali = tk.Button(self.root, text = "Calibration Test", command = self.Calibration)
        
        btn_int.pack()
        btn_ext.pack()
        #btn_cali.pack()
        
        self.root.config(menu = menu)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def __del__(self):
        print("DEL")
        
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
    
    def pcd_visualize(self):
        filename = self.Load_PCD()
        
        pcd = o3d.io.read_point_cloud(filename)
        
        vis = o3d.visualization.Visualizer()
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
            #print(os.path.join(self.int_dirPath, value))
            
            src = cv2.imread(os.path.join(self.int_dirPath, value))
            src = cv2.resize(src, (1000, 700))
            
            img = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            global imgtk
            imgtk = ImageTk.PhotoImage(image=img)
            
            label.config(image = imgtk)
            
            
        def Cali():
            h = eval(h_ent.get())
            w = eval(w_ent.get())
            s = eval(size_ent.get())
            
            global i_mat , d_mat
            
            i_mat, d_mat = cali.intrinsic(w,h,s, self.int_dirPath)
            
            i_lb.config(text = "Camera Matrix : " + i_mat)
            d_lb.config(text = "Distortion Matrix : " + d_mat)
            
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
        w_num = tk.IntVar()
        w_ent = tk.Entry(info_fr, textvariable = w_num)
        w_ent.insert(0, "7")
        w_ent.grid(row = 1, column = 1)
        
        h = tk.Label(info_fr, text = "height")
        h.grid(row = 2, column = 0)
        h_num = tk.IntVar()
        h_ent = tk.Entry(info_fr, textvariable = h_num)
        h_ent.insert(0, "5")
        h_ent.grid(row = 2, column = 1)
        
        size = tk.Label(info_fr, text = "size")
        size.grid(row = 3, column = 0)
        size_num = tk.IntVar()
        size_ent = tk.Entry(info_fr, textvariable = size_num)
        size_ent.insert(0, "40")
        size_ent.grid(row = 3, column = 1)
        
        cal_bt = tk.Button(m_fr, text = "Calculate", command = Cali)
        cal_bt.grid(row = 4)
        
        i_lb = tk.Label(m_fr, text = '').grid(row = 5)
        d_lb = tk.Label(m_fr, text = '').grid(row = 6)
        
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
            img = self.Load_IMG()
            
            if (img != ""):
                cali.extract_points_2D(img)
            else :
                self.Fail_Load(True)
            
        def pcd_ext():
            pcd = self.Load_PCD()
            
            if (pcd != ""):
                cali.extract_points_3D(pcd)
            else :
                self.Fail_Load()
                
        rt = tk.Tk()
        rt.title("Extrinsic Calibration")
        rt.geometry("300x250")
        
        bt = tk.Button(rt, text = "IMG", command = img_ext)
        bt2 = tk.Button(rt, text = "PCD", command = pcd_ext)
        bt3 = tk.Button(rt, text = "Calculate", command = cali.cal_extrinsic)
        
        bt.pack()
        bt2.pack()
        bt3.pack()
        
        rt.protocol("WM_DELETE_WINDOW", on_closing)
        rt.mainloop()
        
def main():
    Cali_Tool()
    
if __name__ == "__main__":
    main()
    
    

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 10:25:05 2024

@author: sshenoy
"""

import os
import sys
from glob import glob
from datetime import datetime

# import pyds9 as ds9
from astropy.io import fits

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QDesktopWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QFrame,
    # QLineEdit,
    QWidget,
    # QDialog,
    QDialogButtonBox,
    QFileDialog
    )

# import matplotlib
# matplotlib.use("TkAgg")
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
import pandas as pd


class MainWindow(QMainWindow):

    DESCRIPTION = """
    Class used to view the downloaded *rate.jpg file and select the file to 
    be used as input to generate flats. If there are lot of files to view 
    then the user can view a subset of files and continue with the rest at 
    a latter time. This fclass tags the view status and the selection 
    status. Files once viewed will not be view at a latter time by default 
    but the user can override it.  
    """

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Select MIRI Imager Data")
        
        self.set_kwargs()
        
        self.initUI()
    
    def set_kwargs(self):
        if len(sys.argv) == 1:
            # self.inpaths = 
            self.set_input_directory()
        else:
            self.inpaths = sys.argv[1:]
        
        self.df = self.get_data_frame(self.inpaths)
        self.num_files = len(self.df)
        
        self.cur_index = 0
        self.index_str = "File {} of {}"
        
        self.cur_file = self.df['Filename'][self.cur_index].split('/')[-1]
        self.file_str = "Filename: {}"
        
        # self.cur_hdr = fits.getheader(self.cur_file)
        self.cur_view = self.df['Viewed'][self.cur_index]
        self.view_str = "Viewed: {}"
        
        self.cur_stat = self.df['Selected'][self.cur_index]
        self.stat_str = "Selected: {}"
        
        self.outpath = self.set_output()
        
    
    def initUI(self):
        
        sizeObject = QDesktopWidget().screenGeometry(-1)
        self.setGeometry(int(sizeObject.width()/2)-320, 0, 640, 480)
        
        widget = QWidget()
        self.setCentralWidget(widget)
        
        layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()
        
        info_layout = QGridLayout()
        info_layout.setAlignment(Qt.AlignTop)
        info_layout.setContentsMargins(12, 12, 12, 12)
        info_layout.setSpacing(44)
        
        info_label = QLabel("File Information")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setFont(QFont("Helvetica", 18, QFont.Bold))
        self.info_label = info_label
        
        indx_label = QLabel(self.index_str.format(self.viewed+self.cur_index+1,
                                                  self.num_files))
        # indx_label = QLineEdit(self.index_str.format(self.cur_index+1,
        #                                           self.num_files))
        # indx_label.returnPressed.connect(self.on_text_changed)
        self.indx_label = indx_label
        
        file_label = QLabel(self.file_str.format(self.cur_file))
        self.file_label = file_label
        
        view_label = QLabel(self.view_str.format(self.cur_view))
        self.view_label = view_label
        
        stat_label = QLabel(self.stat_str.format(self.cur_stat))
        self.stat_label = stat_label
        
        info_layout.addWidget(self.info_label)
        info_layout.addWidget(self.indx_label)
        info_layout.addWidget(self.file_label)
        info_layout.addWidget(self.view_label)
        info_layout.addWidget(self.stat_label)
        
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel | QFrame.Raised)
        
        
        frame.setLayout(info_layout)
        
        layout2.addWidget(frame)
        
        # load_button = QPushButton("Load")
        # load_button.clicked.connect(self.load_clicked)
        # self.load_button = load_button
        
        next_button = QPushButton("Next")
        next_button.clicked.connect(self.next_clicked)
        self.next_button = next_button
        
        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(self.prev_clicked)
        self.prev_button = prev_button
        
        save_button = QPushButton("Save Selection")
        save_button.clicked.connect(self.save_clicked)
        
        slct_button = QPushButton("Select")
        slct_button.clicked.connect(self.slct_clicked)
        self.slct_button = slct_button
        
        uslt_button = QPushButton("Unselect")
        uslt_button.clicked.connect(self.uslt_clicked)
        self.uslt_button = uslt_button
        
        maft_button = QPushButton("Save Manifest")
        maft_button.clicked.connect(self.maft_clicked)
        
        quit_button = QPushButton("Quit", self)
        quit_button.clicked.connect(QApplication.instance().quit)
        
        button_layout = QGridLayout()
        button_layout.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        # button_layout.addWidget(load_button, 0, 0)
        button_layout.addWidget(uslt_button, 0, 1)
        button_layout.addWidget(prev_button, 1, 0)
        button_layout.addWidget(slct_button, 1, 1)
        button_layout.addWidget(next_button, 1, 2)
        button_layout.addWidget(save_button, 2, 0)
        button_layout.addWidget(quit_button, 2, 1)
        button_layout.addWidget(maft_button, 2, 2)
        
        layout2.addLayout(button_layout)
        layout1.addLayout(layout2)
        
        imag_label = QLabel()
        pixmap = QPixmap(self.df['Filename'][self.cur_index])
        # pixmap = QPixmap()
        scl_pm = pixmap.scaled(600, 600 , Qt.KeepAspectRatio)
        imag_label.setPixmap(scl_pm)
        self.imag_label = imag_label
        
        # self.ds9 = ds9.DS9()
        # self.ds9.set(f"file {self.df['Filename'][self.cur_index]}")
        # self.ds9.set("zoom to fit")
        
        # top_layout = QHBoxLayout()
        # top_layout.addWidget(indx_label)
        
        # layout3.addLayout(top_layout)
        layout3.addWidget(imag_label)
        
        layout1.addLayout(layout3)

        
        widget.setLayout(layout1)
        
        self.setCentralWidget(widget)

       
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_S or event.key() == Qt.Key_Down:
            self.slct_clicked()
        elif event.key() == Qt.Key_P or event.key() == Qt.Key_Left:
            self.prev_clicked()
        elif event.key() == Qt.Key_N or event.key() == Qt.Key_Right:
            self.next_clicked()
        elif event.key() == Qt.Key_U or event.key() == Qt.Key_Up:
            self.uslt_clicked()
            
    
    def set_input_directory(self):
        open_dlg = QFileDialog()
        inpath = open_dlg.getExistingDirectory(self, "Load data Directory")
        
        self.inpaths = [inpath]
        
        # return self.inpaths
        
        
    def set_output(self, dirname=None):
        if dirname is None:
            outpath = os.getcwd()
        else:
            outpath = os.path.join(os.getcwd(), dirname)
        
        if not os.path.isdir(outpath):
            os.makedirs(outpath)
        
        return outpath

    
    def get_data_frame(self, inpaths):
        
        filelist = []
        for path in inpaths:

            pth = os.path.abspath(path)
            
            if os.path.isdir(pth):
                flist = glob(os.path.join(pth, '*rate.jpg'))
                flist.sort()
                filelist.extend(flist)
                in_dict = {"Filename": filelist,
                           "Viewed": [False for fl in filelist],
                           "Selected": [False for fl in filelist]}
                
                df = pd.DataFrame(in_dict)
                self.viewed = 0
            elif os.path.isfile(pth):
                df_unsorted = pd.read_csv(pth)
                df = df_unsorted.sort_values(by=["Viewed"]).reset_index(drop=True).copy()
                self.viewed = len(df["Viewed"][df["Viewed"]==True]) - 1
            else:
                print("\n Input directory or file not found.")
                print(" Existing ......")
                sys.exit()

        return df
    
    
    def update_image(self):
        self.cur_istr = self.index_str.format(str(self.viewed+self.cur_index+1),
                                              self.num_files)
        self.cur_file = self.df['Filename'][self.cur_index].split('/')[-1]
        self.cur_fstr = self.file_str.format(self.cur_file)
        self.cur_vstr = self.view_str.format(self.df['Viewed'][self.cur_index])
        self.cur_sstr = self.stat_str.format(self.df['Selected'][self.cur_index])
        
        self.indx_label.setText(self.cur_istr)
        self.file_label.setText(self.cur_fstr)
        self.view_label.setText(self.cur_vstr)
        self.stat_label.setText(self.cur_sstr)
        
        # self.ds9.set(f"file {self.df['Filename'][self.cur_index]}")
        
        pixmap = QPixmap(self.df['Filename'][self.cur_index])
        scl_pm = pixmap.scaled(600, 600, Qt.KeepAspectRatio)
        self.imag_label.setPixmap(scl_pm)
    
    
    def on_text_changed(self):
        new_inx_str = self.indx_label.text()
        new_idx = int(new_inx_str.split(' ')[1]) - 1
        if new_idx >= 0 and new_idx <= self.num_files - 1:
            self.cur_index = new_idx
            self.update_image()
        else:
            msg = "\n Invaid index: {}".format(int(new_inx_str.split(' ')[1]))
            print(msg)
            print(" Index should be between {} and {}".format(1,self.num_files))
        

    def next_clicked(self):
        self.df.loc[self.cur_index, 'Viewed'] = True
        if self.cur_index < self.num_files - 1:
            self.cur_index = self.cur_index + 1
            self.update_image()
        else:
            print("\n This is the last file. Please use the previous ")
            print(" button (or Key p/left-arrow) to view files")
        
        
    def prev_clicked(self):
        self.df.loc[self.cur_index, 'Viewed'] = True
        if self.cur_index > 0:
            self.cur_index = self.cur_index - 1
            self.update_image()
        else:
            print("\n You are already at the first file. Please use")
            print(" the next button (or Key n/right-arrow) to view files.")


    def slct_clicked(self):
        self.df.loc[self.cur_index, 'Selected'] = True
        self.next_clicked()
        
        
    def uslt_clicked(self):
        self.df.loc[self.cur_index, 'Selected'] = False
        self.next_clicked()
        
        
    def save_clicked(self, usr_input=False):
        time_str = datetime.now().strftime("%Y-%m-%dT%H%M%S")
        
        tmp_fname = os.path.join(self.outpath, 
                                 "selected_input_"+time_str+".csv")
        
        print("\n Saving selected data to csv file...")
        
        if usr_input is False:
            self.df.to_csv(tmp_fname, index=False)
        else:
            fl_dlg = QFileDialog()
            out_fname, _ = fl_dlg.getSaveFileName(self, "Save Select File",
                                                      tmp_fname)
            if out_fname == "":
                print("\n\tFile Not Saved. Exiting.....")
            else:
                self.df.to_csv(out_fname, index=False)
            
        
    def maft_clicked(self):
        mani_df = self.df.copy()
        fname_col = mani_df['Filename'].str.replace('jpg', 'fits').str.replace('rate', 'uncal')
        mani_lst =list(fname_col[mani_df['Selected']==True])
        
        fname = os.path.join(self.outpath, 'manifest.lst')
        
        fl_dlg = QFileDialog()
        outfile, _ = fl_dlg.getSaveFileName(self, "Save Manifest", fname)
        
        if outfile == "":
            print("\n Manifest Not Saved.")
        else:
            with open(outfile, 'w+') as f:
                for line in mani_lst:
                    f.write(line+'\n')
        
    
    def closeEvent(self, event):
        self.save_clicked(usr_input=True)
        event.accept()  
        

# class CloseDialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
        
#         self.setWindowTitle("Save File?")
        
#         QBtn = QDialogButtonBox().Yes | QDialogButtonBox().No
        
#         self.buttonBox = QDialogButtonBox(QBtn)
#         self.buttonBox.accepted.connect(self.accept)
#         self.buttonBox.rejected.connect(self.reject)
        
#         layout = QVBoxLayout()
#         message = QLabel("Do you wnat to save the select data file?")
#         layout.addWidget(message)
#         layout.addWidget(self.buttonBox)
#         self.setLayout(layout)
        
        
        
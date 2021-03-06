import numpy as np
import h5py
import os
from PyQt5.QtWidgets import (QWidget, QToolTip,
    QPushButton, QApplication, QMessageBox, QDesktopWidget,QMainWindow,
QAction, qApp, QMenu, QTreeWidget, QVBoxLayout, QLabel,
                QTableWidget, QTreeWidgetItem, QTableWidgetItem,
)
from PyQt5.QtGui import QFont ,  QIcon
from PyQt5.QtCore import Qt, pyqtSlot,QSize
from PyQt5 import QtCore, QtGui
#import PyQt5.QtWidgets as QtGui
import logging
logger = logging.getLogger(__name__)
try:
    from py4xs.hdf import h5exp,h5xs,lsh5
    from py4xs.data2d import Data2d,Axes2dPlot,DataType
except:
    logger.warning('The package py4xs is not installed. Please contact LIX beamline for more information.' )


class aboutWindow(QMessageBox):
    def __init__(self, parent=None):
        super(aboutWindow, self).__init__(parent)
        self.setWindowTitle('About XSH5View')
        self.setText('''
This is a working project for the development of GUI for the visulization of HDF files.
Ver0: Developed by Dr. Yugang Zhang@CHX, NSLS-II
      This version is dedicated to view XPCS results in a particluar HDF format generated by pyCHX package developed at CHX beamline, NSLS-II, BNL.
      The bottons designed for XPCS include plot_g2, show_C12, etc.
Ver1: Collaborated with Dr. JiLiang Liu@LIX, NSLS-II 
      This version applies for the visulizaiton of a general HDF format, such as LIX h5 format and CFN scattering data format
      Developed plot wedges specific to different data format, which can be selected by an option button
Please contact Dr. Yugang Zhang by yuzhang@bnl.gov and Jiliang Liu by jiliang@bnl.gov by for more information.
NOTE: We are not responsible for any issues that may arise from the use of this code, including any loss of data etc.
        ''')

class plotOptionWindow(QWidget):
    def __init__(self, parent=None):
        super(plotOptionWindow, self).__init__(parent)
        self.setWindowTitle('Plot Options')

class tree(QWidget):
    '''Copied from Jiliang's Github:
        https://github.com/ligerliu/pyH5_GUI/blob/master/pyH5_GUI/NewTree.py
    '''
    (FILE,FILE_PATH,H5GROUP) = range(3)
    def __init__(self):
        super().__init__()
        self.title = 'Tree of h5 data'
        self.left = 10
        self.top = 10
        self.width = 720
        self.height = 640

        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)

        self.datalayout= QVBoxLayout()
        self.tree = QTreeWidget()
        header = QTreeWidgetItem(['File'])
        self.tree.setHeaderItem(header)
        self.datalayout.addWidget(self.tree)
        self.group_root = None
    def clear(self):
        self.tree.clear()
        
    def add_group( self, group):          
        self.group_name =  os.path.basename(  group    )
        self.group_file_path = group  
        self.group_root = QTreeWidgetItem(self.tree,[self.group_name,self.group_file_path,''])           

    def add_file(self,h5file, group = None ):
        self.h5_file_path = h5file
        self.f = h5py.File(h5file,'r')
        self.filename = self.f.filename.split('/')[-1]
        
        if group is None:
            self.tree_root = QTreeWidgetItem(self.tree,[self.filename,self.h5_file_path,'']) 
            self.add_branch(self.tree_root,self.f)
        else:
            #print('add group here')
            if self.group_root is None:
                self.add_group( group )      
            hdf_branch =  QTreeWidgetItem( [self.filename,  self.h5_file_path,''] )
            print( self.filename,self.h5_file_path )  
            self.group_root.addChild(  hdf_branch  )  
            
            self.add_branch( hdf_branch ,  self.f)
        self.tree.setColumnWidth(0,250)
        self.tree.setColumnWidth(1,0)
        self.tree.setColumnWidth(2,0)

    def add_branch(self,tree_root,h5file):
        for _ in h5file.keys():
            #print(_)
            branch = QTreeWidgetItem([str(h5file[_].name).split('/')[-1],
                                      str(self.h5_file_path),
                                      str(h5file[_].name)])
            tree_root.addChild(branch)
            if 	isinstance(h5file[_],h5py.Group):
                self.add_branch(branch,h5file[_])

    @pyqtSlot(QTreeWidgetItem,int)
    def onItemClicked(self,item):
        print(self.filename,item.text(2))
        


class titledTable():
    def __init__(self, title):
        self.title = QLabel(title)
        self.table = QTableWidget()
        self.table.setShowGrid(True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.table)


    def clear(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.table.clear()


    def set_item(self, row, col, item):
        if isinstance(item, str):
            self.table.setItem(row, col,  QTableWidgetItem(item))
        else:
            print("Type Error: Item must be a str")


    def num_cols(self, values):
        value_shape = np.shape(values)
        numcols = 1

        if len(value_shape) > 1:
            numcols = value_shape[1]

        return numcols



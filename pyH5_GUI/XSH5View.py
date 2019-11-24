import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QWidget, QToolTip,
    QPushButton, QApplication, QMessageBox, QDesktopWidget,QMainWindow,
QAction, qApp, QMenu, QGridLayout, QTreeWidget,  QTreeWidgetItem, QTableWidget,
 QLabel,  QTableWidgetItem,   QInputDialog, QLineEdit,  QHBoxLayout,    QCheckBox,
 QComboBox,  QActionGroup, QDialog,)
from PyQt5.QtGui import QFont ,  QIcon
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui
import PyQt5.QtWidgets as QtGui
import functools as ft
import h5py
import H5Tree as ht
from PyQt5.QtCore import pyqtSlot
import pyqtgraph as pg
import pyqtgraph.opengl as gl

pg.setConfigOptions( imageAxisOrder = 'row-major')
import pandas as pds
import logger
#pg.setConfigOption('background', 'w')
#pg.setConfigOption('foreground', 'k')
import logging
logger = logging.getLogger(__name__)
try:
    from py4xs.hdf import h5exp,h5xs,lsh5
    from py4xs.data2d import Data2d,Axes2dPlot,DataType
except:
    logger.warning('The package py4xs is not installed. Please contact LIX beamline for more information.' )
import sip
#from chx_format import *
from Plot import *
 

class mainWindow(QMainWindow):
    def __init__(self):
        super(mainWindow, self).__init__() 
        
        self.full_filename_dict = {}  # {    full_filename:  group_name   }
        self.group_name_dict = {}  #group name dict, not necessary now?
        self.current_full_filename = None  #current selected full filename
        self.current_hdf5 = None   #open(  self.current_full_filename, r )
        self.current_hdf5_item = None 
        self.current_group_name = None
        self.current_base_filename = ''  #current selected   base filename
        self.current_item_path = ''      #current item full path. /io/md/...
        self.current_item_name = ''      #current selected item name  md
        
        self.legend = None           
        self.values = np.array([])
        self.logX_plot = False
        self.logY_plot = False
        
        self.X = None        
        self.guiplot_count=0
        self.image_plot_count=0
        self.plot_type= 'curve'
        
        self.colormap_string = 'jet'
        self.colorscale_string = 'log'
        self.show_image_data = False
        self.attributes_flag=False
        self.current_selected_HDF = ''
        self.dataset_type_list =  [ 'CFN','LiX', 'CHX', ]
        self.default_dataset_type =  'CFN'
        self.current_dataset_type =  'CFN'
        
        #########################Tobecleaned
        self.image_data_keys = ['avg_img', 'mask', 'pixel_mask', 'roi_mask', 'g12b']
        self.pds_keys = [ 'g2_fit_paras','g2b_fit_paras', 'spec_km_pds', 'spec_pds', 'qr_1d_pds'] 
        #####################       
        
        self.PWT= PlotWidget(self)
        self.initialise_user_interface()
        
        
    def initialise_user_interface(self):
        '''
        Initialises the main window. '''
        
        
        grid = QGridLayout()
        grid.setSpacing(10)
        self.grid=grid
        #self.file_items_list = ht.titledTree('File Tree')
        self.file_items_list = ht.tree()
        self.file_items_list_property={}
        self.file_items_list.tree.itemClicked.connect(self.item_clicked)
        #self.file_items_list.tree.itemDoubleClicked.connect(self.item_double_clicked)         
        # Make dataset table
        self.dataset_table = ht.titledTable('Values')        
        # Make attribute table
        self.attribute_table =ht.titledTable('Attribute') # QTableWidget()
        self.attribute_table.table.setShowGrid(True)        
        #dataset type to set buttons layout
        self.dataset_type_obj_string = self.default_dataset_type         
        # Initialise all buttons
        self.open_button = self.add_open_button()
        self.dataset_type_box = self.add_dataset_type_box()
        self.plot_curve_button = self.add_plot_curve_button()
        self.plot_img_button = self.add_plot_img_button()
        self.plot_surface_button = self.add_plot_surface_button()        
        self.setX_button = self.add_setX_button()
        self.resetX_button = self.add_resetX_button()
        self.setlogX_box = self.add_setlogX_box()
        self.setlogY_box = self.add_setlogY_box()
        #self.clr_plot_checkbox = self.add_clr_plot_box()
        self.clr_plot_button = self.add_clr_plot_button()
        self.resizeEvent = self.onresize
        # Add 'extra' window components
        self.make_menu_bar()
        self.filename_label =  QLabel('H5FileName')
        ## Add plot window
        self.guiplot = pg.PlotWidget()
        #self.guiplot = pg.ImageView()        
        # Add the created layouts and widgets to the window
        grid.addLayout(self.open_button,        1, 0, 1, 1,  QtCore.Qt.AlignLeft)       
        grid.addLayout(self.dataset_type_box,    1, 0, 1, 1, QtCore.Qt.AlignRight)
        grid.addLayout(self.plot_curve_button,   1, 1, 1, 1,QtCore.Qt.AlignLeft)
        grid.addLayout(self.plot_img_button,     1, 2, 1, 1,QtCore.Qt.AlignLeft)
        grid.addLayout(self.plot_surface_button, 1, 3, 1, 1,QtCore.Qt.AlignLeft)
        grid.addLayout(self.clr_plot_button,     1, 4, 1, 1, QtCore.Qt.AlignLeft)  
        grid.addLayout(self.setX_button, 1, 8, 1, 1,QtCore.Qt.AlignLeft)
        grid.addLayout(self.resetX_button, 2, 8, 1, 1,QtCore.Qt.AlignLeft)  
        
        grid.addLayout(self.setlogX_box, 1, 7, 1, 1,QtCore.Qt.AlignLeft)
        grid.addLayout(self.setlogY_box, 2, 7, 1, 1,QtCore.Qt.AlignLeft)  
        
        grid.addWidget(self.filename_label, 2, 0, 1, 1)
        #filename list
        #grid.addLayout(self.file_items_list.layout, 4, 0, 3, 1)
        grid.addLayout(self.file_items_list.datalayout, 4, 0, 3, 1)
        #data dataset table
        grid.addLayout(self.dataset_table.layout, 4, 1, 1, 8)
        ## Add guiplot window
        grid.addWidget(self.guiplot, 5,  1,  4,   8 ) 
        # attribute tabel
        grid.addLayout(self.attribute_table.layout, 7, 0, 2, 1)
        #grid.addWidget(self.attribute_table, 7, 0, 2, 1 )  
        self.dev_cur_layout(   plot_type ='curve' )       
        self.dev_cur_layout(   plot_type ='image' )    
        self.setCentralWidget( QWidget(self))        
        self.centralWidget().setLayout(grid)   
        # Other tweaks to the window such as icons etc
        self.setWindowTitle('XSH5View--Ver1')
        #QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))  
        self.initialise_layout() #to add different type of layout based on self.dataset_type_obj_string
    
    ########Start Deal with layout
    def initialise_layout(self):  
        if self.dataset_type_obj_string == 'CFN':  
            self.delete_dataset_buttons( 'CHX' )            
        elif self.dataset_type_obj_string == 'LIX':  
            self.delete_dataset_buttons( 'CHX' ) 
        elif self.dataset_type_obj_string == 'CHX':    
            self.dev_dataset_buttons( self.dataset_type_obj_string )              
        else:
            pass
        
    def dev_cur_layout( self, plot_type ):
        if plot_type in plot_curve_type:
            self.CurCrossHair=QLabel( )
            self.CurCrossHair.setAlignment(Qt.AlignRight|Qt.AlignVCenter)          
            self.grid.addWidget(self.CurCrossHair, 9, 2, 1,1 ) 
            self.CrossHair_type = 'curve'
        elif plot_type in plot_image_type:        
            self.imageCrossHair=QLabel()
            self.imageCrossHair.setAlignment(Qt.AlignRight|Qt.AlignVCenter) 
            self.grid.addWidget(self.imageCrossHair, 9, 1, 1,1 )  
            self.CrossHair_type = 'image'
        else:
            self.CrossHair_type = 'None'
             
    def delete_cur_layout( self, plot_type ):
        if plot_type in plot_curve_type:
            try:
                self.deleteLayout( self.imageCrossHair )              
            except:
                pass
        elif plot_type in plot_image_type: 
            try:            
                self.deleteLayout( self.CurCrossHair  )  
            except:
                pass
        else:
            pass 
        
    def dev_dataset_buttons( self, dataset_type):
        if dataset_type == 'CHX':
            self.plot_g2_button = self.add_plot_g2_button()
            self.plot_c12_button = self.add_plot_c12_button()
            self.q_box_input = self.add_q_box(   )
            self.plot_qiq_button = self.add_plot_qiq_button()               
            self.grid.addLayout(self.plot_g2_button,      2, 1, 1, 1,QtCore.Qt.AlignLeft)
            self.grid.addLayout(self.plot_c12_button,     2, 2, 1, 1,QtCore.Qt.AlignLeft)
            self.grid.addLayout(self.plot_qiq_button,     2, 3, 1, 1, QtCore.Qt.AlignLeft)
            self.grid.addLayout(self.q_box_input,         2, 6, 1, 1, QtCore.Qt.AlignLeft)            
    def delete_dataset_buttons( self, dataset_type):
        if dataset_type == 'CHX'  and self.current_dataset_type =='CHX':
            self.deleteLayout( self.plot_g2_button )             
            self.deleteLayout( self.plot_c12_button )
            self.deleteLayout(  self.plot_qiq_button )
            self.deleteLayout(  self.q_box_input  )         
    def deleteLayout(self, layout):
        for i in range(layout.count()):
            layout.itemAt(i).widget().close()
    ########End Deal with layout  
    def onresize(self, event):
        print('Here for resize')
        self.file_items_list.tree.setMaximumWidth(0.3*self.width())
        #self.dataset_table.table.setMinimumHeight(0.1*self.height())
        #self.dataset_table.table.setMaximumWidth( 0.3*self.height() )
        self.attribute_table.table.setMaximumWidth(0.3*self.width())
        self.guiplot.setMinimumHeight( 0.6*self.height() )
        #self.guiplot.setMinimumHeight( 0.6*self.height() )
    def add_open_button(self):
        '''
        Initialises the buttons in the button bar at the top of the main window. '''
        open_file_btn =  QPushButton('Open')
        open_file_btn.clicked.connect(self.choose_file)
        button_section =  QHBoxLayout()
        button_section.addWidget(open_file_btn)
        #button_section.addStretch(0)
        return button_section      
    def add_dataset_type_box(self):
        self.dataset_type_obj = QComboBox()
        self.dataset_type_obj.addItems( self.dataset_type_list )
        self.dataset_type_obj.currentIndexChanged.connect( self.dataset_type_selection_change  )
        self.dataset_type_obj_string = self.dataset_type_obj.currentText()
        box_section = QHBoxLayout()
        box_section.addWidget(self.dataset_type_obj)        
        return box_section     
    
    def  dataset_type_selection_change( self, i  ):
        self.dataset_type_obj_string = self.dataset_type_obj.currentText()
        self.initialise_layout()
        self.current_dataset_type = self.dataset_type_obj.currentText()
        #print( self.dataset_type_obj_string , self.dataset_type_obj.currentText() )

        
    def add_plot_g2_button(self):
        return self.add_generic_plot_button( plot_type = 'g2',  button_name='Plot_g2')
    def add_plot_c12_button(self):
        return self.add_generic_plot_button( plot_type = 'C12',  button_name='Plot_TwoTime')
    
    
    def add_plot_curve_button(self):
        return self.add_generic_plot_button( plot_type = 'curve',  button_name='Plot_Curve')
    def add_plot_qiq_button(self):
        return self.add_generic_plot_button( plot_type = 'qiq',  button_name='Plot_qiq')    
    def add_plot_img_button(self):
        return self.add_generic_plot_button( plot_type = 'image',  button_name='Plot_Image')
    def add_plot_surface_button(self):
        return self.add_generic_plot_button( plot_type = 'surface',  button_name='Plot_Surface')
        

    def add_generic_plot_button(self, plot_type, button_name):
        plot_btn =  QPushButton( button_name)        
        plot_type_dict = {'curve': self.PWT.plot_curve,
                         'g2': self.PWT.plot_g2,
                         'qiq': self.PWT.plot_qiq,
                         'surface': self.PWT.plot_surface,
                         'image': self.PWT.plot_image,
                         'C12': self.PWT.plot_C12,
                         }  
        plot_btn.clicked.connect(  plot_type_dict[plot_type]  )
        button_section =  QHBoxLayout()
        button_section.addWidget(plot_btn)
        return button_section    

    def add_setlogX_box(self):
        self.setlogX_box_obj =   QCheckBox("logX" )
        self.setlogX_box_obj.stateChanged.connect( self.click_setlogX_box )
        button_section =  QHBoxLayout()
        button_section.addWidget(self.setlogX_box_obj )
        return button_section
    def click_setlogX_box (self, state):
        if state == QtCore.Qt.Checked:
            self.logX_plot = True 
        else:
            self.logX_plot = False
        try:
            self.guiplot.setLogMode( x=self.logX_plot,  y=self.logY_plot) 
        except:
            pass               
    def add_setlogY_box(self):
        self.setlogY_box_obj =   QCheckBox("logY" )
        self.setlogY_box_obj.stateChanged.connect( self.click_setlogY_box )
        button_section =  QHBoxLayout()
        button_section.addWidget(self.setlogY_box_obj )
        return button_section
    def click_setlogY_box (self, state):
        if state == QtCore.Qt.Checked:
            self.logY_plot = True  
        else:
            self.logY_plot = False   
        try:
            self.guiplot.setLogMode( x=self.logX_plot,  y=self.logY_plot) 
        except:
            pass   
            
            
    def get_dict_from_qval_dict( self ):
        l = list( self.current_hdf5['qval_dict'].attrs.items() )
        dc = { int(i[0]):i[1] for i in l }
        return dc


    def add_setX_button(self):
        self.setX_btn =  QPushButton('SetX')
        self.setX_btn.clicked.connect(self.setX)
        button_section =  QHBoxLayout()
        button_section.addWidget(self.setX_btn)
        return button_section
    def add_resetX_button(self):
        self.resetX_btn =  QPushButton('ReSetX')
        self.resetX_btn.clicked.connect(self.resetX)
        button_section =  QHBoxLayout()
        button_section.addWidget(self.resetX_btn)
        return button_section
    def add_clr_plot_button(self):
        self.clr_plot_button =   QPushButton("clear plot" )
        self.clr_plot_button.clicked.connect(self.guiplot_clear)
        button_section =  QHBoxLayout()
        button_section.addWidget(self.clr_plot_button )
        return button_section

    def guiplot_clear(self):
        if self.plot_type in ['curve', 'g2', 'qiq']:
            self.guiplot.clear()
            self.guiplot_count=0
            try:
                for item in self.legend.items:
                    self.legend.removeItem(item)
            except:
                pass
        elif self.plot_type in [ 'image']:
            self.guiplot.clear()
            self.guiplot_count=0
        elif self.plot_type in [ 'surface']:
            pass
        try:
            lts = self.guiplot.plotItem.legend.items
            for t in lts:
                self.guiplot.removeItem( t )
        except:
            pass
    def add_q_box( self ):
        # Create textbox
        self.q_box = QLineEdit(   placeholderText="Please enter q-number (int) of two-time function."  )
        button_section =  QHBoxLayout()
        button_section.addWidget(self.q_box )
        return button_section
    def make_menu_bar(self):
        '''
        Initialises the menu bar at the top. '''
        menubar = self.menuBar()
        # Create a File menu and add an open button
        self.file_menu = menubar.addMenu('&File')
        open_action = QtGui.QAction('&Open', self)
        open_action.setShortcut('Ctrl+o')
        open_action.triggered.connect(self.choose_file)
        self.file_menu.addAction(open_action)
        # Add an exit button to the file menu
        exit_action = QtGui.QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Z')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtGui.qApp.quit)
        self.file_menu.addAction(exit_action)
        ## Create a view manu
        self.view_menu = menubar.addMenu('&View')
        #self.view_menu.setShortcut('Alt+v')
        self.image_plot_options_menu = self.view_menu.addMenu('&Image Plot Options')
        self.colormap_options_menu = self.image_plot_options_menu.addMenu('&Colormap')
        group = QActionGroup(    self.colormap_options_menu )
        texts = ["default",  "jet", 'jet_extended', 'albula', 'albula_r', 'goldish', "viridis", 'spectrum', 'vge', 'vge_hdr',  ]
        for text in texts:
            action = QAction(text, self.colormap_options_menu, checkable=True, checked=text==texts[1])
            self.colormap_options_menu.addAction(action)
            group.addAction(action)
        group.setExclusive(True)
        group.triggered.connect(self.onTriggered_colormap)
        self.colorscale_options_menu = self.image_plot_options_menu.addMenu('&ColorScale')
        group = QActionGroup(    self.colorscale_options_menu )
        texts = ["linear", "log" ]
        for text in texts:
            action = QAction(text, self.colormap_options_menu, checkable=True, checked=text==texts[1])
            self.colorscale_options_menu.addAction(action)
            group.addAction(action)
        group.setExclusive(True)
        group.triggered.connect(self.onTriggered_colorscale)
        self.display_image_data_options_menu = self.view_menu.addMenu('&Display Image Data')
        show_image_data_action = QAction('show data', self, checkable=True, checked=False)
        show_image_data_action.triggered.connect(self.onTriggered_show_image_data)
        self.display_image_data_options_menu.addAction(  show_image_data_action  )
        # Create a Help menu and add an about button
        help_menu = menubar.addMenu('&Help')
        about_action = QtGui.QAction('About XSH5FView', self)
        about_action.setStatusTip('About this program')
        about_action.triggered.connect(self.show_about_menu)
        help_menu.addAction(about_action)
        
    def onTriggered_show_image_data(self, action):
        #print(action.text())
        self.show_image_data = action #.text()
    def onTriggered_colormap(self, action):
        #print(action.text())
        self.colormap_string = action.text()
    def onTriggered_colorscale(self, action):
        #print(action.text())
        self.colorscale_string = action.text()
    def show_about_menu(self):
        '''
        Shows the about menu by initialising an about_window object. This class is described in _window_classes.py '''
        self.about_window = ht.aboutWindow()        
        self.about_window.show()
        
        
    def choose_file(self):
        '''
        Opens a QFileDialog window to allow the user to choose the hdf5 file they would like to view. '''
        full_filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                '/home/yugang/Desktop/XPCS_GUI/TestData/test.h5', filter='*.hdf5 *.h5 *.lst')[0]
        ext = full_filename.split('/')[-1].split('.')[-1]
        if ext == 'lst':
            full_filename_list =  np.loadtxt( full_filename, dtype= object, )
            group_name = full_filename.split('/')[-1]
            if group_name not in list( self.group_name_dict.keys() ):
                self.group_name_dict[ group_name ] = full_filename_list
            for fp in full_filename_list:
                self.initiate_file_open(fp, group_name=group_name)
        else:
            self.initiate_file_open(full_filename)
            
    def initiate_file_open(self, full_filename, group_name=None):
        base_filename = full_filename.split('/')[-1]
        self.full_filename_dict[ full_filename ] =  group_name 
        self.dataset_table.clear()
        self.attribute_table.clear()  
        try:
            self.file_items_list.add_file( full_filename, group_name  ) 
            if group_name is None:
                 self.filename_label.setText(  base_filename )
            else:
                 self.filename_label.setText(  group_name ) 
            self.setWindowTitle('XSH5View@CHX - ' +  base_filename )
        except:
            self.filename = '' # if it didn't work keep the old value
            self.filename_label.setText('')
            self.setWindowTitle('XSH5View@CHX')
            self.clear_file_items()
            self.dataset_table.clear()
            self.attribute_table.clear()
            print("Error opening file")
        
    def clear_file_items(self):
        self.file_items_list.clear()

    def get_selected_row_col( self ):
        selected_items = self.dataset_table.table.selectedItems()
        shape = np.shape(self.value)
        Ns = len(shape)
        if len(selected_items) > 0:
            min_row = selected_items[0].row()
            max_row = selected_items[-1].row() + 1
            min_col = selected_items[0].column()
            max_col = selected_items[-1].column() + 1
            self.selected_flag = True
        else:
            if len(shape) == 1:
                max_col = 1
            else:
                max_col = shape[1]
            min_row = 0
            max_row = shape[0]
            min_col = 0
            self.selected_flag = False
        self.min_row, self.max_row, self.min_col, self.max_col=min_row, max_row, min_col, max_col

    def setX(self ):
        self.get_selected_row_col(  )
        min_row, max_row, min_col, max_col = self.min_row, self.max_row, self.min_col, self.max_col
        if self.selected_flag:
            try:
                self.X = self.value[ min_row:max_row, min_col ]
            except:
                self.X = self.value[ min_row:max_row  ]
    def resetX(self ):
        self.X=None    
            
    def get_filename_selected(self):
        self.dataset_table.clear()        
        self.item = self.file_items_list.tree.currentItem()  
        self.current_full_filename = self.item.text(1)   
        self.current_group_name = self.full_filename_dict[ self.current_full_filename  ]
        self.current_hdf5 = h5py.File(self.current_full_filename,'r')
        self.current_base_filename = self.current_full_filename.split('/')[-1]
        self.current_item_path  = self.item.text(2)            
        if self.current_item_path == '':
            self.current_hdf5_item = self.current_hdf5
            self.current_item_name  = self.item.text(2)
        else:
            self.current_hdf5_item = self.current_hdf5[self.current_item_path]
            self.current_item_name  = self.item.text(2).split('/')[-1]  
        
    def display_dataset(self):
        self.get_filename_selected()
        text = self.current_item_path  #self.item.text(2)
        if self.current_item_path != '':
            hdf5_file  = self.current_hdf5_item
            if isinstance(hdf5_file, h5py.Dataset):
                print( 'shows dataset-------------->')
                self.group_data = False
                #self.current_dataset = self.item_path.split('/')[-1]				
                shape = hdf5_file.shape
                Ns = len(shape)
                if Ns==0:
                    try:
                        self.value =  bstring_to_string(  hdf5_file   )#[0]
                    except:
                        self.value =   np.array( [ hdf5_file ] )  #[0]
                    numrows = 1
                    numcols = 1
                elif Ns ==1:
                    numrows = shape[0]
                    numcols = 1	
                    self.value =  hdf5_file[:]						  
                elif Ns ==2:
                    numrows = shape[0]
                    numcols = shape[1]	
                    self.value =  hdf5_file[:]
                elif Ns>=3:  #a 3D array, [x,y,z], show [x,y ]                    
                    if self.current_dataset_type == 'CHX':
                        numrows = shape[0]
                        numcols = shape[1]
                        try:
                            self.value =  hdf5_file[:,:,self.qth]
                        except:
                            print('The max q-th is %s.'%shape[2])
                            self.value =  hdf5_file[text][:,:,0]
                    else:
                        numrows = shape[-2]
                        numcols = shape[-1]
                        try:
                            self.value =  hdf5_file[self.qth,:,:]
                        except:
                            print('The max q-th is %s.'%shape[0])

            elif   isinstance(hdf5_file, h5py.Group):
                print('display the group data here')
                if text in self.pds_keys:
                    d = pds.read_hdf( self.filename, key= text )#[:]
                    self.value =  np.array( d )
                    shape = self.value.shape
                    numrows = shape[0]
                    numcols = shape[1]
                    Ns = len(shape)
                    self.group_data_label=	np.array( d.columns )[:]
                    self.group_data = True
                else:
                    self.dataset_table.clear()
                    self.value = np.array([])
                    self.plot_btn.hide()
            else:
                print( 'Other format!')
            try:
                self.dataset_table.table.setRowCount(numrows)
                self.dataset_table.table.setColumnCount(numcols)
                show_data_flag = True
                if not self.show_image_data:
                    if text  in self.image_data_keys:
                        self.dataset_table.clear()
                        show_data_flag = False
                    try:
                        if self.value.shape[0]>100 and self.value.shape[1]>100:
                            show_data_flag=False
                    except:
                            pass   
                if show_data_flag:                    
                    if Ns!=-1:
                        for i in range(numrows):
                            if numcols > 1:
                                for j in range(numcols):
                                    self.dataset_table.set_item(i, j, str( self.value[i,j]))
                            else:
                                self.dataset_table.set_item(i, 0, str( self.value[i]))
                #print( self.attributes_flag  )
                if not self.attributes_flag:                    
                    self.attribute_table.clear()
                    self.attribute_table.table.setRowCount(1)
                    self.attribute_table.table.setColumnCount(Ns+1)
                    self.attribute_table.table.setItem( 0, 0, QTableWidgetItem( 'shape' ))
                    for i,s in enumerate( shape ):
                        self.attribute_table.table.setItem( 0, i+1, QTableWidgetItem( '%s'%s )) 
            except:
                pass                
                
    def display_attributes(self):
        # reset the value
        self.attribute_table.clear()
        self.get_filename_selected()
        if self.current_item_path != '':    
            print('Here shows the attributes')
            hdf5_file  =   self.current_hdf5_item
            try:
                attributes = list(hdf5_file.attrs.items())
                num_attributes = len(attributes)
                self.attribute_table.table.setRowCount(num_attributes)
                self.attribute_table.table.setColumnCount(0)
            except:
                num_attributes = 0       
            
            if num_attributes > 0:
                self.attribute_table.table.setColumnCount(2)
                self.attributes_flag=True
            else:
                self.attributes_flag=False
            print(   num_attributes,  self.attributes_flag )   
            # Populate the table
            for i in range(num_attributes):
                value = attributes[i][1]
                self.attribute_table.table.setItem(i, 0, QTableWidgetItem(attributes[i][0]))
                if isinstance(value, np.ndarray):
                    N = len(value)
                    self.attribute_table.table.setColumnCount(N+1)
                    j = 1
                    for v in value:
                        self.attribute_table.table.setItem(i, j, QTableWidgetItem(str(v)))
                        #self.attribute_table.setItem(i, 1, QTableWidgetItem(str(value[0].decode())))
                        j+=1
                else:
                    self.attribute_table.table.setItem(i, 1, QTableWidgetItem(str(value)))

    def item_double_clicked(self):
        '''
        Responds to a double click on an item in the file_items_list.'''
         
        #self.display_attributes()
        try:
            self.display_attributes()
            #print('display attributes')
        except:
            pass 
 
    def item_clicked(self):
        
        #############
        #self.display_dataset()
        #################3
        
        try:
            self.qth = int(  self.q_box.text() )
        except:
            self.qth = 0              
        try:
            self.display_attributes()            
            #print('display attributes')
        except:
            pass  
        try:
            self.display_dataset()
        except:
            pass                 
        try:
             
            self.filename_label.setText(   self.current_base_filename     )
            self.setWindowTitle('XSH5View@CHX - ' +  self.current_full_filename  )
        except:
            pass
        #self.display_attributes()

def main():
    app = QApplication(sys.argv)
    pyhdfview_window = mainWindow()
    pyhdfview_window.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()




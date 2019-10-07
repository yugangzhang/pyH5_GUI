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
from ColorMap import (cmap_cyclic_spectrum, cmap_jet_extended, cmap_vge, cmap_vge_hdr,
                      cmap_albula, cmap_albula_r,cmap_hdr_goldish , color_map_dict )
pg.setConfigOptions( imageAxisOrder = 'row-major')
import pandas as pds
#pg.setConfigOption('background', 'w')
#pg.setConfigOption('foreground', 'k')
class mainWindow(QMainWindow):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.filename_dict = {}
        self.hdf5_file_dict = {}
        self.file_items_dict = {}
        self.text = ''
        self.values = np.array([])
        self.current_dataset = ''
        self.file_items = []
        self.X = None
        self.guiplot_count=0
        self.gui_popplot_count =0
        self.image_plot_count=0
        self.image_popplot_count=0
        self.plot_type= 'curve'
        self.pop_plot = False
        self.legend = None
        self.colormap_string = 'jet'
        self.colorscale_string = 'log'
        self.show_image_data = False
        self.attributes_flag=False
        self.image_data_keys = ['avg_img', 'mask', 'pixel_mask', 'roi_mask', 'g12b']
        self.pds_keys = [ 'g2_fit_paras','g2b_fit_paras', 'spec_km_pds', 'spec_pds', 'qr_1d_pds'] 
        self.initialise_user_interface()
        
    def initialise_user_interface(self):
        '''
        Initialises the main window. '''
        grid = QGridLayout()
        grid.setSpacing(10)
        self.file_items_list = ht.titledTree('File Tree')
        self.file_items_list_property={}
        self.file_items_list.tree.itemClicked.connect(self.item_clicked)
        #self.file_items_list.tree.itemDoubleClicked.connect(self.item_double_clicked)
         
        # Make dataset table
        self.dataset_table = ht.titledTable('Values')
        # Make attribute table
        self.attribute_table =  QTableWidget()
        self.attribute_table.setShowGrid(True)
        # Initialise all buttons
        self.pop_plot_box = self.add_pop_plot_box()
        self.open_button = self.add_open_button()
        self.plot_curve_button = self.add_plot_curve_button()
        self.plot_img_button = self.add_plot_img_button()
        self.plot_surface_button = self.add_plot_surface_button()
        self.plot_g2_button = self.add_plot_g2_button()
        self.plot_c12_button = self.add_plot_c12_button()
        self.setX_button = self.add_setX_button()
        self.resetX_button = self.add_resetX_button()
        self.q_box_input = self.add_q_box(   )
        #self.clr_plot_checkbox = self.add_clr_plot_box()
        self.clr_plot_button = self.add_clr_plot_button()
        self.plot_qiq_button = self.add_plot_qiq_button()
        self.resizeEvent = self.onresize
        # Add 'extra' window components
        self.make_menu_bar()
        self.filename_label =  QLabel('H5FileName')
        ## Add plot window
        self.guiplot = pg.PlotWidget()
        #self.guiplot = pg.ImageView()
        self.imageCrossHair=QLabel()
        self.imageCrossHair.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        # Add the created layouts and widgets to the window
        grid.addLayout(self.open_button,        1, 0, 1, 1,  QtCore.Qt.AlignLeft)
        grid.addLayout(self.plot_curve_button,   1, 1, 1, 1,QtCore.Qt.AlignLeft)
        grid.addLayout(self.plot_img_button,     1, 2, 1, 1,QtCore.Qt.AlignLeft)
        grid.addLayout(self.plot_surface_button, 1, 3, 1, 1,QtCore.Qt.AlignLeft)
        grid.addLayout(self.clr_plot_button,     1, 4, 1, 1, QtCore.Qt.AlignLeft)
        #grid.addLayout(self.pop_plot_box,        1, 5, 1, 1, QtCore.Qt.AlignLeft)
        grid.addLayout(self.plot_g2_button,      2, 1, 1, 1,QtCore.Qt.AlignLeft)
        grid.addLayout(self.plot_c12_button,     2, 2, 1, 1,QtCore.Qt.AlignLeft)
        grid.addLayout(self.plot_qiq_button,     2, 3, 1, 1, QtCore.Qt.AlignLeft)
        grid.addLayout(self.q_box_input,         2, 6, 1, 1, QtCore.Qt.AlignLeft)
        #grid.addLayout(self.plot_img_button, 1, 3, 1, 1,QtCore.Qt.AlignLeft)
        grid.addLayout(self.setX_button, 1, 8, 1, 1,QtCore.Qt.AlignLeft)
        grid.addLayout(self.resetX_button, 2, 8, 1, 1,QtCore.Qt.AlignLeft)
        #grid.addLayout(self.box_input, 2, 3, 1, 1, QtCore.Qt.AlignRight)
        grid.addWidget(self.filename_label, 2, 0, 1, 1)
        #filename list
        grid.addLayout(self.file_items_list.layout, 4, 0, 3, 1)
        #data dataset table
        grid.addLayout(self.dataset_table.layout, 4, 1, 1, 8)
        ## Add guiplot window
        grid.addWidget(self.guiplot, 5,  1,  4,   8 )
        grid.addWidget(self.imageCrossHair, 9, 1, 1,1 )
        # attribute tabel
        grid.addWidget(self.attribute_table, 7, 0, 2, 1 )
        self.setCentralWidget( QWidget(self))
        self.centralWidget().setLayout(grid)
        # Other tweaks to the window such as icons etc
        self.setWindowTitle('XSH5View@CHX,NSLS-II--Ver0')
        #QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.grid = grid
    def onresize(self, event):
        self.file_items_list.tree.setMaximumWidth(0.3*self.width())
        #self.dataset_table.table.setMinimumHeight(0.1*self.height())
        #self.dataset_table.table.setMaximumHeight( 0.2*self.height() )
        self.guiplot.setMinimumHeight( 0.6*self.height() )

    def add_open_button(self):
        '''
        Initialises the buttons in the button bar at the top of the main window. '''
        open_file_btn =  QPushButton('Open')
        open_file_btn.clicked.connect(self.choose_file)
        button_section =  QHBoxLayout()
        button_section.addWidget(open_file_btn)
        #button_section.addStretch(0)
        return button_section
    def add_plot_g2_button(self):
        return self.add_generic_plot_button( plot_type = 'g2',  button_name='Plot_g2')
    def add_plot_curve_button(self):
        return self.add_generic_plot_button( plot_type = 'curve',  button_name='Plot_Curve')
    def add_plot_qiq_button(self):
        return self.add_generic_plot_button( plot_type = 'qiq',  button_name='Plot_qiq')
    def add_plot_img_button(self):
        return self.add_generic_plot_button( plot_type = 'image',  button_name='Plot_Image')
    def add_plot_c12_button(self):
        return self.add_generic_plot_button( plot_type = 'C12',  button_name='Plot_TwoTime')
    def add_plot_surface_button(self):
        return self.add_generic_plot_button( plot_type = 'surface',  button_name='Plot_Surface')
    def add_generic_plot_button(self, plot_type, button_name):
        plot_btn =  QPushButton( button_name)
        plot_type_dict = {'curve':self.plot_curve,
                         'g2':self.plot_g2,
                         'qiq':self.plot_qiq,
                         'surface':self.plot_surface,
                         'image':self.plot_image,
                         'C12':self.plot_C12,
                         }
        plot_btn.clicked.connect(  plot_type_dict[plot_type]  )
        button_section =  QHBoxLayout()
        button_section.addWidget(plot_btn)
        return button_section
    def plot_curve( self ):
        try:
            return self.plot_generic_curve( 'curve' )
        except:
            pass
    def plot_g2( self ):
        try:
            return self.plot_generic_curve( 'g2' )
        except:
            pass
    def plot_qiq( self ):
        try:
            return self.plot_generic_curve( 'qiq' )
        except:
            pass
    def plot_image( self ):
        try:
            if not self.pop_plot:
                return self.plot_generic_image( 'image' )
            else:
                return self.plot_image_pop(  )
        except:
            pass
    def plot_C12( self ):
        try:
            return self.plot_generic_image( 'c12' )
        except:
            pass
    def plot_surface(self):
        '''TODOLIST'''
        print( 'here plot the surface...')
        plot_type = 'surface'
        self.configure_plot_type(  plot_type )
        try:
            uid =  'uid=%s-'%self.selected_hdf5_file['md'].attrs[ 'uid' ][:6]
            title = uid  + self.current_dataset
        except:
            title = self.filename_text  + '-' + self.current_dataset
        #print( title, self.value.shape )
        image_min, image_max = np.min( self.value.T ), np.max( self.value.T )
        self.min,self.max=image_min, image_max
        pos=[ 0, 0  ]
        if self.colorscale_string == 'log':
            if image_min<=0:#np.any(self.imageData<=0):
                image_min = 0.1*np.mean(np.abs( self.value.T ))
            tmpData=np.where(self.value.T<=0,1,self.value.T)
            z=  np.log10(tmpData)
        else:
            z = self.value.T
        minZ= np.min(z)
        maxZ= np.max(z)
        try:
            cmap = plt.get_cmap(  self.colormap_string  )
        except:
            cmap = plt.get_cmap('jet')
        rgba_img =  cmap((z-minZ)/(maxZ -minZ))
        p = gl.GLSurfacePlotItem(   z=z,
                                    colors = rgba_img,
                                  )
        try:
            sx,sy = self.value.T.shape
            cx,cy = sx//2, sy//2
            p.translate(-cx,-cy,0)
        except:
            pass
        self.guiplot.addItem( p )

    def image_mouseMoved(self,pos):
        """
        Shows the mouse position of 2D Image on its crosshair label
        """
        try:
            pointer=self.guiplot.getView().vb.mapSceneToView(pos)
            x,y=pointer.x(),pointer.y()
            if (x>self.xmin) and (x<self.xmax) and (y>self.ymin) and (y<self.ymax):
                I =  self.value.T[ int((x-self.xmin)*self.hor_Npt/(self.xmax-self.xmin)),int((y-self.ymin)*self.ver_Npt/(self.ymax-self.ymin)) ]
                self.imageCrossHair.setText("X=%0.4f,Y=%0.4f,I=%.5e"%(x,y,I) )
            else:
                self.imageCrossHair.setText(  'X=%0.4f, Y=%0.4f, I=%.5e'%(x,y,0))
        except:
            pass
    def plot_generic_image( self, plot_type ):
        self.configure_plot_type( plot_type  )
        shape = (self.value.T).shape
        self.hor_Npt= shape[0]
        self.ver_Npt= shape[1]
        self.xmin,self.xmax,self.ymin,self.ymax=0,shape[0],0,shape[1]
        try:
            self.guiplot.getView().vb.scene().sigMouseMoved.connect(self.image_mouseMoved )
        except:
            pass
        if plot_type == 'c12':
            his, bc =  np.histogram( self.value, 1000 )
            pmax = np.argmax(his)
            low, high = bc[pmax-10], bc[pmax+10]
            self.min=low
            self.max=high
            try:
                exp = float( self.selected_hdf5_file['md'].attrs[ 'exposure time' ] )
            except:
                exp = 1
            try:
                #legends = list( self.selected_hdf5_file['qval_dict'].attrs.values() )
                legends = self.get_dict_from_qval_dict(  )
                uid =  'uid=%s'%self.selected_hdf5_file['md'].attrs[ 'uid' ][:6]
                name = '--%s'%( legends[ self.qth ][:] )
                title = uid +  name
            except:
                title = self.filename_text
            print( title, self.value.shape )
            xscale  =    self.value.shape[0]*exp
            yscale =     self.value.shape[1]*exp
            self.guiplot.setImage(    (self.value.T ), #[::-1, : ] ,
                                      levels= [low , high ],
                                     pos = [0,0],
                                     )
            self.plt.setLabels( left = 't2 (s)', bottom='t1 (s)')
            ax = self.plt.getAxis('bottom')
            ax2 = self.plt.getAxis('left')
            pos = np.int_(np.linspace(0, self.value.shape[0], 5 ))
            tick = np.int_(np.linspace(0, self.value.shape[0], 5 )) * exp
            dx = [(pos[i], '%.3f'%(tick[i])) for i in range( len(pos ))   ]
            ax.setTicks([dx, []])
            ax2.setTicks([dx, []] )
        elif plot_type == 'image':
            try:
                uid =  'uid=%s-'%self.selected_hdf5_file['md'].attrs[ 'uid' ][:6]
                title = uid  + self.current_dataset
            except:
                title = self.filename_text  + '-' + self.current_dataset
            print( title, self.value.shape )
            nan_mask = ~np.isnan( self.value )
            
            image_min, image_max = np.min( self.value[nan_mask] ), np.max( self.value[nan_mask] )
            self.min,self.max=image_min, image_max
            pos=[ 0, 0  ]
            if self.colorscale_string == 'log':
                if image_min<=0:#np.any(self.imageData<=0):
                    image_min = 0.1*np.mean(np.abs( self.value[nan_mask] ))
                tmpData=np.where(self.value<=0,1,self.value)
                self.guiplot.setImage(np.log10(tmpData),
                                      levels=(np.log10( image_min),np.log10( image_max)),
                                      pos=pos,
                                      autoRange=True)
            else:
                self.guiplot.setImage( self.value ,
                                       levels=( image_min, image_max),
                                       pos=pos,
                                       autoRange=True)

            self.plt.setLabels( left = 'Y', bottom='X')
            ax = self.plt.getAxis('bottom')
            ax2 = self.plt.getAxis('left')
            pos = np.int_(np.linspace(0, self.value.shape[0], 5 ))
            tick = np.int_(np.linspace(0, self.value.shape[0], 5 ))
            dx = [(pos[i], '%i'%(tick[i])) for i in range( len(pos ))   ]
            ax.setTicks([dx, []])
            ax2.setTicks([dx, []] )
        self.guiplot.setColorMap( self.cmap )
        self.plt.setTitle( title = title )
        self.guiplot.getView().invertY(False)
        self.image_plot_count += 1

    def get_dict_from_qval_dict( self ):
        l = list( self.selected_hdf5_file['qval_dict'].attrs.items() )
        dc = { int(i[0]):i[1] for i in l }
        return dc
    def plot_generic_curve(self, plot_type):
        self.configure_plot_type( plot_type )
        self.get_selected_row_col(  )
        self.legend =   self.guiplot.addLegend()
        min_row, max_row, min_col, max_col = self.min_row, self.max_row, self.min_col, self.max_col
        shape = np.shape(self.value)
        Ns = len(shape)
        if self.group_data:
            legends = self.group_data_label            
        try:
            #legends = list( self.selected_hdf5_file['qval_dict'].attrs.values() )
            if not self.group_data:
                legends = self.get_dict_from_qval_dict(  )
            uid =  'uid=%s'%self.selected_hdf5_file['md'].attrs[ 'uid' ][:6]
        except:
            if not self.group_data:
                legends = list(  range(min_col+1, max_col+2) )
            uid =  self.current_dataset
        ##################
        symbolSize = 6

        ##########################
        setX_flag = False
        if plot_type =='qiq':
            self.X =  self.selected_hdf5_file['q_saxs'][min_row:max_row]
        elif  plot_type =='g2':
            min_row = max( self.min_row, 1)
            self.X =  self.selected_hdf5_file['taus'][min_row:max_row]
        else:
            pass
        if len(self.value) > 0:
            if self.X is not None and len(self.X)==max_row-min_row:
                X = self.X
                setX_flag = True
            if   max_col - min_col   > 1: # for 2d data each plot col by col
                if not setX_flag:
                    X = self.value[min_row:max_row, 0]
                j = 0
                for i in range(min_col, max_col):
                    Y = self.value[min_row:max_row, i ]
                    try:
                        leg = legends[   i  ]
                    except:
                        leg = legends[ i - min_col ]
                    if isinstance(leg, list):
                        leg = leg[:]
                    self.guiplot.plot( X, Y,
                                pen=( self.guiplot_count+j,  10 ),
                                symbolBrush=(self.guiplot_count+j,  10) ,
                                   symbolSize = symbolSize,
                                    name = uid + '-%s'%(    leg ) ,  )
                    j += 1
                    self.guiplot_count += 1
                setX_flag = False

            else: # for 1d data we plot a row
                if not setX_flag:
                    X = np.arange( shape[0] ) [min_row:max_row]
                if Ns > 1:
                    Y = self.value[ min_row:max_row, min_col ]
                else:
                    Y = self.value[ min_row:max_row  ]
                try:
                    leg = legends[ min_col  ]
                except:
                    leg = legends[ min_col - min_col]

                if isinstance(leg, list):
                    leg = leg[:]
                print(X.shape, Y.shape, leg )
                self.guiplot.plot( X, Y,
                                pen=( self.guiplot_count,  10 ),
                                symbolBrush=(self.guiplot_count,  10) ,
                                 symbolSize = symbolSize ,
                                  name= uid + '-%s'%(  leg ) ,
                                     )
                self.guiplot_count += 1
        if plot_type =='qiq':
            self.guiplot.setLogMode(y=True, x=False)
            self.guiplot.showGrid(True, True)
            self.guiplot.setLabel('left', "I(q)")# units='A')
            self.guiplot.setLabel('bottom', "q (A-1)")# units='A')

        elif  plot_type =='g2':
            self.guiplot.setLogMode(x=True, y=False)
            self.guiplot.showGrid(True, True)
            self.guiplot.setLabel('left', "g2(t)")# units='A')
            self.guiplot.setLabel('bottom', "t (s)")# units='A')
        else:
            pass
    def  configure_plot_type(self, plot_type):
        self.plot_type = plot_type
        if plot_type in [ 'curve', 'g2', 'qiq' ] :
            if self.guiplot_count==0:
                self.guiplot = pg.PlotWidget()
                self.grid.addWidget( self.guiplot, 5, 1,  4,8 )
            self.image_plot_count=0
        elif plot_type in ['image', 'c12']:
            self.get_colormap()
            if self.image_plot_count==0:
                self.plt = pg.PlotItem()
                self.guiplot = pg.ImageView( view=self.plt  )
                self.grid.addWidget(self.guiplot, 5, 1,  4,8 )
            self.guiplot_count=0
        elif plot_type  in [ 'surface' ]:
            self.get_colormap()
            self.guiplot = gl.GLViewWidget()
            self.grid.addWidget(self.guiplot, 5, 1,  4,8 )
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
    def add_pop_plot_box(self):
        self.pop_plot_box_obj =   QCheckBox("pop plot" )
        self.pop_plot_box_obj.stateChanged.connect( self.click_pop_plot_box )
        button_section =  QHBoxLayout()
        button_section.addWidget(self.pop_plot_box_obj )
        return button_section
    def click_pop_plot_box(self, state):
        if state == QtCore.Qt.Checked:
            self.pop_plot = True
            self.gui_popplot_count = 0
            self.image_plopplot_count = 0
        else:
            self.pop_plot = False
            self.guiplot_count = 0
            self.image_plot_count = 0
    def guiplot_clear(self):
        if not self.pop_plot:
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
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                '/home/yugang/Desktop/XPCS_GUI/TestData/test.h5', filter='*.hdf5 *.h5 *.lst')[0]
        ext = filename.split('/')[-1].split('.')[-1]
        if ext == 'lst':
            filenames =  np.loadtxt( filename, dtype= object, )
            grandpa_name = filename.split('/')[-1]
            for fp in filenames:
                self.initiate_file_open(fp, grandpa_name=grandpa_name)
        else:
            self.initiate_file_open(filename)

    def initiate_file_open(self, filename, grandpa_name=None):
        #filename =filename
        self.filename = filename
        sfilename = filename.split('/')[-1]
        self.filename_dict[ sfilename] =  filename
        self.dataset_table.clear()
        self.attribute_table.clear()
        self.open_file(filename, grandpa_name )
        #print('HERE')
        try:
            self.file_items_list.add_filename( sfilename, grandpa_name )
            if grandpa_name is None:
                self.file_items_list_property[sfilename]='file'
            else:
                self.file_items_list_property[grandpa_name]='group'
            ##for understanding treelist
            if False:
                self.file_items_list.add_filename( 'XXX' )
                #print( self.file_items_list.parent_list )
                child1 = QTreeWidgetItem( self.file_items_list.parent_list['XXX'] )
                child1.setText(0,  'first item' )
                child2 = QTreeWidgetItem( self.file_items_list.parent_list['XXX'] )
                child2.setText(0,  'second item' )
                child11 = QTreeWidgetItem( child1  )
                child11.setText(0,  '11 item' )
                child21 = QTreeWidgetItem( child2  )
                child21.setText(0,  '21 item' )

            self.populate_file_file_items_list( sfilename, grandpa_name )
            self.filename_label.setText(filename.split('/')[-1])
            self.setWindowTitle('XSH5View@CHX - ' + filename)
        except:
            self.filename = '' # if it didn't work keep the old value
            self.filename_label.setText('')
            self.setWindowTitle('XSH5View@CHX')
            self.clear_file_items()
            self.dataset_table.clear()
            self.attribute_table.clear()
            print("Error opening file")
    def open_file(self, filename, grandpa_name=None):
        '''
        Opens the chosen HDF5 file. '''
        sfilename = filename.split('/')[-1]
        #print( sfilename, grandpa_name )
        #print( self.hdf5_file_dict )

        try:
            sfilename = filename.split('/')[-1]
            if grandpa_name is None:
                self.hdf5_file_dict[  sfilename ] = h5py.File(filename , 'r')
            else:
                if grandpa_name not in list(self.hdf5_file_dict.keys()):
                    self.hdf5_file_dict[grandpa_name]={}
                self.hdf5_file_dict[grandpa_name][  sfilename ] = h5py.File(filename , 'r')
        except:
            #print('Goes wrong here.')
            self.hdf5_file_dict = None
    def find_items(  self, hdf_group):
        '''
        Recursive function for all nested groups and datasets. Populates self.file_items.'''
        file_items = []
        for i in hdf_group.keys():
            #print( 'find items here')
            #print(i)
            file_items.append(hdf_group[i].name)
            if isinstance(hdf_group[i], h5py.Group):
                pass
                #a = find_items(hdf_group[i])
                #print(a)
                #if len(a) >= 1:
                    #file_items.append(a)
        return file_items
    def clear_file_items(self):
        self.file_items = []
        self.file_items_list.clear()
    def add_item_to_file_list(self, items, item_index, n, sfilename, grandpa_name=None):
        item_list = items[item_index]
        for i in range(len(item_list)):
            if isinstance(item_list[i], str):
                if grandpa_name is None:
                    self.file_items_list.add_item(n, item_list[i],
                                              self.hdf5_file_dict[sfilename], sfilename)
                else:
                    self.file_items_list.add_item(n, item_list[i],
                                              self.hdf5_file_dict[grandpa_name][sfilename], sfilename)
            else:
                self.add_item_to_file_list(item_list, i, n+i, sfilename, grandpa_name)
    def populate_file_file_items_list(self, sfilename, grandpa_name=None):
        '''
        Function to populate the file structure list on the main window.
        '''
        # Find all of the items in this file
        if grandpa_name is None:
            file_items = self.find_items(  self.hdf5_file_dict[sfilename] )
            #print( self.hdf5_file_dict[sfilename] )
            #print(file_items)
        else:
            file_items = self.find_items(  self.hdf5_file_dict[grandpa_name][sfilename] )
        self.file_items = file_items
        for i in range(len(self.file_items)):
            if isinstance(self.file_items[i], str):
                if grandpa_name is None:
                    self.file_items_list.add_item(None, self.file_items[i],
                                              self.hdf5_file_dict[sfilename], sfilename)
                else:
                    self.file_items_list.add_item(None, self.file_items[i],
                                              self.hdf5_file_dict[grandpa_name][sfilename], sfilename)

            else:
                self.add_item_to_file_list(self.file_items, i, i-1, sfilename, grandpa_name )
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
    def generatePgColormap(self, cmap ):
        colors = [cmap(i) for i in range(cmap.N)]
        positions = np.linspace(0, 1, len(colors))
        pgMap = pg.ColorMap(positions, colors)
        return pgMap
    def get_colormap( self ):
        if self.colormap_string == 'default':
            pos = np.array([0., 1., 0.5, 0.25, 0.75])
            color = np.array([[0, 0, 255, 255], [255, 0, 0, 255], [0, 255, 0, 255], (0, 255, 255, 255), (255, 255, 0, 255)],
                 dtype=np.ubyte)
            cmap = pg.ColorMap(pos, color)
            self.colormap = cmap
        elif self.colormap_string in [ "jet", 'jet_extended', 'albula', 'albula_r',
                                      'goldish', "viridis", 'spectrum', 'vge', 'vge_hdr',]:
             self.colormap =  color_map_dict[self.colormap_string]
             cmap = self.generatePgColormap(  self.colormap   )
        else:
            pass
        self.cmap = cmap
        return cmap
    def get_filename_selected(self):
        selected_row = self.file_items_list.tree.currentItem()
        pathf = self.file_items_list.full_item_path(selected_row)
        path =  pathf.split('/')[1]
        self.path = path
        if path != '':
            text = path
            rtext = pathf.split('/')[0]
            if self.file_items_list_property[rtext] =='group':
                hdf5_file = self.hdf5_file_dict[rtext][path]
                self.path = pathf.split('/')[2]
            else:
                hdf5_file = self.hdf5_file_dict[rtext]
            self.filename_text = rtext
            self.selected_hdf5_file = hdf5_file
            self.current_dataset =''
            #print(   self.filename_text,   self.selected_hdf5_file  )

    def display_dataset(self):
        self.get_filename_selected()
        if self.path != '':
            text = self.path
            rtext = self.filename_text
            hdf5_file  = self.selected_hdf5_file
            #print('display data here')
            #print( text, self.current_dataset )
            if (not text == self.current_dataset) and isinstance(hdf5_file[text], h5py.Dataset):
                self.group_data = False
                self.current_dataset = text                
                shape = hdf5_file[text].shape
                Ns = len(shape)
                if Ns==0:
                    pass
                elif Ns ==1:
                    numrows = shape[0]
                    numcols = 1    
                    self.value =  hdf5_file[text][:]                        
                elif Ns ==2:
                    numrows = shape[0]
                    numcols = shape[1]  
                    self.value =  hdf5_file[text][:]
                elif Ns==3:  #a 3D array, [x,y,z], show [x,y ]
                    numrows = shape[0]
                    numcols = shape[1]
                    try:
                        self.value =  hdf5_file[text][:,:,self.qth]
                    except:
                        print('The max q-th is %s.'%shape[2])
                        self.value =  hdf5_file[text][:,:,0]
                else:
                    numrows = shape[0]
                    numcols = shape[1]
                    self.value =  hdf5_file[text][:]

                        
            elif   (not text == self.current_dataset) and isinstance(hdf5_file[text], h5py.Group):
                self.current_dataset = text
                print('display the group data here')
                #print( text )
                #print( self.pds_keys )
                if text in self.pds_keys:
                    #print( 'YYES' )
                    print( self.filename, text)                    
                    d = pds.read_hdf( self.filename, key= text )#[:]
                    #print( 
                    #print( d )
                    #print( pds.__version__ )
                    self.value =  np.array( d )
                    shape = self.value.shape
                    #print('the shape is:' )
                    #print( self.value.shape )
                    numrows = shape[0]
                    numcols = shape[1]
                    Ns = len(shape)
                    self.group_data_label=  np.array( d.columns )[:]
                    self.group_data = True
                    
                else:
                    self.dataset_table.clear()
                    self.values = np.array([])
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
                    if Ns!=0:
                        for i in range(numrows):
                            if numcols > 1:
                                for j in range(numcols):
                                    self.dataset_table.set_item(i, j, str( self.value[i,j]))
                            else:
                                self.dataset_table.set_item(i, 0, str( self.value[i]))
                if not self.attributes_flag:
                    self.attribute_table.clear()
                    self.attribute_table.setRowCount(1)
                    self.attribute_table.setColumnCount(Ns+1)
                    self.attribute_table.setItem( 0, 0, QTableWidgetItem( 'shape' ))
                    for i,s in enumerate( shape ):
                        self.attribute_table.setItem( 0, i+1, QTableWidgetItem( '%s'%s )) 
            except:
                pass
                
                
                
                
    def display_attributes(self):
        # reset the value
        self.attribute_table.clear()
        self.get_filename_selected()
        if self.path != '':
            text = self.path
            rtext = self.filename_text
            hdf5_file  = self.selected_hdf5_file
            attributes = list(hdf5_file[text].attrs.items())
            num_attributes = len(attributes)
            self.attribute_table.setRowCount(num_attributes)
            self.attribute_table.setColumnCount(0)
            #print( text, rtext, hdf5_file,  attributes )
            if num_attributes > 0:
                self.attribute_table.setColumnCount(2)
                self.attributes_flag=True
            else:
                self.attributes_flag=False
            #print(   num_attributes   )       
            # Populate the table
            for i in range(num_attributes):
                value = attributes[i][1]
                self.attribute_table.setItem(i, 0, QTableWidgetItem(attributes[i][0]))
                #print( i, value)
                if isinstance(value, np.ndarray):
                    N = len(value)
                    self.attribute_table.setColumnCount(N+1)
                    j = 1
                    for v in value:
                        self.attribute_table.setItem(i, j, QTableWidgetItem(str(v)))
                        #self.attribute_table.setItem(i, 1, QTableWidgetItem(str(value[0].decode())))
                        j+=1
                    #elif isinstance(value, str)  or   isinstance(value, float) or isinstance(value, int):
                    #print('here is a array')
                else:
                    self.attribute_table.setItem(i, 1, QTableWidgetItem(str(value)))
                    #print( i, value )
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
            filename = self.filename_text
            self.filename_label.setText(filename.split('/')[-1])
            self.setWindowTitle('XSH5View@CHX - ' + filename)
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

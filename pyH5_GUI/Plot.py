import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from PyQt5.QtWidgets import (QWidget, QToolTip, QMainWindow, )
from ColorMap import (cmap_cyclic_spectrum, cmap_jet_extended, cmap_vge, cmap_vge_hdr,
                      cmap_albula, cmap_albula_r,cmap_hdr_goldish , color_map_dict )      
import matplotlib.pyplot as plt
                             
plot_curve_type = [ 'curve', 'g2', 'qiq' ]   # some particular format for curve plot 
plot_image_type = ['image', 'c12']           # some particular format  for image plot
plot_surface_type = ['surface']           # some particular format  for surfce plot



class PlotWidget(   ):
    def __init__(self, mainWin ):
        #print('Connect to mainWin here')
        self.mainWin= mainWin
        self.resizeEvent = self.mainWin.onresize

    def generatePgColormap(self, cmap ):
        colors = [cmap(i) for i in range(cmap.N)]
        positions = np.linspace(0, 1, len(colors))
        pgMap = pg.ColorMap(positions, colors)
        return pgMap
    
    def get_colormap( self, mainWin ):
        #print( self.colormap_string )
        if self.mainWin.colormap_string == 'default':
            pos = np.array([0., 1., 0.5, 0.25, 0.75])
            color = np.array([[0, 0, 255, 255], [255, 0, 0, 255], [0, 255, 0, 255], (0, 255, 255, 255), (255, 255, 0, 255)],
                 dtype=np.ubyte)
            cmap = pg.ColorMap(pos, color)
            self.mainWin.colormap = cmap
        elif self.mainWin.colormap_string in [ "jet", 'jet_extended', 'albula', 'albula_r',
                                      'goldish', "viridis", 'spectrum', 'vge', 'vge_hdr',]:
             self.mainWin.colormap =  color_map_dict[self.mainWin.colormap_string]
             cmap = self.generatePgColormap(  self.mainWin.colormap   )
             print('the color string is: %s.'%self.mainWin.colormap_string)
        else:
            pass
        self.mainWin.cmap = cmap
        return cmap
    
    
    def  configure_plot_type(self, plot_type ):
        self.mainWin.plot_type = plot_type
        if plot_type in plot_curve_type :
            #print('For curve plot here')
            if self.mainWin.guiplot_count==0:
                self.mainWin.guiplot = pg.PlotWidget()
                self.mainWin.grid.addWidget( self.mainWin.guiplot, 5, 1,  4,8 )
            self.mainWin.image_plot_count=0
        elif plot_type in plot_image_type:               
            #print('Here should plot the images--in configure plot')            
            self.get_colormap(  self.mainWin )            
            #print( self.mainWin.cmap )            
            if self.mainWin.image_plot_count==0:
                self.mainWin.plt = pg.PlotItem()
                self.mainWin.guiplot = pg.ImageView( view=self.mainWin.plt  )
                self.mainWin.grid.addWidget(self.mainWin.guiplot, 5, 1,  4,8 )
            self.mainWin.guiplot_count=0
            
        elif plot_type  in plot_surface_type:
            self.get_colormap(  self.mainWin )     
            self.mainWin.guiplot = gl.GLViewWidget()
            self.mainWin.grid.addWidget(self.mainWin.guiplot, 5, 1,  4,8 )

        
    def plot_generic_curve(self, plot_type ):        
        self.configure_plot_type( plot_type )
        self.mainWin.get_selected_row_col(  )
        self.mainWin.legend =   self.mainWin.guiplot.addLegend()
        min_row, max_row, min_col, max_col = self.mainWin.min_row, self.mainWin.max_row, self.mainWin.min_col, self.mainWin.max_col
        shape = np.shape(self.mainWin.value)
        Ns = len(shape)
        if self.mainWin.group_data:
            legends = self.mainWin.group_data_label  
            uid =  self.mainWin.current_item_name
        
        if self.mainWin.current_dataset_type =='CHX':   
            try:
                #legends = list( self.mainWin.selected_hdf5_file['qval_dict'].attrs.values() )
                if not self.mainWin.group_data:
                    legends = self.mainWin.get_dict_from_qval_dict(  )
                uid =  'uid=%s'%self.mainWin.selected_hdf5_file['md'].attrs[ 'uid' ][:6]
            except:
                if not self.mainWin.group_data:
                    legends = list(  range(min_col+1, max_col+2) )
                uid =  self.mainWin.current_item_name
                
        print( uid, legends )    
        ##################
        symbolSize = 6

        ##########################
        
        #print( plot_type,   self.mainWin.selected_hdf5_file )
        
        setX_flag = False
        if plot_type =='qiq':
            self.mainWin.X =  self.mainWin.current_selected_HDF['q_saxs'][min_row:max_row]
        elif  plot_type =='g2':
            min_row = max( self.mainWin.min_row, 1)
            #print( self.mainWin.selected_hdf5_file['taus'] )
            self.mainWin.X =  self.mainWin.current_selected_HDF['taus'][min_row:max_row]
        else:
            pass
        #print( plot_type,   self.mainWin.selected_hdf5_file['taus'] )
        #print( self.mainWin.value )
        if len(self.mainWin.value) > 0:
            if self.mainWin.X is not None and len(self.mainWin.X)==max_row-min_row:
                X = self.mainWin.X
                setX_flag = True
            if   max_col - min_col   > 1: # for 2d data each plot col by col
                if not setX_flag:
                    X = self.mainWin.value[min_row:max_row, 0]
                j = 0
                for i in range(min_col, max_col):
                    Y = self.mainWin.value[min_row:max_row, i ]
                    try:
                        leg = legends[   i  ]
                    except:
                        leg = legends[ i - min_col ]
                    if isinstance(leg, list):
                        leg = leg[:]
                    self.mainWin.guiplot.plot( X, Y,
                                pen=( self.mainWin.guiplot_count+j,  10 ),
                                symbolBrush=(self.mainWin.guiplot_count+j,  10) ,
                                   symbolSize = symbolSize,
                                    name = uid + '-%s'%(    leg ) ,  )
                    j += 1
                    self.mainWin.guiplot_count += 1
                setX_flag = False
                
                print('Here for general plot')    

            else: # for 1d data we plot a row
                if not setX_flag:
                    X = np.arange( shape[0] ) [min_row:max_row]
                if Ns > 1:
                    Y = self.mainWin.value[ min_row:max_row, min_col ]
                else:
                    Y = self.mainWin.value[ min_row:max_row  ]
                try:
                    leg = legends[ min_col  ]
                except:
                    leg = legends[ min_col - min_col]

                if isinstance(leg, list):
                    leg = leg[:]
                print(X.shape, Y.shape, leg )
                self.mainWin.guiplot.plot( X, Y,
                                pen=( self.mainWin.guiplot_count,  10 ),
                                symbolBrush=(self.mainWin.guiplot_count,  10) ,
                                 symbolSize = symbolSize ,
                                  name= uid + '-%s'%(  leg ) ,
                                     )
                self.mainWin.guiplot_count += 1
                
        if plot_type =='qiq':
            self.mainWin.guiplot.setLogMode(y=True, x=False)
            self.mainWin.guiplot.showGrid(True, True)
            self.mainWin.guiplot.setLabel('left', "I(q)")# units='A')
            self.mainWin.guiplot.setLabel('bottom', "q (A-1)")# units='A')

        elif  plot_type =='g2':
            self.mainWin.guiplot.setLogMode(x=True, y=False)
            self.mainWin.guiplot.showGrid(True, True)
            self.mainWin.guiplot.setLabel('left', "g2(t)")# units='A')
            self.mainWin.guiplot.setLabel('bottom', "t (s)")# units='A')
        else:
            pass    

    def plot_generic_image( self, plot_type ):
        #print('Here should plot the images')
        self.configure_plot_type( plot_type  )
        shape = (self.mainWin.value.T).shape
        self.mainWin.hor_Npt= shape[0]
        self.mainWin.ver_Npt= shape[1]
        self.mainWin.xmin,self.mainWin.xmax,self.mainWin.ymin,self.mainWin.ymax=0,shape[0],0,shape[1]
        try:
            self.mainWin.guiplot.getView().vb.scene().sigMouseMoved.connect(self.image_mouseMoved )
        except:
            pass
        
        if plot_type == 'c12':
            his, bc =  np.histogram( self.mainWin.value, 1000 )
            pmax = np.argmax(his)
            low, high = bc[pmax-10], bc[pmax+10]
            self.mainWin.min=low
            self.mainWin.max=high
            try:
                exp = float( self.mainWin.selected_hdf5_file['md'].attrs[ 'exposure time' ] )
            except:
                exp = 1
            try:
                #legends = list( self.mainWin.selected_hdf5_file['qval_dict'].attrs.values() )
                legends = self.mainWin.get_dict_from_qval_dict(  )
                uid =  'uid=%s'%self.mainWin.selected_hdf5_file['md'].attrs[ 'uid' ][:6]
                name = '--%s'%( legends[ self.mainWin.qth ][:] )
                title = uid +  name
            except:
                title = self.mainWin.filename_text
            print( title, self.mainWin.value.shape )
            xscale  =    self.mainWin.value.shape[0]*exp
            yscale =     self.mainWin.value.shape[1]*exp
            self.mainWin.guiplot.setImage(    (self.mainWin.value.T ), #[::-1, : ] ,
                                      levels= [low , high ],
                                     pos = [0,0],
                                     )
            self.mainWin.plt.setLabels( left = 't2 (s)', bottom='t1 (s)')
            ax = self.mainWin.plt.getAxis('bottom')
            ax2 = self.mainWin.plt.getAxis('left')
            pos = np.int_(np.linspace(0, self.mainWin.value.shape[0], 5 ))
            tick = np.int_(np.linspace(0, self.mainWin.value.shape[0], 5 )) * exp
            dx = [(pos[i], '%.3f'%(tick[i])) for i in range( len(pos ))   ]
            ax.setTicks([dx, []])
            ax2.setTicks([dx, []] )
        elif plot_type == 'image':            
            #print('Here should plot the images')            
            try:
                uid =  'uid=%s-'%self.mainWin.selected_hdf5_file['md'].attrs[ 'uid' ][:6]
                title = uid  + self.mainWin.current_item_name
            except:
                title = self.mainWin.filename_text  + '-' + self.mainWin.current_item_name
            print( title, self.mainWin.value.shape )
            nan_mask = ~np.isnan( self.mainWin.value )            
            image_min, image_max = np.min( self.mainWin.value[nan_mask] ), np.max( self.mainWin.value[nan_mask] )
            self.mainWin.min,self.mainWin.max=image_min, image_max
            pos=[ 0, 0  ]
            if self.mainWin.colorscale_string == 'log':
                if image_min<=0:#np.any(self.mainWin.imageData<=0):
                    image_min = 0.1*np.mean(np.abs( self.mainWin.value[nan_mask] ))
                tmpData=np.where(self.mainWin.value<=0,1,self.mainWin.value)
                self.mainWin.guiplot.setImage(np.log10(tmpData),
                                      levels=(np.log10( image_min),np.log10( image_max)),
                                      pos=pos,
                                      autoRange=True)
            else:
                self.mainWin.guiplot.setImage( self.mainWin.value ,
                                       levels=( image_min, image_max),
                                       pos=pos,
                                       autoRange=True)
            #print( self.mainWin.colorscale_string   )
            self.mainWin.plt.setLabels( left = 'Y', bottom='X')
            ax = self.mainWin.plt.getAxis('bottom')
            ax2 = self.mainWin.plt.getAxis('left')
            pos = np.int_(np.linspace(0, self.mainWin.value.shape[0], 5 ))
            tick = np.int_(np.linspace(0, self.mainWin.value.shape[0], 5 ))
            dx = [(pos[i], '%i'%(tick[i])) for i in range( len(pos ))   ]
            ax.setTicks([dx, []])
            ax2.setTicks([dx, []] )
        self.mainWin.guiplot.setColorMap( self.mainWin.cmap )
        self.mainWin.plt.setTitle( title = title )
        self.mainWin.guiplot.getView().invertY(False)
        self.mainWin.image_plot_count += 1

    def plot_surface(self):
        '''TODOLIST'''
        print( 'here plot the surface...')
        plot_type = 'surface'
        self.configure_plot_type(  plot_type  )
        try:
            uid =  'uid=%s-'%self.mainWin.selected_hdf5_file['md'].attrs[ 'uid' ][:6]
            title = uid  + self.mainWin.current_item_name
        except:
            title = self.mainWin.filename_text  + '-' + self.mainWin.current_item_name
        #print( title, self.mainWin.value.shape )
        image_min, image_max = np.min( self.mainWin.value.T ), np.max( self.mainWin.value.T )
        self.mainWin.min,self.mainWin.max=image_min, image_max
        pos=[ 0, 0  ]
        if self.mainWin.colorscale_string == 'log':
            if image_min<=0:#np.any(self.mainWin.imageData<=0):
                image_min = 0.1*np.mean(np.abs( self.mainWin.value.T ))
            tmpData=np.where(self.mainWin.value.T<=0,1,self.mainWin.value.T)
            z=  np.log10(tmpData)
        else:
            z = self.mainWin.value.T
        minZ= np.min(z)
        maxZ= np.max(z)        
        #cmap = self.mainWin.cmap
        try:
            cmap = plt.get_cmap(  self.colormap_string	)
        except:
            cmap = plt.get_cmap('jet') 
        rgba_img =  cmap((z-minZ)/(maxZ -minZ))
        p = gl.GLSurfacePlotItem(   z=z,
                                    colors = rgba_img,
                                  )
        try:
            sx,sy = self.mainWin.value.T.shape
            cx,cy = sx//2, sy//2
            p.translate(-cx,-cy,0)
        except:
            pass
        self.mainWin.guiplot.addItem( p )
        

    def image_mouseMoved(self, pos):
        """
        Shows the mouse position of 2D Image on its crosshair label
        """        
        try:
            pointer=self.mainWin.guiplot.getView().vb.mapSceneToView(pos)
            x,y=pointer.x(),pointer.y()
            ang = np.degrees( np.arctan2(y,x))
            if (x>self.mainWin.xmin) and (x<self.mainWin.xmax) and (y>self.mainWin.ymin) and (y<self.mainWin.ymax):
                I =  self.mainWin.value.T[ int((x-self.mainWin.xmin)*self.mainWin.hor_Npt/(self.mainWin.xmax-self.mainWin.xmin)),int((y-self.mainWin.ymin)*self.mainWin.ver_Npt/(self.mainWin.ymax-self.mainWin.ymin)) ]                
                #self.mainWin.imageCrossHair.setText("X=%0.4f, Y=%0.4f, Ang=%0.2f, I=%.5e"%(x,y,ang, I) )
                self.mainWin.imageCrossHair.setText("X=%0.4f, Y=%0.4f, I=%.5e"%(x,y, I) )
            else:
                self.mainWin.imageCrossHair.setText(  'X=%0.4f, Y=%0.4f, I=%.5e'%(x,y, 0))
                #self.mainWin.imageCrossHair.setText("X=%0.4f, Y=%0.4f, Ang=%0.2f, I=%.5e"%(x,y,ang, I) )
        except:
            pass
        
         
    def plot_curve( self ):
           
        try:
            print( 'curve here ------>')     
            return self.plot_generic_curve( 'curve' )
        except:
            pass
    def plot_g2( self ):
          
        try:
            print( 'g2 here ------>')      
            return self.plot_generic_curve( 'g2' )
        except:
            pass
    def plot_qiq( self ):
        
        try:
            print( 'qiq here ------>') 
            return self.plot_generic_curve( 'qiq' )
        except:
            pass
    def plot_image( self ):
        
        try:
            print( 'image here ------>') 
            self.plot_generic_image( 'image')
        except:
            pass
    def plot_C12( self ):
        
        try:
            print( 'C12 here ------>') 
            return self.plot_generic_image( 'c12' )
        except:
            pass       
        
        
        
        
def bstring_to_string( bstring ):
    '''Y.G., Dev@CFN Nov 20, 2019 convert a btring to string
     
    Parameters
    ----------
        bstring: bstring or list of bstring 
    Returns
    -------  
        string:    
    '''
    s =  np.array( bstring )
    if not len(s.shape):
        s=s.reshape( 1, )
        return s
        #return s[0].decode('utf-8')
    else:
        return np.char.decode( s )        
        
        
        
        
        
        


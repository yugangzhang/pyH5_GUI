import sys
import numpy as np
import matplotlib.pyplot as plt
import functools as ft
import h5py
import pandas as pds
from IO import * # h5todict, dicttoh5



## for an example
#x=np.linspace(0,10,100)
#y=np.sin(np.pi*x)
#xy = np.hstack( [ x[:,np.newaxis], y[:,np.newaxis] ] )
#rd = np.random.random([100,100])
#md = {  "Project":'GUI_Development',
#        'Creator':'YGZhang',
#        'Create_Data':'2020-07-10',        
#       }
#d = {'x':x, 'y':y, 'xy': xy, 'rand_2D': rd, 'metadata':md }
#Save the dictionary to a h5 file
#dicttoh5( d, 'test.h5' )


# An example to make a h5 file
data = { }

#Creat a metadata (a description of the data)
md = {  "Project":'GUI_Development',
        'Creator':'YGZhang',
        'Create_Data':'2020-07-10',
        'sample':'A test sample with UV,PL,SEM,SAXS data'
       }
data['metadata']= md

# load data from datafiles, such as dat, txt, csv, tif, and h5.
path = r'C:\\Users\\yuzhang\\Desktop\\Repos\\pyH5_Gui_Develop\\gui_test_data\\'

## Load a life time data
data['Life Time'] = {}
fn = 'Q5STV_525.dat'
fp = path + fn
d = load_data_with_header( fp, data_row_start=1000, max_row=10000 )
data['Life Time'][fn] = d[:,:2]

## Load a UV data
data['UV'] = {}
fn = 'Au20DNA_3ul_460WT.asc'
fp = path + fn
d = load_data_with_header( fp, data_row_start=87, max_row= None )
data['UV'][fn] = d

## Load a SEM data
data['SEM'] = {}
fn = '20100817-1_q17.tif'
fp = path + fn
d = load_img( fp )
data['SEM'][fn] = np.array( d, dtype= np.int)
fn = 'S4_FOR Au NPs SEM.tif'
fp = path + fn
d = load_img( fp )[:,:,0]
data['SEM'][fn] = np.array( d, dtype= np.int)


## Load a image data
data['IMG'] = {}
fn = 'S1 for PD_Au SAXS, SEM, EDS.tif'
fp = path + fn
img = load_img( fp )[:,:,0]
data['IMG'][fn] = np.array( img, dtype= np.int)


## Load a SAXS data
data['SAXS'] = {}
fn = 'sid=1587_suid=2175a962.npz.h5'
fp = path + fn
d = h5todict( fp )
data['SAXS'][fn] = d

fn0 = 'PEG_Data_In_One.h5'
fp = path + fn0
d0 = h5todict( fp )
fp = 'sample_V_5nm_betaLbeta'
d= d0[fp]
data['SAXS'][fp] = d

# Save the fabricated h5 file
#dicttoh5( data, 'test.h5' )









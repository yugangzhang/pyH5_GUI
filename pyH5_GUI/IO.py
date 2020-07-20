# -*- coding: cp1252 -*-
"""
Nov , 2019 Developed by Y.G.@CFN
yuzhang@bnl.gov
This module defines the data IO, file operations ( list, copy, delete, etc)
"""

import numpy as np
from PIL import Image
import shutil,glob, os
from os import listdir
from os.path import isfile, join
import h5py, sys, enum
import pandas as pds
import collections
import logging
logger = logging.getLogger(__name__)



    
######################################
#Functions to load beamline raw data
#####################################
def load_img( filename  ):
    ''' YG DEV at Nov/10/2019@CFN Get data from a CMS scattering data collected pilatus detectors
    Parameters
    ----------
        filename: string, filename of the data
        inDir: string, data folder 
    Returns
    -------
        data: array, 2D numpy array (the data is converted up-side down.
    '''
    im = Image.open(   filename )
    return np.array( im )[::-1]



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
        return s[0].decode('utf-8')
    else:
        return np.char.decode( s )



string_types = (basestring,) if sys.version_info[0] == 2 else (str,)
def _prepare_hdf5_dataset(array_like):
    """Cast a python object into a numpy array in a HDF5 friendly format.
    :param array_like: Input dataset in a type that can be digested by
        ``numpy.array()`` (`str`, `list`, `numpy.ndarray`…)
    :return: ``numpy.ndarray`` ready to be written as an HDF5 dataset
    """
    # simple strings
    if isinstance(array_like, string_types):
        array_like = np.string_(array_like)

    # Ensure our data is a numpy.ndarray
    if not isinstance(array_like, (np.ndarray, np.string_)):
        array = np.array(array_like)
    else:
        array = array_like

    # handle list of strings or numpy array of strings
    if not isinstance(array, np.string_):
        data_kind = array.dtype.kind
        # unicode: convert to byte strings
        # (http://docs.h5py.org/en/latest/strings.html)
        if data_kind.lower() in ["s", "u"]:
            array = np.asarray(array, dtype=np.string_)
    return array

class _SafeH5FileWrite(object):
    """Context manager returning a :class:`h5py.File` object.
    If this object is initialized with a file path, we open the file
    and then we close it on exiting.
    If a :class:`h5py.File` instance is provided to :meth:`__init__` rather
    than a path, we assume that the user is responsible for closing the
    file.
    This behavior is well suited for handling h5py file in a recursive
    function. The object is created in the initial call if a path is provided,
    and it is closed only at the end when all the processing is finished.
    """
    def __init__(self, h5file, mode="w"):
        """
        :param h5file:  HDF5 file path or :class:`h5py.File` instance
        :param str mode:  Can be ``"r+"`` (read/write, file must exist),
            ``"w"`` (write, existing file is lost), ``"w-"`` (write, fail if
            exists) or ``"a"`` (read/write if exists, create otherwise).
            This parameter is ignored if ``h5file`` is a file handle.
        """
        self.raw_h5file = h5file
        self.mode = mode
    def __enter__(self):
        if not isinstance(self.raw_h5file, h5py.File):
            self.h5file = h5py.File(self.raw_h5file, self.mode)
            self.close_when_finished = True
        else:
            self.h5file = self.raw_h5file
            self.close_when_finished = False
        return self.h5file
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.close_when_finished:
            self.h5file.close()

class _SafeH5FileRead(object):
    """Context manager returning a :class:`h5py.File` or a
    :class:`silx.io.spech5.SpecH5` or a :class:`silx.io.fabioh5.File` object.
    The general behavior is the same as :class:`_SafeH5FileWrite` except
    that SPEC files and all formats supported by fabio can also be opened,
    but in read-only mode.
    """
    def __init__(self, h5file):
        """
        :param h5file:  HDF5 file path or h5py.File-like object
        """
        self.raw_h5file = h5file 
    def __enter__(self):
        if not is_file(self.raw_h5file):
            self.h5file = h5py.File(self.raw_h5file, "r")  #h5open(self.raw_h5file)
            self.close_when_finished = True
        else:
            self.h5file = self.raw_h5file
            self.close_when_finished = False 
        return self.h5file
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.close_when_finished:
            self.h5file.close()
            
def dicttoh5(treedict, h5file, h5path='/',
             mode="w", overwrite_data=False,
             create_dataset_args=None):
    """Write a nested dictionary to a HDF5 file, using keys as member names.
    If a dictionary value is a sub-dictionary, a group is created. If it is
    any other data type, it is cast into a numpy array and written as a
    :mod:`h5py` dataset. Dictionary keys must be strings and cannot contain
    the ``/`` character.
    .. note::
        This function requires `h5py <http://www.h5py.org/>`_ to be installed.
    :param treedict: Nested dictionary/tree structure with strings as keys
         and array-like objects as leafs. The ``"/"`` character is not allowed
         in keys.
    :param h5file: HDF5 file name or handle. If a file name is provided, the
        function opens the file in the specified mode and closes it again
        before completing.
    :param h5path: Target path in HDF5 file in which scan groups are created.
        Default is root (``"/"``)
    :param mode: Can be ``"r+"`` (read/write, file must exist),
        ``"w"`` (write, existing file is lost), ``"w-"`` (write, fail if
        exists) or ``"a"`` (read/write if exists, create otherwise).
        This parameter is ignored if ``h5file`` is a file handle.
    :param overwrite_data: If ``True``, existing groups and datasets can be
        overwritten, if ``False`` they are skipped. This parameter is only
        relevant if ``h5file_mode`` is ``"r+"`` or ``"a"``.
    :param create_dataset_args: Dictionary of args you want to pass to
        ``h5f.create_dataset``. This allows you to specify filters and
        compression parameters. Don't specify ``name`` and ``data``.
    """
    if create_dataset_args is None:
        create_dataset_args = {'compression': "gzip", 'shuffle': True,  'fletcher32': True}    
    compssion,shuffle,fletcher32 = ( create_dataset_args['compression'], 
                                     create_dataset_args['shuffle'], 
                                     create_dataset_args['fletcher32'] 
                                   )
    if not h5path.endswith("/"):
        h5path += "/"
    with _SafeH5FileWrite(h5file, mode=mode) as h5f:
        for key in treedict:
            #print(key)
            if isinstance(treedict[key], dict) and len(treedict[key]):
                # non-empty group: recurse
                dicttoh5(treedict[key], h5f, h5path + key,overwrite_data=overwrite_data, create_dataset_args=create_dataset_args)                
            elif treedict[key] is None or (isinstance(treedict[key], dict) and not len(treedict[key])):
                if (h5path + key) in h5f:
                    if overwrite_data is True:
                        del h5f[h5path + key]
                    else:
                        logger.warning('key (%s) already exists. '  'Not overwriting.' % (h5path + key))
                        continue
                # Create empty group
                h5f.create_group(h5path + key)
            else:
                ds = _prepare_hdf5_dataset(treedict[key])
                # can't apply filters on scalars (datasets with shape == () )
                if ds.shape == () or create_dataset_args is None:
                    if h5path + key in h5f:
                        if overwrite_data is True:
                            del h5f[h5path + key]
                        else:
                            logger.warning('key (%s) already exists. ' 'Not overwriting.' % (h5path + key))
                            continue
                    h5f.create_dataset(h5path + key, data=ds)
                else:
                    if h5path + key in h5f:
                        if overwrite_data is True:
                            del h5f[h5path + key]
                        else:
                            logger.warning('key (%s) already exists. ' 'Not overwriting.' % (h5path + key))
                            continue
                    h5f.create_dataset(h5path + key, data=ds, **create_dataset_args)
                    
def _name_contains_string_in_list(name, strlist):
    if strlist is None:
        return False
    for filter_str in strlist:
        if filter_str in name:
            return True
    return False

class H5Type(enum.Enum):
    """Identify a set of HDF5 concepts"""
    DATASET = 1
    GROUP = 2
    FILE = 3
    SOFT_LINK = 4
    EXTERNAL_LINK = 5
    HARD_LINK = 6
def _get_classes_type():
    """Returns a mapping between Python classes and HDF5 concepts.
    This function allow an lazy initialization to avoid recurssive import
    of modules.
    """    
    _CLASSES_TYPE = collections.OrderedDict()
    _CLASSES_TYPE[h5py.Dataset] = H5Type.DATASET
    _CLASSES_TYPE[h5py.File] = H5Type.FILE
    _CLASSES_TYPE[h5py.Group] = H5Type.GROUP
    _CLASSES_TYPE[h5py.SoftLink] = H5Type.SOFT_LINK
    _CLASSES_TYPE[h5py.HardLink] = H5Type.HARD_LINK
    _CLASSES_TYPE[h5py.ExternalLink] = H5Type.EXTERNAL_LINK
    return _CLASSES_TYPE

def get_h5_class(obj=None, class_=None):
    """
    Returns the HDF5 type relative to the object or to the class.
    :param obj: Instance of an object
    :param class_: A class
    :rtype: H5Type
    """
    if class_ is None:
        class_ = obj.__class__
    classes = _get_classes_type()
    t = classes.get(class_, None)
    if t is not None:
        return t
    if obj is not None:
        if hasattr(obj, "h5_class"):
            return obj.h5_class
    for referencedClass_, type_ in classes.items():
        if issubclass(class_, referencedClass_):
            classes[class_] = type_
            return type_
    classes[class_] = None
    return None

def h5type_to_h5py_class(type_):
    """
    Returns an h5py class from an H5Type. None if nothing found.
    :param H5Type type_:
    :rtype: H5py class
    """
    if type_ == H5Type.FILE:
        return h5py.File
    if type_ == H5Type.GROUP:
        return h5py.Group
    if type_ == H5Type.DATASET:
        return h5py.Dataset
    if type_ == H5Type.SOFT_LINK:
        return h5py.SoftLink
    if type_ == H5Type.HARD_LINK:
        return h5py.HardLink
    if type_ == H5Type.EXTERNAL_LINK:
        return h5py.ExternalLink
    return None
def get_h5py_class(obj):
    """Returns the h5py class from an object.
    If it is an h5py object or an h5py-like object, an h5py class is returned.
    If the object is not an h5py-like object, None is returned.
    :param obj: An object
    :return: An h5py object
    """
    if hasattr(obj, "h5py_class"):
        return obj.h5py_class
    type_ = get_h5_class(obj)
    return h5type_to_h5py_class(type_)

def is_group(obj):
    """
    True if the object is a h5py.Group-like object. A file is a group.
    :param obj: An object
    """
    t = get_h5_class(obj)
    return t in [H5Type.GROUP, H5Type.FILE]

def is_file(obj):
    """
    True is the object is an h5py.File-like object.
    :param obj: An object
    """
    t = get_h5_class(obj)
    return t == H5Type.FILE

def Get_h5_keys( filename, h5_path="/", dict_key = None ):
    '''YG Dev 2020/2/20 Sat@CFN
    Extract all the keys in a h5 file to a dict
    Input:
        filename: string, full path of the hdf5 filename
        h5_path: the path of the key in the hdf5, default as '/'
        dict_key: should be None, for recursive load the keys
    Output:
        dict:  keys: the levels in the h5 data
               values: the h5_path
    Example:
        dk = Get_h5_keys(fp)
        dk would be 
            {1: {'/': '', '/os_Msphere': ''},
             2: {'/os_Msphere/lt_SC': ''},
             3: {'/os_Msphere/lt_SC/ls_sphere': ''},
             4: {'/os_Msphere/lt_SC/ls_sphere/base': '',    
    
    ''' 
    if dict_key is None:
        dict_key={}
    with h5py.File( filename, 'r') as h5f:         
        for key in h5f[ h5_path]:                    
            if h5f[  h5_path + "/" + key].__class__  is h5py.Group:   
                if  h5_path != '//':
                    if  h5_path[:2]=='//':
                         h5_path_= h5_path[1:]
                    else:
                         h5_path_= h5_path
                    ps =  h5_path_.split('/')
                    level = len(ps) - 1
                    if level not in list(dict_key.keys()):
                        dict_key[level] = { }  
                    dict_key[level][ h5_path_] = ''                    
                    Get_h5_keys( filename,  h5_path=  h5_path + "/" + key, dict_key = dict_key )
    return dict_key

def h5todict(h5file, path="/", exclude_names=None, asarray=True, return_data=True):
    """Read a HDF5 file and return a nested dictionary with the complete file
    structure and all data.
    .. note:: This function requires `h5py <http://www.h5py.org/>`_ to be
        installed.
    .. note:: If you write a dictionary to a HDF5 file with
        :func:`dicttoh5` and then read it back with :func:`h5todict`, data
        types are not preserved. All values are cast to numpy arrays before
        being written to file, and they are read back as numpy arrays (or
        scalars). In some cases, you may find that a list of heterogeneous
        data types is converted to a numpy array of strings.
    :param h5file: File name or :class:`h5py.File` object or spech5 file or
        fabioh5 file.
    :param str path: Name of HDF5 group to use as dictionary root level,
        to read only a sub-group in the file
    :param List[str] exclude_names: Groups and datasets whose name contains
        a string in this list will be ignored. Default is None (ignore nothing)
    :param bool asarray: True (default) to read scalar as arrays, False to
        read them as scalar
    :return: Nested dictionary
    """
    with _SafeH5FileRead(h5file) as h5f:
        ddict = {}
        #print(path)
        for key in h5f[path]:
            if _name_contains_string_in_list(key, exclude_names):
                continue
            if is_group(h5f[path + "/" + key]):
                ddict[key] = h5todict(h5f,path + "/" + key, exclude_names=exclude_names, asarray=asarray,
                                      return_data=return_data)
            else:
                # Read HDF5 datset
                if  return_data:
                    data = h5f[path + "/" + key][()]
                    if asarray:  # Convert HDF5 dataset to numpy array
                        #print( key)  
                        #print(data)
                        if isinstance( data , bytes):
                            data = bstring_to_string( data )
                        elif ( isinstance( data, np.ndarray )  or isinstance( data, list )  ):
                            if isinstance( data[0] , bytes):
                                data = bstring_to_string( data )  
                        elif ( isinstance( data, float )  or isinstance( data, int )   or isinstance( data, str ) ):
                            pass                                                    
                        else:    
                            data = np.array(data, copy=False) 
                    ddict[key] = data
                else:                    
                    pass
    return ddict
 
def load_data_with_header(filename,data_row_start=1, max_row = None,
                          return_data_header=False, trys=True):
    
    '''YG DEV at 9/19/2017@CHX Loads data from a file containing strings 
    
    Comment on 7/4/2020, Could be replaced by pandas.read_csv( filename, sep = '\t' )
    
    Parameters
    ----------
        filename: string, the filename with full data path
        data_row_start: int, the start data row
        return_data_header: bool, if true return the data and data_header
    Returns
    -------
        None
    '''   
    fin = open( filename, 'r' )    
    p=fin.readlines()
    Np = len(p)
    if max_row is None:
        max_row = Np - data_row_start
    for i in range(data_row_start, max_row + data_row_start):
        line = p[i]
        if return_data_header:
            if data_row_start!=0:
                if i==0:
                    els = line.split()
                    tem=np.array(els, dtype= object )              
                    data_header=tem 
        if i==data_row_start:
            els = line.split()
            tem=np.array(els, dtype=float)              
            data=tem    
        if i>data_row_start:
            els = line.split()
            try:
                tem=np.array(els, dtype=float)
                data=np.vstack( (data,tem))         
            except:
                print('This line is not readable.')
                pass                   
    fin.close()        
    if not return_data_header:
        return data #, None
    else:
        return data,data_header    







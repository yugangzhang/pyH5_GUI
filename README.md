# pyH5_GUI
A GUI to visualize hierarchical h5 files. Primarily, the GUI is designed to show XPCS data generated by pyCHX developed at the CHX beamline.

## Download the package
    Under "Clone or download" tab
        git clone https://github.com/yugangzhang/pyH5_GUI.git  
        Or click "Download Zip"

## How to install
### On Linux
    wget https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh \
    chmod +x Anaconda3-2019.03-Linux-x86_64.sh\
    ./Anaconda3-2019.03-Linux-x86_64.sh\
    source ~/.bashrc\
    conda create --name pyGUI python=3\
    conda activate pyGUI\
    pip install numpy   pyqt5 h5py  pyqtgraph  PyOpenGL  tables pandas logger\
    conda install matplotlib
### On Windows    
    Install Anaconda https://docs.anaconda.com/anaconda/install/windows/ (The follow predure is based on Anaconda 3.0 (64-bit)
    Run Anaconda Navigator
    Lauch a terminal by runing 'Enviroments/base(boot)/Open Terminal'
    pip install PyOpenGL logger  pyqtgraph
## How to use
### On Linux
    source activate pyGUI\
    python XSH5View.py  (go to the pyH5_GUI folder)
### On Windows
    python XSH5View.py  (go to the pyH5_GUI folder, under the lauched terminal with Anaconda Navigator)
## How to uncompress the tar.gz file
### On Linux
    tar -xvf test.tar.gz\
    tar -xvf test.tar
### On Windows
    Download 7-zip https://www.7-zip.org/
    Open 7-Zip file manager and find the test.tar.gz file
    Uncompress three times (gz, tar, tar) and finally get a file with extension as .h5

## Screenshot

![GUI] (https://raw.github.com/yugangzhang/pyH5_GUI/master/images/browser.png "a screenshot for the gui")\
![GUI] (https://raw.github.com/yugangzhang/pyH5_GUI/master/images/compare_curves.png "compare curves")\
![GUI] (https://raw.github.com/yugangzhang/pyH5_GUI/master/images/img1.png "two-D image")\
![GUI] (https://raw.github.com/yugangzhang/pyH5_GUI/master/images/img2.png "two-D image") 

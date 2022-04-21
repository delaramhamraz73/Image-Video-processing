import sys
import cv2
import os
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QLabel
from PyQt5.uic import loadUi


class M1_Project(QDialog):
    def __init__(self):
        super(M1_Project,self).__init__()
        loadUi('M1_project.ui',self)
        self.image = None
        self.Vimage = None
        #self.cannyImage = None
        self.loadButton.clicked.connect(self.loadClicked)
        self.saveButton.clicked.connect(self.saveClicked)
        self.cannyButton.clicked.connect(self.cannyClicked)
        self.sobelButton.clicked.connect(self.sobelClicked)
        self.openButton.clicked.connect(self.openWebcam)
        self.closeButton.clicked.connect(self.closeWebcam)
        self.laplacianButton.clicked.connect(self.laplacianClicked)
        self.boxBlurButton.clicked.connect(self.boxBlurClicked)
        self.blurButton.clicked.connect(self.blurClicked)
        self.gaussianBlurButton.clicked.connect(self.gaussianBlurClicked)
        self.resetButton.clicked.connect(self.resetButtonClicked)
        self.sobelVideoButton.setCheckable(True)
        self.sobel_Enabled = False
        self.sobelVideoButton.toggled.connect(self.sobelVideoClicked)
        
                                            
    @pyqtSlot()
    def loadClicked(self):
        global fname
        fname, filter = QFileDialog.getOpenFileName(None, 'open file', '', "Image Files (*.jpg)")
        if fname:
            self.loadImage(fname)
        else:
            print('Invalid Image!!')

        return(fname)
    @pyqtSlot()
    def saveClicked(self):
        fname, filter = QFileDialog.getSaveFileName(None, 'Save File', '', "Image Files (*.jpg)")
        if fname:
            cv2.imwrite(fname, self.image)
        else:
            print("Error!!")
            
    @pyqtSlot()
    def cannyClicked(self):
       
        gray = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY) if len(self.image.shape)>=3  else   self.image
        self.image = cv2.Canny(gray,100,200)
        self.displayImage(2)

    @pyqtSlot()
    def sobelClicked(self):
        gray = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY) if len(self.image.shape)>=3  else   self.image
        HorizentalEdges = cv2.Sobel(gray, -1, dx = 1, dy = 0, ksize = 5, delta = 0, borderType = cv2.BORDER_DEFAULT)
        VerticalEdges = cv2.Sobel(gray, -1, dx = 0, dy = 1, ksize = 5, delta = 0, borderType = cv2.BORDER_DEFAULT)
        self.image = HorizentalEdges + VerticalEdges
        self.displayImage(2)
        
    @pyqtSlot()
    def laplacianClicked(self):
        gray = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY) if len(self.image.shape)>=3  else   self.image
        self.image = cv2.Laplacian(gray, -1, ksize = 5, scale = 1, delta = 0, borderType = cv2.BORDER_DEFAULT)
        self.displayImage(2)
        
    @pyqtSlot()
    def boxBlurClicked(self):
        self.image = cv2.boxFilter(self.image, -1, (23, 23))
        self.displayImage(2)
        
    @pyqtSlot()
    def blurClicked(self):
        self.image = cv2.blur(self.image, (15, 15))
        self.displayImage(2)
        
    @pyqtSlot()
    def gaussianBlurClicked(self):
        self.image = cv2.GaussianBlur(self.image, (19,19), 0)
        self.displayImage(2)
    
    @pyqtSlot()
    def resetButtonClicked(self):
      
        self.loadImage(fname)
        self.displayImage(2)
       
        
    def openWebcam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        
        self.timer= QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1)
        
        
   
    def sobelVideoClicked(self,status):
       # if status:
          #  self.canny_Enabled = True
           # self.cannyVideoButton.setText('Stop Canny!')
       # else:
        #    self.canny_Enabled = False
         #   self.cannyVideoButton.setText('Canny')   
          self.sobel_Enabled = True
          
            
    def update_status(self):
        scale = 1
        delta = 0
        ddepth = cv2.CV_16S
        
        ret, self.Vimage = self.capture.read()
        self.Vimage = cv2.flip(self.Vimage,3)
        self.displayVideo(self.Vimage,3)
        
        if (self.sobel_Enabled):
            gray = cv2.cvtColor(self.Vimage,cv2.COLOR_BGR2GRAY) 
           # self.Vimage = cv2.Canny(gray,100,200)
            grad_x = cv2.Sobel(gray, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)

    # Gradient-Y
    # grad_y = cv.Scharr(gray,ddepth,0,1)
            grad_y = cv2.Sobel(gray, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    

    
            abs_grad_x = cv2.convertScaleAbs(grad_x)
            abs_grad_y = cv2.convertScaleAbs(grad_y)
    

    
            self.Vimage = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
            self.displayVideo(self.Vimage,4)
        
    

    def closeWebcam(self):
        #self.timer.stop()
        self.capture.release()        

    def loadImage(self,fname):
        self.image=cv2.imread(fname,cv2.IMREAD_COLOR)
        self.displayImage(1)

    def displayImage(self, window = 1):
        qformat=QImage.Format_Indexed8

        if len(self.image.shape)==3:
            if(self.image.shape[2])==4:
                qformat=QImage.Format_RGBA8888
            else:
                qformat=QImage.Format_RGB888
                
        img = QImage(self.image,self.image.shape[1],self.image.shape[0],self.image.strides[0],qformat)
        img = img.rgbSwapped()
        
        if window == 1:
            
            self.imgLabel.setPixmap(QPixmap.fromImage(img))
            #self.imgLabel.setGeometry(40,50,405,540)
            self.imgLabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            
        if window == 2: 
            self.finalLabel.setPixmap(QPixmap.fromImage(img))       
            self.finalLabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        
        if window == 3:
            self.webcamLabel.setPixmap(QPixmap.fromImage(img))       
            self.webcamLabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            
        if window == 4:
            self.webcam2Label.setPixmap(QPixmap.fromImage(img))       
            self.webcam2Label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            
            
    def displayVideo(self,Vimage, window = 3):
        qformatVideo=QImage.Format_Indexed8

        if len(self.Vimage.shape)==3:
            if(self.Vimage.shape[2])==4:
                qformatVideo=QImage.Format_RGBA8888
            else:
                qformatVideo=QImage.Format_RGB888
                
        vid = QImage(self.Vimage,self.Vimage.shape[1],self.Vimage.shape[0],self.Vimage.strides[0],qformatVideo)
        vid = vid.rgbSwapped()
        
     
        if window == 3:
            self.webcamLabel.setPixmap(QPixmap.fromImage(vid))       
            self.webcamLabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            
        if window == 4:
            self.webcam2Label.setPixmap(QPixmap.fromImage(vid))       
            self.webcam2Label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        

app = QApplication(sys.argv)
window=M1_Project()
#window.setGeometry(1000,1000,1000,1000)
window.setWindowTitle('Image and Video Processing!')
window.show()
sys.exit(app.exec_())







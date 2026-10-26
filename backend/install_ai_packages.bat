@echo off
echo Installing AI/ML packages for MAXIMUM POWER training...
echo.
cd backend
echo ============================================
echo Installing Core TensorFlow and Keras...
echo ============================================
pip install tensorflow==2.16.1
pip install keras==3.3.0
pip install numpy==1.26.4
pip install pillow==10.3.0
echo.
echo ============================================
echo Installing Object Detection (YOLO)...
echo ============================================
pip install ultralytics==8.1.0
pip install torch==2.1.0
pip install torchvision==0.16.0
echo.
echo ============================================
echo Installing Face Recognition...
echo ============================================
pip install face-recognition==1.3.0
pip install dlib==19.24.2
pip install opencv-python==4.9.0.80
pip install opencv-contrib-python==4.9.0.80
echo.
echo ============================================
echo Installing Visualization and Metrics...
echo ============================================
pip install matplotlib==3.8.0
pip install seaborn==0.13.0
pip install scikit-learn==1.4.0
echo.
echo ============================================
echo All packages installed successfully!
echo ============================================
echo.
echo System is now ready for MAXIMUM POWER AI training!
echo.
pause

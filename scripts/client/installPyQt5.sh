# install PyQt5
sudo apt update -y
sudo apt install python3-pyqt5 -y
sudo apt install python3-pyqt5.qtsvg -y
# copy package files to virtual environment
cp -a /usr/lib/python3/dist-packages/PyQt5 ./torenv/lib/python3.7/site-packages/
cp -a /usr/lib/python3/dist-packages/sip* ./torenv/lib/python3.7/site-packages/
# export XAUTHORITY variable for accessing screen as root
sudo echo 'if [ -n "$SSH_CONNECTION" ]; then' >> ~/.bashrc
sudo echo '    export XAUTHORITY=/home/pi/.Xauthority' >> ~/.bashrc
sudo echo 'fi' >> ~/.bashrc

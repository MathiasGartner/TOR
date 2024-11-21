# enable root user
echo "root:testtest" | chpasswd

# allow ssh root login
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

# copy all authorized keys from user pi to root
mkdir /root/.ssh
cp /home/pi/.ssh/authorized_keys /root/.ssh/

# reboot to restart all services
echo "reboot..."
reboot
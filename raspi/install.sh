echo "Installing..."
sudo service uart stop
sudo cp uart.sh /etc/init.d/uart
sudo chmod +x /etc/init.d/uart
sudo update-rc.d uart default
sudo service uart start
echo "Done"
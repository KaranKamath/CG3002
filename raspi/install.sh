echo "Installing..."
sudo service uart stop
sudo cp uart.sh /etc/init.d/uart
sudo chmod +x /etc/init.d/uart
sudo service uart start
echo "Done"
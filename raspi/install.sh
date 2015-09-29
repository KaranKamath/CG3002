echo "Installing..."
sudo service uart stop
sudo cp uart.sh /etc/init.d/uart.sh
sudo chmod +x /etc/init.d/uart.sh
sudo update-rc.d uart default
sudo service uart start
echo "Done"
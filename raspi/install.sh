echo "Installing..."
sudo service tweet-ip stop
sudo cp tweet-ip-service.sh /etc/init.d/tweet-ip
sudo chmod +x /etc/init.d/tweet-ip
sudo insserv tweet-ip
sudo service tweet-ip start

sudo service uart stop
sudo cp uart-service.sh /etc/init.d/uart
sudo chmod +x /etc/init.d/uart
sudo insserv uart
sudo service uart start

cron_cmd='@reboot rm -f /home/pi/.ip /home/pi/logs/*'
cron_exists=$(sudo crontab -l | grep "$cron_cmd")
if [ $? -eq 1 ]
then
    echo "Adding Tweet-IP cron..."
    (sudo crontab -l; echo "$cron_cmd" ) | crontab -
else
    echo "Tweet-IP cron exists already."
fi

cron_cmd='* * * * * /home/pi/cg3002/wifi_reconnect.sh'
cron_exists=$(sudo crontab -l | grep "$cron_cmd")
if [ $? -eq 1 ]
then
    echo "Adding Wifi-Reconnect cron..."
    (sudo crontab -l; echo "$cron_cmd" ) | crontab -
else
    echo "Wifi-Reconnect cron exists already."
fi

echo "Done"
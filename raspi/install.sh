echo "Installing..."
sudo service tweet-ip stop
sudo rm -f /home/pi/logs/tweet_ip.log*
sudo cp services/tweet-ip-service.sh /etc/init.d/tweet-ip
sudo chmod +x /etc/init.d/tweet-ip
sudo insserv tweet-ip

sudo service uart stop
sudo rm -f /home/pi/logs/uart.log*
touch /home/pi/logs/uart.log
sudo cp services/uart-service.sh /etc/init.d/uart
sudo chmod +x /etc/init.d/uart
sudo insserv uart

sudo service navi stop
sudo rm -f /home/pi/logs/navi.log*
touch /home/pi/logs/navi.log
sudo cp services/navi-service.sh /etc/init.d/navi
sudo chmod +x /etc/init.d/navi
sudo insserv navi

sudo service localizer stop
sudo rm -f /home/pi/logs/localizer.log*
touch /home/pi/logs/localizer.log
sudo cp services/localizer-service.sh /etc/init.d/localizer
sudo chmod +x /etc/init.d/localizer
sudo insserv localizer

sudo rm -f /home/pi/db/uart.db*
sudo service tweet-ip start
sudo service uart start
sudo service navi start
sudo service localizer start

cron_cmd='@reboot rm -f /home/pi/.ip /home/pi/logs/* /home/pi/db/*'
cron_exists=$(sudo crontab -l | grep -F "$cron_cmd")
if [ $? -eq 1 ]
then
    echo "Adding Tweet-IP cron..."
    (sudo crontab -l; echo "$cron_cmd" ) | crontab -
else
    echo "Tweet-IP cron exists already."
fi

cron_cmd='* * * * * /home/pi/cg3002/wifi_reconnect.sh'
cron_exists=$(sudo crontab -l | grep -F "$cron_cmd")
if [ $? -eq 1 ]
then
    echo "Adding Wifi-Reconnect cron..."
    (sudo crontab -l; echo "$cron_cmd" ) | crontab -
else
    echo "Wifi-Reconnect cron exists already."
fi

echo "Done"
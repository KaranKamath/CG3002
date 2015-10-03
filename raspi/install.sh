echo "Installing..."
sudo service tweet-ip stop
sudo cp tweet-ip-service.sh /etc/init.d/tweet-ip
sudo chmod +x /etc/init.d/tweet-ip
sudo update-rc.d tweet-ip defaults
sudo service tweet-ip start

sudo service uart stop
sudo cp uart-service.sh /etc/init.d/uart
sudo chmod +x /etc/init.d/uart
sudo update-rc.d uart defaults
sudo service uart start

cron_exists=$(sudo crontab -l | grep 'rm -f /home/pi/.ip')
if [ $? -eq 1 ]
then
    echo "Adding cron..."
    cron_cmd='@reboot rm -f /home/pi/.ip'
    (sudo crontab -l; echo "$cron_cmd" ) | crontab -
else
    echo "Cron exists already."
fi
echo "Done"
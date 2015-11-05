echo "Deploying..."
rsync -r --delete ../raspi/ pi@$1:~/cg3002/
scp pi@$1:/home/pi/db/uart.db backups/uart.$(date '+%I-%M-%S').db
scp pi@$1:/home/pi/test_data.txt backups/test_data.$(date '+%I-%M-%S').txt
echo "Done."

COMMAND="cd ~/cg3002;"
if [ "$2" == "--install-prereqs" ]; then
    COMMAND+="sudo ./install_prereqs.sh;"
fi
COMMAND+="sudo ./install.sh;"

ssh pi@$1 "$COMMAND"

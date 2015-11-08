echo "Deploying..."
# scp pi@$1:/home/pi/db/uart.db backups/uart.$(date '+%I-%M-%S').db
# TIMESTAMP=$(date '+%s')
mkdir ../images/$TIMESTAMP
scp -r 'pi@192.168.43.77:/home/pi/cg3002/images/*' ../images/$TIMESTAMP
rsync -r --delete ../raspi/ pi@$1:~/cg3002/
echo "Done."

COMMAND="cd ~/cg3002;"
if [ "$2" == "--install-prereqs" ]; then
    COMMAND+="sudo ./install_prereqs.sh;"
fi
COMMAND+="sudo ./install.sh;"

ssh pi@$1 "$COMMAND"

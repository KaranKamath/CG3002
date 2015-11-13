echo "Deploying..."
TIMESTAMP=$(date '+%s')
mkdir -p ../images/$TIMESTAMP && \
scp pi@$1:/home/pi/db/uart.db backups/uart.$(date '+%I-%M-%S').db && \
# scp -r 'pi@172.20.10.7:/home/pi/cg3002/images/*' ../images/$TIMESTAMP && \
rsync -r --delete ../raspi/ pi@$1:~/cg3002/ && \
echo "Done." || echo "Failed"


FILES=(../images/$TIMESTAMP/*)
if [ ${#FILES[@]} -gt 1 ]; then
    echo "Copied images..."
    rm ../images/$TIMESTAMP/empty.jpg
else
    echo "Removing redundant dir..."
    rm -rf ../images/$TIMESTAMP;
fi


COMMAND="cd ~/cg3002;"
if [ "$2" == "--install-prereqs" ]; then
    COMMAND+="sudo ./install_prereqs.sh;"
fi
COMMAND+="sudo ./install.sh;"

ssh pi@$1 "$COMMAND"

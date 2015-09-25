echo "Deploying..."
rsync -r --delete ../raspi/ pi@$1:~/cg3002/
echo "Done."

COMMAND="cd ~/cg3002;"
if [ "$2" == "--install-prereqs" ]; then
    COMMAND+="sudo ./install_prereqs.sh;"
fi
COMMAND+="sudo ./install.sh;"

ssh pi@$1 "$COMMAND"

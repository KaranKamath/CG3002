echo "Deploying..."
rsync -r --delete * pi@$1:~/cg3002
echo "Done."
if [ "$2" == "-i" ]; then
    ssh pi@$1 'cd ~/cg3002; sudo ./install.sh;'
fi

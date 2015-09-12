echo "Deploying..."
rsync -ru * pi@$1:~/CG3002
echo "Done."
ssh pi@$1 'cd ~/CG3002; sudo ./install.sh;'

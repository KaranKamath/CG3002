echo "Installing Prereqs...";
sudo apt-get install build-essential libssl-dev libffi-dev python-dev;
sudo apt-get autoremove;
sudo pip install -r requirements.txt;
echo "Done.";

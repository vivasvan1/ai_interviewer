apt install -y screen
source ~/.bashrc
screen -dmS fast "./fast.sh"

screen -dmS ngrok "./ngrok.sh"

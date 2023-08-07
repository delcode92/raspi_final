#!/bin/bash
KEY=2SSvqyZhIEy1NgCB5U7WZbkI7bn_3Zu7gPk1KPYsbu6FQFEDx

echo "******************************************"
echo "====== START BUILDING DEPEDENCIES ======== "
echo "******************************************"

# install git
sudo apt install git-all

# install curl
sudo apt install curl

# install ngrok via apt
 curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok

# or via snap
#  snap install ngrok

# add ngrok key
ngrok config add-authtoken $KEY

# go to home
cd ~

# remove last proj
sudo rm -r ~/mk_serv

# clone repo
git clone https://github.com/delcode92/mk_serv.git

echo "******************************************"
echo "=============== FINISH ================== "
echo "******************************************"
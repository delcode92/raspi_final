#!/bin/bash

SERVER="192.168.100.80"
PATH_NGROK="/Users/Admin/Documents/project/raspi_final/ngrok_banget" 
PATH_PROJ="/Users/Admin/Documents/project/raspi_final/"
 
# cd to path
cd $PATH_NGROK

#run ngrok service
ngrok tcp $SERVER:22 &

sleep 3

#run curl service > ngrok_json.txt
curl 127.0.0.1:4040/api/tunnels > ngrok_json.txt & 


sleep 3


cd $PATH_PROJ

git add --all
git commit -m "update" 
git push origin main 


wait

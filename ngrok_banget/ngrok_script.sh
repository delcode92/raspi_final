#!/bin/bash
#2SSvqyZhIEy1NgCB5U7WZbkI7bn_3Zu7gPk1KPYsbu6FQFEDx

SERVER="192.168.100.80"
PATH_NGROK="/Users/Admin/Documents/project/raspi_final/ngrok_banget" 
PATH_PROJ="/Users/Admin/Documents/project/raspi_final/"
 
# cd to path
cd $PATH_NGROK

#run ngrok service
ngrok tcp $SERVER:22 &

sleep 6

#run curl service > ngrok_json.txt
curl 127.0.0.1:4040/api/tunnels > ngrok_json.txt & 


sleep 6


cd $PATH_PROJ


git add --all
git commit -m "update" 
git push origin main 


wait

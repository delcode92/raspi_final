#!/bin/bash

SERVER="127.0.0.1"
PATH_PROJ="~/mk_serv"
 
# cd to path
cd $PATH_PROJ



#run ngrok service
ngrok tcp $SERVER:22 &

sleep 6

#run curl service > ngrok_json.txt
curl 127.0.0.1:4040/api/tunnels > ngrok_json.txt & 


sleep 6


cd $PATH_PROJ

git config --global user.email "projmk9@gmail.com"
git config --global user.name "projmk9"

git add --all
git commit -m "update" 
git push origin main 


wait

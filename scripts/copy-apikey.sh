#!/bin/bash
echo "Copying IBM Cloud apikey into development environment..."
# docker cp ~/.bluemix/apikey.json lab-bluemix-cf:/home/vscode 
# docker exec lab-bluemix-cf sudo chown vscode:vscode /home/vscode/apikey.json
docker cp ~/.bluemix/apikey.json vscode:/home/vscode 
docker exec orders sudo chown vscode:vscode /home/vscode/apikey.json
echo "Complete"

#!/bin/bash

NAME=${1:-app}

if [ -d "./${NAME}" ]; then
  echo ">>> Deleting folder: ./${NAME}/"
  chmod -R u+w ./${NAME}
  rm -r ./${NAME} || { echo "Failed to delete ./${NAME}/. Check permissions."; exit 1; }
else
  echo ">>> Folder does not exist: ./${NAME}/"
fi

if [ -f "${NAME}.zip" ]; then
  echo ">>> Extracting archive: ${NAME}.zip"
  unzip ${NAME}.zip
else
  echo ">>> Archive ${NAME}.zip not found! Exiting."
  exit 1
fi

  cd ${NAME} || { echo ">>> Failed to enter folder ${NAME}. Exiting."; exit 1; }

if [ -f "install_server.sh" ]; then
  echo ">>> chmod 755 install_server.sh"
  chmod 755 install_server.sh
  chmod 755 cleanup_docker.sh
else
  echo ">>> install_server.sh not found! Exiting."
  exit 1
fi


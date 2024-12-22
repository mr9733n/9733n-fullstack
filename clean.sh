#!/bin/bash

NAME=${1:-app}

if [ -d "./${NAME}" ]; then
  echo ">>> Deleting folder: ./${NAME}/"
  chmod -R u+w ./${NAME}
  rm -r ./${NAME} || { echo "Failed to delete ./${NAME}/. Check permissions."; exit 1; }
else
  echo ">>> Folder does not exist: ./${NAME}/"
fi

#!/bin/bash

cleanup_containers() {
  echo ">>> Deleting docker containers..."
  docker container prune -f
}

cleanup_images() {
  echo ">>> Deleting docker images..."
  docker image prune -a -f
}

cleanup_volumes() {
  echo ">>> Deleting docker volumes..."
  docker volume prune -f
}

cleanup_networks() {
  echo ">>> Deleting docker network..."
  docker network prune -f
}

main() {
  echo ">>> Starting deleting docker data..."
  cleanup_containers
  cleanup_images
  cleanup_volumes
  cleanup_networks
  echo ">>> All done!"
}

main

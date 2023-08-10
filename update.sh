#!/bin/sh

set -e

COMPOSE_FILE=compose.yml

if [ "$1" = "--proxy" ]; then
  COMPOSE_FILE=compose.proxy.yml
fi

pretty_printf() {
  COLOR="1;34m"
  STARTCOLOR="\e[$COLOR"
  ENDCOLOR="\e[0m"
  printf "$STARTCOLOR%b$ENDCOLOR\n" "$1"
}

pretty_printf "stopping running containers..."
docker compose -f $COMPOSE_FILE down

pretty_printf "pulling changes from git..."
git pull --rebase --autostash --tags

pretty_printf "pulling changes from docker..."
docker compose pull

pretty_printf "starting containers..."
docker compose -f $COMPOSE_FILE up --build --detach

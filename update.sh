#!/bin/sh

set -e

pretty_printf() {
  COLOR="1;34m"
  STARTCOLOR="\e[$COLOR"
  ENDCOLOR="\e[0m"
  printf "$STARTCOLOR%b$ENDCOLOR\n" "$1"
}

COMPOSE_FILE=compose.yml
PROXY_COMPOSE_FILE=compose.proxy.yml

if [ "$1" = "--proxy" ]; then
  COMPOSE_FILE=$PROXY_COMPOSE_FILE
else
  if docker compose ls | grep -q $PROXY_COMPOSE_FILE; then
    pretty_printf "you have reverse proxy running. are you sure you want to perform update without reverse proxy? (y/n)"
    read -r answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
      pretty_printf "ok. starting update..."
    else
      pretty_printf "abort..."
      exit 1
    fi
  fi
fi

pretty_printf "stopping running containers..."
docker compose -f $COMPOSE_FILE down

pretty_printf "pulling changes from git..."
git pull --rebase --autostash --tags

pretty_printf "pulling changes from docker..."
docker compose pull

pretty_printf "starting containers..."
docker compose -f $COMPOSE_FILE up --build --detach

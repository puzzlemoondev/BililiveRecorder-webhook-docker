.PHONY: build local

build:
	-docker buildx create --name docker-container --driver docker-container
	docker buildx build --builder docker-container --cache-from type=registry,ref=puzzlemoondev/bililive-recorder-webhook:build-cache --load -t puzzlemoondev/bililive-recorder-webhook:local .
up: build local
	docker-compose up --detach
run: build local
	docker-compose run --rm -it webhook sh
exec:
	docker-compose exec webhook sh
down:
	docker-compose down
update:
	chmod +x update.sh
	./update.sh
local:
	sd 'latest|edge' local compose.yml
latest:
	sd 'local|edge' latest compose.yml
edge:
	sd 'local|latest' edge compose.yml

.PHONY: build local

up:
	docker-compose up --build --detach
exec:
	docker-compose exec webhook sh
down:
	docker-compose down
reup: down up
update:
	chmod +x update.sh
	./update.sh
local:
	sd 'latest|edge' local compose.yml
latest:
	sd 'local|edge' latest compose.yml
edge:
	sd 'local|latest' edge compose.yml
.PHONY: down up

up:
	docker compose up --build --detach
exec:
	docker compose exec webhook sh
logs:
	docker compose logs --follow
down:
	docker compose down
reup: down up
update:
	./update.sh

proxy-up:
	docker compose -f compose.proxy.yml up --build --detach
proxy-logs:
	docker compose -f compose.proxy.yml logs --follow
proxy-down:
	docker compose -f compose.proxy.yml down
proxy-reup: proxy-down proxy-up
proxy-update:
	./update.sh --proxy

local:
	sd 'latest|edge' local compose.yml
latest:
	sd 'local|edge' latest compose.yml
edge:
	sd 'local|latest' edge compose.yml
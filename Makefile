export GIT_COMMIT_HASH := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")

build:
	docker compose build $(ARGS)

up:
	docker compose up -d $(ARGS)

deploy:
	git pull origin deploy
	GIT_COMMIT_HASH=$$(git rev-parse --short HEAD) docker compose build $(ARGS)
	docker compose up -d --remove-orphans $(ARGS)

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

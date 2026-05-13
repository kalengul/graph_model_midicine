export GIT_COMMIT_HASH := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")

build:
	docker compose build $(ARGS)

up:
	docker compose up -d $(ARGS)

deploy:
	git pull origin deploy
	docker compose up -d --build $(ARGS)

stop:
	docker compose down

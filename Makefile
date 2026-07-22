export GIT_COMMIT_HASH := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Список доступных команд и их описание
help:
	@awk 'BEGIN {FS=":"} \
	/^# ---/ {printf "\n"; next} \
	/^#/ {comment=substr($$0,3)} \
	/^[a-zA-Z0-9_-]+:/ {printf "\033[36m%-20s\033[0m %s\n", $$1, comment}' Makefile

# --- Production commands ---
# Собрать образы сервисов
prod:
	docker compose build $(ARGS)

# Обновить код, пересобрать и запустить
prod-deploy:
	git pull origin deploy
	GIT_COMMIT_HASH=$$(git rev-parse --short HEAD) docker compose build $(ARGS)
	docker compose up -d --remove-orphans $(ARGS)

# Запустить контейнеры (продакшен)
prod-up:
	docker compose up -d $(ARGS)

# Остановить контейнеры
prod-down:
	docker compose down

# Список запущенных контейнеров
prod-status:
	docker compose ps

# --- Development commands ---
# Собрать dev (без SSL, локальная разработка)
dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml build $(ARGS)

# Запустить dev-сборку
dev-up:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d $(ARGS)

# Остановить dev-сборку
dev-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

# Список запущенных контейнеров dev-сборки
dev-status:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml ps

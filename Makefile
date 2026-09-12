SHELL := powershell.exe
.SHELLFLAGS := -NoProfile -Command

.PHONY: dev up down logs migrate lock

dev:
	docker-compose up --build

up:
	docker-compose up -d --build

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	docker-compose run --rm backend alembic upgrade head

lock:
	# Create or update a pinned requirements file for production use
	backend/infra/scripts/generate-lock.sh

.PHONY: poetry-install-backend poetry-lock-backend poetry-export-reqs-backend

poetry-install-backend:
	# Install dependencies via Poetry
	poetry -C "./backend" install --no-root

poetry-lock-backend:
	# Generate/refresh poetry.lock
	poetry -C "./backend" lock

poetry-export-reqs-backend:
	# Export a pip requirements file for Docker or other tooling
	poetry -C "./backend" export -f requirements.txt --output requirements.txt --without-hashes

.PHONY: start-server start-venv-server poetry-test-backend
start-server:
	cd backend; poetry run python -c "import sys; sys.path.insert(0, 'src'); import uvicorn; uvicorn.run('asset_management_server.main:app', host='0.0.0.0', port=8000, reload=True, reload_dirs=['src'])"

start-venv-server:
	cd backend
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	python -m pip install --upgrade pip setuptools wheel
	pip install -r backend/requirements.txt

poetry-test-backend:
	# Run tests for the backend
	poetry -C "./backend" run pytest
.PHONY: all install install-frontend install-backend dev dev-frontend dev-backend build-frontend migrate migrate-new generate-types test format-backend format-frontend lint-backend lint-frontend


# Install dependencies and setup the project
all: install

# Install dependencies
install: 
	$(MAKE) -j 2 install-frontend install-backend

# Install frontend dependencies
install-frontend:
	bun install

# Install backend dependencies
install-backend:
	python -m venv .venv
	.venv/Scripts/pip install -r requirements.txt

# Build frontend + SSR, then run dev server
preview:
	$(MAKE) build-frontend
	$(MAKE) dev-backend

# run the server
serve:
	cd backend && ../.venv/Scripts/python -m flask --app app run --port 3001 --host 127.0.0.1 --no-reload

# Clear Python bytecode cache (fixes stale app if / returns 404 despite route existing).
clean-py:
	.venv/Scripts/python -c "import shutil,pathlib; [shutil.rmtree(p) for p in pathlib.Path('backend').rglob('__pycache__') if p.is_dir()]"
	@echo "Cleared Python cache. Restart the server (Ctrl+C then make serve)."

# runs development frontend and backend servers
dev:
	@echo "Starting dev servers..."
	@bun x concurrently "make dev-backend" "make dev-frontend" --names "backend,frontend" --kill-others

# starts development frontend for hot module reloading
dev-frontend:
	bunx --bun vite

# starts development database and server
dev-backend: dev-postgres serve

# builds the frontend for production with SSR
build-frontend:
	bunx --bun vite build
	bunx --bun vite build --ssr entry-server.tsx
	.venv/Scripts/python scripts/inject-ssr-template.py

# Run database migrations
migrate:
	cd backend && ../.venv/Scripts/python -m flask --app app db upgrade

# Create a new migration
migrate-new:
	cd backend && ../.venv/Scripts/python -m flask --app app db migrate -m "$(msg)"

# Generate TypeScript types from Pydantic schemas (run from project root)
generate-types:
	.venv/Scripts/pydantic2ts --module backend/schemas.py --output frontend/types/api.ts --json2ts-cmd "bunx json2ts"

# Run unit tests
test:
	bun test

# format backend code with Black
format-backend:
	.venv/Scripts/python -m black backend/

# format frontend code with Biome
format-frontend:
	bunx --bun biome check --write

# format both frontend and backend code with Biome and Black
format:
	$(MAKE) -j 2 format-frontend format-backend

# lint frontend code with Biome
lint-frontend:
	bunx --bun biome lint

# lint backend code with Pylint and Mypy
lint-backend:
	.venv/Scripts/python -m pylint backend/
	.venv/Scripts/python -m mypy backend/

# lint both frontend and backend code with Biome and Pylint
lint:
	$(MAKE) -j 2 lint-frontend lint-backend

# starts development database
dev-postgres:
	docker compose up -d
	@echo "Waiting for Postgres to be ready..."
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		if docker compose exec -T postgres pg_isready -U railreach -d railreach 2>/dev/null; then \
			echo "Postgres is ready"; \
			exit 0; \
		fi; \
		sleep 2; \
	done; \
	echo "Postgres failed to start"; exit 1

clean:
	rm -rf backend/__pycache__ backend/*.pyc backend/.mypy_cache backend/.pytest_cache
	rm -rf .venv/__pycache__ .venv/*.pyc
	rm -rf frontend/dist frontend/.next frontend/.turbo
	rm -rf dist
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete


# Install Python dependencies for scraping/seeding
py-deps:
	python -m pip install -r scripts/python/requirements.txt

# Scrape data for each model (run from scripts/scrape so python.common is importable)
scrape-stations:
	cd scripts/scrape && ../../.venv/Scripts/python scrape_stations.py

scrape-routes:
	cd scripts/scrape && ../../.venv/Scripts/python scrape_routes.py

scrape-regions:
	cd scripts/scrape && ../../.venv/Scripts/python scrape_regions.py

scrape-all: scrape-stations scrape-routes scrape-regions

validate-data:
	cd scripts/scrape && ../../.venv/Scripts/python validate_data.py

# Seed database from scraped JSON (uses Flask backend + PostgreSQL)
seed-db:
	.venv/Scripts/python scripts/scrape/seed_db.py

data-pipeline: scrape-all validate-data seed-db

docker-local: dev-postgres
	docker build -t railreach .
	docker run -p 8000:8000 -e DATABASE_URL="postgresql://railreach:railreach@host.docker.internal:5432/railreach" railreach
	docker network create railreach-net
	docker run -d --name postgres \
		--network railreach-net \
		-e POSTGRES_USER=railreach \
		-e POSTGRES_PASSWORD=railreach \
		-e POSTGRES_DB=railreach \
		postgres:16-alpine
	docker run -p 8000:8000 --network railreach-net \
		-e DATABASE_URL="postgresql://railreach:railreach@postgres:5432/railreach" \
		railreach
	
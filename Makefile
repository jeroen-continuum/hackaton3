.PHONY: db db-stop backend frontend seed load-kbo seed-financials ingest dev

db:
	docker compose -f docker-compose.db.yml up -d

db-stop:
	docker compose -f docker-compose.db.yml down

backend:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

frontend:
	cd frontend && npm start

seed:
	cd backend && source .venv/bin/activate && python -m app.db.seed

# Load all active Belgian companies from the KBO dump (in backend/data/kbo/).
load-kbo:
	cd backend && source .venv/bin/activate && python -m app.db.load_kbo

# Populate synthetic NBB financials for every company (enables size/financial filters).
# Add ARGS=--force to wipe + regenerate.
seed-financials:
	cd backend && source .venv/bin/activate && python -m app.db.seed_financials $(ARGS)

# Enrich + score the candidate pond and rank the Rolling 10.
ingest:
	cd backend && source .venv/bin/activate && python -m app.run_pipeline

dev:
	@echo "Run each in a separate terminal:"
	@echo "  make db        # start postgres container"
	@echo "  make backend   # uvicorn on :8000"
	@echo "  make frontend  # ng serve on :4200"
	@echo ""
	@echo "First time only:"
	@echo "  cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
	@echo "  cd frontend && npm install"
	@echo "  make seed       # solution cases"
	@echo "  make load-kbo        # all active BE companies (needs KBO dump in backend/data/kbo/)"
	@echo "  make seed-financials # synthetic financials so size/financial filters work"
	@echo "  make ingest          # enrich + score -> Rolling 10"

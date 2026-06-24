.PHONY: db db-stop backend frontend seed dev

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

dev:
	@echo "Run each in a separate terminal:"
	@echo "  make db        # start postgres container"
	@echo "  make backend   # uvicorn on :8000"
	@echo "  make frontend  # ng serve on :4200"
	@echo ""
	@echo "First time only:"
	@echo "  cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
	@echo "  cd frontend && npm install"
	@echo "  make seed"

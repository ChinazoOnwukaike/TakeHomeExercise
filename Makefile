.PHONY: install migrate seed test test-frontend dev

install:
	cd backend && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
	cd frontend && npm install

migrate:
	cd backend && FLASK_APP=run.py ./venv/bin/flask db upgrade

seed:
	cd backend && ./venv/bin/python seed.py

test:
	cd backend && ./venv/bin/python -m pytest tests/ -v

test-frontend:
	cd frontend && npm test -- --no-coverage

dev:
	cd frontend && npm run dev:all

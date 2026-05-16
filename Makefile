.PHONY: install seed test dev

install:
	cd backend && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
	cd frontend && npm install

seed:
	cd backend && ./venv/bin/python seed.py

test:
	cd backend && ./venv/bin/python -m pytest tests/ -v

dev:
	cd frontend && npm run dev:all

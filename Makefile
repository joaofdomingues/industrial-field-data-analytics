.PHONY: backend frontend etl test seed docker clean

backend:
	cd backend && python manage.py runserver

frontend:
	cd frontend && npm run dev

etl:
	python etl/process_data.py && python etl/anomaly_detection.py

seed:
	cd backend && python manage.py migrate && python manage.py import_machine_data --reset

test:
	cd backend && python manage.py test

docker:
	docker compose up --build

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
	find . -name "*.pyc" -delete

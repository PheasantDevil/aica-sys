# Makefile for AICA-SyS
# Phase 8-2: Containerization and Orchestration

.PHONY: help build up down logs clean test deploy k8s-deploy k8s-delete

# デフォルトターゲット
help:
	@echo "AICA-SyS - Make Commands"
	@echo ""
	@echo "Docker Compose Commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make logs           - View logs"
	@echo "  make clean          - Clean up containers and volumes"
	@echo "  make restart        - Restart all services"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev-backend    - Start backend in development mode"
	@echo "  make dev-frontend   - Start frontend in development mode"
	@echo "  make test           - Run all tests"
	@echo ""
	@echo "Kubernetes Commands:"
	@echo "  make k8s-deploy     - Deploy to Kubernetes"
	@echo "  make k8s-delete     - Delete from Kubernetes"
	@echo "  make k8s-status     - Check Kubernetes status"
	@echo ""
	@echo "Production Commands:"
	@echo "  make prod-build     - Build production images"
	@echo "  make prod-up        - Start production environment"
	@echo "  make prod-down      - Stop production environment"

# Docker Compose - Development
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v
	docker system prune -f

# Docker Compose - Production
prod-build:
	docker-compose -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

# Development
dev-backend:
	cd backend && source venv/bin/activate && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend:
	cd frontend && npm run dev

# Testing
test:
	@echo "Running backend tests..."
	cd backend && source venv/bin/activate && pytest
	@echo "Running frontend tests..."
	cd frontend && npm run test

test-integration:
	node scripts/comprehensive-load-test.js --users=10 --duration=30

test-load:
	node scripts/verify-scalability.js

# Kubernetes
k8s-deploy:
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/redis-deployment.yaml
	kubectl apply -f k8s/backend-deployment.yaml
	kubectl apply -f k8s/frontend-deployment.yaml
	kubectl apply -f k8s/ingress.yaml

k8s-delete:
	kubectl delete -f k8s/ingress.yaml
	kubectl delete -f k8s/frontend-deployment.yaml
	kubectl delete -f k8s/backend-deployment.yaml
	kubectl delete -f k8s/redis-deployment.yaml
	kubectl delete -f k8s/configmap.yaml

k8s-status:
	kubectl get pods -l app=aica-sys
	kubectl get services -l app=aica-sys
	kubectl get ingress aica-sys-ingress

k8s-logs-backend:
	kubectl logs -f -l component=backend

k8s-logs-frontend:
	kubectl logs -f -l component=frontend

# Database
db-init:
	cd backend && python3 -c "from database import init_db; init_db()"

db-optimize:
	python3 scripts/sqlite-optimization.py

db-backup:
	cp backend/aica_sys.db backend/aica_sys.db.backup.$$(date +%Y%m%d_%H%M%S)

# Installation
install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

install-all: install-backend install-frontend
	npm install

# Deployment
deploy-staging:
	./scripts/deploy.sh staging

deploy-production:
	./scripts/deploy.sh production

# Monitoring
monitoring-up:
	docker-compose -f docker-compose.monitoring.yml up -d

monitoring-down:
	docker-compose -f docker-compose.monitoring.yml down

monitoring-logs:
	docker-compose -f docker-compose.monitoring.yml logs -f

prometheus-ui:
	@echo "Opening Prometheus UI at http://localhost:9090"
	open http://localhost:9090 || xdg-open http://localhost:9090

grafana-ui:
	@echo "Opening Grafana UI at http://localhost:3001"
	@echo "Default credentials: admin / admin123"
	open http://localhost:3001 || xdg-open http://localhost:3001

alertmanager-ui:
	@echo "Opening Alertmanager UI at http://localhost:9093"
	open http://localhost:9093 || xdg-open http://localhost:9093

# Backup and Recovery
backup:
	./scripts/backup.sh

restore:
	./scripts/restore.sh

restore-from:
	./scripts/restore.sh $(BACKUP_FILE)

list-backups:
	@echo "Available backups:"
	@ls -lht backups/*.tar.gz 2>/dev/null | head -10 || echo "No backups found"

# Security
security-check:
	./scripts/security-check.sh

security-reports:
	@echo "Security reports:"
	@ls -lh security-reports/ 2>/dev/null || echo "No reports found"

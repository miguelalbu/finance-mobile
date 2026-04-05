.PHONY: up down backend mobile test logs help

# ── Ambiente completo ──────────────────────────────────────────────────────────

up:
	@echo "Subindo ambiente completo..."
	docker compose up --build -d

down:
	@echo "Derrubando ambiente..."
	docker compose down

# ── Serviços individuais ───────────────────────────────────────────────────────

backend:
	@echo "Subindo apenas o backend..."
	docker compose up --build backend db -d

mobile:
	@echo "Subindo apenas o mobile..."
	docker compose up --build mobile -d

# ── Testes ────────────────────────────────────────────────────────────────────

test:
	@echo "Executando testes do backend..."
	docker compose build backend
	docker compose run --rm backend pytest app/tests -v

test-local:
	@echo "Executando testes localmente..."
	cd back && pytest app/tests -v

# ── Utilitários ───────────────────────────────────────────────────────────────

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-db:
	docker compose logs -f db

# ── Help ──────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  make up           - Sobe todo o ambiente (backend + db + mobile)"
	@echo "  make down         - Derruba todo o ambiente"
	@echo "  make backend      - Sobe apenas backend + banco"
	@echo "  make mobile       - Sobe apenas o mobile"
	@echo "  make test         - Roda testes via Docker"
	@echo "  make test-local   - Roda testes localmente (requer .env no /back)"
	@echo "  make logs         - Exibe logs de todos os serviços"
	@echo "  make logs-backend - Exibe logs apenas do backend"
	@echo ""

# Finance App — Desafio Técnico Fullstack

Aplicação para consulta de cotações de ativos financeiros, com backend em FastAPI, mobile em React Native (Expo) e banco de dados PostgreSQL.

## Sumário

- [Visão geral](#visão-geral)
- [Stack](#stack)
- [Como subir com Docker (recomendado)](#como-subir-com-docker-recomendado)
- [Como rodar o backend](#como-rodar-o-backend)
- [Como rodar o mobile](#como-rodar-o-mobile)
- [Como executar os testes](#como-executar-os-testes)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Regra do ativo em destaque](#regra-do-ativo-em-destaque)
- [Estratégia de atualização periódica](#estratégia-de-atualização-periódica)

---

## Visão geral

O app permite que o usuário:

- Crie uma conta e faça login com JWT
- Cadastre ativos financeiros favoritos (ex: PETR4, VALE3)
- Consulte a cotação atual de cada ativo via [brapi](https://brapi.dev)
- Visualize um ativo em destaque baseado em uma regra de performance
- Veja o histórico de preços de um ativo em gráfico

---

## Stack

| Camada | Tecnologia |
|---|---|
| Mobile | React Native + Expo (TypeScript) |
| Backend | Python + FastAPI |
| Banco de dados | PostgreSQL 16 |
| Infraestrutura | Docker + docker-compose |

---

## Como subir com Docker (recomendado)

### Pré-requisitos

- Docker Desktop instalado e rodando
- Dispositivo mobile com [Expo Go](https://expo.dev/go) instalado
- Computador e dispositivo na **mesma rede Wi-Fi**

### 1. Configure o IP da sua máquina

Descubra o IP local da sua máquina (adaptador Wi-Fi):

```bash
# Windows
ipconfig
# Procure: "Adaptador de Rede sem Fio Wi-Fi" → "Endereço IPv4"

# macOS / Linux
ifconfig | grep "inet "
```

Edite o arquivo `.env` na raiz do projeto:

```env
HOST_IP=192.168.0.183   # substitua pelo seu IP
```

### 2. (Opcional) Configure o token da brapi

Edite `back/.env` e preencha o token:

```env
BRAPI_TOKEN=seu_token_aqui
```

> Sem token, a brapi funciona com limite de requisições. Para uso contínuo, obtenha um token gratuito em [brapi.dev](https://brapi.dev).

### 3. Suba o ambiente completo

```bash
make up
```

### 4. Conecte o mobile

Aguarde os logs mostrarem `Bundled` e acesse pelo Expo Go:

```bash
make logs   # acompanhe os logs
```

No app Expo Go, conecte pelo URL:

```
exp://<HOST_IP>:8081
```

### Comandos disponíveis

```bash
make up             # sobe todo o ambiente (backend + db + mobile)
make down           # derruba todo o ambiente
make backend        # sobe apenas backend + banco
make mobile         # sobe apenas o mobile
make logs           # exibe logs de todos os serviços
make logs-backend   # exibe logs apenas do backend
make test           # roda os testes via Docker
make test-local     # roda os testes localmente
```

---

## Como rodar o backend

### Com Docker

```bash
make backend
```

A API ficará disponível em `http://localhost:8000`.

Documentação interativa: `http://localhost:8000/docs`

### Localmente (sem Docker)

```bash
cd back
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

> Requer PostgreSQL rodando localmente e `back/.env` configurado com `DATABASE_URL` apontando para ele.

---

## Como rodar o mobile

### Com Docker (dispositivo físico)

```bash
make mobile
```

### Localmente

```bash
cd mobile
npm install
npx expo start
```

Configure a URL da API no arquivo `mobile/.env`:

```env
# Dispositivo físico
EXPO_PUBLIC_API_URL=http://<IP_DA_SUA_MAQUINA>:8000/api/v1

# Simulador iOS
EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1

# Emulador Android
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000/api/v1
```

---

## Como executar os testes

### Via Docker

```bash
make test
```

### Localmente

```bash
make test-local

# ou diretamente
cd back
pytest app/tests -v
```

Os testes cobrem:

- Autenticação (registro, login, token inválido, rota protegida)
- CRUD de ativos (criar, listar, buscar, atualizar, deletar, isolamento entre usuários)
- Consulta de cotação (mock da brapi, persistência do histórico, erro de API externa)
- Histórico de preços (brapi e fallback do banco)
- Ativo em destaque (lógica do cálculo, endpoint)
- Atualização periódica (chamada à brapi, deduplicação de símbolos)

---

## Variáveis de ambiente

### Backend (`back/.env`)

| Variável | Descrição | Padrão |
|---|---|---|
| `DATABASE_URL` | URL de conexão com o PostgreSQL | `postgresql://postgres:postgres@db:5432/finance` |
| `SECRET_KEY` | Chave secreta para assinar os JWTs | `troque-esta-chave-em-producao-123456` |
| `ALGORITHM` | Algoritmo do JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do token (minutos) | `1440` (24h) |
| `BRAPI_BASE_URL` | URL base da brapi | `https://brapi.dev/api` |
| `BRAPI_TOKEN` | Token da brapi (opcional) | `` |
| `SCHEDULER_INTERVAL_MINUTES` | Intervalo de atualização periódica | `30` |
| `TESTING` | Desativa o scheduler durante os testes | `false` |

### Raiz do projeto (`.env`)

| Variável | Descrição | Exemplo |
|---|---|---|
| `HOST_IP` | IP local da máquina (Wi-Fi) para o mobile | `192.168.0.183` |

### Mobile (`mobile/.env`)

| Variável | Descrição |
|---|---|
| `EXPO_PUBLIC_API_URL` | URL base da API backend acessível pelo dispositivo |

---

## Regra do ativo em destaque

O **ativo em destaque** é aquele com a **maior variação percentual positiva** (`change_percent`) entre os ativos favoritos do usuário, com base no último registro de histórico de preços de cada ativo.

**Critério de desempate:** se nenhum ativo tiver variação positiva, nenhum destaque é retornado.

**Implementação:** `back/app/services/highlight_service.py`

```
Destaque = max(change_percent) entre os últimos registros históricos dos ativos do usuário
```

---

## Estratégia de atualização periódica

O backend utiliza **APScheduler** com um `BackgroundScheduler` para atualizar as cotações de todos os ativos cadastrados em segundo plano.

**Como funciona:**

1. A cada `SCHEDULER_INTERVAL_MINUTES` minutos (padrão: 30), o job `refresh_assets` é executado
2. O job busca todos os símbolos distintos cadastrados no banco (deduplicados entre usuários)
3. Para cada símbolo, consulta a brapi e persiste um novo registro em `price_history`
4. Ativos de diferentes usuários com o mesmo símbolo recebem registros individuais de histórico

**Vantagem da deduplicação:** se 10 usuários têm PETR4, a brapi é consultada apenas 1 vez por ciclo.

**Implementação:** `back/app/core/scheduler.py` + `back/app/services/quote_service.py` (`refresh_all_assets`)

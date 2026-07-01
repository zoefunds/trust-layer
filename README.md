# TrustLayer

**AI-powered DeFi due diligence powered by GenLayer's decentralized consensus network.**

TrustLayer lets anyone investigate a DeFi protocol in under two minutes. It pulls public evidence from GitHub, DefiLlama, CoinGecko, and on-chain data, then runs it through a GenLayer intelligent contract where 5 consensus validators cross-check 13 independent domain sources and produce a tamper-resistant trust score stored on-chain.

---

## How it works

1. User submits a protocol name (e.g. "Uniswap", "Aave", "Compound").
2. The API collects live evidence: GitHub repo stats, DefiLlama TVL & audit links, CoinGecko token data.
3. That evidence payload is passed to the `TrustLayer` intelligent contract deployed on **GenLayer StudioNet** via the `genlayer-py` SDK.
4. Inside the contract, `gl.vm.run_nondet_unsafe` runs the investigation:
   - The **leader** node executes 5 batched LLM calls covering all 13 source domains.
   - The **4 validator** nodes verify the JSON shape and score ranges, then vote on consensus.
5. Once the transaction is `FINALIZED` (typically 60–90 seconds), the on-chain report is read back and saved to the database.
6. The user receives a score, per-source findings, verified/disputed/unresolved claims, and a risk recommendation.
7. A completion email is sent via Brevo.

---

## 13 Source Domains

Each investigation runs analysis across 13 independent domain sources:

| # | Source | What it covers |
|---|--------|----------------|
| 1 | **Identity** | Project registration, legal entity, official channels |
| 2 | **Founders** | Named team members, LinkedIn/GitHub profiles, background |
| 3 | **Funding** | Raise history, round sizes, funding rounds |
| 4 | **Investors** | VC backers, angel investors, portfolio page verification |
| 5 | **GitHub** | Repository activity, contributors, commits, license, archive status |
| 6 | **Documentation** | Whitepaper, technical docs, README quality |
| 7 | **On-chain** | Deployment addresses, TVL, chain coverage, age |
| 8 | **Tokenomics** | Token supply, distribution, vesting, inflation model |
| 9 | **Security** | Audit reports, bug bounty programs, past exploits |
| 10 | **Community** | Social following, Discord/Telegram activity, DAO participation |
| 11 | **Ecosystem** | Integrations, oracle usage, partner protocols |
| 12 | **Product** | Feature completeness, roadmap, recent shipping activity |
| 13 | **Media** | Press coverage, public perception, news signals |

---

## Tech Stack

### Backend (`apps/api`)
- **FastAPI** — REST API + Server-Sent Events for real-time investigation streaming
- **PostgreSQL** + **SQLAlchemy (async)** — investigation and report storage
- **Redis** — session/cache layer
- **genlayer-py 0.8.1** — synchronous SDK for writing and reading GenLayer intelligent contracts
- **eth-account** — per-user EVM wallet generation and encryption; each user's wallet signs their own GenLayer transactions
- **Brevo (sib-api-v3-sdk)** — transactional email on investigation completion
- **AES-256-GCM** — user private key encryption at rest

### Frontend (`apps/web`)
- **Next.js 14** (App Router)
- **TypeScript**
- **Inline styles** — no CSS framework dependency
- Server-Sent Events for live investigation progress

### Smart Contract (`contracts/trust_layer.py`)
- **GenLayer Intelligent Contract** — Python contract executed by GenLayer's GenVM
- **5 LLM batches** covering all 13 sources (avoids the 600s GenVM leader execution timeout)
- `@staticmethod` pipeline — avoids GenVM pickling warnings from `self` capture in closures
- `gl.vm.run_nondet_unsafe(leader_fn, validator_fn)` — leader runs the full LLM pipeline; validators check JSON shape and score ranges only

### Infrastructure
- **Fly.io** — API hosting (`trustlayer-api.fly.dev`)
- **Vercel** — Frontend hosting
- **GenLayer StudioNet** — testnet (Chain ID 61999, gas-free)

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis
- A GenLayer StudioNet account and deployed contract
- Brevo API key for email

---

## Local Development

### 1. Clone

```bash
git clone https://github.com/zoefunds/trustlayer.git
cd trustlayer
```

### 2. API setup

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/trustlayer
REDIS_URL=redis://localhost:6379
BREVO_API_KEY=your-brevo-key
BREVO_SENDER_EMAIL=you@yourdomain.com
WALLET_ENCRYPTION_KEY=<32-byte hex, e.g. openssl rand -hex 32>
GENLAYER_STUDIO_URL=https://studio.genlayer.com
GENLAYER_CONTRACT_ADDRESS=0x87E814428990b907FaC8DD87Be04c33b8094252c
GENLAYER_PRIVATE_KEY=<your StudioNet account private key>
FRONTEND_URL=http://localhost:3000
```

Run migrations and start:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend setup

```bash
cd apps/web
npm install
```

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
npm run dev
```

Open `http://localhost:3000`.

---

## Deploying the Contract

The intelligent contract lives at `contracts/trust_layer.py`. To deploy a new version to GenLayer StudioNet:

1. Go to [GenLayer Studio](https://studio.genlayer.com)
2. Upload `contracts/trust_layer.py`
3. Click **Deploy**
4. Copy the resulting contract address
5. Set `GENLAYER_CONTRACT_ADDRESS` in your environment (API and Fly.io secrets)

---

## Deploying the API (Fly.io)

```bash
cd apps/api
fly deploy
```

Set secrets:

```bash
fly secrets set \
  SECRET_KEY=... \
  DATABASE_URL=... \
  REDIS_URL=... \
  BREVO_API_KEY=... \
  WALLET_ENCRYPTION_KEY=... \
  GENLAYER_CONTRACT_ADDRESS=0x87E814428990b907FaC8DD87Be04c33b8094252c \
  GENLAYER_PRIVATE_KEY=...
```

---

## Deploying the Frontend (Vercel)

Set environment variable in Vercel project settings:

```
NEXT_PUBLIC_API_URL=https://trustlayer-api.fly.dev
```

Then push to `main` — Vercel auto-deploys.

---

## API Reference

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register with email + password. Returns JWT + a generated EVM wallet address. |
| POST | `/auth/login` | Login. Returns access + refresh tokens. |
| POST | `/auth/refresh` | Exchange refresh token for a new access token. |

### Investigations

| Method | Path | Description |
|--------|------|-------------|
| POST | `/investigations` | Start a new investigation. Body: `{"protocol_name": "Uniswap"}` |
| GET | `/investigations` | List all investigations for the authenticated user. |
| GET | `/investigations/{id}` | Get a specific investigation with full report. |
| GET | `/investigations/{id}/stream` | SSE stream — real-time source-by-source progress. Pass `?token=<jwt>` |

---

## Wallet Architecture

Every user gets a unique EVM wallet on registration (generated server-side, private key encrypted with AES-256-GCM before storage). When an investigation is submitted, the user's own wallet signs the GenLayer transaction — their address appears as the `FROM` address on the GenLayer explorer. Gas on StudioNet is free, so no funding is required.

When moving to GenLayer mainnet, users will either need funded wallets or a relayer can be introduced.

---

## Security Notes

- **Rotate `GENLAYER_PRIVATE_KEY`** before mainnet — the default is the public Hardhat test key, safe only for StudioNet testnet.
- **`WALLET_ENCRYPTION_KEY`** must be 32 bytes (64 hex chars). Never expose it. Loss = loss of all user wallet access.
- **`SECRET_KEY`** signs all JWTs. Rotation invalidates all sessions.
- Rate limiting on investigation creation is recommended before public launch to prevent API abuse.

---

## Project Structure

```
trustlayer/
├── apps/
│   ├── api/                  FastAPI backend
│   │   ├── app/
│   │   │   ├── core/         Config, database, security, auth deps
│   │   │   ├── models/       SQLAlchemy ORM models
│   │   │   ├── routers/      auth.py, investigations.py
│   │   │   ├── schemas/      Pydantic request/response models
│   │   │   ├── services/     genlayer_service.py, email_service.py
│   │   │   └── collectors/   Evidence collection (GitHub, DefiLlama, CoinGecko)
│   │   └── requirements.txt
│   └── web/                  Next.js frontend
│       └── src/app/
│           ├── (auth)/       Login + register pages
│           ├── (dashboard)/  Investigations list + detail
│           └── page.tsx      Landing page
├── contracts/
│   └── trust_layer.py        GenLayer intelligent contract
└── infrastructure/           Fly.io + Vercel config
```

---

## License

MIT

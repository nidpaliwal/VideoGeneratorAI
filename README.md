# VideoGen AI - AI Video Generator for Shorts & Reels

An MVP web app that orchestrates existing AI APIs to generate vertical short-form videos (9:16, 15-90s) from text prompts/scripts.

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14 (App Router) + TypeScript + Tailwind CSS |
| **Backend** | FastAPI (Python) |
| **Queue** | BullMQ (Redis) |
| **Database** | PostgreSQL (via Prisma ORM) |
| **Storage** | Cloudinary + S3-compatible (MinIO for local) |
| **Auth** | NextAuth.js (email + Google OAuth) |
| **Payments** | Stripe + Razorpay |
| **Video Assembly** | FFmpeg (self-hosted on render workers) |
| **Hosting** | Vercel (frontend) + Railway/Render (backend + workers) |

## Project Structure

```
video-generator/
├── apps/
│   ├── web/              # Next.js frontend
│   └── api/              # FastAPI backend
├── packages/
│   ├── db/               # Prisma schema + migrations
│   ├── shared/           # Shared TypeScript types
│   └── ui/               # Shared React components
├── docker-compose.yml    # Local dev (Postgres, Redis, MinIO, FFmpeg)
├── turbo.json            # Turborepo config
└── package.json
```

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- npm 10+

### Local Development

1. **Clone and install dependencies**
```bash
npm install
```

2. **Start local services**
```bash
npm run docker:up
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Generate Prisma client and run migrations**
```bash
npm run db:generate
npm run db:migrate
npm run db:seed
```

5. **Start development servers**
```bash
npm run dev
```

This starts:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Test Users (after seeding)

| Email | Password | Plan |
|-------|----------|------|
| admin@videogen.local | admin123 | Admin |
| test@videogen.local | test123 | Free (3 credits) |
| pro@videogen.local | pro123 | Pro (50 credits) |

## Available Scripts

```bash
# Development
npm run dev              # Start all dev servers
npm run docker:up        # Start Docker services
npm run docker:down      # Stop Docker services

# Database
npm run db:generate      # Generate Prisma client
npm run db:push          # Push schema changes
npm run db:migrate       # Run migrations
npm run db:studio        # Open Prisma Studio
npm run db:seed          # Seed test data

# Code Quality
npm run lint             # Lint all packages
npm run format           # Format with Prettier
npm run typecheck        # TypeScript type checking

# Testing
npm run test             # Run all tests

# Building
npm run build            # Build all packages
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user

### Script Generation
- `POST /api/v1/scripts/generate` - Generate script from topic
- `POST /api/v1/scripts/projects/{id}/script` - Save script to project

### Voiceover
- `POST /api/v1/voiceover/generate` - Generate voiceover
- `GET /api/v1/voiceover/voices` - List available voices

### Visuals
- `POST /api/v1/visuals/search` - Search stock footage
- `POST /api/v1/visuals/select` - Select visuals for segments

### Captions
- `POST /api/v1/captions/generate` - Generate captions
- `GET /api/v1/captions/styles` - Get caption style presets

### Projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects` - List projects
- `GET /api/v1/projects/{id}` - Get project
- `PATCH /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Rendering
- `POST /api/v1/render/projects/{id}/render` - Start render job
- `GET /api/v1/render/jobs/{id}` - Get render job status
- `GET /api/v1/render/projects/{id}/jobs` - List render jobs
- `POST /api/v1/render/projects/{id}/export` - Export video

### Billing
- `POST /api/v1/billing/checkout` - Create checkout session
- `GET /api/v1/billing/subscription` - Get subscription
- `POST /api/v1/billing/portal` - Create billing portal session
- `GET /api/v1/billing/usage` - Get usage stats

### Webhooks
- `POST /api/v1/webhooks/stripe` - Stripe webhook handler

## Environment Variables

See `.env.example` for all required variables.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET` - Secret for JWT tokens
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` - LLM providers
- `ELEVENLABS_API_KEY` / `GOOGLE_CLOUD_TTS_CREDENTIALS` - TTS providers
- `PEXELS_API_KEY` / `PIXABAY_API_KEY` - Stock footage
- `CLOUDINARY_*` - Cloudinary credentials
- `AWS_*` / `S3_*` - S3-compatible storage (MinIO for local)
- `STRIPE_*` - Stripe credentials
- `RAZORPAY_*` - Razorpay credentials

## Deployment

### Frontend (Vercel)
1. Connect repository to Vercel
2. Set environment variables
3. Deploy

### Backend (Railway/Render)
1. Create new service from Dockerfile
2. Add PostgreSQL, Redis services
3. Set environment variables
4. Deploy

### Workers
Deploy the same API image as a background worker with:
```bash
celery -A app.workers.render worker --concurrency=2
```

## Cost Model (Estimated)

| Component | Cost/Video (60s) |
|-----------|------------------|
| LLM (script) | $0.001 |
| TTS (ElevenLabs) | $0.018 |
| Stock Visuals | $0.00 |
| AI Visuals (premium) | $0.10-0.50 |
| Whisper (captions) | $0.00 (self-hosted) |
| FFmpeg Render | $0.002 |
| Storage/CDN | $0.001 |
| **Total (Stock)** | **~$0.022** |

## License

MIT
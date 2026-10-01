# VideoGen AI - AI Video Generator for Shorts & Reels

An MVP web app that orchestrates existing AI APIs to generate vertical short-form videos (9:16, 15-90s) from text prompts/scripts.

## Track: Track 1

**Problem:** Creating vertical short-form videos (YouTube Shorts, Instagram Reels, TikTok) is time-consuming and requires multiple tools: script writing, voiceover generation, visual sourcing, caption creation, and video assembly. Existing solutions are either too complex, lack automation, or don't handle the full pipeline. Additionally, free-tier users need watermarked exports without manual video editing, and all users need reliable, optimized video delivery with automatic format/quality selection.

**How Cloudinary Solves This:**
- **Video Upload & Transformation:** Rendered videos are uploaded to Cloudinary (`resource_type="video"`) with eager transformations for 9:16 vertical crop (`c_fill,ar_9:16,g_auto`) and auto quality/format (`f_auto,q_auto`)
- **Auto-Generated Thumbnails:** Thumbnails extracted from video at 1s mark, delivered with same 9:16 crop and optimization
- **Free-Plan Watermark:** Text overlay transformation (`l_text:Arial_60_bold:VideoGen%20AI,co_white,o_30,g_south_east,x_20,y_20`) applied dynamically at delivery time — no re-encoding, no fake `?watermark=1` URLs
- **Media Management API:** `/api/v1/media` endpoints for listing, uploading, transforming, previewing, and deleting user media with per-folder isolation
- **Signed Upload URLs:** Direct client-to-Cloudinary uploads for large files, bypassing backend bandwidth

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14 (App Router) + TypeScript + Tailwind CSS |
| **Backend** | FastAPI (Python) |
| **Queue** | BullMQ (Redis) / Celery |
| **Database** | PostgreSQL (via Prisma ORM) |
| **Storage** | Cloudinary + S3-compatible (MinIO for local) |
| **Auth** | JWT (email/password) + Google OAuth |
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
- **Cloudinary Account** (free tier works) - sign up at https://cloudinary.com

### Local Development

1. **Clone and install dependencies**
```bash
npm install
```

2. **Start local services** (PostgreSQL, Redis, MinIO)
```bash
npm run docker:up
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys (see Cloudinary Setup below)
```

4. **Generate Prisma client and run migrations**
```bash
npm run db:generate
npm run db:migrate
npm run db:seed
```

5. **Install Python dependencies**
```bash
cd apps/api
pip install -r requirements.txt
cd ../..
```

6. **Start development servers**
```bash
npm run dev
```

This starts:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Cloudinary Setup

1. Create a free Cloudinary account at https://cloudinary.com
2. Go to Dashboard → Settings → Access Keys
3. Copy your **Cloud Name**, **API Key**, and **API Secret**
4. Add to `.env`:
```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```
5. (Optional) Create an unsigned upload preset for direct uploads:
   - Dashboard → Settings → Upload → Upload presets → Add unsigned preset
   - Name: `videogen_unsigned`
   - Folder: `videogen/uploads`
   - Allowed formats: `mp4,webm,mov,jpg,png,webp`

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
- `POST /api/v1/render/projects/{id}/export` - Export video (with watermark for free plan)

### Media Management (Cloudinary Integration)
- `GET /api/v1/media` - List user's media (paginated, filter by resource_type)
- `POST /api/v1/media/upload` - Upload video/image to Cloudinary
- `POST /api/v1/media/transform` - Generate transformed delivery URL
- `GET /api/v1/media/preview/{public_id}` - Get preview URL with transformations
- `GET /api/v1/media/{public_id}` - Get media metadata
- `DELETE /api/v1/media/{public_id}` - Delete media
- `POST /api/v1/media/signed-upload-url` - Get signed upload params for direct upload

### Billing
- `POST /api/v1/billing/checkout` - Create checkout session
- `GET /api/v1/billing/subscription` - Get subscription
- `POST /api/v1/billing/portal` - Create billing portal session
- `GET /api/v1/billing/usage` - Get usage stats

### Webhooks
- `POST /api/v1/webhooks/stripe` - Stripe webhook handler

## How to Test the Cloudinary Integration

### 1. Start the Application
```bash
npm run docker:up
npm run db:generate && npm run db:migrate && npm run db:seed
# Install Python deps
cd apps/api && pip install -r requirements.txt && cd ../..
npm run dev
```

### 2. Sign Up / Log In
- Go to http://localhost:3000
- Click "Get Started" or "Sign In"
- Register a new account (or use seeded test@videogen.local / test123)

### 3. Access Media Library
- Navigate to http://localhost:3000/media (linked in top nav and footer)
- You'll see the Media Library demo page

### 4. Test Upload
- Click "Upload" button
- Select a video file (MP4, WebM, MOV)
- Watch it appear in the grid with auto-generated 9:16 thumbnail

### 5. Test Transformations
- Click any video card to open preview modal
- Click transformation buttons:
  - **9:16 Vertical Crop** - Applies `c_fill,ar_9:16,g_auto`
  - **Auto Quality/Format** - Applies `f_auto,q_auto`
  - **Add Watermark** - Adds "VideoGen AI" text overlay (free plan simulation)
  - **50% Scale** - Resizes to 540x960
  - **Blur Effect** - Adds blur transformation
- Transformations stack and show in the "Applied Transformations" panel
- Click "Clear Transforms" to reset

### 6. Test Free-Plan Watermark Export
- Upload a video via Media Library (or use a rendered video if you have one)
- On export with `includeWatermark: true` and FREE plan:
  - Backend generates Cloudinary URL with text overlay transformation
  - No re-encoding — transformation applied at CDN edge
- Verify the download URL contains transformation parameters, not `?watermark=1`

> **Note:** The full script-to-video render pipeline requires valid API keys for OpenAI, ElevenLabs/Google TTS, Pexels/Pixabay, and FFmpeg. The visual search endpoints return placeholder URLs. For demo purposes, use the Media Library upload + transformations path above.

### 7. Test Direct Upload (Signed URL)
```bash
# Get signed upload params
curl -X POST http://localhost:8000/api/v1/media/signed-upload-url \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"resource_type": "video"}'

# Use returned upload_url and params to upload directly to Cloudinary
```

### 8. Verify Cloudinary Dashboard
- Log into Cloudinary Console → Media Library
- Check `videogen/{user_id}/uploads/`, `videogen/{user_id}/videos/`, `videogen/{user_id}/thumbnails/` folders
- Verify eager transformations generated (9:16 crop, auto quality)
- Check delivery URLs in browser network tab

## Environment Variables

See `.env.example` for all required variables.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET` - Secret for JWT tokens (min 32 chars)
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` - LLM providers
- `ELEVENLABS_API_KEY` / `GOOGLE_CLOUD_TTS_CREDENTIALS` - TTS providers
- `PEXELS_API_KEY` / `PIXABAY_API_KEY` - Stock footage
- `CLOUDINARY_CLOUD_NAME` - Your Cloudinary cloud name
- `CLOUDINARY_API_KEY` - Your Cloudinary API key
- `CLOUDINARY_API_SECRET` - Your Cloudinary API secret
- `AWS_*` / `S3_*` - S3-compatible storage (MinIO for local)
- `STRIPE_*` - Stripe credentials
- `RAZORPAY_*` - Razorpay credentials

## Deployment

### Frontend (Vercel)
1. Connect repository to Vercel
2. Set environment variables (including `NEXT_PUBLIC_API_URL`)
3. Deploy

### Backend (Railway/Render/Fly.io)
1. Create new service from `apps/api/Dockerfile`
2. Add PostgreSQL, Redis services
3. Set all environment variables including Cloudinary credentials
4. Deploy

### Workers
Deploy the same API image as a background worker:
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
| Cloudinary Storage/CDN | $0.001 |
| **Total (Stock)** | **~$0.022** |

## License

MIT
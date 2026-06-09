# Neuro-Tutor Development Plan

> **Audience:** AI coding agents and human developers. Each task below is self-contained with file paths, current-state descriptions, and acceptance criteria. Work phases in order — Phase 1 fixes foundational defects that block everything else.
>
> **Last reviewed:** 2026-06-09 (verified against actual code, not docs — several docs are stale, see Phase 5).

---

## 1. Project Snapshot

**Neuro-Tutor** (a.k.a. Socratic Tutor) is a neurodivergent-friendly Socratic learning assistant. Instead of giving direct answers, it guides students with probing questions. Users can tune verbosity (1–5), explanation style (concise / step-by-step / analogy), reading mode, and visual-aid preferences, which shape the LLM system prompt.

### Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11, FastAPI 0.104, SQLAlchemy 2.x, Pydantic v2, Uvicorn |
| LLM | OpenRouter API (`backend/app/services/llm_client.py`) |
| DB | SQLite (sessions + messages) |
| Frontend | React 19, Vite 5, Tailwind 3, shadcn/ui-style Radix components, partial TypeScript |
| Infra | Docker Compose (backend + frontend), no CI |

### Architecture

```
Browser → ChatPage.tsx → chatService.ts → POST /api/chat/ (FastAPI)
                                              ├── services/sessions.py → SQLite
                                              └── services/llm_client.py → OpenRouter
```

### Key files

| Concern | Path |
|---------|------|
| Backend entry | `backend/app/main.py` |
| Chat API (4 endpoints) | `backend/app/api/chat.py` |
| LLM client + Socratic prompt builder | `backend/app/services/llm_client.py` |
| Session/message persistence | `backend/app/services/sessions.py`, `backend/app/models/chat.py` |
| DB engine | `backend/app/core/db.py` |
| Config | `backend/app/core/config.py`, `backend/app/core/openrouter_secrets.py` |
| Frontend main state | `socratic-tutor-frontend/src/pages/ChatPage.tsx` |
| Frontend API client | `socratic-tutor-frontend/src/services/chatService.ts` |
| Backend tests | `backend/tests/test_chat.py` |

### What works today

- Full chat loop: send message → session auto-created → OpenRouter call with preference-aware Socratic system prompt → reply persisted and rendered.
- Session list, session history loading, session delete (API only), light/dark theme, preferences drawer, typing indicator, friendly error messages injected as assistant bubbles.
- Backend test suite (~287 lines, pytest + TestClient) covering CRUD paths.
- Dockerized backend with healthcheck and non-root user.

---

## 2. Phase 1 — Critical Foundation Fixes (do first, ~small effort, high risk if skipped)

### 1.1 Fix `.gitignore` excluding frontend source ⚠️ REPO-BREAKING

- **Problem:** `.gitignore` line 76 contains `lib/`, which excludes `socratic-tutor-frontend/src/lib/utils.ts` (the `cn()` helper every UI component imports). Fresh clones fail to build.
- **Fix:** Change `lib/` to a more specific pattern (e.g. `/lib/` or remove it), then `git add socratic-tutor-frontend/src/lib/utils.ts`.
- **Accept:** `git ls-files | grep utils.ts` shows the file tracked; fresh clone builds.

### 1.2 Fix Docker frontend API URL

- **Problem:** `docker-compose.yml` line 30 sets `VITE_API_URL=http://backend:8000/api`. The hostname `backend` only resolves inside the Docker network — the **browser** makes these requests, so they fail. Additionally, the frontend `Dockerfile` runs `npm run build` at image-build time with no `ARG VITE_API_URL`, so the compose `environment:` value is never baked into `dist/` anyway.
- **Fix:**
  1. In `socratic-tutor-frontend/Dockerfile`, add `ARG VITE_API_URL` + `ENV VITE_API_URL=$VITE_API_URL` before `npm run build`.
  2. In `docker-compose.yml`, pass it via `build.args` with value `http://localhost:8000/api`.
  3. Remove or fix the source volume mount (`./socratic-tutor-frontend:/app`) — it overlays source onto a container serving prebuilt `dist/`, providing no hot reload. Either drop it (prod-style) or switch the container to `npm run dev` (dev-style).
- **Accept:** `docker compose up` → browser at `localhost:5173` successfully chats end-to-end.

### 1.3 Wire `DATABASE_URL` into the engine

- **Problem:** `backend/app/core/db.py` line 12 hardcodes `sqlite:///./neuro_tutor.db`. Compose sets `DATABASE_URL=sqlite:///./data/neuro_tutor.db` and mounts volume `neuro_tutor_db:/app/data` — the DB is written **outside** the volume, so Docker data is not persisted across rebuilds.
- **Fix:** Read URL from `settings` (add `database_url` field to `backend/app/core/config.py` pydantic-settings, default `sqlite:///./neuro_tutor.db`); only pass `check_same_thread` connect arg when URL starts with `sqlite`.
- **Accept:** With compose env set, DB file appears in `/app/data/` inside container and survives `docker compose down && up`.

### 1.4 Unify the default model

- **Problem:** Conflicting defaults: `config.py` and `openrouter_secrets.py` say `openai/gpt-3.5-turbo`; `backend/.env.example` says `qwen2.5:72b-instruct`; `README.md` says `anthropic/claude-3-haiku`.
- **Fix:** Pick ONE default (recommend a cheap, current OpenRouter model), set it in `config.py` as the single source of truth, make `openrouter_secrets.py` read from settings, update `.env.example` and `README.md`.
- **Accept:** Grep for model strings finds one canonical default.

### 1.5 Remove sensitive/noisy logging

- **Problem:** `llm_client.py` logs the first 10 chars of the API key (~L98–99) and prints full LLM responses to stdout (~L146).
- **Fix:** Remove key logging entirely; gate response logging behind `settings.debug` using the `logging` module, not `print`.
- **Accept:** No API-key material in logs at any level; response bodies only logged when `DEBUG=true`.

### 1.6 Delete dead files

- **Remove:** `Test1.py` (unrelated Azure OpenAI prototype with hardcoded endpoint), `fix-docker-path.ps1`, stale session-log markdowns (`*_RESULT*.md`, `HEALTH_STATUS.md`, `test1.md`, `test2.md`). Move `backend/test_openrouter.py` / `backend/test_api_key.py` into a `backend/scripts/` folder or delete.
- **Accept:** Repo root contains only living docs and code.

---

## 3. Phase 2 — Testing & CI (do before adding features)

### 2.1 Mock the LLM in backend tests

- **Problem:** `backend/tests/test_chat.py` calls real `generate_response()` → hits OpenRouter (flaky, slow, costs money) or silently exercises fallback paths.
- **Fix:** Add a pytest fixture that monkeypatches `app.services.llm_client.generate_response` (or injects via dependency override) returning a canned Socratic reply. Also fix the test DB: app import currently runs `create_tables()` against the production DB (`main.py` ~L17) even when tests override to `sqlite:///./test.db` — guard table creation or use an env var.
- **Accept:** `pytest` passes offline with no `OPENROUTER_API_KEY` set; no `neuro_tutor.db` created by the test run.

### 2.2 Add pytest config and coverage

- **Fix:** Add `pytest-cov` and `pytest-asyncio` to `backend/requirements.txt` (split a `requirements-dev.txt` if preferred). Add `pyproject.toml` or `pytest.ini` with test paths and asyncio mode.
- **Accept:** `pytest --cov=app` runs and reports; coverage ≥ current behavior documented.

### 2.3 Frontend test harness

- **Fix:** Add Vitest + React Testing Library. Minimum suite:
  - `chatService.test.ts` — request shaping, error mapping (the friendly-error logic at `chatService.ts` ~L134–167).
  - `ChatPage` smoke test — renders, sends a message (mock fetch), optimistic message appears.
- **Accept:** `npm test` passes; tests run without backend.

### 2.4 CI pipeline

- **Fix:** Add `.github/workflows/ci.yml`: two jobs — backend (`pip install`, `pytest --cov`) and frontend (`npm ci`, `npm run lint`, `npm test`, `npm run build`). Trigger on PR and push to main.
- **Accept:** CI green on a fresh clone (this also validates fix 1.1).

### 2.5 Fix ESLint coverage of TypeScript

- **Problem:** ESLint 9 config only lints `*.{js,jsx}`; all `.ts`/`.tsx` files (most of the app) are unlinted, and there's no `tsconfig.json`.
- **Fix:** Add `tsconfig.json` (allowJs, strict where feasible), `typescript-eslint`, extend lint globs to `*.{ts,tsx}`. Add `tsc --noEmit` to CI.
- **Accept:** `npm run lint` covers all source; type-check passes (fix surfaced errors).

---

## 4. Phase 3 — Complete Core UX (feature completion)

### 3.1 Persist preferences

- **Problem:** README claims preferences are saved; they're actually in-memory only (`ChatPage.tsx` resets to `defaultPreferences` on reload).
- **Fix (minimum):** Persist to `localStorage` (read on mount, write on change). **Optional later:** per-session preferences stored in DB.
- **Accept:** Change verbosity → refresh page → setting retained.

### 3.2 Session delete (and rename) in UI

- **Problem:** `deleteSession()` exists in `chatService.ts` (~L116–129) but is never called; sidebar has no delete affordance.
- **Fix:** Add a delete button (with confirm) per session row in `ChatSidebar.tsx`; on delete of the active session, select the next session or create a new chat. Optionally add rename (requires a new `PATCH /api/chat/sessions/{id}` endpoint + `update_session_title` in `sessions.py`).
- **Accept:** Delete works end-to-end; deleting active session doesn't strand the UI.

### 3.3 Unify the theme system

- **Problem:** `ThemeProvider.tsx` and `ThemeToggle.tsx` independently manipulate `document.documentElement` + `localStorage('theme')`; `useTheme()` is exported but unused.
- **Fix:** Make `ThemeToggle` consume `useTheme()` from the provider; remove its duplicate logic.
- **Accept:** One source of truth; toggle still works in both themes after reload.

### 3.4 Surface errors properly

- **Problem:** `error` state in `ChatPage.tsx` (~L34) is declared but never set or rendered; errors are only injected as fake assistant messages.
- **Fix:** Either remove the dead state, or (better) add a dismissible error banner/toast for non-conversational failures (session-list load failure, network down). Keep conversational errors in-bubble.
- **Accept:** Killing the backend and clicking around produces visible, dismissible error feedback — no silent failures.

### 3.5 Empty-state bootstrap

- **Problem:** If the DB has zero sessions, the user must manually click "New Chat" before they can type.
- **Fix:** In `ChatPage.tsx` session-load effect (~L64–66), auto-create a local temp session (existing `temp-{timestamp}` pattern) when the list is empty.
- **Accept:** Fresh DB → app loads ready-to-type.

### 3.6 Return message previews in session list

- **Problem:** `api/chat.py` ~L130 computes `get_last_message_preview()` into an unused variable; the response model omits it.
- **Fix:** Add `last_message_preview` to the session list response schema and render it in `ChatSidebar.tsx` under the title.
- **Accept:** Sidebar shows a one-line preview per session.

### 3.7 Markdown rendering + multiline input

- **Fix:** Render assistant messages with `react-markdown` (+ `rehype-highlight` for code blocks) in `MessageBubble.tsx` — Socratic step-by-step replies need lists/formatting. Replace `ChatInput`'s single-line `Input` with an auto-growing textarea (Enter = send, Shift+Enter = newline).
- **Accept:** A reply containing a numbered list and code block renders correctly; multiline questions can be composed.

### 3.8 Frontend cleanup

- Deduplicate `Message` / `ChatSession` type definitions (currently redefined in `ChatSidebar.tsx`, `MessageList.tsx`, `ChatPage.tsx`) — import from `chatService.ts` (or a new `src/types.ts`).
- Clean `index.css`: remove duplicate `@layer base` block and leftover Vite boilerplate (~L108–175) that conflicts with Tailwind tokens.
- Fix nested scroll containers (MessageList `ScrollArea` inside ChatPage's own scroll wrapper) so auto-scroll-to-bottom is reliable.
- Remove the orphaned root `package.json` (Tailwind v4 devDeps unrelated to the v3 frontend) and the unused `@tailwindcss/postcss` dep.

---

## 5. Phase 4 — Production Hardening (after UX complete)

Ordered by recommended sequence:

### 4.1 Streaming responses
Add SSE streaming: `POST /api/chat/stream` using OpenRouter's `stream: true`, FastAPI `StreamingResponse`; frontend consumes via `fetch` + ReadableStream, rendering tokens incrementally. This is the single biggest perceived-quality win for a tutor app.

### 4.2 Rate limiting
Add `slowapi` (or middleware) on the chat endpoint — e.g. 20 req/min per IP — to protect the OpenRouter budget. Return 429 with a friendly message the frontend already knows how to render.

### 4.3 Alembic migrations
Replace startup `create_all()` with Alembic. Generate initial migration from current models. Prereq for any schema change (users, preferences, renames).

### 4.4 Authentication (only if multi-user is actually needed)
FastAPI JWT auth (`python-jose` + `passlib`), `users` table, `user_id` FK on `chat_sessions`, login/register UI. **Decision point:** if this stays a local single-user tool, skip auth and document that explicitly instead.

### 4.5 PostgreSQL option
Once 1.3 (DATABASE_URL) and 4.3 (Alembic) are done, supporting Postgres is config-only: add `psycopg` to requirements, a `db` service in compose, and test.

### 4.6 Misc hardening
- Fix global exception handler in `main.py` (~L76–83): let `HTTPException` propagate via FastAPI's own handler; only catch unexpected exceptions, log with traceback, return generic 500.
- Tighten CORS for production (specific origin, minimal methods/headers).
- Add request logging middleware with timing (structured, no bodies).

---

## 6. Phase 5 — Subject Knowledge Base & RAG (Qdrant)

**Goal:** Let students upload course materials per subject (PPTX, PDFs/books, notes, homework, DOCX, markdown), index them in a Qdrant vector store, and have the tutor ground its Socratic questioning in those materials (retrieval-augmented generation).

**Prerequisites:** 1.3 (DATABASE_URL), 4.3 (Alembic — schema changes ahead). Strongly recommended after 2.1/2.4 (tests + CI) so the ingestion pipeline lands tested.

### Architecture decisions (made up front — follow these unless overridden)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Vector DB | **Qdrant** (official Docker image + `qdrant-client`) | User requirement; great payload filtering |
| Collection layout | **One collection (`materials`) with `subject_id` payload filter** — NOT one collection per subject | Simpler ops, cheaper, Qdrant payload-indexed filtering is fast; per-subject collections complicate backup/migration |
| Embeddings | **FastEmbed** (`fastembed`, e.g. `BAAI/bge-small-en-v1.5`, 384-dim) running locally | Free, offline, no API key; OpenRouter doesn't reliably serve embeddings. Make the model name a setting so a hosted embedder can be swapped in later |
| Chunking | ~512-token chunks, ~64-token overlap; split on slide/page/heading boundaries first | Slide- and page-aware chunks keep citations meaningful |
| Parsing | `python-pptx` (PPTX incl. speaker notes), `pymupdf` (PDF/books), `python-docx` (DOCX), plain text/markdown as-is | Battle-tested, pure-pip installs |
| Ingestion execution | FastAPI `BackgroundTasks` initially; revisit a worker queue only if uploads get large | No new infra for v1 |
| File storage | Original files on disk under `backend/data/uploads/{subject_id}/`, path stored in DB | DB stays small; volume-mounted in Docker |

### 5.1 Qdrant service + client plumbing

- Add `qdrant` service to `docker-compose.yml` (image `qdrant/qdrant`, port 6333, volume `qdrant_storage:/qdrant/storage`).
- Add `qdrant-client` and `fastembed` to `backend/requirements.txt`.
- New `backend/app/core/vector_db.py`: client factory reading `QDRANT_URL` (default `http://localhost:6333`; `http://qdrant:6333` in compose) from settings; idempotent `ensure_collection()` creating `materials` with the embedding dimension + payload index on `subject_id`.
- Update `.env.example` files with `QDRANT_URL`, `EMBEDDING_MODEL`.
- **Accept:** `docker compose up` brings up Qdrant healthy; backend startup creates the collection; backend still runs fine without Qdrant for plain chat (degrade gracefully, log a warning).

### 5.2 Subjects + materials schema

- New SQLAlchemy models in `backend/app/models/`:
  - `subjects`: `id`, `name`, `description`, `created_at`.
  - `materials`: `id`, `subject_id` (FK), `filename`, `file_path`, `file_type` (`pptx|pdf|docx|md|txt`), `material_kind` (`slides|book|notes|homework|other`), `status` (`pending|processing|ready|failed`), `error`, `chunk_count`, `uploaded_at`.
  - Add nullable `subject_id` FK to `chat_sessions`.
- Alembic migration for all of the above.
- **Accept:** Migration applies cleanly to an existing DB with sessions in it.

### 5.3 Ingestion pipeline

- New `backend/app/services/ingestion.py`:
  1. Detect type by extension → parse to text blocks with structure metadata (slide number, page number, heading).
  2. Chunk per the decisions above.
  3. Embed with FastEmbed (batch).
  4. Upsert to Qdrant with payload: `{material_id, subject_id, material_kind, source_filename, locator}` where `locator` is e.g. `"slide 12"` / `"p. 47"`.
  5. Update `materials.status` → `ready` (or `failed` + `error`).
- Deleting a material deletes its Qdrant points (filter by `material_id`) and the file on disk.
- **Tests:** unit-test parsing/chunking with small fixture files (a 2-slide PPTX, 2-page PDF, a markdown note); mock Qdrant client.
- **Accept:** Upload a real PPTX → status reaches `ready`, points visible in Qdrant dashboard (`localhost:6333/dashboard`), delete removes them.

### 5.4 Subjects & materials API

New router `backend/app/api/subjects.py` (prefix `/api/subjects`):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/` | Create subject |
| GET | `/` | List subjects (with material counts) |
| PATCH | `/{id}` | Rename subject |
| DELETE | `/{id}` | Delete subject + all materials + vectors |
| POST | `/{id}/materials` | Multipart upload (validate extension + size limit, e.g. 50 MB); kicks off background ingestion |
| GET | `/{id}/materials` | List materials with status |
| DELETE | `/{id}/materials/{material_id}` | Delete one material |
| POST | `/{id}/search` | Debug/utility endpoint: raw top-k retrieval for a query (useful for tuning before chat wiring) |

- **Accept:** Full CRUD via `/docs`; pytest coverage for each endpoint with mocked ingestion.

### 5.5 RAG-grounded chat

- Chat request gains optional `subject_id`; persisted on the session (5.2).
- In the chat flow (`api/chat.py`), when the session has a subject: embed the user message, query Qdrant top-k (k≈5, score threshold ~0.35, filter `subject_id`), and pass retrieved chunks to `SocraticPromptBuilder`.
- Extend the system prompt (carefully — see Conventions §8.6) with a `COURSE MATERIALS` section: instruct the model to ground its Socratic questions in the excerpts, reference them by locator ("Looking at slide 12…"), and say when the materials don't cover the topic rather than inventing content.
- Return `sources: [{filename, locator, score}]` alongside the reply so the UI can show citations.
- **Tests:** mock retrieval; assert chunks land in the prompt and `sources` round-trips.
- **Accept:** With a subject selected and materials indexed, asking about a topic in the slides produces a reply referencing them; without a subject, chat behaves exactly as before.

### 5.6 Frontend: subjects & materials UI

- `subjectService.ts` mirroring 5.4.
- Subject picker in the sidebar or header (per-session); new-chat flow optionally tags a subject.
- Materials manager (drawer or route): subject list, drag-and-drop upload with progress, material list with status badges (pending/processing/ready/failed) polling while processing, delete with confirm.
- Render `sources` as small citation chips under assistant messages (filename + locator).
- **Accept:** Upload a PPTX from the UI → watch it index → chat about it → see citation chips.

### 5.7 RAG quality pass (after end-to-end works)

- Tune k, score threshold, chunk size against real course materials.
- Add OCR fallback consideration for scanned PDFs (note as known limitation if skipped).
- Optional: hybrid search (Qdrant sparse+dense) if pure dense retrieval misses keyword-heavy homework lookups.

---

## 7. Phase 6 — Documentation Reconciliation

The docs materially contradict the code. Fix after Phases 1–3 and 5 land so docs describe the final state:

| Doc | Stale claim | Reality |
|-----|-------------|---------|
| `BACKEND.md` (~L65–76, L163–177) | Mock LLM responses | Real OpenRouter integration |
| `backend/README.md` (~L11–12, L33) | Mock LLM | Real OpenRouter |
| `PROGRESS.md` (~L13, L100–105, L162) | LLM "placeholder", frontend integration "in progress", DB persistence "pending" | All implemented |
| `README.md` | "Preferences are saved" | Not persisted until 3.1 |

Also: consolidate the doc sprawl. Keep `README.md`, `DEVELOPMENT_PLAN.md` (this file), one setup guide, one deployment guide; archive or delete the rest (`FILE_STRUCTURE.md`, `AI_PROMPT_CODE.md`, `Core.txt`, `Frontend prompt.txt`, etc. → `docs/archive/` if historically useful).

---

## 8. Suggested Execution Order (single roadmap)

| # | Task | Phase | Effort | Depends on |
|---|------|-------|--------|------------|
| 1 | Fix `.gitignore` `lib/` | 1.1 | XS | — |
| 2 | Wire `DATABASE_URL` | 1.3 | S | — |
| 3 | Fix Docker `VITE_API_URL` + Dockerfile ARG | 1.2 | S | — |
| 4 | Unify default model | 1.4 | XS | — |
| 5 | Remove key/response logging | 1.5 | XS | — |
| 6 | Delete dead files | 1.6 | XS | — |
| 7 | Mock LLM in tests + test-DB isolation | 2.1 | M | — |
| 8 | pytest config + coverage deps | 2.2 | XS | 7 |
| 9 | tsconfig + TS linting | 2.5 | S | — |
| 10 | Vitest + RTL harness + first tests | 2.3 | M | 9 |
| 11 | CI workflow | 2.4 | S | 7–10 |
| 12 | Persist preferences (localStorage) | 3.1 | S | — |
| 13 | Session delete UI (+ rename) | 3.2 | M | — |
| 14 | Unify theme system | 3.3 | S | — |
| 15 | Error banner + remove dead state | 3.4 | S | — |
| 16 | Empty-state bootstrap | 3.5 | XS | — |
| 17 | Session previews in sidebar | 3.6 | S | — |
| 18 | Markdown rendering + textarea input | 3.7 | M | — |
| 19 | Frontend dedupe/CSS/scroll cleanup | 3.8 | M | 9 |
| 20 | SSE streaming | 4.1 | L | 7, 11 |
| 21 | Rate limiting | 4.2 | S | — |
| 22 | Alembic migrations | 4.3 | M | 2 |
| 23 | Auth (decision point first) | 4.4 | L | 22 |
| 24 | Postgres support | 4.5 | M | 2, 22 |
| 25 | Hardening misc (exceptions, CORS, logging) | 4.6 | S | — |
| 26 | Qdrant service + client plumbing | 5.1 | S | 2 |
| 27 | Subjects + materials schema (Alembic) | 5.2 | M | 22, 26 |
| 28 | Ingestion pipeline (parse/chunk/embed/upsert) | 5.3 | L | 27 |
| 29 | Subjects & materials API | 5.4 | M | 28 |
| 30 | RAG-grounded chat | 5.5 | M | 29 |
| 31 | Frontend subjects/materials UI + citations | 5.6 | L | 29, 30 |
| 32 | RAG quality tuning pass | 5.7 | M | 31 |
| 33 | Documentation reconciliation | 6 | M | 1–19, 26–31 |

Effort: XS < 30 min · S < 2 h · M < 1 day · L = multi-day.

---

## 9. Conventions for Agents Working on This Repo

1. **Verify against code, not docs** — several markdown files are stale (see Phase 6).
2. **Run tests before and after changes:** backend `cd backend && pytest`; frontend (once 2.3 lands) `cd socratic-tutor-frontend && npm test`.
3. **Don't commit secrets** — `OPENROUTER_API_KEY` lives in `backend/.env` (gitignored); `.env.example` files document required vars.
4. **One source of truth for config** — all backend settings flow through `backend/app/core/config.py` (pydantic-settings). Don't add parallel env reading.
5. **Frontend types** — import `Message`/`ChatSession` from `chatService.ts` (or `src/types.ts` after 3.8); don't redefine.
6. **Preserve the Socratic prompt contract** — `SocraticPromptBuilder` in `llm_client.py` is the product's core; changes to prompt behavior (including the Phase 5 RAG context section) need explicit sign-off.
7. **Keep PRs scoped to one roadmap row** from §8; reference the task number in the commit message.
8. **RAG layer rules (Phase 5):** one Qdrant collection with `subject_id` payload filtering — never create per-subject collections; embeddings go through the configured FastEmbed model in `vector_db.py`; chat must degrade gracefully (plain Socratic mode) when Qdrant is down or a session has no subject.

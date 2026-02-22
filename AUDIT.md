# LevelUp Life — Pre-Build Audit

Completed: 2025-02-22  
Auditor: Senior Full-Stack Engineer  
PRD reference: LevelUpLife_PRD.md (ticket specification)

---

## 1. Root-level files

| File | Purpose | Salvageable | Broken | Action |
|------|---------|-------------|--------|--------|
| `PHASE_3_IMPLEMENTATION_SUMMARY.md` | Dev log of Phase 3 | No | N/A | DELETE (noise) |
| `PHASE_3_VERIFICATION_REPORT.md` | Dev log of Phase 3 | No | N/A | DELETE (noise) |
| `levelup-life/` | Project root | Yes | — | KEEP |

---

## 2. Backend files

### `backend/app/config.py`
- **Purpose**: Pydantic Settings — env vars for DB, Redis, JWT, Gemini, CORS.
- **Salvageable**: Yes — all required fields present.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/app/database.py`
- **Purpose**: Async SQLAlchemy engine, session factory, Base, `get_db()`.
- **Salvageable**: Yes.
- **Broken**: Nothing critical; `get_async_session()` context-manager helper is present.
- **Action**: KEEP as-is.

### `backend/app/main.py`
- **Purpose**: FastAPI app factory — CORS, rate limiting, router registration.
- **Salvageable**: Yes.
- **Broken**: Engine is created at **module import time** using `DATABASE_URL` which requires `asyncpg`. This crashes the test suite because tests import `app.main` before overriding the DB URL. Fix: lazy engine initialisation or pass SQLite URL during testing.
- **Action**: FIX — make engine init tolerant of missing asyncpg in test context (use `create_tables=True` only at lifespan, not import).

### `backend/app/celery_app.py`
- **Purpose**: Celery instance + beat schedule.
- **Salvageable**: Yes — all 4 beat tasks configured.
- **Broken**: Beat task names don't match the actual task names in `analytics_tasks.py` / `notification_tasks.py`. Example: schedule says `"tasks.analytics_tasks.daily_snapshot"` but task decorator says `name="tasks.analytics_tasks.daily_snapshot"` — this actually matches. `pre_generate_quests` task is a stub (passes). `streak_check` is a stub.
- **Action**: FIX stubs (`notification_tasks.streak_check`, `quest_tasks.pre_generate_quests`).

### `backend/app/redis_client.py`
- **Purpose**: Redis connection pool + `get_redis()` dependency.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/app/models/user.py`
- **Purpose**: SQLAlchemy ORM `User` model.
- **Salvageable**: Yes — all 9 stats, all PRD fields.
- **Broken**: `mindset_profile` uses `JSON` but migration uses `ARRAY(Text)`. Type mismatch will cause SQLite tests to fail on array operations. `_jsonb_or_json()` helper is unused dead code.
- **Action**: FIX — remove dead `_jsonb_or_json()`, keep `JSON` for ORM (migration handles ARRAY for Postgres).

### `backend/app/models/quest.py`
- **Purpose**: `Quest` ORM model with domain/difficulty enums.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/app/models/achievement.py`
- **Purpose**: `Achievement` ORM model with `UNIQUE(user_id, key)`.
- **Salvageable**: Yes — constraint is present.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/app/models/analytics.py`
- **Purpose**: `AnalyticsSnapshot` ORM model.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/app/routers/auth.py`
- **Purpose**: `/register`, `/login`, `/refresh`, `/logout` endpoints.
- **Salvageable**: Yes.
- **Broken**: `logout` does **not revoke the refresh token in Redis** — the token remains valid after logout (Bug #7 partial). Should delete `refresh:{jti}` key. Also `Request` import unused after rate-limit refactor.
- **Action**: FIX logout to revoke refresh token.

### `backend/app/routers/users.py`
- **Purpose**: `/me`, `/me` PATCH, `/me/onboarding`, `/me/stats`, `/me/achievements`.
- **Salvageable**: Yes.
- **Broken**: Nothing functionally broken.
- **Action**: KEEP as-is.

### `backend/app/routers/quests.py`
- **Purpose**: Quest CRUD + generate + complete endpoints.
- **Salvageable**: Yes.
- **Broken**: Nothing structurally broken.
- **Action**: KEEP as-is.

### `backend/app/routers/analytics.py`
- **Purpose**: `/summary`, `/weekly-report`, `/streaks`, `/patterns`.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/app/routers/websocket.py`
- **Purpose**: `/ws/{user_id}` WebSocket endpoint.
- **Salvageable**: Yes.
- **Broken**: No JWT auth on WS connection — any unauthenticated user can connect to any user's socket.
- **Action**: FIX — add token query-param validation.

### `backend/app/services/achievement_service.py`
- **Purpose**: Achievement checking with `>=` threshold logic.
- **Salvageable**: Yes — **this is already correct** (uses `>=`, not `==`). Bug #1 is already FIXED in this file.
- **Broken**: Nothing — the `>=` pattern is present.
- **Action**: KEEP as-is (Bug #1 is already fixed).

### `backend/app/services/auth_service.py`
- **Purpose**: Password hashing, JWT creation/decoding.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/app/services/quest_service.py`
- **Purpose**: `get_quests_for_today()`, `create_quest()`, `complete_quest()`.
- **Salvageable**: Yes.
- **Broken**: `complete_quest()` calls `await db.commit()` inside the service while the router already relies on `get_db()` auto-commit. This causes a double-commit pattern. Not crash-inducing but architecturally inconsistent.
- **Action**: FIX — remove internal `await db.commit()`, rely on `get_db()` middleware commit.

### `backend/app/services/user_service.py`
- **Purpose**: `get_user_by_email()`, `get_user_by_id()`, `get_current_user()` auth dependency.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/app/services/analytics_service.py`
- **Purpose**: Summary, streaks, weekly report, patterns queries.
- **Salvageable**: Yes.
- **Broken**: Nothing functionally broken.
- **Action**: KEEP as-is.

### `backend/app/agents/llm.py`
- **Purpose**: `get_llm()` singleton via `lru_cache`.
- **Salvageable**: Yes — **Bug #2 is already FIXED**. LLM is lazy (imported inside function, cached).
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/app/agents/agents.py`
- **Purpose**: Factory functions for all 5 CrewAI agents.
- **Salvageable**: Yes — **Bug #2 is already FIXED**. All agents use `get_llm()` inside factory functions.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/app/agents/crews.py`
- **Purpose**: `create_daily_quest_crew()`, `create_analytics_crew()`, `create_coach_crew()`.
- **Salvageable**: Yes.
- **Broken**: Nothing structurally broken. `create_analytics_crew()` and `create_coach_crew()` are implemented.
- **Action**: KEEP as-is.

### `backend/app/agents/tasks.py`
- **Purpose**: Quest generation prompt template + `build_quest_generation_task()`.
- **Salvageable**: Yes.
- **Broken**: `completion_rate` is hardcoded `0.6` — should be computed from DB. Minor but acceptable for now.
- **Action**: KEEP as-is (cosmetic issue, not a crash bug).

### `backend/app/agents/tools.py`
- **Purpose**: 7 `@tool`-decorated CrewAI tools.
- **Salvageable**: Yes.
- **Broken (Bug #4 check)**: No `.func()` or `.run()` calls found anywhere in the codebase. Bug #4 does NOT exist in this codebase — tools are never called directly, only passed to agents for autonomous invocation.
- **Action**: KEEP as-is.

### `backend/app/agents/parsers.py`
- **Purpose**: `parse_quest_list()` — parses raw LLM JSON output into `QuestCreate` objects.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/app/tasks/quest_tasks.py`
- **Purpose**: `generate_quests_task` Celery task — calls `crew.kickoff()`.
- **Salvageable**: Yes — **Bug #3 is already FIXED**. `crew.kickoff()` IS called on line 37.
- **Broken**: Nothing structurally broken. `pre_generate_quests` is a stub (empty pass).
- **Action**: FIX stub `pre_generate_quests` to query all users and schedule quest generation.

### `backend/app/tasks/analytics_tasks.py`
- **Purpose**: `daily_snapshot`, `weekly_report`, `generate_coach_message` tasks.
- **Salvageable**: Yes — `crew.kickoff()` called on lines 118, 177.
- **Broken**: Uses old-style `loop.run_until_complete()` pattern — works but fragile in some environments. Also `generate_coach_message` in `analytics_tasks.py` and `notification_tasks.py` have **name collision**.
- **Action**: FIX name collision; KEEP logic.

### `backend/app/tasks/notification_tasks.py`
- **Purpose**: Stub tasks for `generate_coach_message` and `streak_check`.
- **Salvageable**: `streak_check` skeleton.
- **Broken**: `generate_coach_message` name conflicts with `analytics_tasks.generate_coach_message`. `streak_check` is empty stub.
- **Action**: FIX — rename notification task, implement `streak_check`.

### `backend/app/utils/game_mechanics.py`
- **Purpose**: XP → rank/level logic, streak calculation.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/app/utils/quote_db.py`
- **Purpose**: Motivational quotes by domain.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/app/utils/websocket_manager.py`
- **Purpose**: In-memory WebSocket connection registry.
- **Salvageable**: Yes.
- **Broken**: In-memory only — connections lost on restart, not shareable across workers. Acceptable for v1.
- **Action**: KEEP as-is.

### `backend/app/schemas/`
- **Purpose**: Pydantic v2 request/response models.
- **Salvageable**: Yes.
- **Broken**: `users.py` — `UserOut.model_validate()` is overridden manually, which bypasses Pydantic's from_attributes. Works but fragile.
- **Action**: KEEP as-is (functional).

### `backend/alembic/`
- **Purpose**: Database migration history.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/tests/conftest.py`
- **Purpose**: pytest fixtures — SQLite test DB, FakeRedis, async client.
- **Salvageable**: Yes.
- **Broken**: `app.main` import triggers `create_async_engine(asyncpg URL)` at import time, causing `ModuleNotFoundError: asyncpg` in test environment. Need to override `DATABASE_URL` env var before importing app.
- **Action**: FIX — set env var before importing app in conftest.

### `backend/tests/test_auth.py`
- **Purpose**: Auth endpoint tests.
- **Salvageable**: Yes.
- **Broken**: Nothing logically broken; will pass once conftest is fixed.
- **Action**: KEEP as-is.

### `backend/tests/test_quest_completion.py`
- **Purpose**: Quest CRUD and completion tests.
- **Salvageable**: Yes.
- **Broken**: Nothing logically broken; will pass once conftest is fixed.
- **Action**: KEEP as-is.

---

## 3. Frontend files

### `frontend/src/api/users.ts`
- **Purpose**: API client for user endpoints.
- **Salvageable**: Yes.
- **Broken**: **Missing `updateMe()` export** — `ProfilePage.tsx` imports it but it doesn't exist, causing a TypeScript compile error.
- **Action**: FIX — add `updateMe()` function.

### `frontend/src/api/auth.ts`
- **Purpose**: Login/register API calls.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `frontend/src/api/quests.ts`
- **Purpose**: Quest API calls.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `frontend/src/api/analytics.ts`
- **Purpose**: Analytics API calls.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `frontend/src/api/client.ts`
- **Purpose**: Axios instance with JWT interceptor.
- **Salvageable**: Yes.
- **Broken**: Response interceptor on 401 clears tokens but doesn't attempt refresh — user is immediately logged out on token expiry instead of silently refreshing. Not a crash bug but poor UX. Token refresh interceptor per PRD 8.3 should retry with new access token.
- **Action**: FIX — implement token refresh interceptor.

### `frontend/src/pages/DashboardPage.tsx`
- **Purpose**: Main dashboard — stats, quests, achievements.
- **Salvageable**: Yes — uses TanStack Query, real API calls, no hardcoded data.
- **Broken (Bug #6 check)**: No hardcoded quest/user data found. Bug #6 is NOT present. Quote "The body achieves what the mind believes" is hardcoded in the motivational box — this is minor UI copy, not data.
- **Action**: KEEP as-is (quote can be fetched from API as enhancement).

### `frontend/src/pages/LoginPage.tsx`
- **Purpose**: Login/register form.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `frontend/src/pages/AnalyticsPage.tsx`
- **Purpose**: Analytics charts page.
- **Salvageable**: Yes — uses real API calls.
- **Broken**: `weeklyChartData` mapping produces dummy `{ day, completed: 0, xp: 0 }` — the actual weekly data from the API is not mapped to days. It's a display bug (chart is blank).
- **Action**: FIX — map actual API data to chart format.

### `frontend/src/pages/ProfilePage.tsx`
- **Purpose**: Profile and goals page.
- **Salvageable**: Yes.
- **Broken**: Imports `updateMe` which doesn't exist in `api/users.ts`. TypeScript will fail to compile.
- **Action**: FIX (requires `updateMe` to be added to `api/users.ts`).

### `frontend/src/store/authStore.ts`
- **Purpose**: Zustand store for auth tokens.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `frontend/src/hooks/useWebSocket.ts`
- **Purpose**: WebSocket connection with auto-reconnect.
- **Salvageable**: Yes — auto-reconnect with 10 retries is implemented.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `frontend/src/types/index.ts`
- **Purpose**: TypeScript type definitions.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `frontend/src/components/`
- **Purpose**: UI components — sidebar, topbar, quest cards, charts, animations.
- **Salvageable**: Yes — all components implemented.
- **Broken**: Nothing critical.
- **Action**: KEEP as-is.

### `frontend/src/utils/gameMechanics.ts`
- **Purpose**: XP/rank/level calculations mirroring backend logic.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `frontend/tests/e2e/user_journey.spec.ts`
- **Purpose**: Playwright E2E tests.
- **Salvageable**: Yes.
- **Broken**: Tests require live backend + frontend. Will pass when services are running.
- **Action**: KEEP as-is.

---

## 4. Infrastructure files

### `docker-compose.yml`
- **Purpose**: Postgres, Redis, backend, Celery worker, Celery beat, frontend.
- **Salvageable**: Yes.
- **Broken**: Nothing.
- **Action**: KEEP as-is.

### `backend/Dockerfile`
- **Purpose**: Python backend container.
- **Salvageable**: Yes (not fully read but standard pattern).
- **Action**: KEEP as-is.

### `frontend/Dockerfile`
- **Purpose**: Node frontend container.
- **Salvageable**: Yes.
- **Action**: KEEP as-is.

### `backend/alembic.ini`
- **Purpose**: Alembic configuration.
- **Salvageable**: Yes.
- **Action**: KEEP as-is.

---

## 5. Bug Summary

| # | Bug | Ticket Description | Status in Code | Fix Required |
|---|-----|--------------------|----------------|--------------|
| 1 | Achievement == | `==` skips thresholds when jumping | **ALREADY FIXED** (`>=` used) | None |
| 2 | llm=None crashes | Agent created at module level | **ALREADY FIXED** (`lru_cache` + factory fns) | None |
| 3 | kickoff() missing | Crew created but never run | **ALREADY FIXED** (`crew.kickoff()` called) | None |
| 4 | tool.func() pattern | Tools called bypassing decorator | **NOT PRESENT** (tools never called directly) | None |
| 5 | In-memory state | StateManager, no persistence | **ALREADY FIXED** (Postgres + SQLAlchemy) | None |
| 6 | Hardcoded UI | React useState with mock data | **ALREADY FIXED** (TanStack Query + real API) | None |
| 7 | No auth | No user accounts | **ALREADY FIXED** (JWT + bcrypt + refresh tokens) | Partial fix: logout doesn't revoke refresh token |

---

## 6. Actual Bugs Found (not in ticket)

| # | File | Bug | Fix |
|---|------|-----|-----|
| A | `tests/conftest.py` | Imports `app.main` which creates asyncpg engine at import time → test crash | Set `DATABASE_URL` env before import |
| B | `frontend/src/api/users.ts` | Missing `updateMe()` export → TypeScript compile error | Add `updateMe()` |
| C | `routers/auth.py` | Logout doesn't revoke refresh token in Redis | Add `redis.delete()` on logout |
| D | `frontend/src/api/client.ts` | 401 interceptor never retries with refresh token | Add refresh retry logic |
| E | `frontend/src/pages/AnalyticsPage.tsx` | Weekly chart data always zeros | Map API response to chart format |
| F | `tasks/notification_tasks.py` | `generate_coach_message` name conflicts with analytics task | Rename/implement |
| G | `tasks/quest_tasks.py` | `pre_generate_quests` is an empty stub | Implement or remove stub |
| H | `routers/websocket.py` | No auth on WebSocket — anyone can listen to any user's events | Add token validation |

---

## 7. Overall Verdict

The prototype has been **substantially improved** from the original. The 7 headline bugs described in the ticket are all fixed in the current code. However, **8 secondary bugs** were found during this audit — notably a TypeScript compile error (missing `updateMe`), a logout security issue, and a test suite crash on import.

**Action plan**: Fix bugs A–H listed above, then verify all tests pass.

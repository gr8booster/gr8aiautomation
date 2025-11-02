# GR8 AI Automation — Build Plan (Core-First, Launch-Ready MVP)

This plan follows Core-First development: Test Core in Isolation → Fix Until It Works → Build App → Test Incrementally. Given the complexity (web scanning + LLM analysis + orchestrator), a POC is required before building the full application.

## 1) Objectives

- Deliver a launch-ready MVP that:
  - Scans any public website URL
  - Uses AI (OpenAI GPT-4 + Anthropic Claude) to analyze the site and recommend actionable automations
  - Lets users activate automations and execute them via a custom orchestrator with a DB-backed state machine
  - Ships with three fully functional automation types (no external APIs required):
    1) AI Website Chatbot/Agent
    2) Lead Capture + Auto-Response (drafts)
    3) Appointment Scheduler (local calendar + ICS export)
  - Beautiful, intuitive UI (React + Tailwind + shadcn/ui + Framer Motion)
  - Clean FastAPI backend, MongoDB models (UUID IDs, UTC timestamps), robust error handling
  - Clear testing, seeded data, and docs

- Defer external connectors (Twilio, Stripe, socials, email providers) until post-MVP keys are available.

- Keep scope tight for a great first working version, then iterate.

## 2) Architecture & Tech

- Frontend: React (no Next.js), TailwindCSS, shadcn/ui, Framer Motion
- Backend: FastAPI, Pydantic v2 models, httpx/requests for fetching, BeautifulSoup + trafilatura/readability for content extraction
- Database: MongoDB (UUID primary keys, timezone-aware timestamps)
- AI: OpenAI GPT-4 + Anthropic Claude via Emergent LLM key (universal key)
- Orchestrator: Custom DB-backed state machine (polling-based, no websockets initially). Background execution via internal scheduler/loops.
- Observability: Structured logs; simple metrics counters in DB (expand later)
- Security: Input validation, safe URL fetching, robots.txt awareness, timeouts, domain allowlist
- Packaging: Emergent environment primary; Docker/K8s manifests prepared post-MVP

### Core Data Models (MongoDB)
- users: { id, email, created_at }
- websites: { id, owner_id, url, fetched_at, analysis_summary, content_digest }
- automation_templates: { id, key, name, description, workflow_json, version, category }
- active_automations: { id, owner_id, website_id, template_id, config, status }
- workflows: { id, owner_id, website_id, name, nodes, edges, variables, version, secrets_ref }
- executions: { id, workflow_id, triggered_by, state, started_at, finished_at, logs, metrics, error }
- messages (chatbot history): { id, website_id, session_id, role, content, created_at }
- leads: { id, website_id, name, email, phone, message, source, status, created_at }
- appointments: { id, website_id, customer_name, email, slot_start, slot_end, notes, status, created_at }

### API (Initial)
- POST /api/analyze { url } → { analysis_id, summary, recommended_automations[] }
- GET /api/automations → list active automations
- POST /api/automations → activate automation from template
- PATCH /api/automations/{id} → update config/status
- GET /api/executions?workflow_id= → list execution runs
- POST /api/workflows/run { workflow_id, input } → enqueue run
- GET /api/orchestrator/status → queue depth, workers, heartbeat
- POST /api/chatbot/message { website_id, session_id, message } → { reply, sources }
- POST /api/lead/submit { website_id, payload } → { lead_id, autoresponse_draft }
- POST /api/appointments/book { website_id, slot } → { appointment_id, ics_download_url }

Return Pydantic-validated responses; always use /api prefix; never hardcode env URLs.

## 3) Development Phases

### Phase 1: Core POC — Website Scanning + AI Analysis (Required)
Goal: Prove we can reliably fetch, extract, and analyze sites; produce actionable automation recommendations.

Tasks:
1. LLM Integration Prep
   - Call Integration Playbook Agent for: "OpenAI (text)" and "Anthropic (text)"
   - Use Emergent LLM Universal Key (no user-provided keys) and validate access
   - Define JSON schema for recommendations; implement Pydantic model validation

2. Website Fetcher & Extractor
   - Implement safe fetch (httpx): timeouts, redirects, content-type checks, size limit
   - Respect robots.txt best-effort; user-agent header; gracefully handle disallow
   - Parse with trafilatura/readability + BeautifulSoup; extract:
     - title, meta description/keywords, h1-h3, nav links, CTAs (buttons/links with verbs), forms (inputs+actions)
     - structured data (JSON-LD, OpenGraph), sitemap links if present
   - Compute heuristics: business type (ecom/service/blog), offerings, current conversion points, content freshness

3. AI Analysis (Dual-model strategy)
   - Prompt(s): system with schema + constraints; user with extracted site summary
   - Call GPT-4 and Claude independently; compare/merge; ensure JSON validity
   - Output: recommended_automations[] = [{ key, title, rationale, expected_impact, workflow_json, config_hints }]

4. POC Test Script: test_website_analyzer.py
   - Inputs: 3 real sites (e-commerce, services, blog)
   - Steps: fetch → extract → LLM analyze → validate JSON → print concise report
   - Success Criteria:
     - All 3 sites produce ≥5 relevant, non-generic recommendations
     - No schema validation failures
     - Avg analysis runtime ≤ 30s per site

5. Iterate until the above pass; improve prompts, extraction fallbacks, and heuristics.

Deliverables:
- test_website_analyzer.py, ai_prompts.json, schema.py
- Sample outputs saved in /tests/poc_outputs/

### Phase 2: MVP App Development (v1)
Goal: Functional app that runs the proven core; no auth initially.

Backend (FastAPI):
- Routes: /api/analyze, /api/automations (CRUD), /api/workflows/run, /api/executions, /api/orchestrator/status, /api/chatbot/message, /api/lead/submit, /api/appointments/book
- Services: analyzer_service.py, orchestrator_service.py, chatbot_service.py, lead_service.py, appointment_service.py
- Models: pydantic models in models/*.py; db helpers; UUID IDs; UTC timestamps; serialize helpers
- Seed: automation_templates (10+ templates spanning chatbot, lead capture, scheduler, email sequence drafts, content scheduler, webhooks, analytics)

Frontend (React + Tailwind + shadcn/ui + Framer Motion):
- Pages/Flows:
  - Landing: hero, value prop, animated steps, URL input
  - Analyze: URL form → progress (skeleton/loading) → analysis summary
  - Recommendations: cards (title, rationale, impact, activate toggle), “Explain plan” modal
  - Dashboard: Active automations, executions, logs, basic metrics
  - Chatbot Demo Widget: embedded panel for quick try
- Components: Card, Badge, Toggle, Toast, Dialog, Skeleton, Progress, Tabs
- States: Loading, success, errors; no drag-and-drop initially

Orchestrator (v1):
- DB-backed state machine: pending → running → completed/failed; retry_count with exponential backoff
- Node executor interface (trigger/action/condition/ai)
- Poll-based worker loop inside backend process (simple interval)
- Idempotency keys for triggers; basic token bucket rate limit per workflow
- Logs persisted per execution step

Testing (end of Phase 2):
- Use Testing Agent for E2E:
  - Analyze flow (URL → recommendations)
  - Activate automation → verify DB record
  - Run workflow → verify execution state transitions and logs
  - Chatbot roundtrip (send message → get reply)
  - Lead capture submit → autoresponse draft generated
  - Appointment booking → ICS URL provided
- Fix issues until clean pass

### Phase 3: Orchestrator + Workflow Engine
Goal: Robust executor + three production-ready automation types.

Workflow Schema:
- workflow { id, owner_id, name, nodes[], edges[], variables{}, version, secrets_ref }
- node { id, type(trigger|action|condition|transform|ai), name, config, retry_policy, timeout_seconds, idempotency_key }

Execution Engine:
- Topological execution; branch on conditions; parallel reserved for later
- Retry policy: exponential backoff, DLQ table for terminal failures
- Rate limit: token bucket per workflow and per node type
- Real-time: frontend polling endpoints; no websockets initially
- Run history: executions table + logs viewer (step-level logs)

Automation Types (implemented end-to-end):
1) AI Chatbot (Website Widget)
   - /api/chatbot/message uses LLM with site context (content digest) and persistent session
   - Provide embed code snippet (script tag calling backend) for websites
2) Lead Capture + Auto-Response
   - Hosted form + embeddable form
   - Store leads; generate LLM-crafted autoresponse DRAFT (viewable; not sent)
3) Appointment Scheduler
   - Hosted booking page + embeddable widget
   - Local availability config; store bookings; generate ICS; email sending deferred

Testing (end of Phase 3):
- E2E coverage for all three automations; error handling; empty states; resilience (retry paths)

### Phase 4: Marketplace + Automation Library
- Template library (10+): publish/clone/fork; version field; migration notes
- Visual builder (lite): form-driven config; preview JSON
- Natural language → workflow JSON: LLM with JSON schema validation
- Testing: template activations end-to-end

### Phase 5: Advanced Features + Polish
- Full visual builder (drag-drop nodes)
- Advanced orchestrator: parallel nodes, long-running waits, correlation IDs
- Observability: metrics page; error tracking hooks
- Team management (auth added after user approval)
- Export/import of workflows; public template share links

### Phase 6: External Integrations (Post-MVP)
- Stripe billing + marketplace payouts (Stripe Connect)
- Twilio SMS/Voice
- Socials (Instagram, X, Facebook, LinkedIn)
- Email providers (Gmail, Outlook)
- CRM & analytics connectors

## 4) Implementation Steps (Tactical)

1) Phase 1 — Core POC
- [ ] Call Integration Playbook Agent for OpenAI + Anthropic; fetch Emergent LLM key programmatically
- [ ] Implement extractor module: fetch → parse → summarize site context
- [ ] Author LLM prompts + Pydantic schema; write merger/validator
- [ ] Create test_website_analyzer.py; run on 3 sites; iterate until success metrics met

2) Phase 2 — V1 App
- Backend
  - [ ] Define models and DB helpers (UUIDs, UTC)
  - [ ] Implement /api/analyze, /api/automations, /api/workflows/run, /api/executions, /api/orchestrator/status
  - [ ] Seed automation_templates
  - [ ] Implement minimal orchestrator loop and node executors
- Frontend
  - [ ] Fetch design guidelines (design agent)
  - [ ] Build Landing, Analyze, Recommendations, Dashboard, Chatbot demo
  - [ ] Wire calls to backend; loading and error states; no auth
- Testing
  - [ ] Run Testing Agent E2E; fix all issues

3) Phase 3 — Engine + 3 Automations
- [ ] Finalize workflow schema; implement robust executor with retries and DLQ
- [ ] Implement chatbot, lead capture, scheduler end-to-end with embeds
- [ ] Add run history + logs viewer; polling status updates
- [ ] Testing Agent round; fix issues

4) Post-MVP (Phases 4-6)
- [ ] Marketplace templates, visual builder lite, NL→Workflow
- [ ] Advanced features + observability
- [ ] External integrations when keys available

## 5) Next Actions (Immediate)
- Create core POC files: extractor, prompts, schema, test_website_analyzer.py
- Call integration playbook for OpenAI + Anthropic; wire Emergent LLM key
- Implement and run POC on 3 real websites; iterate until recommendations are clean and ≥5 per site
- Then build v1 app around proven core

## 6) Success Criteria (MVP: Phases 1-3)
- User can paste website URL and receive analysis + ≥5 relevant automation recommendations
- User can activate recommended automations and run them
- Orchestrator executes workflows reliably with clear state transitions and logs
- Dashboard shows running automations, simple metrics, and run history
- Three automation types fully functional without external APIs
- UI is polished, fast, and error-free; no crashes or critical errors

## 7) Risks & Mitigations
- Dynamic websites hard to parse → Use multiple extractors, graceful fallbacks, and content-size/time limits; improve prompt
- LLM JSON validity → Enforce schema with function-call/JSON modes + server-side validation/repair
- Long-running tasks → Persist state and resume via polling; move to advanced orchestrator later
- Rate limits/costs → Minimal tokens, caching of fetch/extract; short prompts; batching

## 8) Testing Strategy
- POC: assert schema validity, output quality, and runtime thresholds
- App: testing agent for E2E flows (no drag-and-drop or camera tests)
- Error handling: simulate invalid URL, timeouts, empty states; verify messages

## 9) Deliverables
- POC scripts and outputs
- Working frontend+backend MVP (no auth)
- Orchestrator with state machine, retries, logs
- 10+ templates seeded; 3 automations fully implemented
- Basic docs: getting-started.md, API overview

---
Notes:
- Environment rules: use /api prefix; bind backend 0.0.0.0:8001; use REACT_APP_BACKEND_URL and MONGO_URL envs; React .js files (not .jsx).
- Ask before adding auth; it hinders agent testing.

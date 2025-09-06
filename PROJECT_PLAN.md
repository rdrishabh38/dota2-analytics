# 🎮 Dota 2 Personal Analytics — Project Plan

## 1. Vision & Goals
A desktop application that allows casual Dota 2 players to:
- Fetch their match & conduct history directly from Steam Web APIs.
- View rich analytics dashboards (hero stats, win rates, item usage, behavior trends).
- Export data (CSV/Excel) for personal analysis.
- Run with **one-click simplicity** (Windows `.exe` installer).
- Work **offline-first** (data stored locally in SQLite).

---

## 2. Architecture Overview
```
[PySide6 Desktop UI] 
       ⇅ HTTP (localhost)
[FastAPI Backend (embedded in .exe)] 
       ⇅ SQLAlchemy ORM
[SQLite Database (d2analytics.db)]
```

### Development Environment
- Containers with **FastAPI + Postgres 15** for dev/testing.
- Docker Compose for orchestration.
- SQLite used only for **end-user builds**.

### End-User Environment
- `.exe` containing:
  - FastAPI backend
  - SQLite DB (auto-created)
  - PySide6 GUI
- No Docker or Postgres required.

---

## 3. Technology Stack
- **Backend**
  - FastAPI (REST API)
  - SQLAlchemy 2.0 ORM
  - Alembic (migrations)
  - Pydantic (schemas)
  - HTTPX (Steam API client)
- **Database**
  - Dev: Postgres 15 (Dockerized)
  - Prod: SQLite (embedded)
- **Frontend (UI)**
  - PySide6 (Qt for Python)
  - Matplotlib/Plotly (charts)
- **Packaging**
  - PyInstaller (build `.exe`)
- **Testing**
  - Pytest
  - Docker-based integration tests

---

## 4. Data Model (ERD v1)
```
Profile
 ├── MatchHistory (many)
 │     └── MatchDetails (heroes, KDA, items, etc.)
 └── ConductHistory (many)

Profile(id, steam_id, persona_name, mmr_estimate, created_at)
MatchHistory(id, profile_id, match_id, hero_id, kills, deaths, assists, result, duration, played_at)
ConductHistory(id, profile_id, date, reports, commendations, behavior_score)
```

---

## 5. Development Workflow
1. **Spin up containers** (Postgres + FastAPI).
2. **Run migrations** via Alembic.
3. **UI connects to FastAPI** at `localhost:8000`.
4. **Switch to SQLite** in config when packaging app.

---

## 6. Config & DB-Agnostic Setup
- Single backend with config-driven DB switch:
  ```ini
  # .env (dev)
  DB_URL=postgresql+psycopg2://user:pass@db:5432/dota
  ```

  ```ini
  # .env (prod)
  DB_URL=sqlite:///./d2analytics.db
  ```

---

## 7. Features (Planned)
### Phase 1 (MVP)
- Steam login (cookie-based session).
- Fetch & store match history + conduct history.
- Basic dashboards:
  - Hero win rates
  - KDA trends
  - Recent conduct scores
- Export to CSV.

### Phase 2
- Custom chart builder.
- Time-filtered dashboards.
- Player comparison (multiple profiles).
- Excel export.

### Phase 3
- Advanced stats (item timings, lane performance).
- Notification system (e.g., "new conduct score available").
- Cloud sync option (future stretch goal).

---

## 8. Repo Structure
```
dota2-analytics/
  backend/
    app/
      core/
        settings.py
      db/
        session.py
        models/
        migrations/
      api/
      schemas/
      services/
      main.py
  ui/
    main.py
    windows/
    components/
  tests/
  docker-compose.yaml
  Dockerfile
  requirements.txt
  PROJECT_PLAN.md
```

---

## 9. Packaging & Distribution
- Build `.exe` using PyInstaller:
  - Bundles PySide6 UI + FastAPI + SQLite.
  - Runs backend subprocess on launch.
- First launch → auto-create `d2analytics.db`.
- Auto-apply Alembic migrations on version upgrade.

---

## 10. Roadmap
### Month 1
- Backend skeleton (FastAPI + DB setup).
- ERD finalized.
- Alembic migrations.
- Docker dev environment.

### Month 2
- Steam client + ingestion pipeline.
- SQLite switch.
- Basic PySide6 UI.

### Month 3
- Dashboards & charts.
- CSV export.
- PyInstaller packaging.

### Month 4+
- Advanced stats.
- Excel export.
- User polish & auto-updater.

---

✅ With this plan, we’ll have **one codebase**, **two runtime modes** (dev vs prod), and a clear path from MVP → full product.  

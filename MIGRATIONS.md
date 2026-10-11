# Migration compatibility and verification

Run migration checks on disposable databases or restored development copies.
The automated tests supply their own database connections; they never migrate
the database in your local `.env`. PostgreSQL is the deployment database;
SQLite is also exercised as an isolated compatibility test backend.

## Published history

The telemetry chain has one head:

```text
a55a4d867116 -> c0f80578b423 -> 1a0db3d3e168 -> cff8339db910
             -> d2b4c6e8f901 -> e7b91c4a2d60
```

- `c0f80578b423` is an already-published empty marker. Keep it empty; the
  network table definitions belong to `1a0db3d3e168` and later revisions.
- `1a0db3d3e168` creates network persistence and canonical alert history.
- `cff8339db910` creates the separate legacy `security_alerts` table.
  That historical table is retained; new network detections use `alerts` and
  `alert_status_history` (also used by the dashboard and analyst workflows).
- `d2b4c6e8f901` adds telemetry fields, tables, relationships, and indexes.
- `e7b91c4a2d60` repairs installations that already ran an older onboarding
  implementation, and relaxes obsolete required log fields and plaintext
  sensor-key constraints without dropping surviving evidence.

Commit `f620d223` had already replaced the body of `c607f5c28195`. Databases
that ran its original body will not rerun it. The new repair revision explicitly
reconciles those databases using the frozen additive definitions, recreating
missing onboarding/IOC/case/hunting structures. Future fixes must get new
revision IDs. Records destroyed by the original migration cannot be recovered
by a schema repair; recovery requires a pre-migration backup.

## Normal upgrade

From `backend/`, with `DATABASE_URL` (or Alembic-only `DB_OVERRIDE`) pointing
to the intended **development/test** database:

```text
python -m alembic heads
python -m alembic current
python -m alembic upgrade head
python -m alembic current
```

Do not stamp an arbitrary database to `head`, invoke ORM `create_all` as a
replacement for migrations, or edit a published revision to conceal drift.
These compatibility migrations inspect the live schema, so use online
migrations rather than offline `--sql` generation. The new repair is
forward-only and refuses a destructive downgrade.

SQLite table-copy repairs require `PRAGMA foreign_keys=OFF` on the migration
connection **before** its transaction, which is the default for the Alembic
SQLite connection. If enabled, the repair refuses to copy tables rather than
risk cascading deletion of observations or IOC matches. Afterwards run
`PRAGMA foreign_key_check`, then enable foreign keys for application use.
PostgreSQL uses in-place column alterations.

## Existing `security_alerts` before its revision

If an earlier bootstrap already created `security_alerts`, the historical
`cff8339db910` cannot create it again. On a restored development copy:

```text
python -m alembic upgrade 1a0db3d3e168
python adopt_security_alerts.py
python -m alembic upgrade head
```

The adoption utility only accepts a database exactly at `1a0db3d3e168` and
validates all historical columns, types, nullability, primary key, foreign
keys, and indexes against that revision. Only then does it record
`cff8339db910`; it neither recreates the table nor changes its rows. A partial
or incompatible schema stops with an error and keeps its version unchanged.
Resolve that reported discrepancy in a reviewed repair before retrying.

The much older `6a8b7c9d0e1f` drops `audit_logs`. The migration environment now
refuses to cross that revision when the table contains records. Such an old
installation requires a separate data-preserving audit-history migration
before continuing; merely stamping past it would leave an incomplete schema.

## Reproducible checks

```text
# backend/
python -m pip install -r requirements-dev.txt
python -m pytest tests -q

# frontend/
npx tsc --noEmit --incremental false
npm run build
npm run lint

# repository root; set a local SECRET_KEY or use the explicit backend env file
docker compose --env-file backend/.env config --quiet
```

Regression tests cover clean upgrades; upgrades from the empty marker, network,
security-alert, and former head revisions; preservation of existing logs and
security alerts; recovery of missing onboarding tables; legacy sensor-key
constraints with retained child records; rejected unsafe adoption; and API
enrollment, telemetry, dashboard, and alert-history operations on migrated DBs.

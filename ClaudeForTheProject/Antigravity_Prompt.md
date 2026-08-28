Task: Apply the audited Police FIR / CrimeNexus database schema to this repository.

Context: I had an external review done comparing our official ER diagram, our existing
Police_FIR_Schema2.sql, and our actual 10k-row CSV dataset. The reviewer did NOT have
access to this repository, so before changing anything, first inspect the actual codebase
yourself and report back — don't assume the structure below is how our repo is organized.

Step 1 — Inspect before touching anything:
- Find where the database is initialized (SQLite/MySQL/Postgres/other) and which ORM, if any,
  is in use (SQLAlchemy, Prisma, raw SQL, etc.).
- Find existing models/entities, migrations, and seed/import scripts.
- Find every backend service/query that touches: cases, victims, accused, complainants,
  arrests, acts/sections, officers, courts, geography, or chargesheets.
- Report what you find before making changes. If our existing database differs from
  Police_FIR_Schema2.sql, tell me — don't silently pick one.

Step 2 — Reconcile against the attached final schema (Police_FIR_Schema_FINAL.sql):
Compared to our old Police_FIR_Schema2.sql, the reviewed version:
  1. Adds a new Inv_OccuranceTime table (1:1 with CaseMaster) holding IncidentFromDate,
     IncidentToDate, InfoReceivedPSDate, latitude, longitude, and a new OccurrenceBriefFacts
     field — these were pulled OUT of CaseMaster, which keeps only BriefFacts.
  2. Adds a missing AccusedMasterID column + FK on ArrestSurrender (primary accused per
     arrest event); the existing junction table inv_arrestsurrenderaccused still covers
     joint/multiple accused per arrest.
  3. Adds GenderMaster, BloodGroupMaster, and ArrestSurrenderTypeMaster lookup tables
     (these are reasonable additions, not from an official spec — flag if we already have
     equivalent lookups elsewhere in the app, and reuse those instead of duplicating).
  4. Makes Court.DistrictID nullable (state-level courts like the High Court aren't tied to
     one district).

If any of this conflicts with something the real backend already depends on, stop and tell
me the conflict instead of forcing the new schema through.

Step 3 — Migration, not blind replacement:
- Write this as an incremental migration (Alembic/Prisma/raw SQL — whatever this repo
  already uses), not a DROP/CREATE, unless you confirm with me first that a full rebuild
  is safe.
- If application code reads any of the columns being moved (IncidentFromDate etc. out of
  CaseMaster) or the new ArrestSurrender.AccusedMasterID column, update those call sites
  and flag them in your summary — don't leave the app silently broken against the new shape.

Step 4 — Load the real data:
Attached are 25 already-normalized CSVs (normalized_tables.zip) generated directly from our
karnataka_crime_dataset_10k_compliant.csv — one file per table, already deduplicated and
FK-resolved, verified against 0 orphan rows and 0 duplicate business keys. Load these rather
than re-deriving them from the raw CSV, unless you have a reason to redo the ETL yourself (if
so, tell me why before doing it — the mapping logic in CSV_to_Schema_Mapping.csv and the audit
report explain the non-obvious parts, especially: CSV rows are NOT 1:1 with any single entity —
victims and accused are independently deduplicated per case, not paired by row position).

Step 5 — Validate and report back:
Run validation_queries.sql (or your ORM's equivalent) after loading and confirm:
- 0 orphan rows on every parent-child relationship
- 0 duplicate CrimeNo / KGID / (CaseMasterID, PersonID) / (ActCode, SectionCode)
- Row counts match: CaseMaster 5,078 / Victim 6,993 / Accused 8,870 / ArrestSurrender 2,271 /
  ChargesheetDetails 1,522 (see CrimeNexus_Audit_Report.md, Section I, for the full list)

Do not fabricate a "compatibility score" or claim success without actually running these
checks against the real database. If something doesn't reconcile, show me the actual numbers
and the discrepancy.

Open questions I still need to decide (don't resolve these yourself — ask):
- Should CasteMaster/ReligionMaster/OccupationMaster be seeded with a starter reference list?
  (No source data exists for these in the CSV — see audit report, Section J.)
- Is "Arrest"/"Surrender" the correct label for ArrestSurrenderTypeMaster codes 1/2, or does
  our system use different terminology?
- Employee currently has no LastName field (matches the official spec, which only defines
  FirstName) — do we want to add one?

Attached files: Police_FIR_Schema_FINAL.sql, validation_queries.sql,
CSV_to_Schema_Mapping.csv, CrimeNexus_Audit_Report.md, normalized_tables.zip

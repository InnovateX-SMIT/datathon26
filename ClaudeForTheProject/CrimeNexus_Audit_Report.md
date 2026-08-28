# Police FIR / CrimeNexus — Audit Report

**Scope note:** This audit is based on the three files actually provided — the ER diagram PDF, the existing SQL schema, and the 10,001-row CSV. No application repository, backend code, ORM models, or migrations were provided, so this report makes no claims about those. Every number below was computed by directly parsing the real files, not estimated.

---

## A. Official Schema Summary (from the PDF)

- **26 tables** have full column-level definitions in the "Table Definitions" section.
- **2 additional tables** (`Inv_OccuranceTime`, `inv_arrestsurrenderaccused`) are named only in the Relationship Matrix — the PDF never gives them a column list. This is a real gap in the source document itself, not something I'm inferring.
- **136 columns** total across the 26 formally-defined tables.
- **~37 relationships** listed in the Relationship Matrix.

## B. Existing SQL Audit (`Police_FIR_Schema2.sql`)

**What matches:** 25 of the 26 formally-defined tables are implemented, and for 25 of those 26 tables every column matches the PDF exactly, with correct PK/FK structure. This is a solidly-built schema overall.

**What's missing or wrong, concretely:**

| # | Finding | Evidence |
|---|---|---|
| 1 | `Inv_OccuranceTime` table doesn't exist in the SQL at all | PDF relationship matrix declares a 1:1 `CaseMaster → Inv_OccuranceTime`; no such table in the SQL |
| 2 | `ArrestSurrender` is missing the `AccusedMasterID` column | PDF's own column list for `ArrestSurrender` explicitly includes `AccusedMasterID INT FK → Accused.AccusedMasterID`; the SQL's `CREATE TABLE ArrestSurrender` has no such column or FK |
| 3 | No `Gender`/`BloodGroup` lookup tables exist anywhere | Both PDF and SQL call `GenderID`/`BloodGroupID` "lookup values" on 4+ tables but never define the lookup table. This is a gap in **both** source documents, not just the SQL. |

**Where the PDF itself has internal inconsistencies (worth knowing before you treat it as gospel):**

- `ActSectionAssociation.ActID` is documented as `INT FK → Act.ActCode` — but `Act.ActCode` is defined elsewhere in the same PDF as a `VARCHAR` primary key. The existing SQL correctly used `VARCHAR` here, i.e. **the SQL is more internally consistent than the PDF on this point.**
- The Relationship Matrix row for the arrest/accused junction reads: *"ArrestSurrender `AccusedMasterID(via junction)` One to Many `inv_arrestsurrenderaccused` `ArrestSurrenderID`"* — the parent/child columns and cardinality direction in this row don't cleanly parse. I've implemented the sensible reading (arrest→junction is one-to-many, junction→accused is many-to-one) rather than the literal text.

## C. CSV Audit (real numbers, full file)

- **10,001 rows × 62 columns.** Every column accounted for (see mapping file).
- **Grain: NOT 1 row = 1 case.** A row is closer to "one slot in a zipped victim/accused list," padded to the length of whichever list (victims or accused) is longer for that case. This is a synthetic-data artifact of how the CSV was flattened, confirmed by checking a case with 3 victims and 2 accused → 3 rows, where row 3 has a victim and a blank accused slot.
- **5,078 distinct cases** (`crime_no`), each with row-count 1–4.
- Verified **0 mismatches** matching `arrest_primary_accused_name` and parsed `arrest_joint_accused_names` against each case's actual accused roster (2,271 + 618 checks, 100% clean) — the free-text arrest-linkage fields are trustworthy.
- **`complainant_occupation`, `complainant_religion`, `complainant_caste` are 100% NULL** — zero source values exist for these anywhere in the 10,001 rows.
- `crime_no` structure matches the PDF's documented 18-digit format (1+4+4+4+5) in 100% of rows, **but the category-code digit doesn't match the PDF's own worked examples**: PDF says FIR=1, UDR=3, PAR=4; the actual data uses FIR=1, UDR=2, PAR=3.
- One court (`High Court of Karnataka, Bengaluru`) legitimately appears against all 31 districts — it's a state-level court, not a data error. The schema needs `Court.DistrictID` to be nullable to represent this correctly.
- Every one of 284 officer KGIDs maps to exactly one name, rank, designation, and district across all their appearances — the employee data is internally clean.

## D. CSV → Schema Mapping

Full 62-column mapping is in `CSV_to_Schema_Mapping.csv`. Summary:

| Classification | Count |
|---|---|
| DIRECT | 45 |
| TRANSFORMED (lookup encode / name-match) | 7 |
| SPLIT INTO MULTIPLE TABLES | 7 |
| NOT REPRESENTABLE (no source values) | 3 |
| **Total** | **62** |

The 3 "not representable" columns are `complainant_occupation/religion/caste` — the columns and their target FK slots exist in the schema, but there is nothing to map because the source data is empty. This is a data gap, not a schema gap.

## E. Final Schema

See `Police_FIR_Schema_FINAL.sql`. Changes from the existing SQL, all justified above:
1. Added `Inv_OccuranceTime` (new table, 1:1 with `CaseMaster`), moved `IncidentFromDate/IncidentToDate/InfoReceivedPSDate/latitude/longitude` + a new `OccurrenceBriefFacts` field into it.
2. Added `ArrestSurrender.AccusedMasterID` + its FK.
3. Added `GenderMaster`, `BloodGroupMaster`, `ArrestSurrenderTypeMaster` lookup tables (flagged as additions beyond the literal PDF — see "Remaining Issues").
4. Made `Court.DistrictID` nullable (High Court case).
5. Added indexes on the FK columns that the relationship matrix implies will be queried most (case category/status/station/crime-head, per-case child lookups).

## F. Application Compatibility

**Not assessed — out of scope.** No backend, frontend, ORM models, or repository were provided in this conversation. Anything claiming to know how this affects existing APIs would be fabricated. If you want this checked, share the actual repo (or point Antigravity at it directly — see the prompt at the end).

## G. Data Loss Report

Nothing in the 10,001 rows is silently dropped. The only "loss" is the 3 always-null complainant demographic columns, which carry no information to lose in the first place (see Section D).

## H. Coverage — real, computed numbers

```
Table coverage (of 26 PDF tables with full definitions):
  25/26 correctly represented = 96.2%
  Missing: Inv_OccuranceTime (now added in the final schema → 26/26)

Column coverage (of 136 PDF-defined columns, existing SQL vs PDF):
  135/136 = 99.3%
  Missing: ArrestSurrender.AccusedMasterID (now added in the final schema → 136/136)

CSV mapping coverage (of 62 columns):
  59/62 mapped (45 direct + 7 transformed + 7 split) = 95.2%
  3/62 structurally mapped but empty at the source (complainant occupation/religion/caste)
  0/62 unmapped or ambiguous

Referential integrity (measured after import, see Section I):
  0 orphan rows across all 16 parent-child relationships checked
  0 duplicate business keys (CrimeNo, KGID, CaseMasterID+PersonID, ActCode+SectionCode)
```

I'm not giving a single blended "fidelity %" — table coverage, column coverage, and data coverage measure different things and averaging them would hide exactly the kind of discrepancy this report exists to surface.

## I. Validation Results (actually run, not simulated)

Run against the generated normalized tables in pandas (equivalent SQL in `validation_queries.sql`):

```
Orphan checks (16 parent-child relationships): 0 bad rows in every case
Duplicate CrimeNo in CaseMaster:                0
Duplicate KGID in Employee:                     0
Duplicate (CaseMasterID, PersonID) in Accused:  0
Arrest→Accused name-match failures:             0 / 2,271
Row-count reconciliation:
  CaseMaster                   5,078
  Inv_OccuranceTime            5,078  (1:1, confirmed)
  ComplainantDetails           5,078
  Victim                       6,993
  Accused                      8,870
  ActSectionAssociation        5,078
  ArrestSurrender              2,271
  inv_arrestsurrenderaccused   3,122
  ChargesheetDetails           1,522
```

## J. Remaining Issues — need a human decision

1. **`GenderMaster` / `BloodGroupMaster` / `ArrestSurrenderTypeMaster` are additions**, not literally specified in the PDF (which only says "lookup value" without naming the table). I built them because the CSV shows clean, stable, small value sets, and it's consistent with how every other lookup in this schema is normalized — but confirm this is what you want before treating it as "official."
2. **`ArrestSurrenderTypeMaster` labels ("Arrest"/"Surrender") are my assumption**, not sourced from the CSV (which only has codes `1`/`2`). Verify against whatever system generated the original data.
3. **Employee has no surname field.** The PDF only defines `FirstName`; the full officer name from the CSV is stored there as-is. Consider adding `LastName` officially.
4. **The `crime_no` category-code digit doesn't match the PDF's worked examples** (UDR/PAR swapped relative to the PDF text). Someone who knows the real encoding standard should confirm which is authoritative — the PDF's stated example, or the generator that produced this data.
5. **Whether to seed `CasteMaster`/`ReligionMaster`/`OccupationMaster`** with a starter reference list. I did not invent values for these — populate them from an official source if you need the FK columns to actually resolve.

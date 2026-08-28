-- ============================================================================
-- VALIDATION QUERIES — run after loading the normalized CSVs into PoliceFIR
-- Every query below was already run in pandas against the real data during
-- this audit and returned 0 / clean in every case (see report, Section I).
-- Re-running them post-import is how you confirm the load didn't break anything.
-- ============================================================================

-- 1. Orphan children (should all return 0 rows)
SELECT 'orphan_victim' AS check_name, COUNT(*) AS bad_rows
FROM Victim v LEFT JOIN CaseMaster c ON v.CaseMasterID = c.CaseMasterID
WHERE c.CaseMasterID IS NULL;

SELECT 'orphan_accused', COUNT(*) FROM Accused a
LEFT JOIN CaseMaster c ON a.CaseMasterID = c.CaseMasterID WHERE c.CaseMasterID IS NULL;

SELECT 'orphan_complainant', COUNT(*) FROM ComplainantDetails cd
LEFT JOIN CaseMaster c ON cd.CaseMasterID = c.CaseMasterID WHERE c.CaseMasterID IS NULL;

SELECT 'orphan_arrestsurrender', COUNT(*) FROM ArrestSurrender ar
LEFT JOIN CaseMaster c ON ar.CaseMasterID = c.CaseMasterID WHERE c.CaseMasterID IS NULL;

SELECT 'orphan_arrest_accused_fk', COUNT(*) FROM ArrestSurrender ar
LEFT JOIN Accused a ON ar.AccusedMasterID = a.AccusedMasterID
WHERE ar.AccusedMasterID IS NOT NULL AND a.AccusedMasterID IS NULL;

SELECT 'orphan_junction', COUNT(*) FROM inv_arrestsurrenderaccused j
LEFT JOIN ArrestSurrender ar ON j.ArrestSurrenderID = ar.ArrestSurrenderID
LEFT JOIN Accused a ON j.AccusedMasterID = a.AccusedMasterID
WHERE ar.ArrestSurrenderID IS NULL OR a.AccusedMasterID IS NULL;

SELECT 'orphan_chargesheet', COUNT(*) FROM ChargesheetDetails cs
LEFT JOIN CaseMaster c ON cs.CaseMasterID = c.CaseMasterID WHERE c.CaseMasterID IS NULL;

SELECT 'orphan_actsection', COUNT(*) FROM ActSectionAssociation asa
LEFT JOIN CaseMaster c ON asa.CaseMasterID = c.CaseMasterID WHERE c.CaseMasterID IS NULL;

SELECT 'orphan_occurrence', COUNT(*) FROM Inv_OccuranceTime o
LEFT JOIN CaseMaster c ON o.CaseMasterID = c.CaseMasterID WHERE c.CaseMasterID IS NULL;

-- 2. Duplicate business identifiers (should all return 0 rows)
SELECT CrimeNo, COUNT(*) FROM CaseMaster GROUP BY CrimeNo HAVING COUNT(*) > 1;
SELECT KGID, COUNT(*) FROM Employee GROUP BY KGID HAVING COUNT(*) > 1;
SELECT CaseMasterID, PersonID, COUNT(*) FROM Accused GROUP BY CaseMasterID, PersonID HAVING COUNT(*) > 1;
SELECT ActCode, SectionCode, COUNT(*) FROM Section GROUP BY ActCode, SectionCode HAVING COUNT(*) > 1;

-- 3. Row-count reconciliation (compare to the numbers in the report)
SELECT 'CaseMaster' AS tbl, COUNT(*) FROM CaseMaster
UNION ALL SELECT 'Victim', COUNT(*) FROM Victim
UNION ALL SELECT 'Accused', COUNT(*) FROM Accused
UNION ALL SELECT 'ComplainantDetails', COUNT(*) FROM ComplainantDetails
UNION ALL SELECT 'ArrestSurrender', COUNT(*) FROM ArrestSurrender
UNION ALL SELECT 'inv_arrestsurrenderaccused', COUNT(*) FROM inv_arrestsurrenderaccused
UNION ALL SELECT 'ChargesheetDetails', COUNT(*) FROM ChargesheetDetails
UNION ALL SELECT 'ActSectionAssociation', COUNT(*) FROM ActSectionAssociation;

-- 4. Sanity: every CaseMaster row should have exactly one Inv_OccuranceTime row (1:1)
SELECT c.CaseMasterID FROM CaseMaster c
LEFT JOIN Inv_OccuranceTime o ON c.CaseMasterID = o.CaseMasterID
WHERE o.CaseMasterID IS NULL;

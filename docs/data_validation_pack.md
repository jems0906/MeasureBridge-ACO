# Data Validation Pack

The pytest suite is the executable source for service-level validation. SQL below is a PostgreSQL review aid over the modeled `patients.original` JSON; run only after applying migrations and validating required dates. Results should be reconciled to the service evaluator, not treated as an independent production measure implementation.

## SQL reconciliation

```sql
-- Accepted source rows and duplicate identifiers.
SELECT count(*) AS accepted_rows, count(DISTINCT id) AS unique_patients
FROM patients;

-- Duplicate identifiers should return no rows (the primary key also prevents them).
SELECT id, count(*)
FROM patients
GROUP BY id
HAVING count(*) > 1;

-- Educational eligibility count: validated dates, age on 2026-12-31,
-- qualifying encounter, hypertension=true, hospice=false.
SELECT count(*) AS eligible_denominator
FROM patients p
WHERE (p.original->>'hypertension')::boolean = true
  AND (p.original->>'hospice')::boolean = false
  AND (p.original->>'encounter_date')::date BETWEEN DATE '2026-01-01' AND DATE '2026-12-31'
  AND date_part('year', age(DATE '2026-12-31', (p.original->>'date_of_birth')::date)) BETWEEN 18 AND 85;

-- Append-only workflow event counts by provenance.
SELECT provenance, count(*) AS event_count, count(DISTINCT patient_id) AS patients_changed
FROM workflow_events
GROUP BY provenance
ORDER BY provenance;
```

The eligibility query assumes the CSV parser has already rejected invalid date and boolean strings. It is not a substitute for unknown-field handling, exclusion review, or parity testing against `measure_engine.evaluate`.

## Automated boundary and missing-data tests

- Measurement-period start/end and just-outside dates.
- Age 17, 18, 85, and 86 at the fixed 2026-12-31 age date.
- Explicit hospice exclusion and unknown eligibility fields.
- Missing `not_documented`, `not_completed`, and `patient_declined` states remain distinct.
- Completed status with absent, malformed, out-of-range, reversed, wrong-unit, or post-encounter observations is unresolved.
- Duplicate patient ID and malformed CSV row are rejected without denominator admission.
- Provenance-role mismatch, stale event ID, and decline auto-completion attempts are rejected.
- Frozen count, digest, distinct reviewer, and unresolved/import-error approval blockers are exercised.
- Small-cell and complementary equity suppression are exercised.

## Manual chart-review simulation

Use only the fictional fixture. Select a sample that includes at least two records from each classification. A simulated reviewer checks the source row, eligibility evidence, observation date/value/unit, rule version, assigned owner, and event provenance against the explanation shown in the UI. Record a pass/fail and rationale in the review evidence; do not infer clinical appropriateness or recommend treatment. This simulation validates traceability, not chart accuracy or real-world clinical validity.
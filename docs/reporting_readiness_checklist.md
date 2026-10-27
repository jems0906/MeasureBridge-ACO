# Reporting Readiness Checklist

This checklist is for the internal educational package only. Passing it does not produce a CMS-ready submission.

## Before import

- [ ] Confirm the fixture is synthetic and approved for the demo environment.
- [ ] Confirm the intended rule ID, version, measurement period, collection type, and performance direction.
- [ ] Verify file encoding, headers, size, and source provenance.

## Data validation

- [ ] Review accepted and rejected row counts; investigate duplicates and malformed fields.
- [ ] Confirm rejected rows are explicitly dispositioned and excluded from the denominator.
- [ ] Reconcile source rows, accepted patients, baseline results, current results, and exclusions.
- [ ] Review unknown eligibility, missing documentation, not-completed assessment, patient decline, and data defects separately.
- [ ] Verify each changed result has an append-only event, accountable role, evidence, and provenance.
- [ ] Confirm no source record was overwritten and the eligible denominator remains fixed for the constructed demonstration.

## Operational review

- [ ] Verify open follow-up assignments have an owner, role, due date, and barrier.
- [ ] Check that patient preference is preserved and no treatment recommendation is generated.
- [ ] Check small-cell and complementary suppression in equity displays.
- [ ] Review unresolved issues with the accountable Provider, Clinical Assistant, ACO Operations, or EHR/IT owner.

## Freeze and sign-off

- [ ] Resolve or explicitly retain all known issues; unresolved calculations and open import errors must block approval.
- [ ] Freeze a new version after any live data change; never mutate a prior snapshot.
- [ ] Independently compare snapshot counts and rule version with the source cohort.
- [ ] Verify snapshot digest and reviewer identity; reviewer must differ from preparer.
- [ ] Record review evidence and confirm status is clearly draft or internally signed.
- [ ] Label exports INTERNAL / EDUCATIONAL; do not submit them to CMS or a payer.
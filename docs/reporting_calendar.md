# Reporting Calendar and Risk Log

Illustrative internal calendar for a 2026 educational measurement period. These dates are project-planning assumptions, not CMS deadlines.

| Milestone | Target date | Dependency | Owner | Exit evidence |
| --- | --- | --- | --- | --- |
| Confirm educational rule and version | 2026-10-26 | Measure specification reviewed | ACO Operations | Versioned JSON and review status |
| Validate synthetic source fixture | 2026-10-27 | Rule locked | EHR/IT + ACO Operations | Import totals and row-level errors |
| Complete classification and boundary review | 2026-10-29 | Import accepted | Provider + Clinical Assistant + ACO Operations | Test and manual-review record |
| Assign operational follow-up | 2026-10-30 | Queue triaged | ACO Operations | Owner, role, due date, barrier |
| Review simulated workflow changes | 2026-11-06 | Follow-up events captured | Provider + EHR/IT | Provenance and source preservation check |
| Freeze internal reporting snapshot | 2026-11-09 | Reconciliation and error disposition | ACO Operations preparer | Snapshot digest and blocker list |
| Independent internal review | 2026-11-10 | Snapshot frozen with no blockers | Separate ACO Operations reviewer | Sign-off evidence |
| Portfolio retrospective | 2026-11-13 | Review complete | Cross-functional roles | Limitations and lessons learned |

## Escalation triggers

- Any denominator change or unexplained source-to-snapshot count mismatch: pause freeze; escalate to ACO Operations and EHR/IT.
- Any unresolved eligibility or completed-status data defect: retain as unresolved; block sign-off.
- Any open import error: require documented disposition; do not silently include rejected rows.
- Any evidence of source-record mutation, digest mismatch, or duplicate reviewer/preparer: stop approval and investigate.
- Any patient-decline transition to completed or treatment recommendation in the workflow: stop the demo flow and correct the implementation.
- Any intended real CMS/payer use: out of scope; obtain exact applicable specifications, value sets, governance, security review, and independent validation first.

## Risk log

| Risk | Likelihood / impact | Mitigation | Owner |
| --- | --- | --- | --- |
| Educational rule mistaken for a CMS measure | Medium / High | Persistent UI disclaimers, versioned rule, no CMS submission export | ACO Operations |
| Missing documentation mislabeled as care delivered | Medium / High | Distinct status and provenance categories; audit evidence | Provider + Clinical Assistant |
| Source-system defect treated as clinical gap | Medium / High | Separate data repair category owned by EHR/IT | EHR/IT |
| Eligibility uncertainty silently excluded | Low / High | Unknown eligibility stays unresolved and outside confirmed denominator | ACO Operations |
| Synthetic rate change overclaimed as improvement | Medium / High | Fixed denominator and constructed-demonstration label | ACO Operations |
| Small-cell inference from equity display | Medium / Medium | Suppress cells below 11 and complementary aggregates | ACO Operations |
| Local demo credentials or missing production controls reused | Medium / High | Explicit non-production warning; no production deployment claim | EHR/IT |
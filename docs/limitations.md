# Limitations and Non-Goals

- This project uses 100 wholly fictional records. It must not be populated with real patient information.
- EDU-DOC-2026 v1.0.0 is a simplified educational documentation-completeness rule, not a validated clinical quality measure and not CMS Controlling High Blood Pressure.
- The values and ranges are synthetic input-validation bounds, not clinical targets. The application must not suggest medication changes, treatment, or override patient preferences, contraindications, or clinician judgment.
- The MSSP label is explicitly contextual. LEAD is a separate disabled configuration. Neither complete MSSP nor LEAD logic is implemented.
- The fictional contract is not a real payer contract; no Bluestone terms or savings calculations are represented.
- CSV and JSON exports are internal educational packages, never CMS-ready submissions.
- A local field map does not prove FHIR conformance or commercial EHR interoperability. A future FHIR adapter would need profile, terminology, mapping, and conformance tests.
- Role strings are application-level workflow checks, not verified identities or production authorization.
- The application is not production-ready: authentication, authorization infrastructure, PHI protection, formal privacy guarantees, backups, observability, threat modeling, and operational support are absent.
- The equity rule suppresses groups under 11 and complementary aggregates for this demo; this is not a formal de-identification or privacy guarantee.
- The constructed 60% to 75% example is not observed clinical improvement, and quality percentages do not calculate shared savings.
- Burden estimates are assumptions. No production service-level, staffing, clinical, financial, or regulatory claims are made.
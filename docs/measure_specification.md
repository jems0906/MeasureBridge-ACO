# Educational documentation completeness, EDU-DOC-2026 v1.0.0

Written before implementation. This is a fictional documentation rule inspired by blood-pressure workflows, NOT Controlling High Blood Pressure, a validated clinical measure, or a CMS submission specification.

## Exact rules

- Program: EDUCATIONAL_MSSP_CONTEXT; payer: Fictional Demonstration Contract, not Bluestone terms. Year: 2026; collection: synthetic CSV. Version: 1.0.0. Review status: internally reviewed educational specification.
- Measurement period: 2026-01-01 through 2026-12-31, inclusive. Age is calculated on 2026-12-31. Eligible ages: 18 through 85 inclusive. One fictional encounter per patient must fall within the period. The hypertension condition flag must be true.
- Exclusions: explicit hospice=true. Unknown hospice, hypertension, date of birth, or encounter date produces unresolved eligibility, never an assumed exclusion. No exceptions. Eligibility is evaluated before documentation.
- Numerator: documentation status=completed AND observation date within period and no later than encounter date AND systolic 50..300 mmHg AND diastolic 30..200 mmHg AND systolic > diastolic AND units=mmHg. These ranges validate synthetic input, not treatment targets. No BP threshold defines control.
- Missing documentation: not_documented with no observation values is not met, categorized as missing_documentation. not_completed is not met, categorized as true_care_gap (a simulated unperformed assessment, not a treatment recommendation). patient_declined is not met with patient_preference barrier; decline is preserved, never automatically resolved. completed with missing/inconsistent observation fields is unresolved, categorized as data_pipeline_defect.
- Unknown eligibility is unresolved and outside the confirmed denominator; display it separately. Excluded records are outside the denominator. For eligible records, met, not_met, and unresolved documentation all remain in the denominator. Higher documentation completeness is better; this rule is NOT an inverse glycemic measure. Future inverse rules must declare lower_is_better and use a separate validated specification.
- Fixed supplied demonstration: exactly 100 fictional, eligible patients; 60 met, 15 not_documented, 10 not_completed, 5 patient_declined, 10 completed with missing fields. Thus baseline 60/100. Resolving the 15 documentation-only records produces 75/100, +15 percentage points. The demonstration does not claim measured clinical improvement.
- Workflow edits append immutable events over original imported data. Resolution requires role, owner, evidence, date, and provenance (documentation_completion, data_repair, simulated_care_event). Changes may not remove or rewrite original records. A decline cannot become completed through this workflow. Documentation completion cannot be used for not_completed; a simulated care event is required. Data repairs must repair pipeline defects. Eligibility edits are not supported by the point-of-care form.
- Freeze stores source rows, effective records, rule specification, result explanations, event IDs, reconciliation, equity aggregates, and SHA-256 digest. Sign-off records a separate reviewer identity and role; any unresolved calculation or ingestion errors block approval. A signed snapshot stays immutable when live records change. Internal CSV/JSON exports are never CMS-ready submissions.
- Equity: stratify by facility setting or access barrier; count all source patients, confirmed eligible denominator, numerator, missing documentation, and unresolved. Suppress all clinical counts and rate when a stratum has fewer than 11 patients. Also suppress aggregate views when any small cell exists to limit complementary disclosure. Identified operational screens are separate from the aggregate equity display. Not a formal privacy guarantee.

## External context, not executable specifications

CMS publishes performance-year and collection-specific guidance. Review the current official pages and linked 2026 materials before any real implementation:

- https://www.cms.gov/medicare/payment/fee-for-service-providers/shared-savings-program-ssp-acos/quality-measurement-reporting
- https://www.cms.gov/priorities/innovation/innovation-models/lead

Names such as Controlling High Blood Pressure and Diabetes: Glycemic Status Assessment Greater Than 9% do not specify eligibility, value sets, exclusions, or calculation. The latter is inverse, unlike a higher-is-better control measure. No real CMS logic is implemented. LEAD is a separate, disabled program configuration, not an MSSP alias. No commercial payer terms, savings calculations, FHIR interoperability claims, or medication recommendations are provided.
# Stakeholder RACI

R = Responsible, A = Accountable, C = Consulted, I = Informed. Roles are simulated application roles, not real organizational assignments.

| Activity | Provider | Clinical Assistant | ACO Operations | EHR/IT |
| --- | --- | --- | --- | --- |
| Approve educational clinical workflow assumptions | A | C | R | C |
| Maintain versioned measure specification | C | C | A/R | C |
| Validate source extract and import exceptions | I | C | A/R | R |
| Complete missing assessment documentation | A | R | I | I |
| Conduct simulated care-event follow-up | A/R | C | I | I |
| Investigate and repair pipeline defect | C | I | A | R |
| Review eligibility question | C | I | A/R | C |
| Assign follow-up owner, role, deadline, and barrier | C | C | A/R | C |
| Preserve and respect patient decline | A/R | R | I | I |
| Reconcile and freeze reporting package | C | I | A/R | C |
| Independently review and sign off package | C | I | A/R (distinct reviewer) | C |
| Review suppressed equity summaries | C | C | A/R | I |

The product enforces selected boundaries (for example, only ACO Operations can assign work and a separate ACO Operations identity must sign off). It does not provide production identity verification or prove that entered roles correspond to real staff.
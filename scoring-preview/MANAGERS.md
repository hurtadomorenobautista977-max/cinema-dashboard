# Cinema manager profiles

The shared dashboard displays cinema and manager rankings separately on one page. Navigation groups profile, assessment and model management into two accordions. User account administration remains independent of personnel profiles.

Manager source data is loaded only after authorization from `cinema_manager_source_models`. The imported Word document has 17 checklist tables and 67 rows. Both similarly titled audience-service tables are preserved independently. All question text, methods, rubrics, paragraphs and source table cells are preserved; see `manager-source-audit.json`. Basic and professional history fields mirror the first document section, with repeatable career/course details. No numerical education/experience rubric is invented where the document provides none.

`cinema_manager_profiles` stores current identity/details and cinema assignment. `cinema_manager_assessments` stores versioned assessments, the cinema, manager/profile snapshot, immutable model snapshot, responses and computed results. One assessment per manager/model version follows the existing cinema workflow. Editing a draft/final record uses an optimistic timestamp guard. Model overrides and history use the existing owner-controlled override table under the independent `manager-condition-v1` model ID.

Scoring uses the same `CinemaScoring` engine and `CinemaSchemaUI` editor as cinemas: weighted row → parameter → axis → manager averages, quarter-step scores, exclusions with reasons, row conditions, scoped alerts/caps and completeness requirements. Four source performance axes, 17 parameters and 67 scored questions are imported with equal initial sibling weights. Personal information has no score. Manager results never enter cinema scores.

Registration saves the profile then opens the assessment dialog immediately. Closing the initial dialog leaves the profile intact. The evaluation wizard supports manager selection, axis progress, parameter navigation, evidence, draft/final saving, guarded exit and copying responses from an earlier model version.

Validation completed:
- Byte-for-text comparison of all source table cells and paragraphs against the supplied DOCX.
- DOM integration using mocked data: shared dashboard, two accordions, profile creation, optional exit, all 67 answers scored 4 yielding 4, final saving, evidence display, independent ranking and model version history.
- Authenticated database create/update/read and unauthorized read-isolation checks in a transaction rolled back after assertions. No test manager/profile/assessment retained.
- RLS enabled and grants scoped to existing authorized dashboard administrators. No public reads for personal profiles, assessments or source models.

The source payload is intentionally not bundled as a publicly served static asset. It is retained in the authenticated source-model table, and snapshots remain in the database. The original DOCX remains the authoritative imported reference.

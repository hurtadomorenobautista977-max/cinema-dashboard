# Database access grants

The linked Supabase project is bahman (ccjykdpjprjaocglypij).
The migration explicit_dashboard_data_api_grants was applied on 2026-10-22.

After creating public.admin_users, public.cinemas, public.app_config and
public.cinemas_id_seq, and restoring the existing RLS policies, run
explicit_data_api_grants.sql as the database owner. It is safe to rerun.
When writing future CREATE TABLE migrations, include the required explicit
GRANT statements alongside the table and RLS policies.

Access model:
- authenticated: SELECT admin_users (own membership through RLS);
  CRUD cinemas/app_config (admin membership required by RLS);
  USAGE/SELECT cinemas_id_seq.
- service_role: CRUD admin_users for the manage-dashboard-users Edge Function.
- anon: no table grants are added.

This folder is not a complete Supabase migration chain and is not
automatically executed by the static GitHub Pages deployment.
The original CREATE TABLE definitions for cinemas/app_config were not present
in this repository. Do not run db reset expecting this folder to reconstruct
the database. Preserve or recover the original schema and RLS migrations first.
This script does not replace RLS policies or change default privileges.
The other inactive Supabase project and bahmansabz runtime credentials were
not verified; no changes were made to those.

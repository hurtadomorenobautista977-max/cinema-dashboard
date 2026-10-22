-- Run after the table/sequence definitions and existing RLS policies.
-- Required by the authenticated dashboard and manage-dashboard-users.
-- No anonymous access is granted. Existing RLS policies remain in effect.
GRANT USAGE ON SCHEMA public TO authenticated, service_role;
GRANT SELECT ON TABLE public.admin_users TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.admin_users TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.cinemas, public.app_config TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE public.cinemas_id_seq TO authenticated;

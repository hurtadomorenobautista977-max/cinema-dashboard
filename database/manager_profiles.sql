create table public.cinema_manager_profiles (
 id uuid primary key default gen_random_uuid(), name text not null check(length(trim(name))>0),
 cinema_id integer references public.cinemas(id), details jsonb not null default '{}'::jsonb,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table public.cinema_manager_assessments (
 id uuid primary key default gen_random_uuid(), manager_id uuid not null references public.cinema_manager_profiles(id),
 cinema_id integer references public.cinemas(id), model_version integer not null,
 model_snapshot jsonb not null, responses jsonb not null default '{}'::jsonb,
 profile_snapshot jsonb not null default '{}'::jsonb, computed_results jsonb not null default '{}'::jsonb,
 status text not null check(status in ('draft','completed')), updated_by uuid references auth.users(id),
 updated_at timestamptz not null default now(), completed_at timestamptz,
 unique(manager_id,model_version)
);
create table public.cinema_manager_source_models(id text primary key,payload_base64 text not null);
alter table public.cinema_manager_profiles enable row level security;
alter table public.cinema_manager_assessments enable row level security;
alter table public.cinema_manager_source_models enable row level security;
create policy managers_read on public.cinema_manager_profiles for select to authenticated using (exists(select 1 from public.admin_users where user_id=(select auth.uid())));
create policy managers_insert on public.cinema_manager_profiles for insert to authenticated with check (exists(select 1 from public.admin_users where user_id=(select auth.uid())));
create policy managers_update on public.cinema_manager_profiles for update to authenticated using (exists(select 1 from public.admin_users where user_id=(select auth.uid()))) with check (exists(select 1 from public.admin_users where user_id=(select auth.uid())));
create policy manager_assessments_read on public.cinema_manager_assessments for select to authenticated using (exists(select 1 from public.admin_users where user_id=(select auth.uid())));
create policy manager_assessments_insert on public.cinema_manager_assessments for insert to authenticated with check (exists(select 1 from public.admin_users where user_id=(select auth.uid())));
create policy manager_assessments_update on public.cinema_manager_assessments for update to authenticated using (exists(select 1 from public.admin_users where user_id=(select auth.uid()))) with check (exists(select 1 from public.admin_users where user_id=(select auth.uid())));
create policy manager_source_read on public.cinema_manager_source_models for select to authenticated using (exists(select 1 from public.admin_users where user_id=(select auth.uid())));
grant select,insert,update on public.cinema_manager_profiles,public.cinema_manager_assessments to authenticated;
grant select on public.cinema_manager_source_models to authenticated;

-- Muster Out telemetry schema. Two insert only tables behind row level security with no policies,
-- so the anon and authenticated roles can neither read nor write them directly. All writes go
-- through the ingest edge function with the service role after validation and rate limiting.

create table if not exists public.lesson_responses (
  id bigint generated always as identity primary key,
  token text not null,
  nickname text,
  score integer,
  answers jsonb,
  reflection text,
  go_deeper boolean,
  sections_done integer,
  version text,
  ip_hash text,
  created_at timestamptz not null default now()
);
create index if not exists lesson_responses_token_idx on public.lesson_responses (token);
create index if not exists lesson_responses_created_idx on public.lesson_responses (created_at);

create table if not exists public.setup_pings (
  id bigint generated always as identity primary key,
  install_id text not null,
  service text not null,
  path text not null,
  grade text not null,
  version text not null,
  ip_hash text,
  created_at timestamptz not null default now()
);
create unique index if not exists setup_pings_install_idx on public.setup_pings (install_id);
create index if not exists setup_pings_created_idx on public.setup_pings (created_at);

create table if not exists public.ingest_rate (
  ip_hash text not null,
  minute timestamptz not null,
  n integer not null default 0,
  primary key (ip_hash, minute)
);

alter table public.lesson_responses enable row level security;
alter table public.setup_pings enable row level security;
alter table public.ingest_rate enable row level security;
revoke all on public.lesson_responses from anon, authenticated;
revoke all on public.setup_pings from anon, authenticated;
revoke all on public.ingest_rate from anon, authenticated;

-- Aggregates the maintainer reads in the dashboard.
create or replace view public.adoption as
  select date_trunc('week', created_at) as week, service, path, grade, count(*) as boards
  from public.setup_pings group by 1, 2, 3, 4 order by 1 desc;
create or replace view public.lesson_summary as
  select date_trunc('week', created_at) as week, count(*) as responses, round(avg(score), 1) as avg_score, count(distinct token) as people
  from public.lesson_responses group by 1 order by 1 desc;
revoke all on public.adoption from anon, authenticated;
revoke all on public.lesson_summary from anon, authenticated;

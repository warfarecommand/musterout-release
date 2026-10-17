-- SURVEY-B, authorized by TRS on 17 OCT 2026. No row writes or column changes.
-- One DO statement is atomic standalone and also fits APPLY.sql's transaction.
-- Only recommendation checks and the two existing function bodies change.
-- Refuses rollback if after_use rows exist. Preserve them and roll forward instead.
do $survey$
begin
  perform pg_advisory_xact_lock(731903, 17);
  if to_regclass('public.telemetry_recommend') is null
    or to_regprocedure('public.telemetry_record_ok(jsonb)') is null
    or to_regprocedure('public.telemetry_report(text,text,text)') is null then
    raise exception 'SURVEY-B requires the applied telemetry v2 schema';
  end if;
  lock table public.telemetry_recommend in access exclusive mode;
  if exists (select 1 from public.telemetry_recommend where context = 'after_use') then
    raise exception 'SURVEY-B rollback refused: preserve existing after_use rows; roll forward or wait for normal retention';
  end if;
  if (select md5(prosrc) from pg_proc where oid = 'public.telemetry_record_ok(jsonb)'::regprocedure) <> '6dd105e6bf4dea7e1e70676b83ed4bd8'
    or (select md5(prosrc) from pg_proc where oid = 'public.telemetry_report(text,text,text)'::regprocedure) <> '36d02b4938795ab6009396da8ce34fef' then
    raise exception 'SURVEY-B rollback requires the exact reviewed survey functions; stop and review';
  end if;
  if (select count(*) from pg_constraint where conrelid = 'public.telemetry_recommend'::regclass
      and conname in ('telemetry_recommend_context_check', 'telemetry_recommend_check') and contype = 'c' and convalidated) <> 2 then
    raise exception 'SURVEY-B expected validated recommendation constraints are missing';
  end if;
  alter table public.telemetry_recommend
    drop constraint telemetry_recommend_context_check,
    drop constraint telemetry_recommend_check,
    add constraint telemetry_recommend_context_check check (context in ('setup', 'week4')),
    add constraint telemetry_recommend_check check ((context = 'setup' and week_index = 0) or (context = 'week4' and week_index between 4 and 104));
  execute $survey_record_ddl$
create or replace function public.telemetry_record_ok(r jsonb) returns boolean
language plpgsql immutable set search_path = pg_catalog, pg_temp as $$
declare
  common constant text[] := array['schema_version', 'kind', 'product', 'record_id', 'install_id', 'version'];
  steps constant text[] := array['consent', 'release_verified', 'published', 'intake_confirmed', 'plan_verified', 'record_requested'];
  kind text;
  e jsonb;
  pos integer;
  last_pos integer := 0;
  n integer;
begin
  if jsonb_typeof(r) is distinct from 'object' then return false; end if;
  if not (public.telemetry_int_ok(r -> 'schema_version', 2, 2)
      and public.telemetry_str_ok(r -> 'product', '^musterout$')
      and public.telemetry_str_ok(r -> 'record_id', '^[a-f0-9]{32}$')
      and public.telemetry_str_ok(r -> 'install_id', '^[a-f0-9]{16,32}$')
      and public.telemetry_str_ok(r -> 'version', '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$')
      and public.telemetry_enum_ok(r -> 'kind', array['install', 'usage', 'outcome', 'hosted_demand', 'recommend'])) then
    return false;
  end if;
  if char_length(r ->> 'version') > 32 then return false; end if;
  kind := r ->> 'kind';

  if kind = 'install' then
    if not public.telemetry_keys_ok(r, common || array['channel', 'device', 'surface', 'status', 'path', 'grade',
        'eas_month', 'base', 'steps_completed', 'failed_step', 'error_class', 'consent_schema']) then
      return false;
    end if;
    if not (public.telemetry_enum_ok(r -> 'channel', array['chat', 'laptop'])
        and public.telemetry_enum_ok(r -> 'device', array['iphone', 'ipad', 'android', 'desktop', 'other', 'unknown'])
        and public.telemetry_enum_ok(r -> 'surface', array['web', 'ios_app', 'android_app', 'desktop_app', 'code', 'unknown'])
        and public.telemetry_enum_ok(r -> 'status', array['in_progress', 'failed', 'complete'])
        and (jsonb_typeof(r -> 'path') = 'null' or public.telemetry_enum_ok(r -> 'path', array['eas', 'resign', 'retire']))
        and (jsonb_typeof(r -> 'grade') = 'null' or public.telemetry_enum_ok(r -> 'grade', array['e15', 'e67', 'e89', 'o14', 'o5', 'wo13', 'cwo45']))
        and (jsonb_typeof(r -> 'eas_month') = 'null' or public.telemetry_str_ok(r -> 'eas_month', '^[0-9]{4}-(0[1-9]|1[0-2])$'))
        and (jsonb_typeof(r -> 'base') = 'null' or public.telemetry_enum_ok(r -> 'base', array['us_west', 'us_central', 'us_east',
             'hawaii', 'japan', 'other_overseas', 'other_us', 'not_on_installation']))
        and (jsonb_typeof(r -> 'failed_step') = 'null' or public.telemetry_enum_ok(r -> 'failed_step', array['release_verified',
             'published', 'intake_confirmed', 'plan_verified', 'record_requested']))
        and public.telemetry_enum_ok(r -> 'error_class', array['none', 'network', 'unavailable', 'permission', 'validation',
             'save', 'verify', 'rate_limited', 'other'])
        and public.telemetry_str_ok(r -> 'consent_schema', '^tel1-v2$')) then
      return false;
    end if;
    -- Distinct steps in canonical order, starting with consent (no consent, no keyed record).
    if jsonb_typeof(r -> 'steps_completed') <> 'array' then return false; end if;
    n := jsonb_array_length(r -> 'steps_completed');
    if n < 1 or n > 6 then return false; end if;
    for e in select t.value from jsonb_array_elements(r -> 'steps_completed') with ordinality as t(value, ord) order by t.ord loop
      if jsonb_typeof(e) <> 'string' then return false; end if;
      pos := array_position(steps, e #>> '{}');
      if pos is null or pos <= last_pos then return false; end if;
      last_pos := pos;
    end loop;
    if (r -> 'steps_completed' ->> 0) <> 'consent' then return false; end if;
    if r ->> 'status' = 'complete' then
      return n = 6 and jsonb_typeof(r -> 'path') <> 'null' and jsonb_typeof(r -> 'grade') <> 'null'
        and jsonb_typeof(r -> 'base') <> 'null' and jsonb_typeof(r -> 'failed_step') = 'null' and r ->> 'error_class' = 'none';
    elsif r ->> 'status' = 'failed' then
      return jsonb_typeof(r -> 'failed_step') <> 'null';
    end if;
    return jsonb_typeof(r -> 'failed_step') = 'null';

  elsif kind = 'usage' then
    if not (public.telemetry_keys_ok(r, common || array['trigger', 'weeks_active', 'late_count', 'buckets'])
        and public.telemetry_enum_ok(r -> 'trigger', array['update', 'weekly'])
        and public.telemetry_int_ok(r -> 'weeks_active', 0, 105)
        and public.telemetry_int_ok(r -> 'late_count', 0, 10000)) then
      return false;
    end if;
    if jsonb_typeof(r -> 'buckets') <> 'array' or jsonb_array_length(r -> 'buckets') > 26 then return false; end if;
    for e in select t.value from jsonb_array_elements(r -> 'buckets') t loop
      if not public.telemetry_bucket_ok(e) then return false; end if;
    end loop;
    return (select count(distinct t.value ->> 'bucket_id') from jsonb_array_elements(r -> 'buckets') t)
      = jsonb_array_length(r -> 'buckets');

  elsif kind = 'outcome' then
    return public.telemetry_keys_ok(r, common || array['week_index', 'trs_done', 'skillbridge', 'va_claim_before_separation',
        'separation_counseling_done'])
      and public.telemetry_int_ok(r -> 'week_index', 0, 104)
      and jsonb_typeof(r -> 'trs_done') in ('boolean', 'null')
      and jsonb_typeof(r -> 'skillbridge') in ('boolean', 'null')
      and jsonb_typeof(r -> 'va_claim_before_separation') in ('boolean', 'null')
      and jsonb_typeof(r -> 'separation_counseling_done') in ('boolean', 'null');

  elsif kind = 'hosted_demand' then
    return public.telemetry_keys_ok(r, common || array['week_index', 'would_use', 'pay_monthly'])
      and public.telemetry_int_ok(r -> 'week_index', 4, 104)
      and public.telemetry_enum_ok(r -> 'would_use', array['yes', 'no', 'unsure'])
      and public.telemetry_enum_ok(r -> 'pay_monthly', array['zero', 'under_5', '5_to_9', '10_to_19', '20_to_29', '30_or_more', 'unsure']);
  end if;

  -- recommend
  return public.telemetry_keys_ok(r, common || array['context', 'week_index', 'score'])
    and public.telemetry_int_ok(r -> 'score', 0, 10)
    and ((public.telemetry_enum_ok(r -> 'context', array['setup']) and public.telemetry_int_ok(r -> 'week_index', 0, 0))
      or (public.telemetry_enum_ok(r -> 'context', array['week4']) and public.telemetry_int_ok(r -> 'week_index', 4, 104)));
end $$;
$survey_record_ddl$;
  execute $survey_report_ddl$
create or replace function public.telemetry_report(p_metric text, p_dimension text, p_period text)
returns table (dimension_value text, cell text, value bigint)
language plpgsql stable security definer set search_path = pg_catalog, pg_temp as $$
declare
  v_floor constant integer := 10;
  v_now timestamptz := statement_timestamp();
  v_start timestamptz;
  v_end timestamptz;
  v_cells text[];
  v_dims text[];
  v_week integer;
  v_y integer;
  v_w integer;
  v_d date;
  v_n bigint;
begin
  if p_metric is null or p_dimension is null or p_period is null
    or p_metric not in ('installs', 'weekly_active', 'retention_w1', 'retention_w4', 'outcome_trs_done',
      'outcome_skillbridge', 'outcome_va_claim_before_separation', 'outcome_separation_counseling_done',
      'demand_would_use', 'demand_pay_monthly', 'recommend_setup', 'recommend_week4', 'failures', 'setup_taps')
    or p_dimension not in ('none', 'base', 'grade', 'path', 'eas_month')
    or (p_metric in ('failures', 'setup_taps') and p_dimension <> 'none') then
    raise exception 'Invalid report request' using errcode = '22023';
  end if;

  if p_metric in ('installs', 'retention_w1', 'retention_w4', 'setup_taps') then
    if p_period !~ '^[0-9]{4}-(0[1-9]|1[0-2])$' then raise exception 'Invalid report period' using errcode = '22023'; end if;
    v_d := to_date(p_period || '-01', 'YYYY-MM-DD');
    v_start := v_d::timestamp at time zone 'UTC';
    v_end := (v_d + interval '1 month') at time zone 'UTC';
    if v_end > v_now then raise exception 'Report period is not complete' using errcode = '22023'; end if;
    if (p_metric = 'retention_w1' and v_now < v_end + interval '168 hours')
      or (p_metric = 'retention_w4' and v_now < v_end + interval '672 hours') then
      return query select null::text, 'insufficient_cohort'::text, null::bigint;
      return;
    end if;
  elsif p_metric = 'weekly_active' then
    if p_period !~ '^[0-9]{4}-W(0[1-9]|[1-4][0-9]|5[0-3])$' then raise exception 'Invalid report period' using errcode = '22023'; end if;
    v_y := substring(p_period from 1 for 4)::integer;
    v_w := substring(p_period from 7 for 2)::integer;
    if v_w > to_char(make_date(v_y, 12, 28), 'IW')::integer then raise exception 'Invalid report period' using errcode = '22023'; end if;
    v_d := make_date(v_y, 1, 4) - (extract(isodow from make_date(v_y, 1, 4))::integer - 1) + (v_w - 1) * 7;
    v_start := v_d::timestamp at time zone 'UTC';
    v_end := (v_d + 7)::timestamp at time zone 'UTC';
    if v_end > v_now then raise exception 'Report period is not complete' using errcode = '22023'; end if;
  elsif p_period <> 'retained' then
    raise exception 'Invalid report period' using errcode = '22023';
  end if;

  v_cells := case
    when p_metric = 'installs' then array['installs']
    when p_metric = 'weekly_active' then array['active']
    when p_metric in ('retention_w1', 'retention_w4') then array['active', 'not_active']
    when p_metric like 'outcome%' then array['yes', 'no', 'unknown']
    when p_metric = 'demand_would_use' then array['yes', 'no', 'unsure']
    when p_metric = 'demand_pay_monthly' then array['zero', 'under_5', '5_to_9', '10_to_19', '20_to_29', '30_or_more', 'unsure']
    when p_metric like 'recommend%' then array['0-6', '7-8', '9-10']
    when p_metric = 'failures' then array['release_verified', 'published', 'intake_confirmed', 'plan_verified', 'record_requested']
    else array['taps'] end;
  -- EAS months have no fixed domain; their cells come from observed values.
  v_dims := case p_dimension
    when 'none' then array['all']
    when 'base' then array['us_west', 'us_central', 'us_east', 'hawaii', 'japan', 'other_overseas', 'other_us', 'not_on_installation']
    when 'grade' then array['e15', 'e67', 'e89', 'o14', 'o5', 'wo13', 'cwo45']
    when 'path' then array['eas', 'resign', 'retire']
    else null end;
  v_week := case p_metric when 'retention_w1' then 0 else 3 end;

  if p_metric = 'setup_taps' then
    -- Anonymous taps: a global context count only, beside 10 or more completed installs that month.
    select count(*) into v_n
      from public.install_registrations r join public.telemetry_admissions a on a.install_id = r.install_id
      where r.schema_version = 2 and a.class = 'established' and not a.revoked and not a.quarantined
        and a.completed_at >= v_start and a.completed_at < v_end;
    if v_n < v_floor then
      return query select null::text, 'insufficient_cohort'::text, null::bigint;
      return;
    end if;
    return query select 'all'::text, 'taps'::text, count(*)
      from public.setup_intents s where s.created_at >= v_start and s.created_at < v_end;
    return;
  end if;

  if p_metric = 'failures' then
    return query
    -- R1a-8. The same population as every other report: completed v2
    -- registrations whose admission is established, not revoked, not
    -- quarantined. A failure from a still pending install is not counted.
    with f as (
      select distinct e.install_id, e.failed_step as k_cell
      from public.telemetry_install_events e
        join public.telemetry_admissions a on a.install_id = e.install_id
        join public.install_registrations r on r.install_id = e.install_id
      where e.status = 'failed' and r.schema_version = 2 and a.class = 'established'
        and not a.revoked and not a.quarantined
    ), counted as (
      select c.k_cell, count(distinct f.install_id) as k_n
      from unnest(v_cells) as c(k_cell) left join f on f.k_cell = c.k_cell
      group by c.k_cell
    ), verdict as (
      select coalesce(bool_and(k_n >= v_floor), false) as ok from counted
    )
    select 'all'::text, c.k_cell, c.k_n from counted c, verdict v where v.ok
    union all
    select null::text, 'insufficient_cohort'::text, null::bigint from verdict v where not v.ok
    order by 1, 2;
    return;
  end if;

  return query
  with pop as (
    select r.install_id, a.completed_at,
      case p_dimension when 'none' then 'all' when 'base' then r.base when 'grade' then r.grade
        when 'path' then r.path else coalesce(r.eas_month, 'not_set') end as k_dim
    from public.install_registrations r join public.telemetry_admissions a on a.install_id = r.install_id
    where r.schema_version = 2 and a.class = 'established' and not a.revoked and not a.quarantined
  ), facts as (
    select p.install_id, p.k_dim, 'installs'::text as k_cell
      from pop p where p_metric = 'installs' and p.completed_at >= v_start and p.completed_at < v_end
    union all
    select p.install_id, p.k_dim,
        case when exists (select 1 from public.telemetry_usage_buckets b where b.install_id = p.install_id
          and b.week_index = v_week and (b.counters ->> 'opens')::integer > 0) then 'active' else 'not_active' end
      from pop p where p_metric in ('retention_w1', 'retention_w4') and p.completed_at >= v_start and p.completed_at < v_end
    union all
    select p.install_id, p.k_dim, 'active'
      from pop p where p_metric = 'weekly_active' and p.completed_at < v_end
        and exists (select 1 from public.telemetry_chat_runs c where c.install_id = p.install_id
          and c.received_at >= v_start and c.received_at < v_end)
    union all
    select p.install_id, p.k_dim, case when o.answer is null then 'unknown' when o.answer then 'yes' else 'no' end
      from pop p cross join lateral (
        select case p_metric when 'outcome_trs_done' then x.trs_done when 'outcome_skillbridge' then x.skillbridge
          when 'outcome_va_claim_before_separation' then x.va_claim_before_separation
          else x.separation_counseling_done end as answer
        from public.telemetry_outcomes x where x.install_id = p.install_id
        order by x.received_at desc, x.record_id desc limit 1) o
      where p_metric like 'outcome%'
    union all
    select p.install_id, p.k_dim, case when p_metric = 'demand_would_use' then h.would_use else h.pay_monthly end
      from pop p cross join lateral (
        select x.would_use, x.pay_monthly from public.telemetry_hosted_demand x where x.install_id = p.install_id
        order by x.received_at desc, x.record_id desc limit 1) h
      where p_metric like 'demand%'
    union all
    select p.install_id, p.k_dim, case when s.score <= 6 then '0-6' when s.score <= 8 then '7-8' else '9-10' end
      from pop p cross join lateral (
        select x.score from public.telemetry_recommend x where x.install_id = p.install_id
          and x.context = case p_metric when 'recommend_setup' then 'setup' else 'week4' end
        order by x.received_at desc, x.record_id desc limit 1) s
      where p_metric like 'recommend%'
  ), dims as (
    select d as k_dim from unnest(v_dims) d
    union
    select distinct f.k_dim from facts f where v_dims is null
  ), counted as (
    select d.k_dim, c.k_cell, count(distinct f.install_id) as k_n
    from dims d cross join unnest(v_cells) as c(k_cell)
    left join facts f on f.k_dim = d.k_dim and f.k_cell = c.k_cell
    group by d.k_dim, c.k_cell
  ), verdict as (
    select coalesce(bool_and(k_n >= v_floor), false) as ok from counted
  )
  select c.k_dim, c.k_cell, c.k_n from counted c, verdict v where v.ok
  union all
  select null::text, 'insufficient_cohort'::text, null::bigint from verdict v where not v.ok
  order by 1, 2;
end $$;
$survey_report_ddl$;
end $survey$;

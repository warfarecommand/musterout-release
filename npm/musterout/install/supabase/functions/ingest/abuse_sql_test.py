#!/usr/bin/env python3
"""Disposable local PostgreSQL check. Never uses a configured/live database."""
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
SQL = ROOT / '_cook/overhaul/build/sql/learn_tables.sql'
BIN = Path('/opt/homebrew/opt/postgresql@17/bin')
if not (BIN / 'initdb').exists():
    raise SystemExit('Local PostgreSQL 17 required; no live fallback')
with tempfile.TemporaryDirectory(prefix='.abuse-sql-', dir=Path(__file__).parent) as raw:
    work = Path(raw)
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    env = {**os.environ, 'PGHOST': str(work), 'PGPORT': str(port), 'PGDATABASE': 'postgres'}
    for key in ('PGSERVICE', 'PGSERVICEFILE', 'PGPASSWORD', 'PGPASSFILE', 'PGOPTIONS'):
        env.pop(key, None)
    def run(args, **kwargs):
        return subprocess.run(args, env=env, text=True, capture_output=True, **kwargs)
    def query(text, success=True):
        result = run([str(BIN/'psql'), '-X', '-q', '-v', 'ON_ERROR_STOP=1', '-At', '-c', text])
        if (result.returncode == 0) != success:
            raise AssertionError(result.stderr[:1500] + result.stdout[:1000])
        return result.stdout.strip()
    initialized = run([str(BIN/'initdb'), '-D', str(work/'data'), '-A', 'trust', '--no-locale', '--encoding=UTF8'])
    assert initialized.returncode == 0, initialized.stderr
    started = run([str(BIN/'pg_ctl'), '-D', str(work/'data'), '-l', str(work/'postgres.log'), '-o', f'-k {work} -p {port} -h 127.0.0.1', '-w', 'start'])
    assert started.returncode == 0, started.stderr
    try:
        query('create role anon; create role authenticated; create role service_role bypassrls; grant usage on schema public to anon, authenticated, service_role;')
        query('create table public.ingest_rate (ip_hash text, minute timestamptz, n integer, primary key(ip_hash,minute)); grant all on public.ingest_rate to service_role;')
        for table in ['alert_signups','setup_intents','install_registrations','suggestions','email_delivery_receipts']:
            query(f'create table public.{table}(created_at timestamptz, last_sent_at timestamptz, status text);')
        rate = ROOT / 'supabase/migrations/20261010040000_ingest_rate_hit.sql'
        query(rate.read_text())
        query(SQL.read_text())
        query(SQL.read_text())
        assert query("select count(*) from pg_policies where schemaname='public' and tablename in ('feedback_reports','usage_weeks')") == '0'
        assert query("select count(*) from pg_class where relname in ('feedback_reports','usage_weeks') and relrowsecurity") == '2'
        for role in ['anon','authenticated']:
            for table in ['feedback_reports','usage_weeks']:
                query(f'set role {role}; select * from public.{table};', success=False)
                query(f"set role {role}; delete from public.{table};", success=False)
        assert query("select public.learn_version_ok('1.2.3-rc.1+build.01'), public.learn_version_ok('1.2.3-01'), public.learn_week_ok('2026-W53'), public.learn_week_ok('2025-W53')") == 't|f|t|f'
        for bad in ['{}','[]','null','{"secret":1}','{"opens":-1}','{"opens":1.1}','{"opens":10001}','{"opens":"1"}','{"opens":true}']:
            assert query(f"select coalesce(public.learn_counters_ok('{bad}'::jsonb),false)") == 'f'
        assert query("select public.learn_counters_ok('{\"opens\":10000,\"errors_other\":0}'::jsonb)") == 't'
        good="insert into public.feedback_reports (id,install_id,version,pack,path,grade,category,error_class,text,created) values ('report_1234','0123456789abcdef','0.2.2','usmc-2026.10','eas','e67','bug','save','Synthetic',now())"
        query('set role service_role; '+good)
        query(good, success=False)
        for changed in [good.replace('report_1234','short'),good.replace('report_1234','report_oversize').replace("'Synthetic'", "repeat('a',1001)"),good.replace('report_1234','report_bad_enum').replace("'bug'", "'wrong'"),good.replace('report_1234','report_control').replace("'Synthetic'", "chr(10)"),good.replace('report_1234','report_bad_version').replace('0.2.2','v0.2.2')]:
            query(changed,success=False)
        usage="insert into public.usage_weeks(install_id,week,writer,version,counters) values ('0123456789abcdef','2026-W41','aaaaaaaaaaaaaaaa','0.2.2','{\"opens\":3}')"
        query('set role service_role; '+usage)
        query(usage,success=False)
        query(usage.replace('aaaaaaaaaaaaaaaa','bbbbbbbbbbbbbbbb'))
        query(usage.replace('aaaaaaaaaaaaaaaa','cccccccccccccccc').replace('2026-W41','2025-W53'),success=False)
        query("update public.feedback_reports set received = now() - interval '181 days'; update public.usage_weeks set received = case when writer like 'a%' then now()-interval '181 days' else now()-interval '179 days' end")
        dry=query("select table_name||':'||row_count from public.cleanup_retained_data(true) where table_name in ('feedback_reports','usage_weeks')")
        assert dry == 'feedback_reports:1\nusage_weeks:1', dry
        assert query('select count(*) from public.feedback_reports') == '1'
        query('select * from public.cleanup_retained_data(false)')
        assert query('select count(*) from public.feedback_reports') == '0'
        assert query('select count(*) from public.usage_weeks') == '1'
        query('select * from public.cleanup_retained_data(null)',success=False)
        assert query("set role service_role; select public.ingest_rate_hit('learn:feedback:synthetic',date_trunc('minute',now()))") == '1'
        abuse = ROOT / '_cook/overhaul/build/sql/abuse_budget.sql'
        query(abuse.read_text())
        query(abuse.read_text())
        for role in ['anon', 'authenticated']:
            for table in ['learn_abuse_budgets', 'learn_install_cohorts']:
                query(f'set role {role}; select * from public.{table}', success=False)
            query(f"set role {role}; select public.learn_abuse_admit('usage',repeat('a',24),repeat('a',16),0)", success=False)
        def reset():
            query('truncate public.learn_abuse_budgets, public.learn_install_cohorts, public.feedback_reports, public.usage_weeks')
        def hit(kind, ip=1, install=1, units=0):
            return query(f"set role service_role; select public.learn_abuse_admit('{kind}',lpad(to_hex({ip}),24,'0'),lpad(to_hex({install}),16,'0'),{units})")
        def admitted(result):
            import json
            return json.loads(result)['admitted']
        reset()
        for i in range(1, 11):
            assert admitted(hit('feedback', install=i))
            query(f"insert into public.feedback_reports(id,install_id,version,pack,path,grade,category,error_class,created) values ('cohort_{i:08}',lpad(to_hex({i}),16,'0'),'0.2.2','usmc-2026.10','eas','e67','bug','save',now())")
            assert admitted(hit('usage', install=i))
        assert query('select count(*) from public.learn_install_cohorts where quarantined') == '10'
        assert query('select count(*) from public.feedback_reports f join public.learn_install_cohorts c using(install_id) where not c.quarantined') == '0'
        query("update public.learn_install_cohorts set first_seen=now()-interval '2 hours'")
        assert admitted(hit('usage', install=11))
        assert query("select quarantined from public.learn_install_cohorts where install_id=lpad(to_hex(11),16,'0')") == 'f'
        first = query("select ip_hash||':'||first_seen from public.learn_install_cohorts where install_id=lpad(to_hex(11),16,'0')")
        assert admitted(hit('feedback', ip=20, install=11))
        assert first == query("select ip_hash||':'||first_seen from public.learn_install_cohorts where install_id=lpad(to_hex(11),16,'0')")
        # Exact boundary: the first five IDs are eligible; sixth quarantines all six.
        reset()
        for i in range(1, 6): assert admitted(hit('usage', install=i))
        assert query('select count(*) from public.learn_install_cohorts where quarantined') == '0'
        assert admitted(hit('feedback', install=6))
        assert query('select count(*) from public.learn_install_cohorts where quarantined') == '6'
        for kind, ip_cap, cap, total in [('feedback',20,90,201),('usage',100,2000,5001)]:
            reset()
            for i in range(ip_cap): assert admitted(hit(kind))
            assert not admitted(hit(kind))
            assert query("select overflow from public.learn_abuse_budgets where scope='global'") == '1'
            reset()
            # One database statement exercises every distributed overflow call.
            out = query(f"select count(*) filter (where (r->>'admitted')::boolean), count(*) filter (where not (r->>'admitted')::boolean) from (select public.learn_abuse_admit('{kind}',lpad(to_hex(n),24,'0'),lpad(to_hex(n),16,'0'),0) r from generate_series(1,{total}) n) x")
            assert out == f'{cap}|{total-cap}', out
            assert query('select count(*) from public.learn_abuse_budgets') == str(cap + 1)
            assert query("select accepted||':'||overflow from public.learn_abuse_budgets where scope='global'") == f'{cap}:{total-cap}'
            # Prior week's filled bucket cannot block the new server week.
            query("update public.learn_abuse_budgets set week=week-interval '7 days'")
            assert admitted(hit(kind, ip=99999))
        reset()
        for i in range(8): assert admitted(hit('feedback',ip=i+1,units=12002))
        assert not admitted(hit('feedback',ip=9,units=12002))
        assert query('select count(*) from public.learn_abuse_budgets') == '9'
        assert admitted(hit('feedback',ip=10,units=3984))
        assert not admitted(hit('feedback',ip=11,units=1))
        assert query("select text_units from public.learn_abuse_budgets where scope='global'") == '100000'
        for args in ["null,repeat('a',24),repeat('a',16),0", "'other',repeat('a',24),repeat('a',16),0", "'usage','raw-ip',repeat('a',16),0", "'usage',repeat('a',24),'bad',0", "'usage',repeat('a',24),repeat('a',16),1", "'feedback',repeat('a',24),repeat('a',16),-1", "'feedback',repeat('a',24),repeat('a',16),12003"]:
            query(f'select public.learn_abuse_admit({args})', success=False)
        # Concurrent calls across different IPs cannot overshoot a global ceiling.
        reset()
        query("insert into public.learn_abuse_budgets(week,kind,scope,accepted) values (date_trunc('week',now() at time zone 'UTC') at time zone 'UTC','feedback','global',89)")
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=8) as pool:
            outcomes = list(pool.map(lambda i: admitted(hit('feedback',ip=i+1,install=i+1)),range(16)))
        assert sum(outcomes) == 1, outcomes
        assert query("select accepted||':'||overflow from public.learn_abuse_budgets where scope='global'") == '90:15'
        reset()
        hit('usage')
        query("update public.learn_install_cohorts set first_seen=now()-interval '181 days'; update public.learn_abuse_budgets set week=now()-interval '181 days'")
        assert query("select table_name||':'||row_count from public.cleanup_retained_data(true) where table_name like 'learn_%'") == 'learn_install_cohorts:1\nlearn_abuse_budgets:2'
        query('select * from public.cleanup_retained_data(false)')
        assert query('select count(*) from public.learn_install_cohorts') == '0'
        assert query('select count(*) from public.learn_abuse_budgets') == '0'
        # A27: query the admitted source rows through the real agent query, then
        # render a complete brief with safe aggregates and the actual overflow.
        import datetime as dt
        import importlib.util
        import json
        import sys
        from unittest.mock import patch
        agent_path = Path.home() / 'dev/personal-agents/17_WC_Learn/learn.py'
        spec = importlib.util.spec_from_file_location('d2_learn', agent_path)
        agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent)
        reset()
        query("with admissions as materialized (select n, public.learn_abuse_admit('feedback',lpad(to_hex(n),24,'0'),lpad(to_hex(n),16,'0'),11) r from generate_series(1,201) n) insert into public.feedback_reports(id,install_id,version,pack,path,grade,category,error_class,text,created) select 'volume_'||lpad(n::text,8,'0'),lpad(to_hex(n),16,'0'),'0.2.2','usmc-2026.10','eas','e67','bug','save','Synthetic',now() from admissions where (r->>'admitted')::boolean")
        query("with admissions as materialized (select n, public.learn_abuse_admit('usage',lpad(to_hex(n),24,'0'),lpad(to_hex(n),16,'0'),0) r from generate_series(1,5001) n) insert into public.usage_weeks(install_id,week,writer,version,counters) select lpad(to_hex(n),16,'0'),'2026-W41',repeat('a',16),'0.2.2','{\"opens\":3}' from admissions where (r->>'admitted')::boolean")
        stamp = dt.datetime.now(dt.timezone.utc)
        start, end = stamp - dt.timedelta(days=1), stamp + dt.timedelta(days=6)
        def local_rows(sql):
            return json.loads(query('select coalesce(json_agg(t),\'[]\'::json) from (' + sql + ') t'))
        feedback_rows = local_rows(agent.sql_for('feedback_reports',start,end))
        usage_rows = local_rows(agent.sql_for('usage_weeks',start,end))
        assert len(feedback_rows) == 90 and len(usage_rows) == 2000
        agent.validate_rows(feedback_rows,'feedback_reports')
        agent.validate_rows(usage_rows,'usage_weeks')
        cells = agent.aggregates(feedback_rows,usage_rows)
        refs, prompt = agent.model_inputs(feedback_rows)
        assert len(refs) == 90 and len(prompt.encode()) < agent.MAX_PROMPT_BYTES
        clusters = agent.validated_clusters({'clusters':[{'topic':'other','members':list(refs)}]},refs)
        with patch.object(agent,'query',side_effect=local_rows):
            brief, proposals = agent.draft(stamp.date(),start,end,cells,clusters,False)
        assert '111 rejected reports' in brief and '3001 rejected reports' in brief
        assert 'Abuse alert:' in brief and 'INCOMPLETE' not in brief and proposals['complete']
        assert any(c['source']=='usage' and c['installs']==2000 for c in cells)
        # Retroactive quarantine changes both SQL inputs and cannot meet a cell.
        query('update public.learn_install_cohorts set quarantined=true')
        assert local_rows(agent.sql_for('feedback_reports',start,end)) == []
        assert local_rows(agent.sql_for('usage_weeks',start,end)) == []
        # Worst-case text bound across two quota weeks remains under the prompt cap.
        worst = [dict(feedback_rows[0], id=f'bounded_{n:08}', text='\U00010000'*1000) for n in range(16)]
        worst.extend(dict(feedback_rows[0], id=f'remainder_{n:08}', text='A') for n in range(164))
        assert len(agent.model_inputs(worst)[1].encode()) < agent.MAX_PROMPT_BYTES
        print('SQL passed: idempotence, RLS/grants, weekly/IP/text boundaries, A26 quarantine, A27 complete brief/overflow for 201/5001 volume, rollover, concurrency, retention')
    finally:
        result=run([str(BIN/'pg_ctl'),'-D',str(work/'data'),'-m','immediate','-w','stop'])
        assert result.returncode == 0, result.stderr

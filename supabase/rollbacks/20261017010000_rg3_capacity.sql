-- MTN-69 safe rollback: pause collection without restoring the vulnerable cap.
-- Apply before reverting the receiver. Keep retention, data, and all denylist hashes.
begin;
select pg_advisory_xact_lock(731903,3);
update public.rg3_budget set accepting=false,usage_accepting=false where singleton;
commit;
-- Keep both RPC signatures so known deletions and revocation replay still work.
-- Do not drop tables, truncate revocations, or restore an older denylist snapshot.

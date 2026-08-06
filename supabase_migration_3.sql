-- Migracao 3: adiciona colunas pra relatorio de DSR
-- Cole no SQL Editor do Supabase e aperte Run.

alter table holerites add column if not exists comissoes_raw numeric(12,2);
alter table holerites add column if not exists reflexo_dsr_raw numeric(12,2);

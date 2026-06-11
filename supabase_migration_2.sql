-- =============================================================================
-- Migracao 2 — Suporte a competencia + decimo terceiro
-- =============================================================================
-- Cole este arquivo INTEIRO no SQL Editor do Supabase e aperte "Run".
-- Roda uma unica vez. Adiciona 3 colunas e ajusta a restricao de unicidade.
-- =============================================================================

-- 1) Adiciona colunas (tipo eh obrigatorio, competencia eh opcional)
alter table meses add column if not exists tipo text not null default 'regular';
alter table meses add column if not exists competencia_mes int;
alter table meses add column if not exists competencia_ano int;

-- 2) Restringe valores possiveis de tipo
alter table meses drop constraint if exists meses_tipo_check;
alter table meses add constraint meses_tipo_check
    check (tipo in ('regular', '13_1', '13_2'));

-- 3) Substitui a unicidade antiga (loja+ano+mes) pela nova (loja+ano+mes+tipo)
alter table meses drop constraint if exists meses_loja_id_ano_mes_key;
alter table meses drop constraint if exists meses_loja_id_ano_mes_tipo_key;
alter table meses add constraint meses_loja_id_ano_mes_tipo_key
    unique (loja_id, ano, mes, tipo);

-- 4) Pra meses ja cadastrados (sem competencia), preenche com "mes do
--    pagamento - 1" como padrao. Voce pode editar depois pela tela.
update meses
   set competencia_mes = case when mes = 1 then 12 else mes - 1 end,
       competencia_ano = case when mes = 1 then ano - 1 else ano end
 where tipo = 'regular' and competencia_mes is null;

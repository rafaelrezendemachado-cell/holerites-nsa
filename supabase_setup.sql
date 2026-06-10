-- =============================================================================
-- Holerites Arezzo / Schutz — script de criação inicial do banco
-- =============================================================================
-- Cole este arquivo INTEIRO no SQL Editor do Supabase e aperte "Run".
-- Roda uma única vez. Cria todas as tabelas, deixa pronto pra o app.
-- =============================================================================

-- Extensão pra UUIDs
create extension if not exists "uuid-ossp";


-- =============================================================================
-- TABELAS
-- =============================================================================

-- Lojas (multi-tenancy: Arezzo Dourados, Schutz Dourados, etc.)
create table if not exists lojas (
    id          uuid primary key default uuid_generate_v4(),
    codigo      text unique not null,
    nome        text not null,
    ativo       boolean not null default true,
    created_at  timestamptz not null default now()
);

-- Bancos / formas de pagamento (cada loja tem suas próprias)
create table if not exists bancos (
    id          uuid primary key default uuid_generate_v4(),
    loja_id     uuid not null references lojas(id) on delete cascade,
    nome        text not null,
    ordem       int not null default 0,
    ativo       boolean not null default true,
    created_at  timestamptz not null default now(),
    unique (loja_id, nome)
);

-- Funcionárias
create table if not exists funcionarias (
    id              uuid primary key default uuid_generate_v4(),
    loja_id         uuid not null references lojas(id) on delete cascade,
    nome            text not null,
    banco_id        uuid references bancos(id) on delete set null,
    comissionada    boolean not null default false,
    ativa           boolean not null default true,
    data_admissao   date,
    data_inativacao date,
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now()
);

-- Meses de pagamento (ex: Junho 2026, Julho 2026)
create table if not exists meses (
    id              uuid primary key default uuid_generate_v4(),
    loja_id         uuid not null references lojas(id) on delete cascade,
    ano             int not null,
    mes             int not null check (mes between 1 and 12),
    data_pagamento  date not null,
    created_at      timestamptz not null default now(),
    unique (loja_id, ano, mes)
);

-- Holerites (1 por mês por funcionária)
create table if not exists holerites (
    id               uuid primary key default uuid_generate_v4(),
    mes_id           uuid not null references meses(id) on delete cascade,
    funcionaria_id   uuid not null references funcionarias(id) on delete cascade,
    banco_id         uuid references bancos(id) on delete set null,
    comissionada     boolean not null default false,
    motivacional     numeric(12,2) not null default 0,
    he               numeric(12,2) not null default 0,
    domingo          numeric(12,2) not null default 0,
    vales            numeric(12,2) not null default 0,
    uniodonto        numeric(12,2) not null default 0,
    plano_saude      numeric(12,2) not null default 0,
    emprestimo       numeric(12,2) not null default 0,
    vale_transporte  numeric(12,2) not null default 0,
    liquido          numeric(12,2) not null default 0,
    updated_at       timestamptz not null default now(),
    unique (mes_id, funcionaria_id)
);


-- =============================================================================
-- ÍNDICES (busca rápida)
-- =============================================================================

create index if not exists idx_funcionarias_loja on funcionarias(loja_id);
create index if not exists idx_funcionarias_banco on funcionarias(banco_id);
create index if not exists idx_meses_loja_ano_mes on meses(loja_id, ano, mes);
create index if not exists idx_holerites_mes on holerites(mes_id);
create index if not exists idx_holerites_func on holerites(funcionaria_id);


-- =============================================================================
-- SEGURANÇA (Row Level Security)
-- =============================================================================
-- Liga RLS em todas as tabelas sem criar policies — só o service_role do app
-- consegue acessar. A chave service_role fica guardada no Streamlit Secrets,
-- nunca no código.

alter table lojas enable row level security;
alter table bancos enable row level security;
alter table funcionarias enable row level security;
alter table meses enable row level security;
alter table holerites enable row level security;


-- =============================================================================
-- DADOS INICIAIS — Lojas
-- =============================================================================

insert into lojas (codigo, nome) values
    ('AZ-DOU', 'Arezzo Dourados'),
    ('SZ-DOU', 'Schutz Dourados')
on conflict (codigo) do nothing;


-- =============================================================================
-- DADOS INICIAIS — Bancos da Arezzo Dourados
-- =============================================================================

insert into bancos (loja_id, nome, ordem)
select id, 'Caixa Econômica', 1 from lojas where codigo = 'AZ-DOU'
on conflict (loja_id, nome) do nothing;

insert into bancos (loja_id, nome, ordem)
select id, 'Dinheiro', 2 from lojas where codigo = 'AZ-DOU'
on conflict (loja_id, nome) do nothing;

insert into bancos (loja_id, nome, ordem)
select id, 'Sicredi', 3 from lojas where codigo = 'AZ-DOU'
on conflict (loja_id, nome) do nothing;


-- =============================================================================
-- DADOS INICIAIS — Funcionárias da Arezzo Dourados (junho/2026)
-- =============================================================================
-- Pode editar pelo app depois (tela "Funcionárias"). Esta carga é só pra você
-- não ter que cadastrar tudo na mão na primeira vez.

-- CEF (18 funcionárias)
with cef as (select id from bancos where loja_id = (select id from lojas where codigo = 'AZ-DOU') and nome = 'Caixa Econômica'),
     loja as (select id from lojas where codigo = 'AZ-DOU')
insert into funcionarias (loja_id, nome, banco_id, comissionada)
values
    ((select id from loja), 'Amanda Caroline do Nascimento Queiroz', (select id from cef), true),
    ((select id from loja), 'Amanda Gabryela Duarte Pedroso',        (select id from cef), false),
    ((select id from loja), 'Crislaine Amaral Gomes',                (select id from cef), true),
    ((select id from loja), 'Eliane de Oliveira Alves',              (select id from cef), false),
    ((select id from loja), 'Francieli de Souza Cunha de Morais',    (select id from cef), false),
    ((select id from loja), 'Glauce Coutinho Arsamendia',            (select id from cef), false),
    ((select id from loja), 'Izabeli dos Santos Ribeiro',            (select id from cef), false),
    ((select id from loja), 'Jamila Russo Tarouco',                  (select id from cef), true),
    ((select id from loja), 'Josieli Ortiz Silva',                   (select id from cef), true),
    ((select id from loja), 'Juliana Teixeira Baldez',               (select id from cef), false),
    ((select id from loja), 'Karine Cansian',                        (select id from cef), true),
    ((select id from loja), 'Katia Franciele dos Santos',            (select id from cef), true),
    ((select id from loja), 'Larissa dos Santos Ferreira',           (select id from cef), false),
    ((select id from loja), 'Maria Luíza Gallindo de Carvalho',      (select id from cef), false),
    ((select id from loja), 'Sineia de Brito Pimenta',               (select id from cef), true),
    ((select id from loja), 'Talita Kelen Silva Liborio',            (select id from cef), true),
    ((select id from loja), 'Tatiane Aparecida Lacerda Gamarra',     (select id from cef), true),
    ((select id from loja), 'Vania Verao de Oliveira',               (select id from cef), false);

-- Caixa da Loja (Dinheiro) — 9 funcionárias
with cdl as (select id from bancos where loja_id = (select id from lojas where codigo = 'AZ-DOU') and nome = 'Dinheiro'),
     loja as (select id from lojas where codigo = 'AZ-DOU')
insert into funcionarias (loja_id, nome, banco_id, comissionada)
values
    ((select id from loja), 'Amanda da Silva Santos',                (select id from cdl), false),
    ((select id from loja), 'Ana Gabriely Matos de Paula',           (select id from cdl), false),
    ((select id from loja), 'Geisiane Guilherme Vilhalva',           (select id from cdl), true),
    ((select id from loja), 'Gislaine Marconsini da Silva',          (select id from cdl), true),
    ((select id from loja), 'Krishma Evelyn Freitas Goncalves',      (select id from cdl), true),
    ((select id from loja), 'Luzia Tais Pereira da Silva',           (select id from cdl), false),
    ((select id from loja), 'Mariete Souza Cavalcante',              (select id from cdl), true),
    ((select id from loja), 'Thielly Portilho da Mata',              (select id from cdl), false),
    ((select id from loja), 'Yasmim Alves Tenorio Bitsch',           (select id from cdl), false);


-- =============================================================================
-- FIM
-- =============================================================================
-- Tudo pronto. Próximo passo: o app vai conectar usando a chave service_role.
-- =============================================================================

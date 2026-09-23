CREATE TABLE culturas (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE safras (
    id SERIAL PRIMARY KEY,
    cultura_id INTEGER NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE,
    status TEXT NOT NULL DEFAULT 'em_andamento',
    FOREIGN KEY (cultura_id) REFERENCES culturas(id)
);

CREATE TABLE precos (
    id SERIAL PRIMARY KEY,
    cultura_id INTEGER NOT NULL,
    data DATE NOT NULL,
    valor_por_saca NUMERIC NOT NULL,
    FOREIGN KEY (cultura_id) REFERENCES culturas(id)
);

CREATE TABLE cargas (
    id SERIAL PRIMARY KEY,
    safra_id INTEGER NOT NULL,
    data DATE NOT NULL,
    quantidade_sacas NUMERIC NOT NULL,
    preco_id INTEGER,
    valor_total NUMERIC,
    FOREIGN KEY (safra_id) REFERENCES safras(id),
    FOREIGN KEY (preco_id) REFERENCES precos(id)
);

CREATE TABLE trabalhadores (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    tipo_pagamento TEXT NOT NULL
);

CREATE TABLE custos (
    id SERIAL PRIMARY KEY,
    safra_id INTEGER NOT NULL,
    descricao TEXT NOT NULL,
    valor NUMERIC NOT NULL,
    data DATE NOT NULL,
    FOREIGN KEY (safra_id) REFERENCES safras(id)
);

CREATE TABLE pagamentos_trabalhadores (
    id SERIAL PRIMARY KEY,
    trabalhador_id INTEGER NOT NULL,
    safra_id INTEGER NOT NULL,
    data DATE NOT NULL,
    valor NUMERIC NOT NULL,
    FOREIGN KEY (trabalhador_id) REFERENCES trabalhadores(id),
    FOREIGN KEY (safra_id) REFERENCES safras(id)
);
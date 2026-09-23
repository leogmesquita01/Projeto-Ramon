CREATE TABLE culturas (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    peso_saca_kg NUMERIC NOT NULL 
);


CREATE TABLE safras (
    id SERIAL PRIMARY KEY,
    cultura_id INTEGER NOT NULL REFERENCES culturas(id),
    nome TEXT NOT NULL, 
    talhao TEXT,
    data_inicio DATE,
    data_fim DATE
);


CREATE TABLE cargas (
    id SERIAL PRIMARY KEY,
    safra_id INTEGER NOT NULL REFERENCES safras(id),
    data DATE NOT NULL,
    peso_total_kg NUMERIC NOT NULL,
    comprador TEXT,
    preco_por_saca NUMERIC

);


CREATE TABLE custos_producao (
    id SERIAL PRIMARY KEY,
    safra_id INTEGER NOT NULL REFERENCES safras(id),
    categoria TEXT NOT NULL,
    descricao TEXT,
    valor NUMERIC NOT NULL,
    data DATE NOT NULL
);


CREATE TABLE trabalhadores (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    funcao TEXT,
    tipo_contrato TEXT
);


CREATE TABLE pagamentos (
    id SERIAL PRIMARY KEY,
    trabalhador_id INTEGER NOT NULL REFERENCES trabalhadores(id),
    safra_id INTEGER REFERENCES safras(id),
    descricao TEXT,
    valor NUMERIC NOT NULL,
    data DATE NOT NULL
);
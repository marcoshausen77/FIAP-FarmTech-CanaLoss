CREATE TABLE talhoes (
    id VARCHAR2(30 CHAR) PRIMARY KEY,
    nome VARCHAR2(100 CHAR) NOT NULL,
    area_ha NUMBER NOT NULL,
    CONSTRAINT ck_talhao_id CHECK (REGEXP_LIKE(id, '^[A-Z0-9][A-Z0-9_-]{0,29}$', 'c')),
    CONSTRAINT ck_talhao_nome CHECK (TRIM(nome) IS NOT NULL),
    CONSTRAINT ck_talhao_area CHECK (area_ha > 0 AND area_ha <= 1000000000 AND area_ha = ROUND(area_ha, 4))
);
CREATE TABLE colheitas (
    id VARCHAR2(30 CHAR) PRIMARY KEY,
    talhao_id VARCHAR2(30 CHAR) NOT NULL,
    data DATE NOT NULL,
    area_ha NUMBER NOT NULL,
    producao_t NUMBER NOT NULL,
    perda_kg_ha NUMBER NOT NULL,
    preco_t NUMBER NOT NULL,
    CONSTRAINT fk_colheita_talhao FOREIGN KEY (talhao_id) REFERENCES talhoes(id),
    CONSTRAINT uq_talhao_data UNIQUE (talhao_id, data),
    CONSTRAINT ck_colheita_id CHECK (REGEXP_LIKE(id, '^[A-Z0-9][A-Z0-9_-]{0,29}$', 'c')),
    CONSTRAINT ck_colheita_data CHECK (data >= DATE '1900-01-01' AND data = TRUNC(data)),
    CONSTRAINT ck_colheita_area CHECK (area_ha > 0 AND area_ha <= 1000000000 AND area_ha = ROUND(area_ha, 4)),
    CONSTRAINT ck_colheita_producao CHECK (producao_t >= 0 AND producao_t <= 1000000000 AND producao_t = ROUND(producao_t, 4)),
    CONSTRAINT ck_colheita_perda CHECK (perda_kg_ha >= 0 AND perda_kg_ha <= 1000000000 AND perda_kg_ha = ROUND(perda_kg_ha, 4)),
    CONSTRAINT ck_colheita_preco CHECK (preco_t > 0 AND preco_t <= 1000000000 AND preco_t = ROUND(preco_t, 4))
);

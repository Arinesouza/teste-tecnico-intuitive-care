SET client_encoding = 'UTF8';
DROP TABLE IF EXISTS despesas_agregadas;
DROP TABLE IF EXISTS despesas_consolidadas;
DROP TABLE IF EXISTS operadoras_cadastrais;

CREATE TABLE operadoras_cadastrais (
    registro_ans TEXT PRIMARY KEY,
    cnpj TEXT, razao_social TEXT, nome_fantasia TEXT, modalidade TEXT, uf TEXT,
    c7 TEXT, c8 TEXT, c9 TEXT, c10 TEXT, c11 TEXT, c12 TEXT, 
    c13 TEXT, c14 TEXT, c15 TEXT, c16 TEXT, c17 TEXT, c18 TEXT, c19 TEXT, c20 TEXT
);

CREATE TABLE despesas_consolidadas (
    id SERIAL PRIMARY KEY,
    registro_ans TEXT,
    razao_social_temp TEXT,
    trimestre DATE,
    ano DATE,
    valor_despesa DECIMAL(20, 2)
);
CREATE INDEX idx_ans_despesas ON despesas_consolidadas(registro_ans);

CREATE TABLE despesas_agregadas (
    razao_social TEXT, uf TEXT, total_despesas TEXT, media_despesas TEXT, extra_lixo TEXT
);

\copy operadoras_cadastrais FROM '../PARTE2/Relatorio_cadop.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true, QUOTE '"', ENCODING 'LATIN1');
\copy despesas_consolidadas(registro_ans, razao_social_temp, trimestre, ano, valor_despesa) FROM '../PARTE1/output/consolidado_despesas.csv' WITH (FORMAT csv, DELIMITER ',', HEADER true);
\copy despesas_agregadas FROM '../PARTE2/output/despesas_agregadas.csv' WITH (FORMAT csv, DELIMITER ';', HEADER true);


SELECT '--- RANKING DESPESAS POR UF ---' AS status;
SELECT uf,
SUM(CAST(total_despesas AS DECIMAL)) AS despesa_total,
AVG(CAST(total_despesas AS DECIMAL)) AS media_por_operadora
FROM despesas_agregadas 
WHERE uf IS NOT NULL AND uf <> '' AND uf <> 'N/I'
GROUP BY uf 
ORDER BY despesa_total DESC 
LIMIT 5;

SELECT '--- TOP 5 CRESCIMENTO PERCENTUAL ---' AS status;
WITH calculo_tri AS (
    SELECT 
        registro_ans,
        SUM(CASE WHEN ano = 2025 AND trimestre = 1 THEN valor_despesa ELSE 0 END) as v1,
        SUM(CASE WHEN ano = 2025 AND trimestre = 2 THEN valor_despesa ELSE 0 END) as v2
    FROM despesas_consolidadas
    GROUP BY registro_ans
)
SELECT 
    c.razao_social,
    ROUND(((v2 - v1) / NULLIF(v1, 0)) * 100, 2) as crescimento_pct
FROM calculo_tri t
JOIN operadoras_cadastrais c ON t.registro_ans = c.registro_ans
WHERE v1 > 1000 
ORDER BY crescimento_pct DESC LIMIT 5;

SELECT '--- OPERADORAS ACIMA DA MÉDIA (MIN 2 TRIMESTRES) ---' AS status;
WITH MediaGlobal AS (
    SELECT ano, trimestre, AVG(valor_despesa) as media_valor
    FROM despesas_consolidadas GROUP BY ano, trimestre
)
SELECT 
    c.razao_social, 
    COUNT(*) as trimestres_acima
FROM despesas_consolidadas d
JOIN MediaGlobal m ON d.ano = m.ano AND d.trimestre = m.trimestre
JOIN operadoras_cadastrais c ON d.registro_ans = c.registro_ans
WHERE d.valor_despesa > m.media_valor
GROUP BY c.razao_social 
HAVING COUNT(*) >= 2
ORDER BY trimestres_acima DESC LIMIT 10;
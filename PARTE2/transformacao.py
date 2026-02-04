import pandas as pd
from pathlib import Path
import zipfile
import re

BASE_DIR = Path(__file__).parent
ARQ_CONSOLIDADO = BASE_DIR.parent / "PARTE1" / "output" / "consolidado_despesas.csv"
ARQ_CADOP = BASE_DIR / "Relatorio_cadop.csv"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

CSV_FINAL = OUTPUT_DIR / "despesas_agregadas.csv"
ZIP_FINAL = BASE_DIR / "Teste_Arine_Souza.zip"

def validar_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', str(cnpj))
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    
    def calc_dig(cnpj_parcial, pesos):
        soma = sum(int(d) * p for d, p in zip(cnpj_parcial, pesos))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    pesos1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    d1 = calc_dig(cnpj[:12], pesos1)
    d2 = calc_dig(cnpj[:12] + d1, [6]+pesos1)
    return cnpj[-2:] == d1 + d2

df = pd.read_csv(ARQ_CONSOLIDADO)
cadop = pd.read_csv(ARQ_CADOP, sep=';', encoding='latin1')
cadop.columns = cadop.columns.str.strip()

df['REG_ANS_JOIN'] = df['CNPJ'].astype(str).str.strip()
cadop['REG_ANS_JOIN'] = cadop['REGISTRO_OPERADORA'].astype(str).str.strip()

cadop_clean = cadop.drop_duplicates(subset='REG_ANS_JOIN', keep='last')

df_enriquecido = df.merge(
    cadop_clean[['REG_ANS_JOIN', 'CNPJ', 'Razao_Social', 'Modalidade', 'UF']], 
    on='REG_ANS_JOIN', 
    how='left',
    suffixes=('_old', '')
)

df_enriquecido['CNPJ_REAL'] = df_enriquecido['CNPJ'].fillna("00000000000000")
df_enriquecido['RazaoSocial'] = df_enriquecido['Razao_Social'].fillna("Operadora Não Identificada")
df_enriquecido['UF'] = df_enriquecido['UF'].fillna("N/I")

df_enriquecido['CNPJ_VALIDO'] = df_enriquecido['CNPJ_REAL'].apply(validar_cnpj)

resultado = (
    df_enriquecido.groupby(['RazaoSocial', 'UF'])
    .agg(
        TotalDespesas=('ValorDespesas', 'sum'),
        MediaTrimestral=('ValorDespesas', 'mean'),
        DesvioPadrao=('ValorDespesas', 'std')
    )
    .reset_index()
)

resultado = resultado.fillna(0)

resultado = resultado.sort_values(by='TotalDespesas', ascending=False).round(2)

resultado.to_csv(CSV_FINAL, index=False, sep=';', encoding='utf-8-sig')

with zipfile.ZipFile(ZIP_FINAL, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(CSV_FINAL, arcname='despesas_agregadas.csv')

print(f"Teste de transformação e validação de dados concluída. Arquivo gerado: {ZIP_FINAL}")
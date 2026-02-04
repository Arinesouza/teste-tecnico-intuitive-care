import pandas as pd
from pathlib import Path
import zipfile
import re

BASE_DIR = Path(__file__).parent

PASTA_OUTPUT = BASE_DIR / "output"
PASTA_OUTPUT.mkdir(exist_ok=True)
CSV_FINAL = PASTA_OUTPUT / "consolidado_despesas.csv"
ZIP_FINAL = PASTA_OUTPUT / "consolidado_despesas.zip"

def ler_csv(caminho):
    return pd.read_csv(
        caminho,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
        on_bad_lines='skip'
    )

def processar_pasta(pasta):
    match = re.match(r"(\d)T(\d{4})", pasta.name)
    if not match:
        return None
    trimestre, ano = match.groups()

    arquivos = [f for f in pasta.iterdir() if f.is_file()]
    if not arquivos:
        return None

    arquivo = arquivos[0]
    df = ler_csv(arquivo)

    
    if 'CD_CONTA_CONTABIL' in df.columns:
        df['CD_CONTA_CONTABIL'] = df['CD_CONTA_CONTABIL'].astype(str)
        df = df[df['CD_CONTA_CONTABIL'].str.startswith('411')].copy()


    df = df.rename(columns={
        "REG_ANS": "CNPJ",
        "VL_SALDO_FINAL": "ValorDespesas"
    })

    df["ValorDespesas"] = pd.to_numeric(df["ValorDespesas"], errors="coerce").fillna(0)
    
    df = df[df["ValorDespesas"] > 0].copy()

    df["RazaoSocial"] = "NA"
    df["Trimestre"] = trimestre
    df["Ano"] = ano

    return df[["CNPJ", "RazaoSocial", "Trimestre", "Ano", "ValorDespesas"]]

def main():
    dfs = []

    for pasta in sorted(BASE_DIR.iterdir()):
        if pasta.is_dir() and re.match(r"\dT\d{4}", pasta.name):
            print(f"Processando {pasta.name}...")
            df_processado = processar_pasta(pasta)
            if df_processado is not None and not df_processado.empty:
                dfs.append(df_processado)

    if not dfs:
        print(" Nenhuma pasta trimestral com dados válidos encontrada.")
        return

    df_consolidado = pd.concat(dfs, ignore_index=True)

    df_consolidado.to_csv(CSV_FINAL, index=False, encoding='utf-8-sig')

    with zipfile.ZipFile(ZIP_FINAL, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(CSV_FINAL, arcname="consolidado_despesas.csv")

    print(f"Processamento concluído! Arquivo gerado em: {ZIP_FINAL}")

if __name__ == "__main__":
    main()
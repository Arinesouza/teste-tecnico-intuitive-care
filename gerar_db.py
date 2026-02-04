import sqlite3
import pandas as pd
from sqlalchemy import create_engine

pg_engine = create_engine("postgresql://postgres:1234@localhost:5432/teste_ans")

with sqlite3.connect("PARTE4/backend/database.db") as sl_conn:
    for tab in ["operadoras_cadastrais", "despesas_consolidadas", "despesas_agregadas"]:
        df = pd.read_sql(f"SELECT * FROM {tab} LIMIT 200", pg_engine)
        df.to_sql(tab, sl_conn, if_exists="replace", index=False)
print("Arquivo database.db gerado com sucesso!")
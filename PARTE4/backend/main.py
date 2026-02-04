import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não configurada")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="API Operadoras ANS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def consertar_acentuacao(texto):
    """Detecta e corrige caracteres especiais corrompidos (Mojibake)."""
    if not texto:
        return texto
    try:
        return texto.encode('latin-1').decode('utf-8').upper().strip()
    except (UnicodeEncodeError, UnicodeDecodeError):
        return str(texto).upper().strip()

def sanitizar_dados(obj):
    """Aplica a correção de acentuação nos campos de texto do dicionário."""
    if not obj:
        return obj
    d = dict(obj)
    campos_texto = ["razao_social", "modalidade", "uf", "label"]
    for campo in campos_texto:
        if campo in d and d[campo]:
            d[campo] = consertar_acentuacao(d[campo])
    return d

@app.get("/api/operadoras")
def listar_operadoras(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    """Lista operadoras com paginação e busca."""
    offset = (page - 1) * limit
    params = {"limit": limit, "offset": offset}
    where = ""
    if search:
        where = "WHERE cnpj ILIKE :search OR razao_social ILIKE :search"
        params["search"] = f"%{search}%"

    total = db.execute(text(f"SELECT COUNT(*) FROM operadoras_cadastrais {where}"), params).scalar()
    
    rows = db.execute(
        text(f"""
            SELECT cnpj, registro_ans, razao_social, modalidade, c11 AS uf 
            FROM operadoras_cadastrais {where} 
            ORDER BY razao_social LIMIT :limit OFFSET :offset
        """),
        params
    ).mappings().all()

    return {
        "data": [sanitizar_dados(row) for row in rows],
        "total": total,
        "page": page,
        "limit": limit
    }

@app.get("/api/operadoras/{cnpj}")
def detalhe_operadora(cnpj: str, db: Session = Depends(get_db)):
    """Retorna detalhes de uma operadora específica."""
    cnpj_limpo = "".join(filter(str.isdigit, cnpj)).zfill(14)
    row = db.execute(
        text("SELECT cnpj, registro_ans, razao_social, modalidade, c11 AS uf FROM operadoras_cadastrais WHERE cnpj = :cnpj"),
        {"cnpj": cnpj_limpo}
    ).mappings().first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")
    return sanitizar_dados(row)

@app.get("/api/operadoras/{cnpj}/despesas")
def despesas_operadora(cnpj: str, db: Session = Depends(get_db)):
    """Retorna histórico de despesas consolidado por período."""
    cnpj_limpo = "".join(filter(str.isdigit, cnpj)).zfill(14)
    registro = db.execute(
        text("SELECT registro_ans FROM operadoras_cadastrais WHERE cnpj = :cnpj"), 
        {"cnpj": cnpj_limpo}
    ).scalar()
    
    if not registro:
        return []
    
    result = db.execute(
        text("""
            SELECT ano, trimestre, SUM(valor_despesa) AS valor_despesa 
            FROM despesas_consolidadas 
            WHERE registro_ans = :registro 
            GROUP BY ano, trimestre 
            ORDER BY ano DESC, trimestre DESC
        """), 
        {"registro": registro}
    ).mappings().all()
    
    return [dict(row) for row in result]

@app.get("/api/estatisticas/despesas_por_uf")
def despesas_por_uf(db: Session = Depends(get_db)):
    """Estatísticas agregadas para o gráfico (Top 10 UFs)."""
    query = text("""
        SELECT uf AS label, SUM(CAST(total_despesas AS DECIMAL)) AS valor
        FROM despesas_agregadas 
        WHERE uf IS NOT NULL AND uf <> '' AND uf <> 'N/I'
        GROUP BY uf ORDER BY valor DESC LIMIT 10
    """)
    res = db.execute(query).mappings().all()
    return [sanitizar_dados({"label": row.label, "valor": float(row.valor)}) for row in res]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
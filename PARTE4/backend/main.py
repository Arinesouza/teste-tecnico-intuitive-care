import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

IF_RENDER = os.getenv("RENDER") == "True"

if IF_RENDER:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "database.db")
    DATABASE_URL = f"sqlite:///{db_path}"
else:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
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
    if not texto: return texto
    try:
        return texto.encode('latin-1').decode('utf-8').upper().strip()
    except:
        return str(texto).upper().strip()

def sanitizar_dados(obj):
    if not obj: return obj
    d = dict(obj)
    for campo in ["razao_social", "modalidade", "uf", "label"]:
        if campo in d and d[campo]:
            d[campo] = consertar_acentuacao(d[campo])
    return d

@app.get("/api/operadoras")
def listar_operadoras(page: int = Query(1, ge=1), limit: int = Query(12, ge=1), search: str = None, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    params = {"limit": limit, "offset": offset}
    where = ""
    if search:
        op_like = "LIKE" if IF_RENDER else "ILIKE"
        where = f"WHERE cnpj {op_like} :search OR razao_social {op_like} :search"
        params["search"] = f"%{search}%"
    
    total = db.execute(text(f"SELECT COUNT(*) FROM operadoras_cadastrais {where}"), params).scalar()
    rows = db.execute(
        text(f"SELECT cnpj, registro_ans, razao_social, modalidade, c11 AS uf FROM operadoras_cadastrais {where} ORDER BY razao_social LIMIT :limit OFFSET :offset"),
        params
    ).mappings().all()
    
    return {"data": [sanitizar_dados(row) for row in rows], "total": total, "page": page, "limit": limit}

@app.get("/api/estatisticas/despesas_por_uf")
def despesas_por_uf(db: Session = Depends(get_db)):
    query = text("""
        SELECT uf AS label, SUM(CAST(total_despesas AS NUMERIC)) AS valor 
        FROM despesas_agregadas 
        WHERE uf IS NOT NULL AND uf <> '' AND uf <> 'N/I' 
        GROUP BY uf ORDER BY valor DESC LIMIT 10
    """)
    try:
        res = db.execute(query).mappings().all()
        return [sanitizar_dados({"label": row.label, "valor": float(row.valor or 0)}) for row in res]
    except Exception as e:
        print(f"Erro Analitico: {e}")
        return []

current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(current_dir, "..", "frontend", "dist")

if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith(("api", "docs")): return {"detail": "Not Found"}
        return FileResponse(os.path.join(frontend_path, "index.html"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
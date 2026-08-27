from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import io

app = FastAPI(title="PoC Booth Flow", version="1.0.0")

class AnagraficaInput(BaseModel):
    id_exploplanning: str
    tipo: str
    ragione_sociale: str
    partita_iva: Optional[str] = None
    codice_fiscale: Optional[str] = None
    indirizzo: Optional[str] = None
    tipo_cliente: Optional[str] = "NORMALE"
    codice_iva_default: Optional[str] = "22"

@app.get("/")
def home():
    return {"status": "PoC Attivo", "docs": "/docs"}

@app.post("/api/anagrafica/sync-sap")
def sync_sap(dati: AnagraficaInput):
    valido = bool(dati.ragione_sociale and (dati.partita_iva or dati.codice_fiscale) and dati.indirizzo)
    if not valido:
        return {"status": "PROSPECT", "messaggio": "Dataset incompleto per SAP"}
    return {
        "status": "SYNCED",
        "codice_sap": f"SAP-{dati.id_exploplanning[-4:]}",
        "cliente": dati.ragione_sociale
    }

@app.post("/api/distinta/import-xls")
async def import_distinta(wbs_code: str, file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    return {
        "wbs": wbs_code,
        "totale_righe": len(df),
        "colonne_rilevate": list(df.columns)
    }
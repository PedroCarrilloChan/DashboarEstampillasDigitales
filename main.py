# main.py - Versión con la configuración de CORS corregida
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
import sqlite3
import json
from typing import Optional, Dict
from datetime import date, timedelta

# --- Configuración ---
DATABASE_FILE = "dashboard_data.db"

# --- Descripción de la API ---
app = FastAPI(
    title="API Dashboard de Estampillas con Base de Datos",
    description="Sirve los KPIs para un programa de lealtad usando una base de datos SQLite persistente.",
    version="5.1.0", # Versión actualizada
)

# --- Configuración de CORS ---
# Orígenes permitidos. Aquí le damos permiso a tu dominio.
origins = [
    "https://dashboard.smartpasses.io",
    # También puedes añadir orígenes de desarrollo si los necesitas
    # "http://localhost",
    # "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # <-- Cambio clave: Usamos la lista de orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todas las cabeceras
)

# --- Modelos de Datos (sin cambios) ---
class KpiData(BaseModel):
    total_members: int = 0
    passes_installed: int = 0
    android_installs: int = 0
    iphone_installs: int = 0
    recurring_customers_current_month: int = 0
    stamps_given_current_month: int = 0
    completed_cards_current_month: int = 0
    acquisition_channels: Dict[str, int] = {}
    redemption_rate_percentage: int = 0
    avg_days_to_complete_card: int = 0

class KpiUpdate(BaseModel):
    total_members: Optional[int] = None
    passes_installed: Optional[int] = None
    android_installs: Optional[int] = None
    iphone_installs: Optional[int] = None
    recurring_customers_current_month: Optional[int] = None
    stamps_given_current_month: Optional[int] = None
    completed_cards_current_month: Optional[int] = None
    acquisition_channels: Optional[Dict[str, int]] = None
    redemption_rate_percentage: Optional[int] = None
    avg_days_to_complete_card: Optional[int] = None

class KpiResponse(BaseModel):
    current_data: KpiData
    previous_month_data: KpiData

# --- Funciones de la Base de Datos ---
def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kpi_history (
            record_date TEXT PRIMARY KEY,
            data TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_kpis_from_db(record_date: str) -> KpiData:
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM kpi_history WHERE record_date = ?", (record_date,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return KpiData(**json.loads(row[0]))
    else:
        return KpiData()

def update_kpis_in_db(record_date: str, update_data: KpiUpdate) -> KpiData:
    current_kpis = get_kpis_from_db(record_date)
    stored_data = current_kpis.model_dump()
    new_data = update_data.model_dump(exclude_unset=True)
    if "acquisition_channels" in new_data:
        stored_data["acquisition_channels"].update(new_data.pop("acquisition_channels"))
    stored_data.update(new_data)
    updated_json_data = json.dumps(stored_data)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO kpi_history (record_date, data) VALUES (?, ?)", (record_date, updated_json_data))
    conn.commit()
    conn.close()
    print(f"KPIs actualizados en BD para la fecha {record_date}:", new_data)
    return KpiData(**stored_data)

# --- Endpoints de la API ---
@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/", response_class=FileResponse, tags=["Frontend"])
async def read_index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

@app.get("/kpis", response_model=KpiResponse, tags=["API"])
def get_kpis_for_date(query_date: str = date.today().isoformat()):
    current_date_obj = date.fromisoformat(query_date)
    previous_month_date_str = (current_date_obj - timedelta(days=30)).isoformat()
    current_data = get_kpis_from_db(query_date)
    previous_month_data = get_kpis_from_db(previous_month_date_str)
    return KpiResponse(current_data=current_data, previous_month_data=previous_month_data)

@app.post("/update-kpis", response_model=KpiData, tags=["API"])
def update_kpis(kpi_data: KpiUpdate, update_date: str = date.today().isoformat()):
    return update_kpis_in_db(update_date, kpi_data)

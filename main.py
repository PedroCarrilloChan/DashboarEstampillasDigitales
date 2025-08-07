# main.py - Versión con Historial de Datos por Fecha
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
from typing import Optional, Dict
from datetime import date, timedelta

# --- Descripción de la API ---
app = FastAPI(
    title="API Dashboard de Estampillas con Historial",
    description="Sirve los KPIs para un programa de lealtad, permitiendo consultas por fecha.",
    version="4.0.0",
)

# --- Configuración de CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos de Datos ---
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

# Modelo para la respuesta que incluye datos actuales y del mes pasado
class KpiResponse(BaseModel):
    current_data: KpiData
    previous_month_data: KpiData

# --- "Base de Datos" en Memoria con Historial ---
# La clave es una fecha en formato string "YYYY-MM-DD"
db: Dict[str, KpiData] = {}

# Crear datos de ejemplo para hoy y el mes pasado para que el dashboard no se vea vacío al inicio
today_str = date.today().isoformat()
last_month_date = date.today() - timedelta(days=30)
last_month_str = last_month_date.isoformat()

db[today_str] = KpiData(
    total_members=500, passes_installed=420, android_installs=150, iphone_installs=270,
    recurring_customers_current_month=150, stamps_given_current_month=850,
    completed_cards_current_month=75, acquisition_channels={"facebook": 120, "instagram": 200, "web": 80, "gloriafood": 100},
    redemption_rate_percentage=45, avg_days_to_complete_card=25
)
db[last_month_str] = KpiData(
    total_members=450, passes_installed=380, android_installs=130, iphone_installs=250,
    recurring_customers_current_month=120, stamps_given_current_month=700,
    completed_cards_current_month=60, acquisition_channels={"facebook": 100, "instagram": 180, "web": 70, "gloriafood": 30},
    redemption_rate_percentage=40, avg_days_to_complete_card=28
)


# --- Endpoints de la API ---

@app.get("/", response_class=FileResponse, tags=["Frontend"])
async def read_index():
    """
    Este endpoint carga y devuelve el archivo index.html.
    Es lo que verás cuando visites la URL principal.
    """
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)

@app.get("/kpis", response_model=KpiResponse, tags=["API"])
def get_kpis_for_date(query_date: str = date.today().isoformat()):
    """
    Obtiene los KPIs para una fecha específica y los compara con el mismo día del mes anterior.
    """
    try:
        current_date_obj = date.fromisoformat(query_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usar YYYY-MM-DD.")

    # Calcular la fecha del mes anterior para comparación
    previous_month_date_obj = current_date_obj - timedelta(days=30)
    previous_month_date_str = previous_month_date_obj.isoformat()

    # Obtener datos o usar un objeto vacío si no existen
    current_data = db.get(query_date, KpiData())
    previous_month_data = db.get(previous_month_date_str, KpiData())

    return KpiResponse(current_data=current_data, previous_month_data=previous_month_data)

@app.post("/update-kpis", response_model=KpiData, tags=["API"])
def update_kpis(kpi_data: KpiUpdate, update_date: str = date.today().isoformat()):
    """
    Actualiza los KPIs para una fecha específica.
    Si la fecha no existe, crea un nuevo registro.
    """
    global db

    # Obtener el registro existente o crear uno nuevo si no existe
    current_record = db.get(update_date, KpiData())
    stored_data = current_record.model_dump()

    update_data = kpi_data.model_dump(exclude_unset=True)

    if "acquisition_channels" in update_data:
        stored_data["acquisition_channels"].update(update_data["acquisition_channels"])
        del update_data["acquisition_channels"]

    stored_data.update(update_data)
    db[update_date] = KpiData(**stored_data)

    print(f"KPIs actualizados para la fecha {update_date}:", update_data)
    return db[update_date]

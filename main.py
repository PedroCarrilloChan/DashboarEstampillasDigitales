# main.py - Versión Final que sirve el Frontend
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# ¡Nuevas importaciones importantes!
from fastapi.responses import FileResponse
import os

# --- Descripción de la API ---
app = FastAPI(
    title="API y Servidor de Dashboard de Lealtad",
    description="Sirve los KPIs y la interfaz del dashboard.",
    version="2.0.0",
)

# --- Configuración de CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelo de Datos (Pydantic) ---
class KpiData(BaseModel):
    roi_percentage: float = 210.0
    roi_trend_percentage: float = 25.0
    active_members: int = 4850
    active_members_trend_percentage: float = 12.0
    attributable_revenue_k: float = 185.0
    attributable_revenue_trend_percentage: float = 18.0
    retention_rate_percentage: float = 85.0
    retention_rate_trend_percentage: float = 5.0
    aov_members: float = 850.0
    aov_non_members: float = 680.0
    purchase_freq_members: float = 2.1
    purchase_freq_non_members: float = 1.5
    digital_pass_adoption_percentage: int = 82
    chatbot_csat_score: float = 4.6
    chatbot_resolution_percentage: int = 93

# --- "Base de Datos" en Memoria ---
db = KpiData()

# --- Endpoints de la API ---

# Endpoint para servir el frontend (la página web)
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

# Endpoint para que el dashboard obtenga los datos
@app.get("/kpis", response_model=KpiData, tags=["API"])
def get_kpis():
    """
    Endpoint GET para que el JavaScript del dashboard obtenga los datos.
    """
    return db

# Endpoint para que el chatbot actualice los datos
@app.post("/update-kpis", response_model=KpiData, tags=["API"])
def update_kpis(kpi_data: KpiData):
    """
    Endpoint POST para que tu chatbot builder actualice los datos de los KPIs.
    """
    global db
    db = kpi_data
    print("KPIs actualizados:", db.model_dump_json(indent=2))
    return db

# Para desarrollo local, agregar esto al final:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

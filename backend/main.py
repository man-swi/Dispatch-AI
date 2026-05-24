from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import datetime
from elevenlabs.client import ElevenLabs
from elevenlabs import save
import whisper

# =====================================================
# LOAD ENV VARIABLES
# =====================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI()

# =====================================================
# SUPABASE CONNECTION
# =====================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# =====================================================
# ELEVENLABS CLIENT
# =====================================================

client_voice = ElevenLabs(
    api_key=ELEVENLABS_API_KEY
)

# =====================================================
# WHISPER MODEL
# =====================================================

whisper_model = whisper.load_model("base")

# =====================================================
# REQUEST MODELS
# =====================================================

class ShipmentUpdate(BaseModel):
    shipment_id: str
    status: str
    updated_eta: str
    delay_reason: str
    delay_minutes: int


class EventLog(BaseModel):
    event_id: str
    shipment_id: str
    event_type: str


class DelayTrigger(BaseModel):
    shipment_id: str
    delay_minutes: int


class VoiceRequest(BaseModel):
    message: str


# =====================================================
# UPDATED INCIDENT MODEL
# =====================================================

class IncidentHistoryRequest(BaseModel):
    shipment_id: str
    driver_name: str
    delay_reason: str
    severity: str
    escalation_status: str
    operational_summary: str

    # NEW INTELLIGENCE FIELDS
    route: str
    origin: str
    destination: str

# =====================================================
# HOME ROUTE
# =====================================================

@app.get("/")
def home():
    return {
        "message": "Dispatch AI Backend Running"
    }

# =====================================================
# FETCH SHIPMENTS
# =====================================================

@app.get("/shipments")
def get_shipments():

    response = (
        supabase
        .table("shipments")
        .select("*")
        .execute()
    )

    return response.data

# =====================================================
# UPDATE SHIPMENT
# =====================================================

@app.post("/update-shipment")
def update_shipment(data: ShipmentUpdate):

    # Severity Classification
    if data.delay_minutes > 120:
        severity = "high"

    elif data.delay_minutes < 30:
        severity = "low"

    else:
        severity = "medium"

    response = (
        supabase.table("shipments")
        .update({
            "status": data.status,
            "updated_eta": data.updated_eta,
            "delay_reason": data.delay_reason,
            "severity": severity
        })
        .eq("shipment_id", data.shipment_id)
        .execute()
    )

    return {
        "message": "Shipment updated successfully",
        "severity": severity,
        "data": response.data
    }

# =====================================================
# LOG OPERATIONAL EVENT
# =====================================================

@app.post("/log-event")
def log_event(event: EventLog):

    response = (
        supabase
        .table("call_logs")
        .insert({
            "event_id": event.event_id,
            "shipment_id": event.shipment_id,
            "event_type": event.event_type
        })
        .execute()
    )

    return {
        "message": "Event logged successfully",
        "data": response.data
    }

# =====================================================
# TRIGGER DELAY WORKFLOW
# =====================================================

@app.post("/trigger-delay")
def trigger_delay(data: DelayTrigger):

    if data.delay_minutes > 120:
        severity = "high"

    elif data.delay_minutes < 30:
        severity = "low"

    else:
        severity = "medium"

    return {
        "message": "Delay workflow triggered",
        "shipment_id": data.shipment_id,
        "delay_minutes": data.delay_minutes,
        "severity": severity
    }

# =====================================================
# TRANSCRIBE DRIVER AUDIO
# =====================================================

@app.post("/transcribe-audio")
def transcribe_audio():

    result = whisper_model.transcribe(
        "voice/driver_response.mp3"
    )

    return {
        "transcript": result["text"]
    }

# =====================================================
# GENERATE DISPATCH VOICE
# =====================================================

@app.post("/generate-dispatch-voice")
def generate_dispatch_voice(request: VoiceRequest):

    audio = client_voice.text_to_speech.convert(
        voice_id="NAsBsaz5a9n5VnIJBbE7",
        model_id="eleven_multilingual_v2",
        text=request.message
    )

    output_path = "voice/dispatch_response.mp3"

    save(audio, output_path)

    return {
        "status": "success",
        "audio_file": output_path,
        "message": request.message
    }

# =====================================================
# STORE INCIDENT HISTORY
# =====================================================

@app.post("/store-incident")
def store_incident(data: IncidentHistoryRequest):

    response = (
        supabase
        .table("incident_history")
        .insert({
            "shipment_id": data.shipment_id,
            "driver_name": data.driver_name,
            "delay_reason": data.delay_reason,
            "severity": data.severity,
            "escalation_status": data.escalation_status,
            "operational_summary": data.operational_summary,

            # NEW INTELLIGENCE DATA
            "route": data.route,
            "origin": data.origin,
            "destination": data.destination,

            "created_at": datetime.utcnow().isoformat()
        })
        .execute()
    )

    return {
        "message": "Incident stored successfully",
        "data": response.data
    }

# =====================================================
# GET INCIDENT HISTORY
# =====================================================

@app.get("/get-incident-history/{shipment_id}")
def get_incident_history(shipment_id: str):

    response = (
        supabase
        .table("incident_history")
        .select("*")
        .eq("shipment_id", shipment_id)
        .execute()
    )

    return {
        "shipment_id": shipment_id,
        "history": response.data
    }

# =====================================================
# INCIDENT ANALYTICS
# =====================================================

@app.get("/incident-analytics")
def incident_analytics():

    incidents = (
        supabase
        .table("incident_history")
        .select("*")
        .execute()
    )

    data = incidents.data

    total_incidents = len(data)

    high_severity = len([
        x for x in data
        if x["severity"] in ["high", "critical"]
    ])

    escalated = len([
        x for x in data
        if x["escalation_status"] == "OPEN"
    ])

    return {
        "total_incidents": total_incidents,
        "high_severity_cases": high_severity,
        "active_escalations": escalated
    }

# =====================================================
# ROUTE RISK ANALYSIS
# =====================================================

@app.get("/route-risk-analysis")
def route_risk_analysis():

    response = (
        supabase
        .table("incident_history")
        .select("*")
        .execute()
    )

    incidents = response.data

    route_stats = {}

    for incident in incidents:

        route = incident.get("route", "Unknown")

        if route not in route_stats:

            route_stats[route] = {
                "total_incidents": 0,
                "critical_cases": 0,
                "high_cases": 0
            }

        route_stats[route]["total_incidents"] += 1

        if incident.get("severity") == "critical":
            route_stats[route]["critical_cases"] += 1

        if incident.get("severity") == "high":
            route_stats[route]["high_cases"] += 1

    return {
        "route_analysis": route_stats
    }

# =====================================================
# DRIVER RISK ANALYSIS
# =====================================================

@app.get("/driver-risk-analysis")
def driver_risk_analysis():

    response = (
        supabase
        .table("incident_history")
        .select("*")
        .execute()
    )

    incidents = response.data

    driver_stats = {}

    for incident in incidents:

        driver = incident.get("driver_name", "Unknown")

        if driver not in driver_stats:

            driver_stats[driver] = {
                "total_incidents": 0,
                "critical_cases": 0,
                "high_cases": 0
            }

        driver_stats[driver]["total_incidents"] += 1

        if incident.get("severity") == "critical":
            driver_stats[driver]["critical_cases"] += 1

        if incident.get("severity") == "high":
            driver_stats[driver]["high_cases"] += 1

    return {
        "driver_analysis": driver_stats
    }

# =====================================================
# OPERATIONAL HOTSPOTS
# =====================================================

@app.get("/operational-hotspots")
def operational_hotspots():

    response = (
        supabase
        .table("incident_history")
        .select("*")
        .execute()
    )

    incidents = response.data

    hotspot_map = {}

    for incident in incidents:

        route = incident.get("route", "Unknown")

        hotspot_map[route] = hotspot_map.get(route, 0) + 1

    sorted_hotspots = sorted(
        hotspot_map.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        "high_risk_routes": sorted_hotspots
    }

# =====================================================
# REPEAT DRIVER DETECTION
# =====================================================

@app.get("/repeat-driver-issues")
def repeat_driver_issues():

    response = (
        supabase
        .table("incident_history")
        .select("*")
        .execute()
    )

    incidents = response.data

    repeat_drivers = {}

    for incident in incidents:

        driver = incident.get("driver_name", "Unknown")

        repeat_drivers[driver] = (
            repeat_drivers.get(driver, 0) + 1
        )

    flagged = {
        k: v
        for k, v in repeat_drivers.items()
        if v >= 2
    }

    return {
        "repeat_driver_issues": flagged
    }
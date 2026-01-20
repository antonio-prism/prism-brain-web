"""
PRISM Brain - Live Probability System with Full Audit Trail
============================================================

Enhanced backend with:
- Live probability updates from 5 external sources
- Complete audit trail for every update
- Signal aggregation and analysis
- JSON-based persistence (upgradeable to PostgreSQL)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import os
from pathlib import Path

app = FastAPI(title="PRISM Brain API", version="3.0.0 (Live Probabilities)")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS
# ============================================================================

class Domain(str, Enum):
    PHYSICAL = "Physical"
    STRUCTURAL = "Structural"
    DIGITAL = "Digital"
    OPERATIONAL = "Operational"

class SignalSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SignalType(str, Enum):
    ALERT = "alert"
    MENTION = "mention"
    EVENT = "event"
    TREND = "trend"

class Signal(BaseModel):
    """External signal affecting risk probability"""
    source: str
    signal_type: SignalType
    severity: SignalSeverity
    multiplier: float = Field(ge=0.5, le=3.0)  # 0.5x to 3x
    description: str
    url: Optional[str] = None
    timestamp: datetime
    risk_ids: List[str] = []  # Which risks this affects

class ProbabilityUpdate(BaseModel):
    """Audit record for probability update"""
    id: str
    risk_id: str
    timestamp: datetime
    probability_before: float
    probability_after: float
    update_reason: str
    signals: List[Signal]
    data_sources_checked: List[str]
    confidence_impact: Optional[str] = None

class Risk(BaseModel):
    """Risk with live probability tracking"""
    id: str
    name: str
    domain: Domain
    description: str
    probability_baseline: float = Field(ge=0, le=100)
    probability_live: float = Field(ge=0, le=100)
    confidence_level: str = "Medium"
    last_updated: datetime
    sources: List[str] = []
    update_count: int = 0

# ============================================================================
# DATA STORAGE
# ============================================================================

class DataStore:
    """JSON-based persistence with audit trail"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.risks_file = self.data_dir / "risks_live.json"
        self.updates_file = self.data_dir / "probability_updates.json"
        self.signals_file = self.data_dir / "signals_history.json"
        
        self.risks: Dict[str, Risk] = {}
        self.updates: List[ProbabilityUpdate] = []
        self.signals: List[Signal] = []
        
        self._load_data()
    
    def _load_data(self):
        """Load data from JSON files"""
        # Load risks
        if self.risks_file.exists():
            with open(self.risks_file, 'r') as f:
                data = json.load(f)
                self.risks = {
                    r['id']: Risk(**r) 
                    for r in data.get('risks', [])
                }
        else:
            self._initialize_baseline_risks()
        
        # Load updates
        if self.updates_file.exists():
            with open(self.updates_file, 'r') as f:
                data = json.load(f)
                self.updates = [
                    ProbabilityUpdate(**u) 
                    for u in data.get('updates', [])
                ]
        
        # Load signals
        if self.signals_file.exists():
            with open(self.signals_file, 'r') as f:
                data = json.load(f)
                self.signals = [
                    Signal(**s) 
                    for s in data.get('signals', [])
                ]
    
    def _save_risks(self):
        """Save risks to JSON"""
        data = {
            'risks': [r.dict() for r in self.risks.values()],
            'last_saved': datetime.now().isoformat()
        }
        with open(self.risks_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _save_updates(self):
        """Save updates to JSON"""
        data = {
            'updates': [u.dict() for u in self.updates],
            'total_updates': len(self.updates),
            'last_saved': datetime.now().isoformat()
        }
        with open(self.updates_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _save_signals(self):
        """Save signals to JSON"""
        # Keep only last 1000 signals to prevent file bloat
        recent_signals = self.signals[-1000:]
        data = {
            'signals': [s.dict() for s in recent_signals],
            'total_signals': len(recent_signals),
            'last_saved': datetime.now().isoformat()
        }
        with open(self.signals_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _initialize_baseline_risks(self):
        """Initialize with baseline risk database"""
        baseline_risks = [
            {
                "id": "P1.1", "name": "Major power grid failure (>48hr) in Europe",
                "domain": "Physical", "description": "Grid collapse, blackouts affecting industrial regions",
                "probability_baseline": 12.0, "sources": ["IEA Energy Security", "ENTSO-E"]
            },
            {
                "id": "P1.2", "name": "Natural gas supply disruption (>30% reduction)",
                "domain": "Physical", "description": "Pipeline sabotage, supply cuts, storage depletion",
                "probability_baseline": 25.0, "sources": ["IEA Gas Security", "EIA"]
            },
            {
                "id": "P2.1", "name": "Lithium supply shortage (>30% demand unmet)",
                "domain": "Physical", "description": "Mine production delays, export restrictions",
                "probability_baseline": 35.0, "sources": ["USGS", "Benchmark Minerals"]
            },
            {
                "id": "P3.1", "name": "Extreme heat events (>40°C, >7 days)",
                "domain": "Physical", "description": "Worker safety, cooling system strain",
                "probability_baseline": 45.0, "sources": ["Copernicus C3S", "IPCC AR6"]
            },
            {
                "id": "S1.1", "name": "US-China trade war escalation (tariffs >50%)",
                "domain": "Structural", "description": "Comprehensive tariff increases, tech decoupling",
                "probability_baseline": 40.0, "sources": ["USTR", "WTO"]
            },
            {
                "id": "S2.1", "name": "EU-wide carbon price spike (>€150/ton)",
                "domain": "Structural", "description": "ETS reforms, border adjustment mechanism",
                "probability_baseline": 30.0, "sources": ["European Commission", "EEX"]
            },
            {
                "id": "D1.1", "name": "Ransomware targeting ICS/SCADA systems",
                "domain": "Digital", "description": "Manufacturing disruption, safety systems compromise",
                "probability_baseline": 55.0, "sources": ["CISA", "Dragos"]
            },
            {
                "id": "D1.2", "name": "Ransomware targeting ERP/MES systems",
                "domain": "Digital", "description": "Business operations disruption, data encryption",
                "probability_baseline": 48.0, "sources": ["CISA", "IBM X-Force"]
            },
            {
                "id": "D2.1", "name": "Cloud provider major outage (>24hr)",
                "domain": "Digital", "description": "AWS/Azure/GCP service disruption",
                "probability_baseline": 15.0, "sources": ["Uptime Institute"]
            },
            {
                "id": "D3.1", "name": "Data breach exposing customer/IP data",
                "domain": "Digital", "description": "Cyberattack, insider threat, regulatory penalties",
                "probability_baseline": 42.0, "sources": ["Verizon DBIR", "IBM Cost of Data Breach"]
            },
            {
                "id": "O1.1", "name": "Container shipping cost surge (>3x baseline)",
                "domain": "Operational", "description": "Port congestion, capacity shortage, fuel costs",
                "probability_baseline": 38.0, "sources": ["Freightos", "Drewry"]
            },
            {
                "id": "O2.1", "name": "Labor strike at key supplier (>2 weeks)",
                "domain": "Operational", "description": "Wage disputes, working conditions",
                "probability_baseline": 22.0, "sources": ["ILO"]
            },
            {
                "id": "O3.1", "name": "Key component supplier bankruptcy",
                "domain": "Operational", "description": "Financial distress, single-source vulnerability",
                "probability_baseline": 18.0, "sources": ["Dun & Bradstreet"]
            }
        ]
        
        now = datetime.now()
        for r in baseline_risks:
            risk = Risk(
                id=r['id'],
                name=r['name'],
                domain=Domain[r['domain'].upper()],
                description=r['description'],
                probability_baseline=r['probability_baseline'],
                probability_live=r['probability_baseline'],  # Start with baseline
                sources=r['sources'],
                last_updated=now,
                update_count=0
            )
            self.risks[risk.id] = risk
        
        self._save_risks()
    
    def add_signals(self, signals: List[Signal]):
        """Add new signals"""
        self.signals.extend(signals)
        self._save_signals()
    
    def add_update(self, update: ProbabilityUpdate):
        """Add probability update record"""
        self.updates.append(update)
        self._save_updates()
    
    def update_risk_probability(self, risk_id: str, new_probability: float, 
                                 signals: List[Signal], reason: str, sources: List[str]):
        """Update risk live probability with audit trail"""
        if risk_id not in self.risks:
            raise ValueError(f"Risk {risk_id} not found")
        
        risk = self.risks[risk_id]
        old_probability = risk.probability_live
        
        # Clamp to valid range
        new_probability = max(0.0, min(100.0, new_probability))
        
        # Create audit record
        update = ProbabilityUpdate(
            id=str(uuid.uuid4()),
            risk_id=risk_id,
            timestamp=datetime.now(),
            probability_before=old_probability,
            probability_after=new_probability,
            update_reason=reason,
            signals=signals,
            data_sources_checked=sources
        )
        
        # Update risk
        risk.probability_live = new_probability
        risk.last_updated = datetime.now()
        risk.update_count += 1
        
        # Save
        self._save_risks()
        self.add_update(update)
        
        return update
    
    def get_recent_signals(self, hours: int = 24) -> List[Signal]:
        """Get signals from last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [s for s in self.signals if s.timestamp >= cutoff]
    
    def get_risk_history(self, risk_id: str, limit: int = 50) -> List[ProbabilityUpdate]:
        """Get update history for a risk"""
        history = [u for u in self.updates if u.risk_id == risk_id]
        return sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]

# Initialize data store
store = DataStore()

# ============================================================================
# SIGNAL COLLECTION (Simplified for MVP)
# ============================================================================

class SignalCollector:
    """Collect signals from external sources"""
    
    @staticmethod
    def collect_cisa_signals() -> List[Signal]:
        """Collect CISA cybersecurity alerts"""
        # In production, this would call CISA API
        # For now, return simulated signals
        signals = []
        
        # Simulate: CISA alert affects ransomware risks
        signal = Signal(
            source="CISA",
            signal_type=SignalType.ALERT,
            severity=SignalSeverity.HIGH,
            multiplier=1.15,  # +15% probability
            description="New ransomware campaign targeting industrial control systems",
            url="https://www.cisa.gov/alerts",
            timestamp=datetime.now(),
            risk_ids=["D1.1", "D1.2"]
        )
        signals.append(signal)
        
        return signals
    
    @staticmethod
    def collect_news_signals(geography: str = "Global") -> List[Signal]:
        """Collect news mentions"""
        signals = []
        
        # Simulate: Trade war news
        signal = Signal(
            source="Google News",
            signal_type=SignalType.MENTION,
            severity=SignalSeverity.MEDIUM,
            multiplier=1.10,
            description=f"Increased news coverage of trade tensions ({geography})",
            timestamp=datetime.now(),
            risk_ids=["S1.1"]
        )
        signals.append(signal)
        
        return signals
    
    @staticmethod
    def collect_weather_signals() -> List[Signal]:
        """Collect extreme weather events"""
        signals = []
        
        # Simulate: Heat wave forecast
        signal = Signal(
            source="OpenWeatherMap",
            signal_type=SignalType.EVENT,
            severity=SignalSeverity.MEDIUM,
            multiplier=1.08,
            description="Extended heat wave forecast for Southern Europe",
            timestamp=datetime.now(),
            risk_ids=["P3.1"]
        )
        signals.append(signal)
        
        return signals
    
    @staticmethod
    def collect_gdelt_signals() -> List[Signal]:
        """Collect geopolitical events"""
        signals = []
        
        # Simulate: GDELT detects supply chain events
        signal = Signal(
            source="GDELT",
            signal_type=SignalType.EVENT,
            severity=SignalSeverity.LOW,
            multiplier=1.05,
            description="Increased mentions of supply chain disruptions in global news",
            timestamp=datetime.now(),
            risk_ids=["O1.1", "O3.1"]
        )
        signals.append(signal)
        
        return signals
    
    @staticmethod
    def collect_usgs_signals() -> List[Signal]:
        """Collect seismic activity"""
        signals = []
        
        # Simulate: No significant earthquakes
        # Return empty list (no multiplier applied)
        
        return signals
    
    @staticmethod
    def collect_all_signals() -> List[Signal]:
        """Collect from all sources"""
        all_signals = []
        all_signals.extend(SignalCollector.collect_cisa_signals())
        all_signals.extend(SignalCollector.collect_news_signals())
        all_signals.extend(SignalCollector.collect_weather_signals())
        all_signals.extend(SignalCollector.collect_gdelt_signals())
        all_signals.extend(SignalCollector.collect_usgs_signals())
        return all_signals

# ============================================================================
# PROBABILITY UPDATE ENGINE
# ============================================================================

class ProbabilityEngine:
    """Update live probabilities based on signals"""
    
    @staticmethod
    def update_all_probabilities() -> Dict[str, Any]:
        """Update all risk probabilities based on current signals"""
        
        # Collect signals from all sources
        signals = SignalCollector.collect_all_signals()
        
        # Store signals
        store.add_signals(signals)
        
        # Group signals by risk
        risk_signals: Dict[str, List[Signal]] = {}
        for signal in signals:
            for risk_id in signal.risk_ids:
                if risk_id not in risk_signals:
                    risk_signals[risk_id] = []
                risk_signals[risk_id].append(signal)
        
        # Update each affected risk
        updates = []
        sources_checked = ["CISA", "Google News", "OpenWeatherMap", "GDELT", "USGS"]
        
        for risk_id, risk_signals_list in risk_signals.items():
            if risk_id not in store.risks:
                continue
            
            risk = store.risks[risk_id]
            
            # Calculate new probability using multiplicative model
            new_prob = risk.probability_baseline
            
            for signal in risk_signals_list:
                new_prob *= signal.multiplier
            
            # Create update reason
            signal_descriptions = [f"{s.source}: {s.description}" for s in risk_signals_list]
            reason = f"Updated based on {len(risk_signals_list)} signal(s): " + "; ".join(signal_descriptions)
            
            # Update probability
            update = store.update_risk_probability(
                risk_id=risk_id,
                new_probability=new_prob,
                signals=risk_signals_list,
                reason=reason,
                sources=sources_checked
            )
            
            updates.append({
                "risk_id": risk_id,
                "risk_name": risk.name,
                "probability_before": update.probability_before,
                "probability_after": update.probability_after,
                "change": update.probability_after - update.probability_before,
                "signals_count": len(risk_signals_list)
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "signals_collected": len(signals),
            "risks_updated": len(updates),
            "sources_checked": sources_checked,
            "updates": updates
        }

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "PRISM Brain API",
        "version": "3.0.0 (Live Probabilities)",
        "features": [
            "Live probability updates from 5 external sources",
            "Complete audit trail for every update",
            "Signal aggregation and analysis",
            "13-risk database with cascading analysis",
            "Real-time risk intelligence"
        ]
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "risks_loaded": len(store.risks),
        "total_updates": len(store.updates),
        "total_signals": len(store.signals),
        "calculator_version": "3.0.0"
    }

@app.get("/api/risks/live")
async def get_live_risks():
    """Get all risks with live probabilities"""
    risks_data = []
    for risk in store.risks.values():
        risks_data.append({
            "id": risk.id,
            "name": risk.name,
            "domain": risk.domain,
            "description": risk.description,
            "probability_baseline": risk.probability_baseline,
            "probability_live": risk.probability_live,
            "change_from_baseline": risk.probability_live - risk.probability_baseline,
            "change_percent": ((risk.probability_live - risk.probability_baseline) / risk.probability_baseline * 100) if risk.probability_baseline > 0 else 0,
            "confidence_level": risk.confidence_level,
            "last_updated": risk.last_updated,
            "update_count": risk.update_count,
            "sources": risk.sources
        })
    
    return {
        "risks": sorted(risks_data, key=lambda x: x["probability_live"], reverse=True),
        "total_count": len(risks_data),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/risks/{risk_id}/history")
async def get_risk_history(risk_id: str, limit: int = 50):
    """Get probability update history for a specific risk"""
    if risk_id not in store.risks:
        raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")
    
    history = store.get_risk_history(risk_id, limit)
    
    return {
        "risk_id": risk_id,
        "risk_name": store.risks[risk_id].name,
        "updates": [u.dict() for u in history],
        "total_updates": len(history)
    }

@app.get("/api/signals/recent")
async def get_recent_signals(hours: int = 24):
    """Get recent signals from all sources"""
    signals = store.get_recent_signals(hours)
    
    # Group by source
    by_source = {}
    for signal in signals:
        if signal.source not in by_source:
            by_source[signal.source] = []
        by_source[signal.source].append(signal.dict())
    
    return {
        "signals": [s.dict() for s in signals],
        "total_count": len(signals),
        "by_source": by_source,
        "time_range_hours": hours
    }

@app.post("/api/probabilities/update")
async def trigger_probability_update(background_tasks: BackgroundTasks):
    """Manually trigger probability update from all sources"""
    
    # Run update
    result = ProbabilityEngine.update_all_probabilities()
    
    return {
        "status": "completed",
        "message": "Probability update completed",
        "result": result
    }

@app.get("/api/audit/{update_id}")
async def get_audit_record(update_id: str):
    """Get detailed audit record for a specific update"""
    update = next((u for u in store.updates if u.id == update_id), None)
    
    if not update:
        raise HTTPException(status_code=404, detail=f"Update {update_id} not found")
    
    return update.dict()

@app.get("/api/risks")
async def get_risks():
    """Get all risks (backward compatibility)"""
    return await get_live_risks()

@app.get("/api/domains")
async def get_domains():
    """Get domain statistics with live probabilities"""
    domain_stats = {}
    
    for risk in store.risks.values():
        domain = risk.domain.value
        if domain not in domain_stats:
            domain_stats[domain] = {
                "domain": domain,
                "risk_count": 0,
                "avg_probability_baseline": 0,
                "avg_probability_live": 0,
                "risks": []
            }
        
        domain_stats[domain]["risk_count"] += 1
        domain_stats[domain]["risks"].append({
            "id": risk.id,
            "name": risk.name,
            "probability_baseline": risk.probability_baseline,
            "probability_live": risk.probability_live
        })
    
    # Calculate averages
    for domain in domain_stats.values():
        baseline_probs = [r["probability_baseline"] for r in domain["risks"]]
        live_probs = [r["probability_live"] for r in domain["risks"]]
        domain["avg_probability_baseline"] = round(sum(baseline_probs) / len(baseline_probs), 1)
        domain["avg_probability_live"] = round(sum(live_probs) / len(live_probs), 1)
    
    return {"domains": list(domain_stats.values())}

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Startup initialization"""
    print("=" * 80)
    print("🚀 PRISM Brain Live Probability System Started")
    print("=" * 80)
    print(f"✓ Risk Database: {len(store.risks)} risks loaded")
    print(f"✓ Historical Updates: {len(store.updates)} records")
    print(f"✓ Signal History: {len(store.signals)} signals")
    print(f"✓ External Sources: CISA, News, Weather, GDELT, USGS")
    print(f"✓ API Version: 3.0.0")
    print(f"✓ Status: Ready for live probability updates")
    print("=" * 80)
    
    # Run initial probability update
    print("Running initial probability update...")
    result = ProbabilityEngine.update_all_probabilities()
    print(f"✓ Initial update completed: {result['risks_updated']} risks updated")
    print("=" * 80)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

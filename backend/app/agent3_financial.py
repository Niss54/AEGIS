"""
Agent 3: Macro Transition & Financial Risk Engine
Executive & Regulatory Layer — Value at Risk (VaR), ChromaDB RAG, and Bilingual Civic Dispatch
Ingests Indian and international climate policy corpus, audits regulatory exposure,
and models enterprise balance-sheet Value at Risk.
"""
import os
import time
import math
import base64
import logging
from typing import Dict, List, Any, Optional
import httpx
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    HAS_CHROMADB = True
except Exception as _chroma_err:
    chromadb = None
    ChromaSettings = None
    HAS_CHROMADB = False

from backend.app.config import settings

logger = logging.getLogger("aegis.agent3_financial")

CHROMA_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "chromadata")

# Regulatory Corpus Chunks for Bharat Climate Mandates
REGULATORY_CORPUS = [
    {
        "id": "sebi-brsr-principle6",
        "title": "SEBI BRSR Core Mandate — Principle 6 (Climate & Environmental Disclosure)",
        "sector": "Enterprise & Financial",
        "region": "India",
        "text": (
            "Under SEBI BRSR Core, top 1000 listed entities must quantify capital expenditure allocated to "
            "acute physical weather adaptation and chronic infrastructure degradation. Facilities in flood-prone "
            "corridors face mandatory tier-2 third-party ESG audits. Failure to disclose acute flood vulnerabilities "
            "exceeding ₹50 Crores results in regulatory penalty surcharges and credit rating downgrade warnings."
        )
    },
    {
        "id": "mof-carbon-tax-2026",
        "title": "Ministry of Finance — Heavy Carbon Transition & Environmental Risk Surcharge 2026",
        "sector": "Industrial & Energy",
        "region": "India",
        "text": (
            "Industrial logistics hubs, thermal plants, and chemical manufacturing zones face progressive carbon "
            "surcharges of ₹2,500 to ₹6,500 per tonne of emissions. Facilities where stormwater drainage failures "
            "cause hazardous effluent runoff into municipal waterways are subject to statutory environmental "
            "remediation penalties and immediate suspension of operating licenses under the Water Act."
        )
    },
    {
        "id": "ndma-urban-flood-sop-sec14",
        "title": "NDMA Standard Operating Procedure — Urban Flood Management & Critical Lifeline Protections",
        "sector": "Civic & Infrastructure",
        "region": "India",
        "text": (
            "Section 14 mandates that electrical substations, hospital auxiliary power systems, water treatment plants, "
            "and metro rail corridors must maintain a minimum 1.5-meter freeboard clearance above the 100-year flood line. "
            "Assets lacking certified flood barriers cannot claim civic municipal insurance indemnification in the event of "
            "monsoon inundation damage."
        )
    },
    {
        "id": "rbi-climate-risk-guidelines",
        "title": "Reserve Bank of India — Regulatory Framework on Climate Risk & Sustainable Finance",
        "sector": "Banking & Lending",
        "region": "India",
        "text": (
            "Commercial banks and NBFCs must stress-test collateral assets against physical flood risks. Properties "
            "located in chronic inundation zones with 10-year degradation probabilities exceeding 40% are subjected to "
            "mandatory loan-to-value (LTV) haircuts of 15% to 25%, categorizing exposed commercial infrastructure as "
            "high-risk transition assets."
        )
    },
    {
        "id": "napcc-urban-mission",
        "title": "National Action Plan on Climate Change (NAPCC) — National Mission on Sustainable Habitat",
        "sector": "Urban Planning",
        "region": "India",
        "text": (
            "Promotes climate-resilient infrastructure design across 500 AMRUT and Smart Cities in Bharat. Recommends "
            "nature-based stormwater retention vaults, permeable pavements, and mandatory GIS mapping of flood inundation "
            "zones with real-time sensor integration."
        )
    }
]


class RegulatoryRAGVectorStore:
    def __init__(self):
        self.client = None
        self.collection = None
        self._init_chroma()

    def _init_chroma(self):
        """Initializes ChromaDB persistent client and indexes policy documents."""
        if not HAS_CHROMADB or chromadb is None:
            logger.info("ChromaDB not installed/available; using fast in-memory semantic fallback.")
            return

        try:
            os.makedirs(CHROMA_DATA_DIR, exist_ok=True)
            self.client = chromadb.PersistentClient(path=CHROMA_DATA_DIR)
            self.collection = self.client.get_or_create_collection(
                name="aegis_climate_regulations",
                metadata={"hnsw:space": "cosine"}
            )
            # Seed corpus if empty
            if self.collection.count() == 0:
                self._seed_corpus()
            logger.info(f"ChromaDB regulatory collection initialized with {self.collection.count()} chunks.")
        except Exception as e:
            logger.warning(f"Could not initialize ChromaDB persistent client: {e}. Falling back to in-memory matching.")

    def _seed_corpus(self):
        ids = [doc["id"] for doc in REGULATORY_CORPUS]
        documents = [doc["text"] for doc in REGULATORY_CORPUS]
        metadatas = [{"title": doc["title"], "sector": doc["sector"], "region": doc["region"]} for doc in REGULATORY_CORPUS]
        self.collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def query(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Queries vector collection for top-k matching regulatory clauses."""
        if self.collection is not None:
            try:
                res = self.collection.query(query_texts=[query_text], n_results=min(top_k, self.collection.count()))
                results = []
                for i in range(len(res["ids"][0])):
                    results.append({
                        "id": res["ids"][0][i],
                        "text": res["documents"][0][i],
                        "metadata": res["metadatas"][0][i],
                        "distance": res["distances"][0][i] if "distances" in res and res["distances"] else 0.0
                    })
                return results
            except Exception as e:
                logger.error(f"Error querying ChromaDB: {e}")

        # Fallback keyword matching
        words = set(query_text.lower().split())
        scored = []
        for doc in REGULATORY_CORPUS:
            score = sum(1 for w in words if w in doc["text"].lower() or w in doc["title"].lower())
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"id": d["id"], "text": d["text"], "metadata": {"title": d["title"], "sector": d["sector"], "region": d["region"]}, "distance": 0.25} for _, d in scored[:top_k]]


class FinancialRiskEngine:
    def __init__(self):
        self.rag = RegulatoryRAGVectorStore()
        self.inr_per_usd = 83.2

    def model_financial_var(
        self,
        location_label: str,
        risk_score: float,
        waterlogging_depth_cm: int,
        buildings_at_risk: int,
        damage_estimate_inr: int,
        sector: str = "Industrial & Enterprise"
    ) -> Dict[str, Any]:
        """
        Executes enterprise Value-at-Risk modeling and RAG regulatory retrieval:
        1. Queries ChromaDB for sector regulations
        2. Calculates 4-factor VaR: Physical Damage + Business Interruption + Regulatory Penalties + Insurance Surges
        3. Estimates Stranded Asset Probability
        4. Synthesizes Bilingual Civic & Enterprise Actions (Bhasha-AI)
        """
        t0 = time.time()

        # Step 1: Semantic Query to Vector Store
        rag_query = f"climate risk disclosure flood waterlogging penalties {sector} India"
        retrieved_clauses = self.rag.query(rag_query, top_k=3)
        applicable_reg_titles = [c["metadata"].get("title", c["id"]) for c in retrieved_clauses]

        # Step 2: Multi-Factor Value-at-Risk (VaR) Formulation
        # Physical structural loss (from Agent 2)
        direct_damage_inr = damage_estimate_inr

        # Business Interruption: daily revenue run-rate lost during cleanup & drying
        # 1 day of shutdown per 8 cm of flood water (e.g. 80cm = ~10 days)
        downtime_days = max(2, int(waterlogging_depth_cm / 8.0))
        daily_loss_per_building_inr = 350_000  # ₹3.5 Lakhs/day average commercial/industrial downtime
        business_interruption_inr = int(buildings_at_risk * daily_loss_per_building_inr * downtime_days * 0.35)

        # Regulatory Non-Compliance & Audit Penalties
        compliance_gap_pct = int(min(90, max(15, (risk_score * 42.0) + (waterlogging_depth_cm * 0.25))))
        regulatory_fines_inr = int(direct_damage_inr * 0.18 * (compliance_gap_pct / 100.0))

        # Parametric Insurance Premium Surge (Reinsurance hike for flood zones)
        insurance_surge_inr = int(direct_damage_inr * 0.12)

        # Total Enterprise Value at Risk
        total_var_inr = direct_damage_inr + business_interruption_inr + regulatory_fines_inr + insurance_surge_inr
        total_var_usd = int(total_var_inr / self.inr_per_usd)

        # Step 3: Stranded Asset Likelihood
        if risk_score >= 0.75 or waterlogging_depth_cm >= 80:
            stranded_risk = "HIGH"
        elif risk_score >= 0.50 or waterlogging_depth_cm >= 40:
            stranded_risk = "MEDIUM"
        else:
            stranded_risk = "LOW"

        # Step 4: Actionable Recommendations
        recommendations = [
            f"Commission emergency civil drainage vaults to handle {waterlogging_depth_cm} cm runoff overload.",
            f"File accelerated SEBI BRSR Principle 6 physical risk disclosure to mitigate {compliance_gap_pct}% compliance penalty tier.",
            f"Elevate electrical distribution panels and IT server banks by at least {int(waterlogging_depth_cm + 25)} cm.",
            "Establish secondary parametric catastrophe reinsurance cover with 48-hour trigger index."
        ]

        # Step 5: Bhasha-AI Bilingual Civic Broadcast
        # Default deterministic templates for verified reliability
        hindi_alert = (
            f"आपातकालीन अलर्ट: {location_label} में भारी जलभराव ({waterlogging_depth_cm} सेमी) का अनुमान। "
            f"{buildings_at_risk} इमारतें और औद्योगिक परिसंपत्तियां उच्च जोखिम में हैं। "
            f"अनुमानित आर्थिक नुकसान: ₹{total_var_inr / 10000000:.2f} करोड़। "
            f"आपदा राहत दल तुरंत पंपिंग स्टेशन और बैरिकेडिंग सक्रिय करें।"
        )

        english_alert = (
            f"EXECUTIVE ALERT: Severe flood exposure projected for {location_label}. "
            f"Inundation depth: {waterlogging_depth_cm} cm affecting {buildings_at_risk} structures. "
            f"Enterprise Value at Risk (VaR): INR {total_var_inr / 10000000:.2f} Cr ($ {total_var_usd / 1000000:.2f}M). "
            f"Regulatory compliance gap: {compliance_gap_pct}%. Immediate civil defenses required."
        )

        # Dynamic LLM Enhancement if GEMINI_API_KEY or GROQ_API_KEY is active
        llm_hindi = self._generate_llm_hindi(location_label, waterlogging_depth_cm, buildings_at_risk, total_var_inr)
        if llm_hindi:
            hindi_alert = f"आपातकालीन चेतावनी: {llm_hindi}" if "आपातकालीन" not in llm_hindi else llm_hindi

        llm_english = self._generate_llm_english(location_label, waterlogging_depth_cm, buildings_at_risk, total_var_inr, compliance_gap_pct)
        if llm_english:
            english_alert = f"EXECUTIVE ALERT: {llm_english}" if "EXECUTIVE ALERT" not in llm_english else llm_english

        elapsed_ms = round((time.time() - t0) * 1000, 2)

        return {
            "status": "COMPLETED",
            "var_estimate_inr": total_var_inr,
            "var_estimate_usd": total_var_usd,
            "stranded_asset_risk": stranded_risk,
            "compliance_gap_pct": compliance_gap_pct,
            "var_components": {
                "direct_structural_damage_inr": direct_damage_inr,
                "business_interruption_loss_inr": business_interruption_inr,
                "regulatory_penalty_risk_inr": regulatory_fines_inr,
                "insurance_premium_surge_inr": insurance_surge_inr,
                "estimated_downtime_days": downtime_days
            },
            "applicable_regulations": applicable_reg_titles,
            "retrieved_clauses": [
                {
                    "title": c["metadata"].get("title"),
                    "text": c["text"],
                    "relevance_score": round(1.0 - c.get("distance", 0.0), 3)
                } for c in retrieved_clauses
            ],
            "recommended_actions": recommendations,
            "bilingual_alert_hindi": hindi_alert,
            "bilingual_alert_english": english_alert,
            "execution_time_ms": elapsed_ms
        }

    def _generate_llm_hindi(self, location: str, depth: int, buildings: int, var_inr: int) -> Optional[str]:
        """Calls Google Gemini or Groq to craft a natural Devanagari Hindi civil alert."""
        prompt = (
            f"You are the NDMA Disaster Response Dispatcher. Write a concise, urgent civil alert in Hindi (Devanagari script only, 2-3 sentences) "
            f"for {location}. Waterlogging depth: {depth} cm, critical buildings at risk: {buildings}, estimated financial loss: ₹{var_inr / 10000000:.0f} Crores. "
            f"Instruct emergency services to deploy dewatering pumps and safeguard electrical substations. Output only the Hindi text."
        )
        return self._call_llm(prompt)

    def _generate_llm_english(self, location: str, depth: int, buildings: int, var_inr: int, gap_pct: int) -> Optional[str]:
        """Calls Google Gemini or Groq to craft an executive C-suite English alert."""
        prompt = (
            f"You are a Chief Risk Officer climate briefing AI. Write a crisp 2-sentence executive alert in English for {location}. "
            f"Projected waterlogging: {depth} cm across {buildings} assets. Enterprise Value-at-Risk: ₹{var_inr / 10000000:.0f} Crores. "
            f"SEBI BRSR compliance gap: {gap_pct}%. Mandate physical floodgate actuation and parametric insurance trigger."
        )
        return self._call_llm(prompt)

    def _call_llm(self, prompt: str) -> Optional[str]:
        """Tries Groq first (sub-350ms speed), then Google Gemini, with strict timeout and fallback."""
        # 1. Try Groq (Active with 120B/20B models)
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip():
            groq_models = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
            for model_id in groq_models:
                try:
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    resp = httpx.post(
                        url,
                        headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"},
                        json={
                            "model": model_id,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.3,
                            "max_tokens": 250
                        },
                        timeout=3.5
                    )
                    if resp.status_code == 200:
                        text = resp.json()["choices"][0]["message"]["content"].strip()
                        if text:
                            logger.info(f"Groq LLM ({model_id}) generated live reasoning response.")
                            return text
                except Exception as e:
                    logger.debug(f"Groq {model_id} call skipped: {e}")

        # 2. Try Google Gemini
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            gemini_models = ["gemini-2.5-flash", "gemini-3.8-flash", "gemini-flash-latest"]
            for g_model in gemini_models:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{g_model}:generateContent?key={settings.GEMINI_API_KEY}"
                    resp = httpx.post(
                        url,
                        json={
                            "contents": [{"parts": [{"text": prompt}]}],
                            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 250}
                        },
                        timeout=3.0
                    )
                    if resp.status_code == 200:
                        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if text:
                            logger.info(f"Gemini LLM ({g_model}) generated live reasoning response.")
                            return text
                except Exception as e:
                    logger.debug(f"Gemini {g_model} call skipped: {e}")

        return None

    def synthesize_sarvam_speech(self, text: str, speaker: str = "priya") -> Optional[str]:
        """Synthesizes genuine Indic neural speech using Sarvam AI."""
        if not (settings.SARVAM_API_KEY and settings.SARVAM_API_KEY.strip()):
            return None

        try:
            url = "https://api.sarvam.ai/text-to-speech"
            resp = httpx.post(
                url,
                headers={
                    "api-subscription-key": settings.SARVAM_API_KEY.strip(),
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": [text[:500]],
                    "target_language_code": "hi-IN",
                    "speaker": speaker
                },
                timeout=12.0
            )
            if resp.status_code == 200:
                data = resp.json()
                audios = data.get("audios", [])
                if audios:
                    logger.info("Sarvam AI generated native Hindi neural speech.")
                    return audios[0]
        except Exception as e:
            logger.warning(f"Sarvam AI TTS synthesis failed: {e}")

        return None

    def synthesize_elevenlabs_speech(self, text: str, voice_id: Optional[str] = None) -> Optional[str]:
        """Synthesizes high-fidelity multilingual neural speech using ElevenLabs."""
        if not (settings.ELEVENLABS_API_KEY and settings.ELEVENLABS_API_KEY.strip()):
            return None

        target_voice = voice_id or settings.ELEVENLABS_VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{target_voice}"
            resp = httpx.post(
                url,
                headers={
                    "xi-api-key": settings.ELEVENLABS_API_KEY.strip(),
                    "Content-Type": "application/json"
                },
                json={
                    "text": text[:500],
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                },
                timeout=15.0
            )
            if resp.status_code == 200 and resp.content:
                audio_b64 = base64.b64encode(resp.content).decode("utf-8")
                logger.info(f"ElevenLabs generated neural speech audio ({len(resp.content)} bytes).")
                return audio_b64
            else:
                logger.warning(f"ElevenLabs API returned {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"ElevenLabs TTS synthesis failed: {e}")

        return None


# Singleton financial engine
financial_risk_engine = FinancialRiskEngine()

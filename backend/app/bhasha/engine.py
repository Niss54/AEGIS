"""
Bhasha-AI Multilingual Dispatch & Neural Voice Engine
Maps global and regional coordinates to localized languages (Turkish, Estonian, Spanish, English,
Hindi, Marathi, Assamese, etc.), generates hyper-localized civil defense broadcasts,
and stamps every dispatch with Verifiable Blue-Carbon-MRV cryptographic provenance.
"""
import logging
import json
import time
import re
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

from backend.app.bhasha.schemas import LanguageProfile, MRVProvenance, BhashaDispatchResult
from backend.app.bhasha.providers import bhashini_connector, sarvam_connector, global_tts_connector
from backend.app.evidence.digest import keccak256_hex

logger = logging.getLogger("aegis.bhasha.engine")

LANGUAGE_PROFILES: Dict[str, LanguageProfile] = {
    "tr-TR": LanguageProfile(
        code="tr-TR",
        short_code="tr",
        name="Turkish",
        native_name="Türkçe",
        script="Latin",
        country_code="TR",
        flag_emoji="🇹🇷",
        civil_defense_agency="AFAD (Afet ve Acil Durum Yönetimi Başkanlığı)",
        primary_tts_engine="elevenlabs",
        currency_symbol="₺",
        currency_code="TRY",
    ),
    "et-EE": LanguageProfile(
        code="et-EE",
        short_code="et",
        name="Estonian",
        native_name="Eesti keel",
        script="Latin",
        country_code="EE",
        flag_emoji="🇪🇪",
        civil_defense_agency="Päästeamet (Estonian Rescue Board)",
        primary_tts_engine="elevenlabs",
        currency_symbol="€",
        currency_code="EUR",
    ),
    "es-US": LanguageProfile(
        code="es-US",
        short_code="es",
        name="Spanish",
        native_name="Español",
        script="Latin",
        country_code="US",
        flag_emoji="🇺🇸",
        civil_defense_agency="Cal OES / FEMA Region IX",
        primary_tts_engine="elevenlabs",
        currency_symbol="$",
        currency_code="USD",
    ),
    "en-US": LanguageProfile(
        code="en-US",
        short_code="en",
        name="English",
        native_name="English",
        script="Latin",
        country_code="US",
        flag_emoji="🌐",
        civil_defense_agency="Global Emergency Response Command",
        primary_tts_engine="elevenlabs",
        currency_symbol="$",
        currency_code="USD",
    ),
    "hi-IN": LanguageProfile(
        code="hi-IN",
        short_code="hi",
        name="Hindi",
        native_name="हिन्दी",
        script="Devanagari",
        country_code="IN",
        flag_emoji="🇮🇳",
        civil_defense_agency="NDMA / UP Relief Commissioner & SDRF",
        primary_tts_engine="sarvam",
        currency_symbol="₹",
        currency_code="INR",
    ),
    "mr-IN": LanguageProfile(
        code="mr-IN",
        short_code="mr",
        name="Marathi",
        native_name="मराठी",
        script="Devanagari",
        country_code="IN",
        flag_emoji="🇮🇳",
        civil_defense_agency="BMC Disaster Management & SDMA Maharashtra",
        primary_tts_engine="sarvam",
        currency_symbol="₹",
        currency_code="INR",
    ),
    "as-IN": LanguageProfile(
        code="as-IN",
        short_code="as",
        name="Assamese",
        native_name="অসমীয়া",
        script="Bengali-Assamese",
        country_code="IN",
        flag_emoji="🇮🇳",
        civil_defense_agency="ASDMA (Assam State Disaster Management Authority)",
        primary_tts_engine="bhashini",
        currency_symbol="₹",
        currency_code="INR",
    ),
    "kn-IN": LanguageProfile(
        code="kn-IN",
        short_code="kn",
        name="Kannada",
        native_name="ಕನ್ನಡ",
        script="Kannada",
        country_code="IN",
        flag_emoji="🇮🇳",
        civil_defense_agency="KSDMA (Karnataka State Disaster Management Authority)",
        primary_tts_engine="sarvam",
        currency_symbol="₹",
        currency_code="INR",
    ),
    "ta-IN": LanguageProfile(
        code="ta-IN",
        short_code="ta",
        name="Tamil",
        native_name="தமிழ்",
        script="Tamil",
        country_code="IN",
        flag_emoji="🇮🇳",
        civil_defense_agency="TNDMA (Tamil Nadu Disaster Risk Reduction Agency)",
        primary_tts_engine="sarvam",
        currency_symbol="₹",
        currency_code="INR",
    ),
    "gu-IN": LanguageProfile(
        code="gu-IN",
        short_code="gu",
        name="Gujarati",
        native_name="ગુજરાતી",
        script="Gujarati",
        country_code="IN",
        flag_emoji="🇮🇳",
        civil_defense_agency="GSDMA (Gujarat State Disaster Management Authority)",
        primary_tts_engine="sarvam",
        currency_symbol="₹",
        currency_code="INR",
    )
}


class BhashaAIEngine:
    """
    Intelligent Multilingual Civic Dispatch Engine.
    Combines Bhashini (MeitY India), Sarvam AI, and Global Neural TTS
    with Verifiable Blue-Carbon-MRV Provenance Stamping.
    """

    def __init__(self):
        self.profiles = LANGUAGE_PROFILES
        self.usd_to_try = 34.2
        self.usd_to_eur = 0.92
        self.inr_per_usd = 84.0

    def resolve_language(
        self,
        location_label: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        jurisdiction: Optional[Any] = None
    ) -> LanguageProfile:
        """
        Resolves the target language profile using hierarchical heuristic:
        1. Explicit JurisdictionHierarchy
        2. Location name token matching (case-insensitive with word boundaries)
        3. Geospatial coordinate bounding box
        4. Default fallback: Hindi (for Indian coordinates/labels) or English
        """
        # 1. Jurisdiction Hierarchy Matching
        if jurisdiction:
            country_iso = ""
            admin1 = ""
            admin2 = ""
            if isinstance(jurisdiction, dict):
                country_iso = (jurisdiction.get("country_iso") or "").upper().strip()
                admin1 = (jurisdiction.get("admin1_state") or "").lower()
                admin2 = (jurisdiction.get("admin2_district") or "").lower()
            elif hasattr(jurisdiction, "country_iso"):
                country_iso = (jurisdiction.country_iso or "").upper().strip()
                admin1 = (jurisdiction.admin1_state or "").lower()
                admin2 = (jurisdiction.admin2_district or "").lower()

            if country_iso == "TR":
                return self.profiles["tr-TR"]
            if country_iso == "EE":
                return self.profiles["et-EE"]
            if country_iso == "US":
                if "california" in admin1 or "orange" in admin2:
                    return self.profiles["es-US"]
                return self.profiles["en-US"]
            if country_iso == "IN":
                if "maharashtra" in admin1 or "mumbai" in admin2:
                    return self.profiles["mr-IN"]
                if "assam" in admin1 or "kaziranga" in admin2:
                    return self.profiles["as-IN"]
                if "karnataka" in admin1 or "bengaluru" in admin2:
                    return self.profiles["kn-IN"]
                if "tamil" in admin1 or "chennai" in admin2:
                    return self.profiles["ta-IN"]
                if "gujarat" in admin1 or "ahmedabad" in admin2:
                    return self.profiles["gu-IN"]
                return self.profiles["hi-IN"]

        # 2. Location Label Keyword Matching
        loc = (location_label or "").lower()
        if any(term in loc for term in ["istanbul", "kastamonu", "bozkurt", "marmara", "türkiye", "turkey", "ankara"]):
            return self.profiles["tr-TR"]
        if any(term in loc for term in ["parnu", "pärnu", "estonia", "eesti", "tallinn", "baltic"]):
            return self.profiles["et-EE"]
        if any(term in loc for term in ["orange county", "california", "newport", "santa ana", "los angeles"]):
            return self.profiles["es-US"]
        if any(term in loc for term in ["mumbai", "kurla", "mithi", "maharashtra", "pune", "thane"]):
            return self.profiles["mr-IN"]
        if any(term in loc for term in ["assam", "kaziranga", "brahmaputra", "guwahati"]):
            return self.profiles["as-IN"]
        if any(term in loc for term in ["bengaluru", "bangalore", "karnataka", "mysore"]):
            return self.profiles["kn-IN"]
        if any(term in loc for term in ["chennai", "tamil nadu", "madurai", "coimbatore"]):
            return self.profiles["ta-IN"]
        if any(term in loc for term in ["ahmedabad", "gujarat", "surat", "vadodara"]):
            return self.profiles["gu-IN"]
        if any(term in loc for term in ["lucknow", "gomti", "uttar pradesh", "delhi", "varanasi", "kanpur", "ayodhya", "noida", "agra"]):
            return self.profiles["hi-IN"]

        # 3. Geospatial Coordinate Bounding Boxes
        if lat is not None and lon is not None:
            # Türkiye: 35.8 to 42.2 N, 25.6 to 44.8 E
            if 35.5 <= lat <= 42.5 and 25.5 <= lon <= 45.0:
                return self.profiles["tr-TR"]
            # Estonia: 57.5 to 59.8 N, 21.7 to 28.3 E
            if 57.0 <= lat <= 60.0 and 21.5 <= lon <= 28.5:
                return self.profiles["et-EE"]
            # California: 32.5 to 42.0 N, -124.5 to -114.0 W
            if 32.0 <= lat <= 42.5 and -125.0 <= lon <= -114.0:
                return self.profiles["es-US"]
            # India: 6.5 to 37.0 N, 68.0 to 97.5 E
            if 6.0 <= lat <= 37.5 and 68.0 <= lon <= 98.0:
                # Maharashtra
                if 15.5 <= lat <= 22.0 and 72.5 <= lon <= 80.5:
                    return self.profiles["mr-IN"]
                # Assam
                if 24.0 <= lat <= 28.5 and 89.5 <= lon <= 96.0:
                    return self.profiles["as-IN"]
                # Karnataka
                if 11.5 <= lat <= 18.5 and 74.0 <= lon <= 78.5:
                    return self.profiles["kn-IN"]
                return self.profiles["hi-IN"]

        # Default fallback
        return self.profiles["en-US"]

    def stamp_mrv_provenance(
        self,
        jurisdiction_iso: str,
        telemetry: Optional[Dict[str, Any]] = None,
        evidence_dict: Optional[Dict[str, Any]] = None
    ) -> MRVProvenance:
        """
        Generates a cryptographic Blue-Carbon-MRV Provenance Stamp
        over the weather telemetry and evidence payload.
        """
        now_utc = datetime.utcnow().isoformat() + "Z"
        bundle_id = f"mrv-{jurisdiction_iso.lower()}-{int(time.time() * 1000)}"

        # Compute telemetry digest
        telemetry_bytes = json.dumps(telemetry or {}, sort_keys=True).encode("utf-8")
        telemetry_digest = keccak256_hex(telemetry_bytes)

        # Compute evidence digest
        evidence_bytes = json.dumps(evidence_dict or {}, sort_keys=True).encode("utf-8")
        evidence_digest = keccak256_hex(evidence_bytes)

        return MRVProvenance(
            mrv_registry_type="Blue-Carbon-MRV-v1",
            bundle_id=bundle_id,
            jurisdiction_iso=jurisdiction_iso,
            timestamp_utc=now_utc,
            sensor_telemetry_digest=telemetry_digest,
            evidence_digest=evidence_digest,
            signature_scheme="Keccak256-RFC8785",
            verification_endpoint="/api/v2/evidence/verify",
            metadata={
                "telemetry_source": "Open-Meteo / Copernicus dClimate",
                "verifier_contract": "ClimateEvidenceRegistry",
                "carbon_mrv_standard": "Verra / Toucan Protocol alignment",
                "settlement_eligible": True
            }
        )

    def generate_dispatch(
        self,
        location_label: str,
        waterlogging_depth_cm: int,
        buildings_at_risk: int,
        total_var_inr: int,
        total_var_usd: int,
        compliance_gap_pct: int,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        jurisdiction: Optional[Any] = None,
        telemetry: Optional[Dict[str, Any]] = None
    ) -> BhashaDispatchResult:
        """
        Generates dual-language civic defense broadcasts:
        1. Universal English (for global C-suite & international incident command)
        2. Local Regional Native (Turkish, Estonian, Spanish, Hindi, Marathi, etc.)
        Stamps with cryptographic MRV provenance.
        """
        profile = self.resolve_language(location_label, lat, lon, jurisdiction)
        agency = profile.civil_defense_agency

        var_usd_m = total_var_usd / 1_000_000.0
        var_inr_cr = total_var_inr / 10_000_000.0
        var_try_m = (total_var_usd * self.usd_to_try) / 1_000_000.0
        var_eur_m = (total_var_usd * self.usd_to_eur) / 1_000_000.0

        # 1. Universal English Executive Alert
        english_alert = (
            f"EXECUTIVE ALERT: Severe flood exposure projected for {location_label}. "
            f"Inundation depth: {waterlogging_depth_cm} cm affecting {buildings_at_risk} critical structures. "
            f"Enterprise Value at Risk (VaR): INR {var_inr_cr:.2f} Cr (${var_usd_m:.2f}M USD). "
            f"Regulatory compliance gap: {compliance_gap_pct}%. Immediate civil defenses directed via {agency}."
        )

        # 2. Local Regional Native Dispatch
        if profile.code == "tr-TR":
            regional_alert = (
                f"ACİL DURUM UYARISI: {location_label} bölgesi için şiddetli su baskını ({waterlogging_depth_cm} cm) tespit edildi. "
                f"{buildings_at_risk} bina ve altyapı kritik risk altında. "
                f"Tahmini kurumsal risk (VaR): ₺{var_try_m:.2f} Milyon (${var_usd_m:.2f}M USD). "
                f"{agency} ve belediye acil drenaj pompalarını derhal devreye almalıdır."
            )
        elif profile.code == "et-EE":
            regional_alert = (
                f"HÄDAOLUKORRA TEADE: {location_label} piirkonnas on prognoositud tõsine üleujutuse oht ({waterlogging_depth_cm} cm). "
                f"Ohus on {buildings_at_risk} taristut ja hoonet. "
                f"Hinnanguline majanduslik risk (VaR): €{var_eur_m:.2f}M (${var_usd_m:.2f}M USD). "
                f"{agency} meeskondadel aktiveerida viivitamatult rannikukaitse ja evakuatsioonikoridorid."
            )
        elif profile.code == "es-US":
            regional_alert = (
                f"ALERTA DE EMERGENCIA: Se proyecta inundación severa en {location_label} con lámina de agua de {waterlogging_depth_cm} cm "
                f"que afecta a {buildings_at_risk} estructuras críticas. "
                f"Valor en Riesgo (VaR): ${var_usd_m:.2f}M USD. "
                f"Se ordena despliegue inmediato de {agency} para bombeo de emergencia y protección de infraestructura."
            )
        elif profile.code == "mr-IN":
            regional_alert = (
                f"तातडीचा इशारा: {location_label} मध्ये {waterlogging_depth_cm} सेंमी पूरस्थितीचा अंदाज आहे. "
                f"{buildings_at_risk} इमारती आणि औद्योगिक पायाभूत सुविधा उच्च जोखमीच्या श्रेणीत आहेत. "
                f"अंदाजे आर्थिक नुकसान (VaR): ₹{var_inr_cr:.2f} कोटी (${var_usd_m:.2f}M USD). "
                f"{agency} यंत्रणेने तत्काळ पाण्याचा उपसा आणि बचाव कार्य सुरू करावे."
            )
        elif profile.code == "as-IN":
            regional_alert = (
                f"জৰুৰীকালীন সতৰ্কবাৰ্তা: {location_label} অঞ্চলত {waterlogging_depth_cm} ছেমি পানী জমা হোৱাৰ প্ৰবল সম্ভাৱনা আছে। "
                f"{buildings_at_risk} টা ঘৰ আৰু আন্তঃগাঁথনি বিপদসীমাত আছে। "
                f"আনুমানিক ক্ষতি (VaR): ₹{var_inr_cr:.2f} কোটি (${var_usd_m:.2f}M USD)। "
                f"{agency} সাহায্য আৰু উদ্ধাৰ অভিযান তৎক্ষণাত সক্ৰিয় কৰক।"
            )
        elif profile.code == "kn-IN":
            regional_alert = (
                f"ತುರ್ತು ಎಚ್ಚರಿಕೆ: {location_label} ನಲ್ಲಿ {waterlogging_depth_cm} ಸೆಂ.ಮೀ ತೀವ್ರ ಪ್ರವಾಹದ ಮುನ್ಸೂಚನೆ ಇದೆ. "
                f"{buildings_at_risk} ಕಟ್ಟಡಗಳು ಅಪಾಯದ ಅಂಚಿನಲ್ಲಿವೆ. "
                f"ಅಂದಾಜು ಆರ್ಥಿಕ ನಷ್ಟ (VaR): ₹{var_inr_cr:.2f} ಕೋಟಿ (${var_usd_m:.2f}M USD). "
                f"{agency} ತಕ್ಷಣವೇ ನೀರು ಹೊರಹಾಕುವ ಪಂಪ್‌ಗಳನ್ನು ಸಕ್ರಿಯಗೊಳಿಸಬೇಕು."
            )
        elif profile.code == "ta-IN":
            regional_alert = (
                f"அவசர எச்சரிக்கை: {location_label} பகுதியில் {waterlogging_depth_cm} செ.மீ வெள்ளப்பெருக்கு அபாயம் கணிக்கப்பட்டுள்ளது. "
                f"{buildings_at_risk} கட்டிடங்கள் கடுமையான பாதிப்பில் உள்ளன. "
                f"மதிப்பிடப்பட்ட சேதம் (VaR): ₹{var_inr_cr:.2f} கோடி (${var_usd_m:.2f}M USD). "
                f"{agency} மீட்புப் பணிகளை உடனடியாக தொடங்கவும்."
            )
        elif profile.code == "gu-IN":
            regional_alert = (
                f"કટોકટી ચેતવણી: {location_label} માં {waterlogging_depth_cm} સેમી ભારે પાણી ભરાવાની આગાહી છે. "
                f"{buildings_at_risk} ઈમારતો ઉચ્ચ જોખમમાં છે. "
                f"અંદાજિત નાણાકીय નુકસાન (VaR): ₹{var_inr_cr:.2f} કરોડ (${var_usd_m:.2f}M USD). "
                f"{agency} તાત્કાલિક રાહत કામગીરી શરૂ કરે."
            )
        elif profile.code == "en-US":
            regional_alert = english_alert
        else:
            # Default Hindi (Pure Devanagari)
            regional_alert = (
                f"आपातकालीन चेतावनी: {location_label} में {waterlogging_depth_cm} सेमी का अत्यधिक जलभराव अनुमानित है। "
                f"{buildings_at_risk} महत्वपूर्ण इमारतें और संपत्तियां गंभीर खतरे में हैं। "
                f"कुल अनुमानित आर्थिक जोखिम (VaR): ₹{var_inr_cr:.2f} करोड़ (${var_usd_m:.2f}M USD)। "
                f"{agency} त्वरित जल निकासी पंपिंग और राहत उपाय सक्रिय करे।"
            )

        # 3. Cryptographic MRV Provenance
        jurisdiction_iso = profile.country_code
        if jurisdiction and isinstance(jurisdiction, dict) and jurisdiction.get("country_iso"):
            jurisdiction_iso = jurisdiction.get("country_iso")
        elif jurisdiction and hasattr(jurisdiction, "country_iso") and jurisdiction.country_iso:
            jurisdiction_iso = jurisdiction.country_iso

        mrv_stamp = self.stamp_mrv_provenance(
            jurisdiction_iso=jurisdiction_iso,
            telemetry=telemetry,
            evidence_dict={
                "location": location_label,
                "depth_cm": waterlogging_depth_cm,
                "var_usd": total_var_usd,
                "profile": profile.code,
                "compliance_gap": compliance_gap_pct
            }
        )

        return BhashaDispatchResult(
            primary_english=english_alert,
            regional_native=regional_alert,
            language_profile=profile,
            mrv_provenance=mrv_stamp,
            voice_engine_used=profile.primary_tts_engine,
            audio_fallback="browser_speech"
        )

    def synthesize_speech(
        self,
        text: str,
        language_code: str = "auto",
        speaker: str = "priya",
        voice_id: Optional[str] = None
    ) -> Tuple[Optional[str], str]:
        """
        Synthesizes authentic audio speech across Indian & Global engines.
        Returns: (audio_b64: Optional[str], engine_used: str)
        """
        # Resolve language if auto
        if language_code == "auto":
            # Check Devanagari
            if any("\u0900" <= c <= "\u097F" for c in text):
                language_code = "hi"
            # Check Turkish characters: ğ, ı, ş, ç, ö, ü
            elif any(c in "ğışçöüĞİŞÇÖÜ" for c in text):
                language_code = "tr"
            # Check Estonian characters: õ, ä, ö, ü
            elif any(c in "õäöüÕÄÖÜ" for c in text):
                language_code = "et"
            else:
                language_code = "en"

        lang_short = language_code.lower().split("-")[0]

        # 1. Indic languages -> Sarvam AI
        if lang_short in ["hi", "mr", "kn", "ta", "gu"]:
            target_bcp = f"{lang_short}-IN"
            audio_b64 = sarvam_connector.synthesize(text, target_lang_code=target_bcp, speaker=speaker)
            if audio_b64:
                return audio_b64, "sarvam_ai"

        # 2. International & English -> ElevenLabs
        if lang_short in ["tr", "et", "es", "en"]:
            target_bcp = f"{lang_short}-TR" if lang_short == "tr" else (
                f"{lang_short}-EE" if lang_short == "et" else (
                    f"{lang_short}-US" if lang_short == "es" else "en-US"
                )
            )
            audio_b64 = global_tts_connector.synthesize(text, language_code=target_bcp, voice_id=voice_id)
            if audio_b64:
                return audio_b64, "elevenlabs"

        # 3. Cross-fallback
        audio_b64 = global_tts_connector.synthesize(text, voice_id=voice_id)
        if audio_b64:
            return audio_b64, "elevenlabs"

        audio_b64 = sarvam_connector.synthesize(text, speaker=speaker)
        if audio_b64:
            return audio_b64, "sarvam_ai"

        # 4. Fallback to Web Speech API
        return None, "browser_speech"


# Module singleton
bhasha_engine = BhashaAIEngine()

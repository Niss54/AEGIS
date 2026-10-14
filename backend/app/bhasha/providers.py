"""
Bhasha-AI Provider Connectors
Integrates:
1. Bhashini ULCA API (Govt of India MeitY) with resilient offline fallback
2. Sarvam AI Indic Neural TTS
3. ElevenLabs / Global Neural Multilingual TTS
"""
import logging
import base64
from typing import Optional, Dict, Any, List
import httpx
from backend.app.config import settings

logger = logging.getLogger("aegis.bhasha.providers")


class BhashiniConnector:
    """
    MeitY Bhashini (National Language Translation Mission, Govt of India) Connector.
    Uses Bhashini ULCA Inference Pipeline API for Indic translations and TTS.
    Provides verified high-fidelity offline fallback when external credentials are unconfigured.
    """

    def __init__(self):
        self.api_key = settings.BHASHINI_API_KEY
        self.user_id = settings.BHASHINI_USER_ID
        self.pipeline_id = settings.BHASHINI_PIPELINE_ID
        self.endpoint = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and self.user_id and self.user_id.strip())

    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Translates text via Bhashini ULCA pipeline or returns None to trigger local template synthesizer."""
        if not self.is_configured():
            return None

        try:
            headers = {
                "Authorization": self.api_key.strip(),
                "userID": self.user_id.strip(),
                "Content-Type": "application/json"
            }
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": {
                            "language": {
                                "sourceLanguage": source_lang,
                                "targetLanguage": target_lang
                            }
                        }
                    }
                ],
                "inputData": {
                    "input": [{"source": text}]
                }
            }
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(self.endpoint, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    pipeline_response = data.get("pipelineResponse", [])
                    if pipeline_response and "output" in pipeline_response[0]:
                        target_text = pipeline_response[0]["output"][0].get("target")
                        if target_text:
                            logger.info(f"Bhashini translated text ({source_lang}->{target_lang}) successfully.")
                            return target_text
        except Exception as e:
            logger.warning(f"Bhashini translation call failed, falling back to local template: {e}")

        return None


class SarvamAIConnector:
    """
    Sarvam AI Indic Speech Connector.
    Generates authentic neural speech in Indian languages (Hindi, Marathi, Kannada, Tamil, etc.).
    """

    def __init__(self):
        self.api_key = settings.SARVAM_API_KEY
        self.endpoint = "https://api.sarvam.ai/text-to-speech"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def synthesize(self, text: str, target_lang_code: str = "hi-IN", speaker: str = "priya") -> Optional[str]:
        """Synthesizes speech returning base64 audio string or None."""
        if not self.is_configured():
            return None

        try:
            headers = {
                "api-subscription-key": self.api_key.strip(),
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": [text[:500]],
                "target_language_code": target_lang_code,
                "speaker": speaker,
                "model": "bulbul:v3"
            }
            resp = httpx.post(self.endpoint, headers=headers, json=payload, timeout=12.0)
            if resp.status_code == 200:
                data = resp.json()
                audios = data.get("audios", [])
                if audios:
                    logger.info(f"Sarvam AI generated native {target_lang_code} speech audio.")
                    return audios[0]
            else:
                logger.warning(f"Sarvam AI returned status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"Sarvam AI speech synthesis failed: {e}")

        return None


class GlobalNeuralTTSConnector:
    """
    Multilingual Neural TTS for international emergency broadcasts.
    Supports Turkish (tr-TR), Estonian (et-EE), Spanish (es-US), and English (en-US).
    """

    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.voice_id = settings.ELEVENLABS_VOICE_ID or "21m00Tcm4TlvDq8ikWAM"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def synthesize(self, text: str, language_code: str = "en-US", voice_id: Optional[str] = None) -> Optional[str]:
        """Synthesizes speech returning base64 audio string or None."""
        if not self.is_configured():
            return None

        target_voice = voice_id or self.voice_id
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{target_voice}"
            headers = {
                "xi-api-key": self.api_key.strip(),
                "Content-Type": "application/json"
            }
            payload = {
                "text": text[:500],
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            resp = httpx.post(url, headers=headers, json=payload, timeout=15.0)
            if resp.status_code == 200 and resp.content:
                audio_b64 = base64.b64encode(resp.content).decode("utf-8")
                logger.info(f"ElevenLabs generated {language_code} neural speech audio ({len(resp.content)} bytes).")
                return audio_b64
            else:
                logger.warning(f"ElevenLabs returned status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"ElevenLabs TTS synthesis failed: {e}")

        return None


# Module singletons
bhashini_connector = BhashiniConnector()
sarvam_connector = SarvamAIConnector()
global_tts_connector = GlobalNeuralTTSConnector()

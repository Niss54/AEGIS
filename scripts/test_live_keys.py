"""
Live API Key Verification Script for AEGIS-CLIMATE
Tests every external service credential configured in .env against its official live endpoint.
"""
import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv(".env")

async def test_gemini():
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return "MISSING", "No GEMINI_API_KEY in .env"
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(url)
            if r.status_code == 200:
                data = r.json()
                models = [m.get("name", "") for m in data.get("models", [])[:3]]
                return "PASS", f"Valid (Found models: {models})"
            else:
                return "FAIL", f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            return "ERROR", str(e)

async def test_groq():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        return "MISSING", "No GROQ_API_KEY in .env"
    url = "https://api.groq.com/openai/v1/models"
    headers = {"Authorization": f"Bearer {key}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                models = [m.get("id", "") for m in data.get("data", [])[:3]]
                return "PASS", f"Valid (Found models: {models})"
            else:
                return "FAIL", f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            return "ERROR", str(e)

async def test_openai():
    key = os.getenv("OPENAI_API_KEY", "").strip() or os.getenv("Open-API-Key", "").strip()
    if not key:
        return "MISSING", "No OPENAI_API_KEY in .env"
    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {key}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                models = [m.get("id", "") for m in data.get("data", [])[:3]]
                return "PASS", f"Valid (Found models: {models})"
            else:
                return "FAIL", f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            return "ERROR", str(e)

async def test_mapbox():
    token = os.getenv("MAPBOX_API_TOKEN", "").strip()
    if not token:
        return "MISSING", "No MAPBOX_API_TOKEN in .env"
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/Lucknow.json?access_token={token}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(url)
            if r.status_code == 200:
                data = r.json()
                features = [f.get("place_name", "") for f in data.get("features", [])[:1]]
                return "PASS", f"Valid (Resolved place: {features})"
            else:
                return "FAIL", f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            return "ERROR", str(e)

async def test_elevenlabs():
    key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    if not key:
        return "MISSING", "No ELEVENLABS_API_KEY in .env"
    url = "https://api.elevenlabs.io/v1/user"
    headers = {"xi-api-key": key}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                tier = data.get("subscription", {}).get("tier", "unknown")
                return "PASS", f"Valid (Subscription tier: {tier})"
            else:
                return "FAIL", f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            return "ERROR", str(e)

async def test_sarvam():
    key = os.getenv("SARVAM_API_KEY", "").strip()
    if not key:
        return "MISSING", "No SARVAM_API_KEY in .env"
    url = "https://api.sarvam.ai/text-to-speech"
    headers = {
        "api-subscription-key": key,
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": ["नमस्ते, यह ऐजिस मौसम प्रणाली है।"],
        "target_language_code": "hi-IN",
        "speaker": "priya",
        "pitch": 0,
        "pace": 1.0,
        "loudness": 1.5,
        "speech_sample_rate": 16000,
        "enable_preprocessing": True,
        "model": "bulbul:v3"
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            r = await client.post(url, headers=headers, json=payload)
            if r.status_code == 200:
                data = r.json()
                audios = data.get("audios", [])
                audio_len = len(audios[0]) if audios else 0
                return "PASS", f"Valid (Synthesized Hindi speech, audio base64 len: {audio_len})"
            else:
                return "FAIL", f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            return "ERROR", str(e)

async def test_bhashini():
    user_id = os.getenv("BHASHINI_USER_ID", "").strip() or os.getenv("Udyat_Key", "").strip()
    api_key = os.getenv("BHASHINI_API_KEY", "").strip() or os.getenv("Inference", "").strip()
    if not (user_id and api_key):
        return "MISSING", "No BHASHINI_USER_ID / BHASHINI_API_KEY in .env"
    
    url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
    headers = {
        "Authorization": api_key,
        "userID": user_id,
        "Content-Type": "application/json"
    }
    payload = {
        "pipelineTasks": [
            {
                "taskType": "translation",
                "config": {
                    "language": {
                        "sourceLanguage": "en",
                        "targetLanguage": "hi"
                    }
                }
            }
        ],
        "inputData": {
            "input": [{"source": "Severe flood alert issued for Gomti river basin."}]
        }
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            r = await client.post(url, headers=headers, json=payload)
            if r.status_code == 200:
                data = r.json()
                resp = data.get("pipelineResponse", [])
                output = resp[0]["output"][0]["target"] if resp else "None"
                return "PASS", f"Valid (Bhashini translation: '{output}')"
            else:
                return "FAIL", f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            return "ERROR", str(e)

async def test_pinata():
    jwt = os.getenv("PINATA_JWT", "").strip()
    api_key = os.getenv("PINATA_API_KEY", "").strip()
    api_secret = os.getenv("PINATA_API_SECRET", "").strip() or os.getenv("PINATA_SECRET_KEY", "").strip()
    
    headers = {}
    if jwt:
        headers["Authorization"] = f"Bearer {jwt}"
    elif api_key and api_secret:
        headers["pinata_api_key"] = api_key
        headers["pinata_secret_api_key"] = api_secret
    else:
        return "MISSING", "No Pinata credentials in .env"
        
    url = "https://api.pinata.cloud/data/testAuthentication"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                msg = data.get("message", "Authenticated")
                return "PASS", f"Valid ({msg})"
            else:
                return "FAIL", f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            return "ERROR", str(e)

async def test_polygonscan():
    key = os.getenv("POLYGONSCAN_API_KEY", "").strip()
    if not key:
        return "MISSING", "No POLYGONSCAN_API_KEY in .env"
    url = f"https://api.etherscan.io/v2/api?chainid=80002&module=account&action=balance&address=0x89C57973B8e72faFE2c510D12E6B1D0bB5d8C971&apikey={key}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(url)
            if r.status_code == 200:
                data = r.json()
                status = data.get("status")
                message = data.get("message")
                result = data.get("result")
                return "PASS", f"Valid (Status: {message}, Result: {result})"
            else:
                return "FAIL", f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            return "ERROR", str(e)

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

async def main():
    print("=" * 70)
    print("AEGIS-CLIMATE LIVE CREDENTIAL TEST SUITE")
    print("=" * 70)
    
    test_funcs = [
        ("Google Gemini", test_gemini),
        ("Groq Cloud", test_groq),
        ("OpenAI", test_openai),
        ("Mapbox", test_mapbox),
        ("ElevenLabs", test_elevenlabs),
        ("Sarvam AI", test_sarvam),
        ("Bhashini (MeitY)", test_bhashini),
        ("Pinata (IPFS)", test_pinata),
        ("PolygonScan", test_polygonscan),
    ]
    
    for name, fn in test_funcs:
        try:
            status, detail = await fn()
        except Exception as err:
            status, detail = "ERROR", str(err)
            
        badge = "[PASS]" if status == "PASS" else "[WARN]" if status == "WARN" else "[FAIL]"
        print(f"{badge:7} {name:20} -> {detail}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())

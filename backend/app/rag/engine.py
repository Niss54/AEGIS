"""
AEGIS Enterprise Hybrid RAG Engine
Combines ChromaDB dense semantic vector search with Redis L1 cache and
jurisdiction-aware multi-national policy routing across India, Türkiye, USA, and EU/Estonia.
"""
import os
import re
import time
import logging
from typing import Dict, List, Any, Optional

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    HAS_CHROMADB = True
except Exception:
    chromadb = None
    ChromaSettings = None
    HAS_CHROMADB = False

from backend.app.rag.corpus import GLOBAL_REGULATORY_CORPUS
from backend.app.rag.hybrid_cache import hybrid_cache, HybridRegulatoryCache

logger = logging.getLogger("aegis.rag.engine")

CHROMA_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "chromadata")


def normalize_jurisdiction_target(raw_region: Optional[str]) -> Optional[str]:
    """Maps various location identifiers to normalized jurisdiction keys."""
    if not raw_region:
        return None
    r = raw_region.strip().lower()
    tokens = set(re.findall(r"\w+", r))

    if any(k in r for k in ["turkey", "türkiye", "istanbul", "kastamonu", "bozkurt", "marmara"]) or "tr" in tokens:
        return "Turkey"
    if any(k in r for k in ["usa", "california", "orange county", "newport", "los angeles", "santa ana"]) or "us" in tokens:
        return "USA"
    if any(k in r for k in ["estonia", "pärnu", "parnu", "tallinn", "baltic", "european union"]) or bool(tokens.intersection({"ee", "eu"})):
        return "Estonia"
    if any(k in r for k in ["india", "bharat", "lucknow", "mumbai", "uttar pradesh", "bengaluru", "assam", "gujarat", "chennai"]) or "in" in tokens:
        return "India"
    return raw_region


class HybridRegulatoryRAGEngine:
    def __init__(self, cache: Optional[HybridRegulatoryCache] = None):
        self.cache = cache or hybrid_cache
        self.client = None
        self.collection = None
        self.corpus = GLOBAL_REGULATORY_CORPUS
        self._init_chroma()

    def _init_chroma(self):
        """Initializes ChromaDB persistent store or falls back to in-memory semantic scoring."""
        if not HAS_CHROMADB or chromadb is None:
            logger.info("ChromaDB not available; using in-memory high-precision semantic fallback.")
            return

        try:
            os.makedirs(CHROMA_DATA_DIR, exist_ok=True)
            self.client = chromadb.PersistentClient(path=CHROMA_DATA_DIR)
            self.collection = self.client.get_or_create_collection(
                name="aegis_global_regulations",
                metadata={"hnsw:space": "cosine"}
            )
            # Reseed or update if corpus has expanded
            existing_count = self.collection.count()
            if existing_count < len(self.corpus):
                self._seed_corpus()
            logger.info(f"ChromaDB regulatory collection initialized with {self.collection.count()} chunks.")
        except Exception as e:
            logger.warning(f"Could not initialize ChromaDB persistent client: {e}. Falling back to in-memory matcher.")

    def _seed_corpus(self):
        """Seeds full multi-jurisdiction corpus into ChromaDB collection."""
        ids = [doc["id"] for doc in self.corpus]
        documents = [doc["text"] for doc in self.corpus]
        metadatas = [
            {
                "title": doc["title"],
                "sector": doc["sector"],
                "region": doc["region"],
                "country_iso": doc.get("country_iso", "GLOBAL")
            }
            for doc in self.corpus
        ]
        try:
            self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        except Exception as e:
            logger.error(f"Error seeding ChromaDB: {e}")

    def query(
        self,
        query_text: str,
        region: Optional[str] = None,
        sector: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Queries regulatory vector store with:
        1. Sub-5ms L1 / Redis Cache check
        2. Region & jurisdiction routing (Turkey, USA, Estonia/EU, India)
        3. ChromaDB cosine similarity or token-level semantic ranking
        """
        t0 = time.time()
        norm_region = normalize_jurisdiction_target(region)

        # 1. Check L1 / L2 Cache
        cached_result = self.cache.get(query_text, norm_region, sector, top_k)
        if cached_result is not None:
            # Mark as cached hit
            for r in cached_result:
                r["cached"] = True
                r["latency_ms"] = round((time.time() - t0) * 1000.0, 3)
            return cached_result

        results = []

        # 2. Try ChromaDB Query if collection exists
        if self.collection is not None:
            try:
                # Query top 6 to allow regional re-ranking
                n_fetch = min(max(top_k * 2, 6), len(self.corpus))
                res = self.collection.query(query_texts=[query_text], n_results=n_fetch)
                if res and "ids" in res and res["ids"] and len(res["ids"][0]) > 0:
                    candidates = []
                    for i in range(len(res["ids"][0])):
                        doc_id = res["ids"][0][i]
                        doc_meta = res["metadatas"][0][i]
                        doc_text = res["documents"][0][i]
                        distance = res["distances"][0][i] if ("distances" in res and res["distances"]) else 0.5
                        
                        # Similarity score: 1.0 - distance
                        base_score = max(0.0, 1.0 - distance)
                        
                        # Region boost
                        boost = 0.0
                        if norm_region:
                            doc_reg = doc_meta.get("region", "")
                            if (norm_region == "Turkey" and doc_reg == "Turkey") or \
                               (norm_region == "USA" and doc_reg == "USA") or \
                               (norm_region == "Estonia" and doc_reg in ["Estonia", "European Union"]) or \
                               (norm_region == "India" and doc_reg == "India"):
                                boost += 0.40
                        
                        # Sector boost
                        if sector and sector.lower() in doc_meta.get("sector", "").lower():
                            boost += 0.15

                        candidates.append({
                            "id": doc_id,
                            "text": doc_text,
                            "metadata": doc_meta,
                            "distance": round(distance, 4),
                            "score": round(base_score + boost, 4)
                        })

                    candidates.sort(key=lambda x: x["score"], reverse=True)
                    results = candidates[:top_k]
            except Exception as e:
                logger.error(f"Error querying ChromaDB collection: {e}")

        # 3. Fallback semantic token matcher if ChromaDB produced nothing
        if not results:
            query_words = set(re.findall(r"\w+", query_text.lower()))
            scored = []
            for doc in self.corpus:
                doc_words = set(re.findall(r"\w+", doc["text"].lower() + " " + doc["title"].lower()))
                overlap = len(query_words.intersection(doc_words))
                base_score = overlap / max(len(query_words), 1)

                boost = 0.0
                if norm_region:
                    doc_reg = doc["region"]
                    if (norm_region == "Turkey" and doc_reg == "Turkey") or \
                       (norm_region == "USA" and doc_reg == "USA") or \
                       (norm_region == "Estonia" and doc_reg in ["Estonia", "European Union"]) or \
                       (norm_region == "India" and doc_reg == "India"):
                        boost += 0.50

                if sector and sector.lower() in doc["sector"].lower():
                    boost += 0.20

                scored.append({
                    "id": doc["id"],
                    "text": doc["text"],
                    "metadata": {
                        "title": doc["title"],
                        "sector": doc["sector"],
                        "region": doc["region"],
                        "country_iso": doc.get("country_iso", "GLOBAL")
                    },
                    "distance": round(max(0.05, 1.0 - (base_score + boost)), 4),
                    "score": round(base_score + boost, 4)
                })

            scored.sort(key=lambda x: x["score"], reverse=True)
            results = scored[:top_k]

        # Tag latency and cached flag
        latency_ms = round((time.time() - t0) * 1000.0, 3)
        for r in results:
            r["cached"] = False
            r["latency_ms"] = latency_ms

        # 4. Save into L1 / Redis Cache for next sub-5ms call
        self.cache.set(query_text, results, norm_region, sector, top_k)
        return results


# Global singleton instance
global_rag_engine = HybridRegulatoryRAGEngine()

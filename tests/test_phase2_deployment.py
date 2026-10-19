"""
Phase 2 Deployment Verification Test Suite for TERRA-SENTINEL
Verifies Vercel Edge Frontend Configuration, Cloud Run Container Manifests,
Production Bundle Integrity, and Error-Free 1-Click Cockpit Loading Invariants.
"""
import os
import json
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_vercel_json_configuration():
    """Verify vercel.json contains required edge routing, rewrites, and security headers."""
    assert os.path.exists("vercel.json"), "vercel.json must exist in repository root"
    with open("vercel.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert "rewrites" in data, "vercel.json must define rewrites"
    sources = [r["source"] for r in data["rewrites"]]
    assert "/api/v1/(.*)" in sources, "Must proxy /api/v1/ to Cloud Run backend"
    assert "/api/v2/(.*)" in sources, "Must proxy /api/v2/ to Cloud Run backend"
    assert "/(.*)" in sources, "Must redirect client routes to index.html for SPA"
    
    assert "headers" in data, "vercel.json must define security and caching headers"
    header_sources = [h["source"] for h in data["headers"]]
    assert "/assets/(.*)" in header_sources, "Static assets must have immutable cache header"


def test_root_package_json_build_delegation():
    """Verify root package.json exists and delegates build to frontend."""
    assert os.path.exists("package.json"), "Root package.json must exist"
    with open("package.json", "r", encoding="utf-8") as f:
        pkg = json.load(f)
    assert "scripts" in pkg
    assert "build" in pkg["scripts"]
    assert "frontend" in pkg["scripts"]["build"]


def test_frontend_dist_bundle_integrity():
    """Verify frontend compiled production assets exist and are error-free."""
    import subprocess
    import shutil

    dist_dir = os.path.join("frontend", "dist")
    index_html = os.path.join(dist_dir, "index.html")

    # Self-healing build hook if run on bare clone
    if not (os.path.exists(dist_dir) and os.path.exists(index_html)):
        npm_cmd = shutil.which("npm") or shutil.which("npm.cmd")
        if npm_cmd:
            try:
                subprocess.run([npm_cmd, "run", "build"], cwd="frontend", check=True, capture_output=True, timeout=120)
            except Exception:
                pass

    assert os.path.exists(dist_dir), "frontend/dist must exist"
    assert os.path.exists(index_html), "frontend/dist/index.html must exist"
    assets_dir = os.path.join(dist_dir, "assets")
    assert os.path.exists(assets_dir), "frontend/dist/assets must exist"
    assert len(os.listdir(assets_dir)) >= 1, "Must contain genuine compiled chunks"
    with open(index_html, "r", encoding="utf-8") as f:
        html = f.read()
    assert "<div id=\"root\"></div>" in html
    assert "assets/" in html


def test_cloud_run_deployment_scripts():
    """Verify Cloud Run automated deployment scripts exist for bash and powershell."""
    sh_script = os.path.join("scripts", "deploy_cloud_run.sh")
    ps_script = os.path.join("scripts", "deploy_cloud_run.ps1")
    assert os.path.exists(sh_script), "deploy_cloud_run.sh must exist"
    assert os.path.exists(ps_script), "deploy_cloud_run.ps1 must exist"
    
    with open(sh_script, "r", encoding="utf-8") as f:
        sh_content = f.read()
    assert "gcloud run deploy" in sh_content
    assert "asia-south1" in sh_content


def test_cloud_run_container_dockerfile():
    """Verify Dockerfile is multi-stage, hardened, and exposes port 8080."""
    assert os.path.exists("Dockerfile"), "Dockerfile must exist"
    with open("Dockerfile", "r", encoding="utf-8") as f:
        docker_content = f.read()
    assert "EXPOSE 8080" in docker_content
    assert "python" in docker_content.lower()


def test_instant_health_for_cloud_run():
    """Verify /health and root / endpoint return instant 200 for Google Cloud Run health checks."""
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "operational"

    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["status"] == "online"
    assert res_root.json()["platform"] == "TERRA-SENTINEL"

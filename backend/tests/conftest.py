from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import app as backend_app_module


@pytest.fixture(scope="session")
def app():
    backend_app_module.app.config.update(TESTING=True)
    return backend_app_module.app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def backend_module():
    return backend_app_module

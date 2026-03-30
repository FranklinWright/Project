from __future__ import annotations

import os
import socket
import subprocess
import time
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

import pytest
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.chrome.options import Options

BASE_URL = os.getenv("RAILREACH_BASE_URL", "http://127.0.0.1:3000")
ROOT = Path(__file__).resolve().parents[2]


def _terminate_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _url_is_up(url: str) -> bool:
    try:
        with urlopen(url, timeout=1):
            return True
    except (URLError, TimeoutError, OSError):
        return False


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def _find_free_port(host: str = "127.0.0.1") -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def _server_is_up(base_url: str) -> bool:
    return _url_is_up(base_url) and _url_is_up(f"{base_url}/api/stations")


def _wait_for_server(base_url: str, timeout_seconds: float = 30) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if _server_is_up(base_url):
            return True
        time.sleep(0.5)
    return False


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session", autouse=True)
def app_server(base_url: str):
    if _server_is_up(base_url):
        yield
        return

    parsed = urlparse(base_url)
    frontend_host = parsed.hostname or "127.0.0.1"
    frontend_port = parsed.port or 3000
    requested_api_port = int(os.getenv("RAILREACH_MOCK_API_PORT", "3001"))
    api_host = "127.0.0.1"
    mock_api_port = requested_api_port
    mock_api_base = f"http://{api_host}:{mock_api_port}"
    started_processes: list[subprocess.Popen] = []

    using_existing_api = _url_is_up(f"{mock_api_base}/api/stations")

    if not using_existing_api and _port_in_use(api_host, mock_api_port):
        mock_api_port = _find_free_port(api_host)
        mock_api_base = f"http://{api_host}:{mock_api_port}"

    if not using_existing_api:
        mock_env = os.environ.copy()
        mock_env["MOCK_API_PORT"] = str(mock_api_port)
        mock_api_process = subprocess.Popen(
            ["bun", "tests/mock-api-server.ts"],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=mock_env,
        )
        started_processes.append(mock_api_process)

        if not _wait_for_server(mock_api_base):
            for process in reversed(started_processes):
                _terminate_process(process)
            raise RuntimeError("Timed out waiting for mock API server to start")

    if not _url_is_up(base_url):
        frontend_env = os.environ.copy()
        frontend_env["VITE_API_PROXY_TARGET"] = mock_api_base
        frontend_process = subprocess.Popen(
            [
                "bunx",
                "--bun",
                "vite",
                "--host",
                frontend_host,
                "--port",
                str(frontend_port),
            ],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=frontend_env,
        )
        started_processes.append(frontend_process)

    if not _wait_for_server(base_url):
        for process in reversed(started_processes):
            _terminate_process(process)
        raise RuntimeError("Timed out waiting for app server to start")

    try:
        yield
    finally:
        for process in reversed(started_processes):
            _terminate_process(process)


@pytest.fixture()
def browser():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,900")

    try:
        driver = webdriver.Chrome(options=options)
    except WebDriverException as error:
        pytest.skip(f"Chrome WebDriver unavailable in this environment: {error}")

    driver.implicitly_wait(5)
    try:
        yield driver
    finally:
        driver.quit()

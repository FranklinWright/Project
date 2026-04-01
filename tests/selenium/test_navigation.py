from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_home_page_renders(browser, base_url: str) -> None:
    browser.get(base_url)

    heading = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    assert "RailReach" in heading.text


def test_nav_to_stations_page(browser, base_url: str) -> None:
    browser.get(base_url)

    browser.find_element(By.CSS_SELECTOR, "a[aria-label='Stations']").click()

    heading = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    assert heading.text.strip() == "Stations"


def test_station_page_links_to_route_instance(browser, base_url: str) -> None:
    browser.get(f"{base_url}/stations/AUS")

    route_link = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/routes/texas-eagle']"))
    )
    route_href = route_link.get_attribute("href")
    try:
        route_link.click()
    except Exception:  # noqa: BLE001
        if route_href:
            browser.get(route_href)
        else:
            raise

    heading = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    assert "Texas Eagle" in heading.text


def test_nav_to_routes_page(browser, base_url: str) -> None:
    browser.get(base_url)

    browser.find_element(By.CSS_SELECTOR, "a[aria-label='Routes']").click()

    heading = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    assert heading.text.strip() == "Routes"


def test_nav_to_regions_page(browser, base_url: str) -> None:
    browser.get(base_url)

    browser.find_element(By.CSS_SELECTOR, "a[aria-label='Regions']").click()

    heading = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    assert heading.text.strip() == "Regions"


def test_nav_to_about_page(browser, base_url: str) -> None:
    browser.get(base_url)

    browser.find_element(By.CSS_SELECTOR, "a[aria-label='About']").click()

    heading = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    assert "RailReach" in heading.text


def test_routes_page_links_to_route_instance(browser, base_url: str) -> None:
    browser.get(f"{base_url}/routes")

    route_link = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/routes/texas-eagle']"))
    )
    route_href = route_link.get_attribute("href")
    try:
        route_link.click()
    except Exception:  # noqa: BLE001
        if route_href:
            browser.get(route_href)
        else:
            raise

    heading = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    assert "Texas Eagle" in heading.text


def test_route_page_links_to_station_instance(browser, base_url: str) -> None:
    browser.get(f"{base_url}/routes/texas-eagle")

    station_link = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/stations/AUS']"))
    )
    station_href = station_link.get_attribute("href")
    try:
        station_link.click()
    except Exception:  # noqa: BLE001
        if station_href:
            browser.get(station_href)
        else:
            raise

    heading = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    assert "Austin Station" in heading.text


def test_route_page_links_to_region_instance(browser, base_url: str) -> None:
    browser.get(f"{base_url}/routes/texas-eagle")

    region_link = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/regions/TX']"))
    )
    region_href = region_link.get_attribute("href")
    try:
        region_link.click()
    except Exception:  # noqa: BLE001
        if region_href:
            browser.get(region_href)
        else:
            raise

    heading = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    assert "Texas" in heading.text


def test_accessibility_toggle_switch(browser, base_url: str) -> None:
    browser.get(base_url)

    browser.find_element(By.CSS_SELECTOR, "button[aria-label='Accessible Mode']").click()

    toggle = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[role='switch']"))
    )
    assert toggle.get_attribute("aria-checked") == "false"

    toggle.click()
    WebDriverWait(browser, 10).until(
        lambda d: d.find_element(By.CSS_SELECTOR, "button[role='switch']").get_attribute(
            "aria-checked"
        )
        == "true"
    )

from __future__ import annotations

class _FakeQuery:
    def __init__(self, result=None):
        self._result = result

    def get(self, _id):
        return self._result

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self._result


class _FakeRoutesCollection:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


class _FakeRouteRef:
    def __init__(self, route):
        self.route = route


class _FakeRouteStationRef:
    def __init__(self, station, is_major: bool, sort_order: int):
        self.station = station
        self.is_major = is_major
        self.sort_order = sort_order


def _base_pagination():
    return {
        "totalItems": 1,
        "totalPages": 1,
        "currentPage": 1,
        "pageSize": 10,
        "hasNextPage": False,
        "hasPreviousPage": False,
        "links": {
            "self": "http://railreach.me/api/stations?page=1&pageSize=10",
            "next": None,
            "previous": None,
            "first": "http://railreach.me/api/stations?page=1&pageSize=10",
            "last": "http://railreach.me/api/stations?page=1&pageSize=10",
        },
    }


def test_get_stations_list(client, backend_module, monkeypatch) -> None:
    def fake_paginated_response(endpoint, _query, _schema, _response):
        assert endpoint == "/api/stations"
        return backend_module.jsonify(
            {
                "data": [{"id": 1, "name": "Austin Station", "code": "AUS"}],
                "pagination": _base_pagination(),
            }
        )

    monkeypatch.setattr(backend_module, "_paginated_response", fake_paginated_response)

    response = client.get("/api/stations")
    payload = response.get_json()

    assert response.status_code == 200
    assert isinstance(payload["data"], list)
    assert payload["data"][0]["code"] == "AUS"


def test_get_station_instance(client, backend_module, monkeypatch) -> None:
    route_obj = object()
    region_obj = object()

    class _FakeStation:
        route_refs = [_FakeRouteRef(route_obj)]
        region = region_obj

    station_obj = _FakeStation()

    class _FakeStationModel:
        query = _FakeQuery(station_obj)

    mapping = {
        station_obj: {"id": 1, "name": "Austin Station", "code": "AUS"},
        route_obj: {"id": 1, "name": "Texas Eagle"},
        region_obj: {"id": 1, "name": "Texas", "code": "TX"},
    }

    monkeypatch.setattr(backend_module, "StationModel", _FakeStationModel)
    monkeypatch.setattr(backend_module, "orm_to_dict", lambda obj: mapping[obj])

    response = client.get("/api/stations/1")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["name"] == "Austin Station"
    assert payload["code"] == "AUS"
    assert payload["linkedRegion"]["code"] == "TX"
    assert payload["linkedRoutes"][0]["name"] == "Texas Eagle"


def test_get_regions_list(client, backend_module, monkeypatch) -> None:
    def fake_paginated_response(endpoint, _query, _schema, _response):
        assert endpoint == "/api/regions"
        return backend_module.jsonify(
            {
                "data": [{"id": 1, "name": "Texas", "code": "TX"}],
                "pagination": _base_pagination(),
            }
        )

    monkeypatch.setattr(backend_module, "_paginated_response", fake_paginated_response)

    response = client.get("/api/regions")
    payload = response.get_json()

    assert response.status_code == 200
    assert isinstance(payload["data"], list)
    assert any(item["code"] == "TX" for item in payload["data"])


def test_get_region_instance(client, backend_module, monkeypatch) -> None:
    station_obj = object()
    route_obj = object()

    class _FakeRegion:
        stations = [station_obj]
        routes = _FakeRoutesCollection([route_obj])

    region_obj = _FakeRegion()

    class _FakeRegionModel:
        query = _FakeQuery(region_obj)

    mapping = {
        region_obj: {"id": 1, "name": "Texas", "code": "TX"},
        station_obj: {"id": 1, "name": "Austin Station", "code": "AUS"},
        route_obj: {"id": 1, "name": "Texas Eagle"},
    }

    monkeypatch.setattr(backend_module, "RegionModel", _FakeRegionModel)
    monkeypatch.setattr(backend_module, "orm_to_dict", lambda obj: mapping[obj])

    response = client.get("/api/regions/1")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["code"] == "TX"
    assert payload["name"] == "Texas"
    assert payload["linkedStations"][0]["code"] == "AUS"
    assert payload["linkedRoutes"][0]["name"] == "Texas Eagle"


def test_get_routes_list(client, backend_module, monkeypatch) -> None:
    def fake_paginated_response(endpoint, _query, _schema, _response):
        assert endpoint == "/api/routes"
        return backend_module.jsonify(
            {
                "data": [{"id": 1, "name": "Texas Eagle"}],
                "pagination": _base_pagination(),
            }
        )

    monkeypatch.setattr(backend_module, "_paginated_response", fake_paginated_response)

    response = client.get("/api/routes")
    payload = response.get_json()

    assert response.status_code == 200
    assert isinstance(payload["data"], list)
    assert payload["data"][0]["name"] == "Texas Eagle"


def test_get_route_instance(client, backend_module, monkeypatch) -> None:
    station_obj = object()
    region_obj = object()

    class _FakeRoute:
        route_station_refs = [
            _FakeRouteStationRef(station_obj, is_major=True, sort_order=1),
            _FakeRouteStationRef(station_obj, is_major=False, sort_order=2),
        ]
        regions_refs = [region_obj]

    route_obj = _FakeRoute()

    class _FakeRouteModel:
        query = _FakeQuery(route_obj)

    mapping = {
        route_obj: {"id": 1, "name": "Texas Eagle"},
        station_obj: {"id": 1, "name": "Austin Station", "code": "AUS"},
        region_obj: {"id": 1, "name": "Texas", "code": "TX"},
    }

    monkeypatch.setattr(backend_module, "RouteModel", _FakeRouteModel)
    monkeypatch.setattr(backend_module, "orm_to_dict", lambda obj: mapping[obj])

    response = client.get("/api/routes/1")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["name"] == "Texas Eagle"
    assert payload["linkedStations"][0]["code"] == "AUS"
    assert payload["linkedRegions"][0]["code"] == "TX"

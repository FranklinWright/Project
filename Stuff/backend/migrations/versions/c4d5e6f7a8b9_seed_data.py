"""Seed initial data

Revision ID: c4d5e6f7a8b9
Revises: d5e6f7a8b9c4
Create Date: 2026-03-10

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import insert, select, text

from sqlalchemy import MetaData, Table, Column, Integer, ForeignKey

from models import (
    Region,
    Route,
    Station,
    TransportSystem,
    region_transport_systems,
    route_regions,
    station_connected_regions,
    station_nearby_stations,
)

# Standalone tables for seed (matches schema at this revision; route_major_stations dropped by later migration)
_meta = MetaData()
route_major_stations = Table(
    "route_major_stations",
    _meta,
    Column("route_id", Integer, ForeignKey("routes.id"), primary_key=True),
    Column("station_id", Integer, ForeignKey("stations.id"), primary_key=True),
    Column("sort_order", Integer, nullable=False, server_default="0"),
)
route_stations = Table(
    "route_stations",
    _meta,
    Column("route_id", Integer, ForeignKey("routes.id"), primary_key=True),
    Column("station_id", Integer, ForeignKey("stations.id"), primary_key=True),
)

revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "d5e6f7a8b9c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Seed data
REGIONS = [
    {
        "id": 1,
        "name": "Texas",
        "code": "TX",
        "population": 31700000,
        "median_household_income": 73000,
        "no_vehicle_available_percent": 5.3,
        "poverty_rate_percent": 13.9,
        "transport_names": ["DART", "METRO", "CapMetro", "VIA", "Trinity Metro"],
        "image_url": "https://i.natgeofe.com/n/edb78803-2870-4668-8c79-ff004ae70c74/h_14776707.jpg",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Texas",
        "tourism_url": "https://www.traveltexas.com/",
        "twitter_url": "https://twitter.com/TravelTexas",
        "railroads_overview": "Part of the state's tradition of cowboys is derived from the massive cattle drives which its ranchers organized in the nineteenth century to drive livestock to railroads and markets.\n\nThe first railroad to operate in Texas was the Buffalo Bayou, Brazos and Colorado Railway, opening in August 1853. The first railroad to enter Texas from the north, completed in 1872, was the Missouri–Kansas–Texas Railroad. With increasing railroad access, the ranchers did not have to take their livestock up to the Midwest and shipped beef out from Texas. This caused a decline in the economies of the cow towns.\n\nSince 1911, Texas has led the nation in length of railroad miles within the state. Texas railway length peaked in 1932 at 17,078 miles (27,484 km), but declined to 14,006 miles (22,540 km) by 2000. While the Railroad Commission of Texas originally regulated state railroads, in 2005 the state reassigned these duties to TxDOT.\n\nIn the Dallas–Fort Worth area, three public transit agencies provide rail service: Dallas Area Rapid Transit (DART), Denton County Transportation Authority (DCTA), and Trinity Metro. DART began operating the first light rail system in the Southwest United States in 1996. The Trinity Railway Express (TRE) commuter rail service, which connects Fort Worth and Dallas, is provided by Trinity Metro and DART. Trinity Metro also operates the TEXRail commuter rail line, connecting downtown Fort Worth and Northeast Tarrant County to DFW Airport. The A-train commuter rail line, operated by DCTA, acts as an extension of the DART Green line into Denton County. In the Austin area, Capital Metropolitan Transportation Authority operates a commuter rail service known as Capital MetroRail to the northwestern suburbs. The Metropolitan Transit Authority of Harris County, Texas (METRO) operates light rail lines called METRORail in the Houston area.\n\nAmtrak provides Texas with limited intercity passenger rail service. Three scheduled routes serve the state: the daily Texas Eagle (Chicago–San Antonio); the tri-weekly Sunset Limited (New Orleans–Los Angeles), with stops in Texas; and the daily Heartland Flyer (Fort Worth–Oklahoma City). Texas may get one of the nation's first high-speed rail line. Plans for a privately funded high-speed rail line between Dallas and Houston have been planned by the Texas Central Railway company.",
        "number_of_amtrak_stations": 19,
        "number_of_amtrak_routes": 3,
        "updated_at": "2024-05-20T14:30:00Z",
    },
    {
        "id": 2,
        "name": "California",
        "code": "CA",
        "population": 39500000,
        "median_household_income": 91900,
        "no_vehicle_available_percent": 7.0,
        "poverty_rate_percent": 12.0,
        "transport_names": [
            "LA Metro",
            "SFMTA (Muni)",
            "BART",
            "San Diego MTS",
            "AC Transit",
        ],
        "image_url": "https://i.natgeofe.com/n/94966d6f-d643-409f-92e3-34af874609a8/Highway-image.jpg",
        "wikipedia_url": "https://en.wikipedia.org/wiki/California",
        "tourism_url": "https://www.visitcalifornia.com/",
        "twitter_url": "https://twitter.com/VisitCA",
        "railroads_overview": "Inter-city rail travel is provided by Amtrak California; the three routes, the Capitol Corridor, Pacific Surfliner, and Gold Runner, are funded by Caltrans. These services are the busiest intercity rail lines in the U.S. outside the Northeast Corridor and ridership is continuing to set records. The routes are becoming increasingly popular over flying, especially on the LAX-SFO route. Integrated subway and light rail networks are found in Los Angeles (Los Angeles Metro Rail) and San Francisco (Muni Metro). Light rail systems are also found in San Jose (VTA light rail), San Diego (San Diego Trolley), Sacramento (SacRT light rail), and Northern San Diego County (Sprinter). Furthermore, commuter rail networks serve the San Francisco Bay Area (Altamont Corridor Express, Bay Area Rapid Transit, Caltrain, Sonoma–Marin Area Rail Transit), Greater Los Angeles (Metrolink), and San Diego County (Coaster).\n\nThe California High-Speed Rail Authority was authorized in 1996 by the state legislature to plan a California High-Speed Rail system to put before the voters. The plan they devised, 2008 California Proposition 1A, connecting all the major population centers in the state, was approved by the voters at the November 2008 general election. The first phase of construction was begun in 2015, and the first segment, 171 miles (275 km) long, is planned to be put into operation by the end of 2030. Planning and work on the rest of the system is continuing, with funding for completing it an ongoing issue. California's 2023 integrated passenger rail master plan includes a high-speed rail system.",
        "number_of_amtrak_stations": 55,
        "number_of_amtrak_routes": 9,
        "updated_at": "2024-05-20T14:30:00Z",
    },
    {
        "id": 3,
        "name": "Illinois",
        "code": "IL",
        "population": 12800000,
        "median_household_income": 76700,
        "no_vehicle_available_percent": 10.4,
        "poverty_rate_percent": 11.9,
        "transport_names": ["CTA", "Metra", "Pace", "NITA", "Bi-State Development"],
        "image_url": "https://i.natgeofe.com/n/6c531f9e-081f-45cb-ae6c-42bed4c67f45/chicago-travel_16x9.jpg",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Illinois",
        "tourism_url": "https://www.enjoyillinois.com/",
        "twitter_url": "https://twitter.com/EnjoyIllinois",
        "railroads_overview": "Illinois has an extensive passenger and freight rail transportation network. Chicago is a national Amtrak hub and in-state passengers are served by Amtrak's Illinois Service, featuring the Chicago to Carbondale Illini and Saluki, the Chicago to Quincy Carl Sandburg and Illinois Zephyr, and the Chicago to St. Louis Lincoln Service. Currently there is trackwork on the Chicago–St. Louis line to bring the maximum speed up to 110 mph (180 km/h), which would reduce the trip time by an hour and a half. Nearly every North American railway meets at Chicago (including all six Class I railroads), making it the largest and most active rail hub in the country. Extensive heavy rail service is provided in the city proper and some immediate suburbs by the Chicago Transit Authority's 'L' system. One of the largest suburban commuter rail system in the United States, operated by Metra, uses existing rail lines to provide direct commuter rail access for hundreds of suburbs to the city and beyond.",
        "number_of_amtrak_stations": 30,
        "number_of_amtrak_routes": 17,
        "updated_at": "2024-05-20T14:30:00Z",
    },
]

NEARBY_STATIONS = [
    {"id": 4, "name": "San Marcos, TX", "code": "SMC", "region_id": 1},
    {"id": 5, "name": "Taylor, TX", "code": "TAY", "region_id": 1},
    {"id": 6, "name": "Davis, CA", "code": "DAV", "region_id": 2},
    {"id": 7, "name": "Roseville, CA", "code": "RSV", "region_id": 2},
    {"id": 8, "name": "Homewood, IL", "code": "HMW", "region_id": 3},
    {"id": 9, "name": "Dyer, IN", "code": "DYE", "region_id": 3},
]

STATIONS = [
    {
        "id": 1,
        "name": "Austin Station",
        "code": "AUS",
        "address": "250 North Lamar Boulevard, Austin, TX 78703",
        "timezone": "America/Chicago",
        "description": "The brick depot was built in 1947 for the Missouri Pacific Railroad. Austin, a center of high-tech industry as well as the state capital, also styles itself the Live Music Capital of the World.",
        "hours": "Station Building: 9:00 AM - 7:00 PM Daily",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Austin_Amtrak_Station.jpg/1280px-Austin_Amtrak_Station.jpg",
        "region_id": 1,
        "routes_served_count": 1,
        "amtrak_url": "https://www.amtrak.com/stations/aus",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Austin_station_(Amtrak)",
        "facebook_url": "https://www.facebook.com/Amtrak/",
        "twitter_url": "https://twitter.com/Amtrak",
        "poi_image_url": "https://quiddity.com/wp-content/uploads/2021/05/Texas-Capitol-Complex-8-scaled.jpg",
        "poi_image_label": "Texas State Capitol",
        "history": "Austin's brick station, built in 1947 for the Missouri Pacific Railroad, provides a small waiting room, ticket office and restroom for passengers.\n\nThe Houston and Texas Central Railroad came to Austin in 1871, with its main tracks on Pine (now Fifth) Street. The stone Old Depot Hotel built by Carl Schaeffer with architect Abner Cook was Austin's and the state's first railroad station and was operational from 1871 to 1872. Known as Railroad House, it still stands on 5th Street and houses Carmelo's Italian Restaurant. At the time it was built, it accommodated passengers traveling to other railroads and four stagecoach lines. This building was placed on the Texas State Historical Survey.\n\nThe other two signature depots which once served Austin stood opposite each other at Congress Avenue and Third Street; about four blocks away from Railroad House and have both have been razed. The buff brick International & Great Northern (later Missouri Pacific) station, with its distinctive round turret, was built in 1881, and the red brick Houston and Texas Central Railroad (later Southern Pacific) was built in 1902. During its heyday, in the 1920s, 18 trains a day would come through the tracks on Third Street.\n\nAustin's first documented non-Native settlement came in 1835, when English-speaking Americans began arriving in the area and founded the village of Waterloo on the bank of the Colorado River. According to local folklore, Stephen F. Austin, the \"father of Texas,\" negotiated a boundary treaty with the local Native Americans at Treaty Oak. This tree, the last of the 24 Comanche Council Oaks, is estimated to be 500 years old, and still stands in the city.",
        "nearby_codes": ["SMC", "TAY"],
        "points_of_interest": ["Lady Bird Lake", "Zilker Park", "Texas State Capitol"],
        "region_codes": ["IL", "TX"],
        "updated_at": "2024-05-20T14:30:00Z",
    },
    {
        "id": 2,
        "name": "Sacramento Valley Station",
        "code": "SAC",
        "address": "401 I Street, Sacramento, CA, 95814",
        "timezone": "America/Los Angeles",
        "description": "Opened in 1926, the historic station is undergoing a multi-year renovation that includes track relocation, construction of new platforms and rehabilitation of the interiors.",
        "hours": "Station Building: 5:00 AM - 11:59 PM Daily",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Sacramento_Valley_Station.JPG/1280px-Sacramento_Valley_Station.JPG",
        "region_id": 2,
        "routes_served_count": 4,
        "amtrak_url": "https://www.amtrak.com/stations/sac",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Sacramento_Valley_Station",
        "facebook_url": "https://www.facebook.com/Amtrak/",
        "twitter_url": "https://twitter.com/Amtrak",
        "poi_image_url": "https://lh3.googleusercontent.com/gps-cs-s/AHVAweo4PJ2ZKvnUPsVzQeJm5wk98JPQJy_DjmQkw5KzOvalgx89CAvt-t7nK2nz1_BM1wDvDuF2ZbOdqOUlzNHVQtdUmt6dB983dTHWD0lTeOtsSrNOtRpFzVQn-WBEWBc6DPoUyLSU=s1360-w1360-h1020-rw",
        "poi_image_label": "State Railroad Museum",
        "history": "The original Sacramento station was the terminal of the Central Pacific Railroad. The present building, designed by the San Francisco architectural firm of Bliss and Faville for the Southern Pacific Railroad, was built in 1926 on the site of China Slough in the Renaissance Revival style. Decorative features include a red tile roof and terracotta trim, as well as large arches on the main facade. Inside, the waiting room has a mural by artist John A. MacQuarrie that depicts the celebration of the groundbreaking for the First transcontinental railroad on January 8, 1863, in Sacramento. The Central Pacific started from Sacramento and built east to Promontory Summit, Utah, where it met the Union Pacific Railroad. The station is now owned by the City of Sacramento. With the creation of Amtrak on May 1, 1971, the station became Amtrak-only. The station was listed on the National Register of Historic Places in 1975 as \"Southern Pacific Railroad Company's Sacramento Depot\".\n\nFor most of Amtrak's first two decades, the only trains calling at Sacramento were long-distance routes. The California Zephyr and its predecessors have served the station from Amtrak's inception; several pre-Amtrak predecessors of the Zephyr stopped in Sacramento from the 1930s onward. The Coast Starlight arrived in 1982. From 1981, the Spirit of California ran as a sleeper to Los Angeles along the far southern leg of the Coast Starlight route. Service expanded dramatically in 1991 with the introduction of the Capitols service, now the Capitol Corridor. Partly due to its success, it is now the second-busiest station in the Western United States, behind only Los Angeles Union Station, and the seventh-busiest station overall.",
        "nearby_codes": ["DAV", "RSV"],
        "points_of_interest": ["Old Sacramento", "State Railroad Museum", "Golden 1 Center"],
        "region_codes": ["CA"],
        "updated_at": "2024-05-20T14:30:00Z",
    },
    {
        "id": 3,
        "name": "Chicago Union Station",
        "code": "CHI",
        "address": "255 South Clinton Street, Chicago, IL 60606",
        "timezone": "America/Chicago",
        "description": "Best known for its majestic Great Hall, often bathed in soft light, Chicago Union Station is the hub for mid-western corridor services and national network trains serving the west.",
        "hours": "Station Building: 5:30 AM - 11:59 PM Daily",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Chicago_Union_Station.jpg/1280px-Chicago_Union_Station.jpg",
        "region_id": 3,
        "routes_served_count": 16,
        "amtrak_url": "https://www.amtrak.com/stations/chi",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Chicago_Union_Station",
        "facebook_url": "https://www.facebook.com/Amtrak/",
        "twitter_url": "https://twitter.com/Amtrak",
        "poi_image_url": "https://www.chicagomag.com/wp-content/uploads/2024/05/C2024_06_01_077MillenniumPark.jpg",
        "poi_image_label": "Millennium Park",
        "history": 'Chicago Union Station was first envisioned by famed architect Daniel Burnham. Ultimately designed by Graham, Anderson, Probst and White, Union Station opened in 1925 after ten years of construction. The station was built by a "union" of four railroads to accommodate the ever expanding demand for passenger rail to and from Chicago. Construction included not only the station itself, but also the rail yards coming into the station and the many blocks of viaducts and bridges necessary to separate trains from other traffic.\n\nIts awe-inspiring looks are the result of sweeping limestone exteriors (quarried in Bedford, Indiana) and larger-than-life ornate interiors. This grandeur is best experienced in the Great Hall, the station\'s main waiting room spanned by a 219-foot-long, barrel-vaulted skylight that soars 115 feet over the room. The skylight ceiling was blacked out during World War II in order to make the station less of a target for enemy aircraft.',
        "nearby_codes": ["HMW", "DYE"],
        "points_of_interest": ["Willis Tower", "Art Institute of Chicago", "Millennium Park"],
        "region_codes": ["IL", "CA"],
        "updated_at": "2024-05-20T14:30:00Z",
    },
]

ROUTES = [
    {
        "id": 1,
        "name": "Texas Eagle",
        "description": "Ready for a real adventure? Let Amtrak take you deep in the heart of Texas. Hop aboard the Texas Eagle, traveling between Chicago and San Antonio, through major cities from Austin to Dallas. Connecting service between San Antonio and Los Angeles is available via the Sunset Limited. Wind through the Land of Lincoln, across the Mississippi River, and through the Ozarks to Little Rock and the piney woods of East Texas. Onward to colorful, cosmopolitan Dallas, through Austin (home of the University of Texas), and finally to San Antonio, where the legend of the Alamo and the Riverwalk attract people from all over the world.",
        "major_station_codes": ["CHI", "AUS"],
        "menu": [
            "Signature Flat Iron Steak",
            "Pan Roasted Chicken Breast",
            "Atlantic Salmon",
            "Railroad French Toast",
        ],
        "travel_time_in_hours": "32 hours 25 minutes (Chicago - San Antonio); 65 hours 20 minutes (Chicago - Los Angeles)",
        "region_codes": ["TX", "CA", "IL"],
        "station_codes": ["CHI", "AUS", "SMC", "TAY"],
        "image_url": "https://www.amtrak.com/content/dam/projects/dotcom/english/public/images/heros/Route_TexasEasgle_HeroBanner_1_2.jpg/_jcr_content/renditions/cq5dam.web.2125.1195.jpeg",
        "amtrak_url": "https://www.amtrak.com/texas-eagle-train",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Texas_Eagle",
        "youtube_url": "https://www.youtube.com/watch?v=Mp9wDYiteGs",
        "updated_at": "2024-05-20T14:30:00Z",
    },
    {
        "id": 2,
        "name": "California Zephyr",
        "description": "Experienced travelers say the California Zephyr is one of the most beautiful train trips in all of North America. As you climb through the heart of the Rockies, and further west through the snow-capped Sierra Nevadas, you may find it hard to disagree. The Zephyr runs between Chicago and San Francisco, coursing through the plains of Nebraska to Denver, across the Rockies to Salt Lake City, and then through Reno and Sacramento into Emeryville/San Francisco. Connections in to San Francisco and Oakland stations via Amtrak Connection bus service at Emeryville, California.",
        "major_station_codes": ["CHI", "SAC"],
        "menu": [
            "Signature Flat Iron Steak",
            "Pan Roasted Chicken Breast",
            "Atlantic Salmon",
            "Railroad French Toast",
        ],
        "travel_time_in_hours": "51 hours 20 minutes",
        "region_codes": ["IL", "CA"],
        "station_codes": ["CHI", "SAC", "DAV", "RSV", "HMW", "DYE"],
        "image_url": "https://www.amtrak.com/content/dam/projects/dotcom/english/public/images/heros/Route_CaliforniaZephyr_HeroBanner_1_1.jpg/_jcr_content/renditions/cq5dam.web.2125.1195.jpeg",
        "amtrak_url": "https://www.amtrak.com/california-zephyr-train",
        "wikipedia_url": "https://en.wikipedia.org/wiki/California_Zephyr",
        "youtube_url": "https://www.youtube.com/watch?v=1dYslCbPEGo",
        "updated_at": "2024-05-20T14:30:00Z",
    },
    {
        "id": 3,
        "name": "Coast Starlight",
        "description": "A grand west coast train adventure, en route daily between Los Angeles and Seattle, the Coast Starlight train passes through Santa Barbara, the San Francisco Bay Area, Sacramento and Portland. Widely regarded as one of the most spectacular of all train routes, the Coast Starlight links the greatest cities on the West Coast. The scenery along the Coast Starlight route is unsurpassed. The dramatic snow-covered peaks of the Cascade Range and Mount Shasta, lush forests, fertile valleys and long stretches of Pacific Ocean shoreline provide a stunning backdrop for your journey.",
        "major_station_codes": ["SAC"],
        "menu": [
            "Signature Flat Iron Steak",
            "Pan Roasted Chicken Breast",
            "Atlantic Salmon",
            "Railroad French Toast",
        ],
        "travel_time_in_hours": "35 hours",
        "region_codes": ["CA"],
        "station_codes": ["SAC", "DAV", "RSV"],
        "image_url": "https://www.amtrak.com/content/dam/projects/dotcom/english/public/images/heros/Route_CoastStarlight_HeroBanner_1_0.jpg/_jcr_content/renditions/cq5dam.web.2125.1195.jpeg",
        "amtrak_url": "https://www.amtrak.com/coast-starlight-train",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Coast_Starlight",
        "youtube_url": "https://www.youtube.com/watch?v=ISRl3gYnzOw",
        "updated_at": "2024-05-20T14:30:00Z",
    },
]


def upgrade() -> None:
    conn = op.get_bind()

    # Skip if already seeded
    if conn.execute(text("SELECT 1 FROM regions LIMIT 1")).fetchone():
        return

    def ts(name):
        result = conn.execute(
            select(TransportSystem.__table__.c.id).where(
                TransportSystem.__table__.c.name == name
            )
        )
        row = result.fetchone()
        if row:
            return row[0]
        result = conn.execute(
            insert(TransportSystem.__table__).values(name=name).returning(
                TransportSystem.__table__.c.id
            )
        )
        return result.fetchone()[0]

    code_to_region_id = {r["code"]: r["id"] for r in REGIONS}

    # Regions with transport systems
    for cfg in REGIONS:
        cfg = dict(cfg)
        transport_names = cfg.pop("transport_names")
        region_row = {k: v for k, v in cfg.items()}
        conn.execute(insert(Region.__table__).values(**region_row))
        for tname in transport_names:
            tid = ts(tname)
            conn.execute(
                insert(region_transport_systems).values(
                    region_id=cfg["id"], transport_system_id=tid
                )
            )

    # Nearby stations
    for cfg in NEARBY_STATIONS:
        conn.execute(insert(Station.__table__).values(**cfg))

    # Main stations with junctions
    code_to_id = {r["code"]: r["id"] for r in NEARBY_STATIONS}
    for cfg in STATIONS:
        cfg = dict(cfg)
        nearby_codes = cfg.pop("nearby_codes", [])
        region_codes = cfg.pop("region_codes", [])
        conn.execute(insert(Station.__table__).values(**cfg))
        station_id = cfg["id"]
        for code in nearby_codes:
            other_id = code_to_id.get(code)
            if other_id and other_id != station_id:
                conn.execute(
                    insert(station_nearby_stations).values(
                        station_id=station_id, nearby_station_id=other_id
                    )
                )
        for code in region_codes:
            region_id = code_to_region_id.get(code)
            if region_id:
                conn.execute(
                    insert(station_connected_regions).values(
                        station_id=station_id, region_id=region_id
                    )
                )
        code_to_id[cfg["code"]] = station_id

    # Routes with major stations, regions, stations, and menu
    for cfg in ROUTES:
        cfg = dict(cfg)
        major_station_codes = cfg.pop("major_station_codes", [])
        region_codes = cfg.pop("region_codes", [])
        station_codes = cfg.pop("station_codes", [])
        conn.execute(insert(Route.__table__).values(**cfg))
        route_id = cfg["id"]
        for i, code in enumerate(major_station_codes):
            sid = code_to_id.get(code)
            if sid:
                conn.execute(
                    insert(route_major_stations).values(
                        route_id=route_id, station_id=sid, sort_order=i
                    )
                )
        for code in region_codes:
            region_id = code_to_region_id.get(code)
            if region_id:
                conn.execute(
                    insert(route_regions).values(route_id=route_id, region_id=region_id)
                )
        for code in station_codes:
            sid = code_to_id.get(code)
            if sid:
                conn.execute(
                    insert(route_stations).values(route_id=route_id, station_id=sid)
                )


def downgrade() -> None:
    op.execute(text("DELETE FROM route_stations"))
    op.execute(text("DELETE FROM route_regions"))
    op.execute(text("DELETE FROM route_major_stations"))
    op.execute(text("DELETE FROM station_connected_regions"))
    op.execute(text("DELETE FROM station_nearby_stations"))
    op.execute(text("DELETE FROM region_transport_systems"))
    op.execute(text("DELETE FROM stations"))
    op.execute(text("DELETE FROM routes"))
    op.execute(text("DELETE FROM transport_systems"))
    op.execute(text("DELETE FROM regions"))

"""ArcGIS Network Analyst drive-time lookup for comparison against Google Maps.
Uses a locally licensed ArcGIS Pro install and a local Network Analyst dataset
via arcpy -- no public demo server, rate limits, or OSM speed data involved.
"""

from urllib.parse import quote

import arcpy
import requests

NETWORK_DATASET = r"C:\Users\REPLACEWITHYOURLOCALPATH\NetworkDataset.gdb\Transportation\Streets_ND"
ORIGIN_ADDRESS = "1 Main St, Burlington, VT 05401"
DESTINATION_ADDRESS = "1 National Life Drive, Montpelier, VT 05602"

# Requires an active Network Analyst extension license, checked out for
# the duration of the solve and returned afterward.
arcpy.CheckOutExtension("network")

# Geocode via OSM's free Nominatim service, same method used in the OSRM
# scripts, just to get coordinates to feed into the network dataset solve.
nominatim_url = "https://nominatim.openstreetmap.org/search"
headers = {"User-Agent": "drivetime-script"}
origin = requests.get(nominatim_url, params={"q": ORIGIN_ADDRESS, "format": "json", "limit": 1}, headers=headers).json()[0]
destination = requests.get(nominatim_url, params={"q": DESTINATION_ADDRESS, "format": "json", "limit": 1}, headers=headers).json()[0]

route_solver = arcpy.nax.Route(NETWORK_DATASET)
route_solver.travelMode = arcpy.nax.GetTravelModes(NETWORK_DATASET)["Driving a Car"]

wgs84 = arcpy.SpatialReference(4326)
with route_solver.insertCursor(arcpy.nax.RouteInputDataType.Stops, ["SHAPE@"]) as cursor:
    cursor.insertRow((arcpy.PointGeometry(arcpy.Point(float(origin["lon"]), float(origin["lat"])), wgs84),))
    cursor.insertRow((arcpy.PointGeometry(arcpy.Point(float(destination["lon"]), float(destination["lat"])), wgs84),))

result = route_solver.solve()
if not result.solveSucceeded:
    raise RuntimeError(result.solverMessages(arcpy.nax.MessageSeverity.All))

routes_fc = r"in_memory\drivetime_route"
result.export(arcpy.nax.RouteOutputDataType.Routes, routes_fc)
with arcpy.da.SearchCursor(routes_fc, ["Total_Minutes", "Total_Kilometers"]) as cursor:
    duration_minutes, distance_km = next(cursor)
arcpy.management.Delete(routes_fc)

arcpy.CheckInExtension("network")

# This travel mode's speeds are modeled/historical values baked into the
# network dataset itself (commercial routing data), not a generic per-road-type
# default like OSRM's -- so expect this to land closer to Google's estimate
# than the OSRM scripts do, though still not an exact match (Google also
# factors live conditions at the moment you check).
google_url = (
    f"https://www.google.com/maps/dir/?api=1"
    f"&origin={quote(ORIGIN_ADDRESS)}"
    f"&destination={quote(DESTINATION_ADDRESS)}"
)

print(f"ArcGIS Network Analyst drive time: {duration_minutes:.1f} minutes ({distance_km:.1f} km)")
print(f"Compare to Google Maps: {google_url}")

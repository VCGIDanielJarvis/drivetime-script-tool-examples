# ArcGIS Network Analyst drive-time lookup for comparison against Google Maps.
# Uses a locally licensed ArcGIS Pro install and a local Network Analyst dataset.
# R has no native Network Analyst binding, so `reticulate` calls into arcpy
# running in the ArcGIS Pro Python environment -- no public demo server,
# rate limits, or OSM speed data involved.

library(reticulate)
library(tmaptools)

use_python("C:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe", required = TRUE)
arcpy <- import("arcpy")

network_dataset <- "C:/Users/REPLACEWITHYOURLOCALPATH/NetworkDataset.gdb/Transportation/Streets_ND"
origin_address <- "1 Main St, Burlington, VT 05401"
destination_address <- "1 National Life Drive, Montpelier, VT 05602"

# osrmRoute() needs coordinates, not addresses -- geocode via OSM's
# free Nominatim service (same method used in the OSRM scripts).
origin <- geocode_OSM(origin_address)$coords
destination <- geocode_OSM(destination_address)$coords

# Requires an active Network Analyst extension license, checked out for
# the duration of the solve and returned afterward.
invisible(arcpy$CheckOutExtension("network"))

route_solver <- arcpy$nax$Route(network_dataset)
route_solver$travelMode <- arcpy$nax$GetTravelModes(network_dataset)[["Driving a Car"]]

wgs84 <- arcpy$SpatialReference(4326L)
cursor <- route_solver$insertCursor(arcpy$nax$RouteInputDataType$Stops, list("SHAPE@"))
invisible(cursor$insertRow(tuple(arcpy$PointGeometry(arcpy$Point(unname(origin["x"]), unname(origin["y"])), wgs84))))
invisible(cursor$insertRow(tuple(arcpy$PointGeometry(arcpy$Point(unname(destination["x"]), unname(destination["y"])), wgs84))))
invisible(cursor$`__exit__`(NULL, NULL, NULL))

result <- route_solver$solve()
if (!result$solveSucceeded) {
  stop(result$solverMessages(arcpy$nax$MessageSeverity$All))
}

routes_fc <- "in_memory/drivetime_route"
invisible(result$export(arcpy$nax$RouteOutputDataType$Routes, routes_fc))
search_cursor <- arcpy$da$SearchCursor(routes_fc, list("Total_Minutes", "Total_Kilometers"))
row <- iter_next(search_cursor)
invisible(search_cursor$`__exit__`(NULL, NULL, NULL))
duration_minutes <- row[[1]]
distance_km <- row[[2]]
invisible(arcpy$management$Delete(routes_fc))

invisible(arcpy$CheckInExtension("network"))

# This travel mode's speeds are modeled/historical values baked into the
# network dataset itself (commercial routing data), not a generic per-road-type
# default like OSRM's -- so expect this to land closer to Google's estimate
# than the OSRM scripts do, though still not an exact match (Google also
# factors live conditions at the moment you check).
google_url <- paste0(
  "https://www.google.com/maps/dir/?api=1&origin=", URLencode(origin_address),
  "&destination=", URLencode(destination_address)
)

cat(sprintf("ArcGIS Network Analyst drive time: %.1f minutes (%.1f km)\n", duration_minutes, distance_km))
cat(sprintf("Compare to Google Maps: %s\n", google_url))

# Basic OSRM drive-time lookup for comparison against Google Maps
# Uses the public OSRM demo server via the `osrm` package.
# Runs two methods -- geocoded addresses vs. manually specified coordinates --
# so the results (and their limitations) can be compared.

library(osrm)
library(tmaptools)

origin_address <- "1 Main St, Burlington, VT 05401"
destination_address <- "1 National Life Drive, Montpelier, VT 05602"

# Method 1: geocode addresses via OSM's free Nominatim service (same
# data source OSRM itself routes on) to get precise coordinates.
geocoded_origin <- geocode_OSM(origin_address)$coords
geocoded_destination <- geocode_OSM(destination_address)$coords
geocoded_route <- osrmRoute(src = geocoded_origin, dst = geocoded_destination, overview = FALSE)

# Method 2: manually specified coordinates (approximate, hand-picked --
# no geocoding step, so Nominatim's usage-policy limits don't apply here).
manual_origin <- c(lon = -73.2121, lat = 44.4759)
manual_destination <- c(lon = -72.5745, lat = 44.2612)
manual_route <- osrmRoute(src = manual_origin, dst = manual_destination, overview = FALSE)

google_url <- paste0(
  "https://www.google.com/maps/dir/?api=1&origin=", URLencode(origin_address),
  "&destination=", URLencode(destination_address)
)

# Discrepancy & limitations:
# - Any gap between Method 1 and Method 2 comes from coordinate precision:
#   manual coordinates are hand-picked approximations and may snap to a
#   different nearby road segment than the geocoded point.
# - Both methods still rely on OSRM's generic per-road-type speed profile,
#   not real-world or live-traffic speeds like Google Maps uses -- so
#   neither will match Google's estimate exactly.
# - Method 1 depends on Nominatim's free public endpoint: rate-limited
#   (~1 request/sec), not meant for bulk use, and match quality varies by
#   region and address completeness.
# - Method 2 skips that limit but requires coordinates obtained some other
#   way, and has no address validation -- a wrong or stale coordinate
#   fails silently rather than erroring out.

cat(sprintf("Method 1 (geocoded address):   %.1f minutes (%.1f km)\n", geocoded_route[["duration"]], geocoded_route[["distance"]]))
cat(sprintf("Method 2 (manual coordinates):  %.1f minutes (%.1f km)\n", manual_route[["duration"]], manual_route[["distance"]]))
cat(sprintf("Compare to Google Maps: %s\n", google_url))

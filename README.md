# api-bus-app

Live bus arrivals for Singapore bus stops.

## API

[`arrivelah2`](https://arrivelah2.busrouter.sg/) — a CORS-open proxy for LTA bus arrival data.
No API key, no backend needed.

```
GET https://arrivelah2.busrouter.sg/?id=83139
```

Returns `{ services: [ { no, operator, next, next2, next3, subsequent } ] }`, where each
arrival slot carries `duration_ms`, `load` (`SEA` / `SDA` / `LSD`), `feature` (`WAB`),
`type` (`SD` / `DD` / `BD`) and the bus's live `lat` / `lng`. An unknown stop code returns
`{"services":[]}` with HTTP 200, not an error.

Stop names and coordinates: [`data.busrouter.sg/v1/stops.json`](https://data.busrouter.sg/v1/stops.json)
— 5,207 stops keyed by code, as `[lng, lat, name, road]`. Also CORS-open.

Both are by [cheeaun](https://github.com/cheeaun).

## Status

Stub. Nothing built yet.

# Run For It

> **Aisha is standing outside her office in one-north with 45 minutes of lunch break left, and
> this screen tells her which bus to start walking for right now if she wants to eat in Holland
> Village and still get back in time.**

Live at **[jiaxuanf.github.io/api-bus-app](https://jiaxuanf.github.io/api-bus-app/)**

A departures board answers *when is the bus*. That is not the decision anyone standing on a
pavement is actually making. The decision is **do I run, or is there another one soon enough that
I don't have to?** — and answering it needs three numbers, not one: how long the bus is, how long
*you* are from the stop, and whether the difference is bigger than zero.

So the screen leads with a verdict, in a word you can read at arm's length while walking:

| Verdict | What it means |
|---|---|
| **Run** | Under 45 seconds of slack between the walk and the bus |
| **Walk now** | Under 4 minutes of slack — set off, don't dawdle |
| **You have time** | 4 minutes or more; finish your coffee |
| **Board now** / **Nearly here** | Same thing, when you're already standing at the stop |
| **Missed it** | All three live arrivals leave before you could get there |

Under the verdict is every way to make the trip — one bus or one change — ranked by **when you
actually arrive**, not by how soon something departs. A bus leaving in 2 minutes that crawls is a
worse answer than one leaving in 9 that doesn't, and the ranking says so.

## What's live and what's estimated

This distinction matters, so the app states it in its own footer too.

**Live:** arrivals at your boarding stop, from `arrivelah2`, refreshed every 20 seconds — including
crowding (`SEA` / `SDA` / `LSD`, drawn as the three-bar load meter) and the next three buses, so a
"Missed it" can look past the first one.

**Estimated**, with every constant named at the top of the script so you can argue with them:

```js
const WALK_MPM      = 78;    // metres/min — 4.7 km/h, an unhurried pace
const WALK_DETOUR   = 1.35;  // you can't walk through buildings
const BUS_KMH       = 18;    // SG average once dwell time at stops is counted
const TRANSFER_WAIT = 6;     // assumed wait for a connecting bus
const UNKNOWN_WAIT  = 8;     // assumed wait when a service reports no live arrival
```

Ride time is that speed along the **real route path** — the sum of the distances between the actual
stops the bus calls at, not a straight line from A to B. Walking distances get the detour factor
for the same reason.

## Honest limits

- **One change, maximum.** Cross-island trips that need two changes return "no route found".
  Tuas → Pasir Ris is genuinely beyond it.
- **Buses only.** No MRT, so some journeys look far worse than how you'd really travel.
- **The second leg's wait is a guess.** Live arrivals tell you about *now*, not about the moment
  you'll reach the transfer stop 20 minutes from now. A flat 6 minutes is assumed and labelled
  `~` wherever it's shown.
- **Stops, not addresses.** Destination search covers the 5,207 bus stops. SG stop names are
  landmarks ("Holland V", "one-north Stn", "Bugis Stn/Parkview Sq") so this goes further than it
  sounds, but it isn't a place search. OneMap's would need an API token, which would mean a backend.

## APIs

All three are CORS-open and keyless, which is the whole reason this runs as a static page with no
server and no secrets.

| | |
|---|---|
| [`arrivelah2`](https://arrivelah2.busrouter.sg/) | Live arrivals — `?id=83139`. An unknown code returns `{"services":[]}` with HTTP 200, not a 404 |
| [`stops.json`](https://data.busrouter.sg/v1/stops.json) | 5,207 stops as `[lng, lat, name, road]` |
| [`services.json`](https://data.busrouter.sg/v1/services.json) | 605 services, each with its ordered stop list per direction — this is what makes routing possible |
| [2-hour forecast](https://api-open.data.gov.sg/v2/real-time/api/two-hr-forecast) | data.gov.sg, 47 areas. Whether it's about to pour changes whether you run |

The first three are by [cheeaun](https://github.com/cheeaun), whose
[busrouter.sg](https://busrouter.sg/) is the reference for what a genuinely useful product on this
data looks like — and is where to go for the map, the full route lists, and the trips this planner
gives up on.

## How the routing works

1. Index every stop → the services and positions that call at it (605 services × 2 directions).
2. Take all stops within 500 m of origin and destination.
3. **Direct:** any service+direction hitting an origin stop at index `i` and a destination stop at
   `j > i`.
4. **One change:** everything reachable on a first bus, intersected with everything that feeds a
   destination stop on a second — including changes that need a short walk, found through a
   ~278 m spatial grid so it stays fast.
5. Drop any change that arrives later than the best direct bus. Nobody transfers to get there slower.
6. Fetch live arrivals for the distinct boarding stops, then re-rank by real arrival time.

## Run it

No build step, no dependencies beyond a Google Fonts link.

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```

Opening `index.html` from the filesystem works too, except geolocation, which browsers only allow
on `localhost` or HTTPS.

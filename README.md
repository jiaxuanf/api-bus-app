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

## The whole trip, with a clock time on every step

Tap the crosshair and it reads your location, finds the stop to walk to, and lays out the journey
as a timeline — not a list of durations you have to add up yourself:

```
13:54   set off — 110 m on foot
13:56   reach Bef Quality Rd                          2 min
14:01   board bus 246                            5 min wait
~14:08  alight Blk 151 · 7 stops                      7 min
~14:09  walk 40 m to CISCO Recall                     1 min
~14:15  board bus 30                             6 min wait
~14:42  alight Bef Pasir Panjang PO · 20 stops       28 min
~14:45  walk 160 m — arrive Opp West Coast Pk         3 min
```

Every row carries the time you'll *be* there. A leading `~` means that time rests on a modelled
number rather than a live one — so you can see at a glance exactly where the certainty runs out:
everything up to boarding is real, everything after it is arithmetic.

## Location

The crosshair beside **From** is one tap. If you've already granted permission on a previous
visit, the app uses it on load without prompting again; if you haven't, nothing happens until you
ask for it. Either way the coordinates are used in the browser to sort the stop list and never
leave it — there is no server here to send them to.

## Trains

MRT is in, and it changes the question. Singapore publishes **no live train-arrival feed** — nothing
public, keyed or otherwise — so an MRT leg cannot be measured, only modelled. Which means the app's
central verdict has to change on a train leg, and it does: it says **No rush**, never *Run*.

That isn't a cop-out. Trains come every few minutes, so "should I sprint?" isn't a real decision —
and manufacturing urgency out of an absence of data would be worse than saying nothing. The one
question the app exists to answer honestly has a different answer for trains, so it gives one.

Routing is a Dijkstra over `(station, line)` nodes, which makes interchanges fall out naturally:

```
14:13   you're at Changi Airport
14:17   board the Changi Airport Branch          4 min wait
~14:25  alight Tanah Merah · 2 stops                 9 min
~14:29  board the East West Line                 4 min wait
~14:50  alight City Hall · 9 stops                  21 min
~14:54  board the North South Line               4 min wait
~14:59  alight Orchard · 3 stops — you're there      5 min
```

Journeys can now mix modes — **bus → train** for a feeder to the nearest station, **train → bus**
for the last mile — and every option is ranked against the others by arrival time, so a 47-minute
train wins over a 61-minute bus without you having to compare them.

Line chips carry the real line colours, because that's how the network is read on the ground.

**Tuas → Pasir Ris now works.** It was the example of failure in this README's previous version;
rail routing solves it in 93 minutes.

## What's live and what's estimated

This distinction matters, so the app states it in its own footer too.

**Live:** arrivals at your boarding stop, from `arrivelah2`, refreshed every 20 seconds — including
crowding (`SEA` / `SDA` / `LSD`, drawn as the three-bar load meter) and the next three buses, so a
"Missed it" can look past the first one. Times shown without a `~` are anchored to this.

**Estimated**, with every constant named at the top of the script so you can argue with them:

```js
const WALK_MPM      = 78;    // metres/min — 4.7 km/h, an unhurried pace
const WALK_DETOUR   = 1.35;  // you can't walk through buildings
const BUS_KMH       = 18;    // SG average once dwell time at stops is counted
const TRANSFER_WAIT = 6;     // assumed wait for a connecting bus
const UNKNOWN_WAIT  = 8;     // assumed wait when a service reports no live arrival
const RAIL_KMH      = 45;    // trains, including dwell
const RAIL_WAIT     = 4;     // assumed headway to board
const RAIL_CHANGE   = 4;     // platform to platform, plus the wait
```

Sanity-checked against real journeys: Bugis → Jurong East 33 min, Bugis → Punggol 34, Changi Airport
→ Orchard 47, Woodlands → Marina Bay 46. All within a couple of minutes of the real thing.

Ride time is that speed along the **real route path** — the sum of the distances between the actual
stops the bus calls at, not a straight line from A to B. Walking distances get the detour factor
for the same reason.

## Honest limits

- **One bus change, maximum.** Rail can interchange as often as it needs to, and a journey may
  combine one bus with rail, but bus → bus → bus is beyond it.
- **No LRT.** The Bukit Panjang, Sengkang and Punggol lines are loops, and station-code order
  doesn't describe a loop's direction, so including them would produce confidently wrong journeys.
  Their MRT interchange stations are in.
- **No live trains anywhere in the model**, because no such feed exists to consume.
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
| `data/rail.json` | 146 MRT stations, vendored here — 10 KB distilled from [cheeaun/sgraildata](https://github.com/cheeaun/sgraildata) by `scripts/build-rail-data.py`. Same origin as the page, so no third-party fetch and no upstream outage can take the trains away. Rebuild it with `python3 scripts/build-rail-data.py` |

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
5. **Rail:** Dijkstra over `(station, line)` nodes. Adjacency comes from consecutive station codes
   — NS7 follows NS6 — and an interchange is simply a station appearing on two lines, so a node like
   Dhoby Ghaut (NS24 / NE6 / CC1) needs no special case. Sources carry the cost of getting there, so
   one pass ranks walking to a station and taking a feeder bus to one against each other.
6. Drop any change that arrives later than the best single-leg option. Nobody transfers to get there slower.
7. Fetch live arrivals for the distinct boarding stops, then re-rank by real arrival time.

## Run it

No build step, no dependencies beyond a Google Fonts link.

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```

Opening `index.html` from the filesystem works too, except geolocation, which browsers only allow
on `localhost` or HTTPS.

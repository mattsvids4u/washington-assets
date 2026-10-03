# DC-F02 — EVIDENCE (Senate Office Building, C7) — updated for asset-v003

Pass 1, 2026-10-02, claude-cloud-agent. **Pass 4 (photo match), 2026-10-02:** Matt supplied five
photographs in chat. These were the first images actually inspected; see "Inspected photographs"
below. They supersede the "link-cited only" limit for E10 and E11.

## Inspected photographs (asset-v002)

| ID | File (stored?) | Source / date / creator | Rights | Viewpoint | Establishes | Known mismatch / limits |
|---|---|---|---|---|---|---|
| E11 | `references/REF_E11_SOB_SW_corner_c1909_AmericanPressAssn_LoC.jpg` (**stored**) | LoC 2003655456, "D.C. Washington - Old Senate Office Building", c.1909–10, © American Press Ass'n (watermark in image) | Published before 1929, so US public domain. LoC catalog lists no known restrictions | Across the Delaware × Constitution intersection, looking NE at the SW corner | **Corner pavilion:** a flat chamfer with two solid piers and a recessed central bay. **Two free-standing columns** stand before **one tall round-arched window**. One **round-arched doorway** sits over a **projecting stair with cheek blocks**. The piers have framed piano-nobile windows with carved ornaments above. The corner attic is **raised**, with a tablet and the **flagpole**. **Round-arched ground-storey windows** run along both fronts. The rusticated base, the Constitution colonnade and the Delaware pilastrade are all visible | Pre-1933 (the First St wing is not visible; irrelevant from this view). Awnings are seasonal dressing, not modelled. Tablet inscription not legible |
| E10 | `references/REF_E10_Senate_side_aerial_1967-03-27_Leffler_LoC.jpg` (**stored**) | LoC 2024639984, Warren K. Leffler (U.S. News & World Report), 27 Mar 1967 | USN&WR collection: no known restrictions per LoC | Aerial from above Union Station, looking S | 1967 state (nearest to 1963). **Closed quadrangle** with slim wings and a large open court. Flat roof behind the parapet. Square NW/NE corners and the chamfered SW corner. Proportions consistent with PARAMS (wing ≈ 1/7 of width) | Oblique and distant, so it can't give exact metres. DC-R02 card still needed |
| E15 | not stored (rights unconfirmed) | User-supplied modern colour photo of the SW corner from Constitution Ave (appears to be an AOC/Senate photograph; source not confirmed) | unconfirmed, so link/description only | Constitution Ave, looking N/NE | Confirms E11 survives unchanged: tall arched window between two columns, arched doorway with stair and cheek walls, framed pier windows, raised attic with flagpole, arched base windows. Windows original (E05) | Modern lamps, signals, cars and trees are not 1963 evidence |
| E16 | not stored (rights unconfirmed) | User-supplied modern photo, dusk, SW corner from the Delaware/Constitution intersection | unconfirmed | as E11 | Same as E15. Also shows the solid raised attic block and the central tablet | Modern bollards and lamps are not 1963 evidence |
| E17 | not stored (**Alamy watermark**, stock licence) | User-supplied 1960s B&W of the **New Senate Office Building** (1958), with 1960s cars | stock / watermarked, so not redistributable | Corner of the New SOB | For the **New SOB, planned as asset-v004**: stripped-classical facade, tall recessed window bays, a central pedimented portico with columns, square attic windows, a corner entrance | Not the v001/v002 building |

### Pass 5 close reading (asset-v003)

Enlarged crops of E11 (corner, colonnade, Delaware front) were re-read against E15 and E16:

- **The chamfer piers are plain** in E11, E15 and E16. The framed windows with carved ornament
  above are on the **return bays**, not the chamfer. v002 put them on the chamfer, which was wrong.
- **Corner returns:** each street front next to the chamfer repeats the motif:
  framed-window pier | recessed bay with 2 columns before a tall arched window | framed-window pier.
  The colonnade (Constitution) and the pilastrade (Delaware) start only after it. Seen in E11 (both
  returns), E15 (Delaware return) and E16 (both).
- **Framed return windows** carry low pediments (E15, E16). The ornament above them is a carved
  cartouche (E11).
- **Tall arched windows** in the recesses are small-paned grids, about 4 lights wide (E11), with a
  radiating fanlight.
- **Arched ground-storey windows are tall and narrow:** about 0.36 of a bay wide and about 3× as tall
  as wide (E11 colonnade crop). v002 had widened them, which was wrong.
- **Chamfer base:** plain rustication either side of the door (E11). Console brackets flank the door
  head under the window balconette (E11, E15). The stair sits between wide granite podium blocks
  running across the chamfer (E11, E16).
- **Raised corner attic** is only slightly higher than the parapet (E16).
- **"Double colonnade" (E02)** = free-standing columns with matching pilasters (responds) on the
  loggia wall behind. Visible in the E11 colonnade crop; already modelled.
- **Delaware centre pavilion:** E11 (low resolution, far left) suggests the same pier / columns in
  antis / pier motif rather than plain pilasters. Modelled that way, **APPROXIMATE**.

Changes driven by these photos (asset-v002): the SW corner pavilion was rebuilt; the base windows
became round-arched; a raised corner attic and a flag socket were added. See HANDOFF.md.

**Target state:** autumn 1963, as seen from Constitution Ave NE on the north-loop escort route
(road-plans canon v002).

**1963-facing name:** "Senate Office Building" (canon lock). From 1958 it was commonly called the
"Old Senate Office Building", once the New Senate Office Building opened. It was named for Richard
B. Russell only in 1972 (E06). "Russell" is a production label only. Nothing in the mesh displays a name.

## Access limits (read this first)

- **Archive hosts are blocked from this sandbox.** loc.gov, tile.loc.gov, commons.wikimedia.org,
  upload.wikimedia.org, en.wikipedia.org, aoc.gov and catalog.archives.gov all fail through the
  egress proxy (curl 000 / WebFetch EGRESS_BLOCKED).
  - Every photo record below was found by web search and is **link-cited only**. None was opened
    or inspected as an image, so none clears the photo gate on its own.
  - No image was downloaded or redistributed.
- **No Senate Office Building image exists in Drive** (search on 2026-10-02). The DC-F02 References
  folder holds only the two Willard Hotel starter images, which are out of v001 scope.
- **DC-R02 evidence cards are out of reach.** The SOB footprint, height and year cards are in the
  full R02 package, which lives only on Matt's PC. v001 dimensions are therefore APPROXIMATE and
  parameterised in `build.py` (`PARAMS`), so they can be replaced with R02 values.
- **Gap to close next pass:** Matt (or a local agent) drops 3+ permitted SOB photos into
  `References/DC-F02/` so the cloud agent can inspect them through Drive. The highest-value ones
  are E10, E11 and E12.

## Sources

| ID | Source | Date | Creator / institution | Rights | Establishes | Limits |
|---|---|---|---|---|---|---|
| E01 | AOC, "Russell Senate Office Building" — https://www.aoc.gov/explore-capitol-campus/buildings-grounds/senate-office-buildings/russell | page current 2026 (building 1903–09; First St wing 1931–33) | Architect of the Capitol | US Gov work | Site bounded by Constitution Ave, First St, Delaware Ave and C St NE. Carrère & Hastings with Edward Clark. Beaux-Arts. Rusticated base with a colonnade, entablature and balustrade above. **34 Doric columns on Constitution Ave**, echoed by **pilasters on Delaware Ave**. Rotunda at the main entrance, 18 Corinthian columns, 57 ft 4 in diameter. | Text only, via search snippet |
| E02 | U.S. Senate Historical Office, "The Russell Senate Office Building" briefing — https://www.senate.gov/artandhistory/history/common/briefing/RSOB.htm | 2000s text | US Senate | US Gov work | **Three storeys above ground on Constitution Ave; five above ground on C St** (steep slope). Materials: **Vermont marble** on the Constitution and Delaware fronts, on a **New Hampshire grey granite base and terrace**. **Georgia marble** on C St and the later First St elevations. **Bedford (Indiana) limestone** on the court fronts. Rusticated lower base, "double colonnade" supporting entablature and heavy cornice, classical balustrade; Louvre-colonnade model. Opened 5 Mar 1909. Originally U-shaped, open to First St. | Text only |
| E03 | AOC / Senate.gov First Street wing text (same pages) | wing contract Mar 1932, complete Apr 1933 | AOC | US Gov work | Nathan Wyeth & Francis P. Sullivan. Same marble/limestone as the original. The wing **closed the court**, so in 1963 the plan is a closed quadrangle. | — |
| E04 | SAH Archipedia DC-01-CH03 — https://sah-archipedia.org/buildings/DC-01-CH03 | 2010s | Society of Architectural Historians | Text, © SAH | Located at the **NE corner of Delaware and Constitution Aves**. Colonnades on the main fronts, pilastrades with central pavilions on the secondary fronts. **Two-storey circular entry vestibule (rotunda) at the corner.** Louvre reference. | Text only |
| E05 | AOC blog / Russell Exterior Envelope Project — https://www.aoc.gov/what-we-do/projects/russell-exterior-envelope-project and https://www.aoc.gov/explore-capitol-campus/blog/100-year-old-russell-senate-office-building-getting-some-work-done | 2010s–FY2023 | AOC | US Gov work | **622 windows, most original to the building.** The envelope project (FY2023) restored the original windows and stone. So window openings and sash pattern seen in modern photos are carry-forward evidence for 1963. | Modern restoration cleaned the stone, so 1963 stone was dirtier → Age + Use stage (W01), not this stage |
| E06 | U.S. Senate, "Senate Office Buildings Named" — https://www.senate.gov/artandhistory/history/minute/Senate_Office_Buildings_Named.htm | — | US Senate | US Gov work | Buildings named Russell/Dirksen in 1972. 1963 names: (Old) Senate Office Building / New Senate Office Building | — |
| E07 | DC Preservation League, historicsites item 543 — https://historicsites.dcpreservation.org/items/show/543 | — | DCPL | text | Beaux-Arts exemplar; same facts as E01/E02 | Text only |
| E08 | Gatehouse note (E01/E04 snippets) | 1930s? | AOC | — | Gatehouse at Delaware Ave & C St, with a matching one across the street | Belongs to Senate Park / grounds. **Not** modelled in v001 (out of building scope) |

## Photo records (link-cited, NOT inspected — see access limits)

| ID | Record | Date | Creator | Rights (per catalog) | Would establish |
|---|---|---|---|---|---|
| E10 | LoC 2024639984 "[Aerial view of the Senate side of the U.S. Capitol Complex showing the Russell Senate Office Building, the Dirksen Senate Office Building and Senate Park]" — https://www.loc.gov/item/2024639984/ | **27 Mar 1967** (nearest dated view to 1963) | Warren K. Leffler, U.S. News & World Report | USN&WR collection: no known restrictions (verify on record) | Roof, court, wing depths, footprint proportions, the 1933 east wing, slope context |
| E11 | LoC 2003655456 "D.C. Washington - Old Senate Office Building" — https://www.loc.gov/item/2003655456/ | c.1910 | — | check record | Constitution Ave colonnade and corner, before the 1933 wing |
| E12 | LoC 2019683168 "Russell Senate Office Building. Northwest corner…, Delaware Ave. and C St. II" — https://www.loc.gov/item/2019683168/ | c.1920 | Theodor Horydczak | Horydczak collection: no known restrictions (verify) | NW corner, the C St slope, exposed basement storeys, Delaware pilastrade |
| E13 | Wikimedia Commons Category:Russell_Senate_Office_Building — https://commons.wikimedia.org/wiki/Category:Russell_Senate_Office_Building | various, incl. HABS | various | mixed (PD/CC) | Modern elevations; windows are original (E05) |
| E14 | LoC U.S. News & World Report collection finding aid (pp021007) | 1962–64 | USN&WR | — | Archive lead for exact-period Capitol Hill street views |

## Feature table (what v001 builds and on what authority)

| Feature | v001 treatment | Label |
|---|---|---|
| Site, closed quadrangle (1933 wing) | Hollow rectangle with inner court | VERIFIED (E01–E03) |
| Footprint 143.0 × 110.0 m, wing depth 20 m | Parameter | **APPROXIMATE** (replace with R02 card) |
| Grade drop of 7.0 m from Constitution Ave to C St (3 vs 5 storeys) | Linear N–S slope; extra rusticated basement storeys exposed on C St and the sides | Storey counts VERIFIED (E02); 7.0 m and the linear profile **APPROXIMATE** |
| Constitution Ave: rusticated base + colonnade of 34 Doric columns in a loggia + entablature + balustrade | Modelled: 34 fluted Doric columns, recessed loggia wall, two window tiers per bay, triglyph frieze, cornice, balustrade with pedestals over columns | Count + parti VERIFIED (E01, E02). Column height, spacing and loggia depth **APPROXIMATE** |
| End pavilions on Constitution Ave | Slightly projecting pavilions with paired pilasters | **APPROXIMATE** (typical of the parti, E04 "pavilions") |
| Delaware Ave, C St, First St fronts: pilastrades with central pavilions | Engaged Doric pilasters, flush wall, central pavilion | VERIFIED as parti (E01, E04). Bay counts **APPROXIMATE** |
| Corner rotunda entrance at Delaware & Constitution (SW corner) | **v003:** plain chamfer piers; recessed central bay with 2 Doric columns in antis (in the pier plane, architrave flush) before a tall small-paned arched window with a balconette on console brackets; one arched bronze doorway between granite podium blocks with a 6-riser stair; low raised attic block with a blank tablet. **v002 (superseded):** chamfer with two solid piers (framed windows, oval cartouches, arris pilasters). Recessed central bay with 2 free-standing Doric columns before a tall round-arched window with a balconette. One round-arched bronze doorway with a fanlight, over a projecting 6-riser granite stair with cheek blocks. Arched base windows in the piers. Raised attic block with a blank tablet. Flag socket. (v001's 4 columns and 3 doors were wrong.) | **VERIFIED by photo (E11, E15, E16).** Exact widths, column order detail and cartouche carving **APPROXIMATE** |
| Corner-pavilion returns (Constitution and Delaware) | **v003:** 12 m return on each front: framed-window pier (pediment, cartouche) / recessed bay with 2 columns and a tall arched window / framed-window pier, over 3 arched base windows | **VERIFIED by photo (E11, E15, E16).** Widths **APPROXIMATE** |
| Delaware centre pavilion | **v003:** same pier / columns in antis / pier motif | **APPROXIMATE** (E11, low resolution) |
| Ground-storey windows | **v003:** round-arched, tall and narrow (1.2 m wide × 4.1 m), stone spandrels, fanlight, keystone, on all street fronts | **VERIFIED by photo (E11, E15, E16)** for the Constitution and Delaware fronts. C St / First St fronts assumed the same (**APPROXIMATE**) |
| Materials: Vermont marble (S, W), Georgia marble (N, E), NH granite base/terrace, Indiana limestone courts | Separate material slots | VERIFIED (E02) |
| Windows: original wood sash, 6-over-6 (piano nobile), 6-over-6 (upper), 2-over-2 (base) | Real openings, frames, sash bars, glazing | Openings VERIFIED (E05). Sash pattern **APPROXIMATE** |
| Roof: flat, behind the balustrade, with low skylight ridges over corridors | Flat roof plus parapet | Flat roof behind the parapet **VERIFIED (E10, 1967)**. Skylight ridges **APPROXIMATE** |
| Window AC units, flags, lamps, signage | Not modelled (no signage on the building in 1963 that is known) | — |
| Window interior states (lit / dark / blinds) for the night read | Atlas on the glazing, seeded per window | **FICTIONALISED** (gameplay dressing) |

## asset-v004 (New Senate Office Building): Pass 1 text evidence, 2026-10-03 (scheduled run)

Scope: the **New Senate Office Building** (1963 name; it was named Dirksen in 1972, E06). It was
accepted for occupancy on 15 Oct 1958, so in Oct–Nov 1963 it was five years old. The Hart building
on its east side dates from 1982 and **must not appear**.

Access limit for this run: the sandbox network policy blocks loc.gov, wikimedia, wikipedia,
senate.gov, aoc.gov and sah-archipedia.org (direct and WebFetch). Only WebSearch result text was
available. **No NSOB photograph was inspected this run.** E17 (Alamy, 1960s, inspected in an earlier
session and not stored) is still the only NSOB image anyone has looked at.

| ID | Source (as surfaced by WebSearch, not opened) | Date | Supports | Status |
|---|---|---|---|---|
| E23 | AOC, "Dirksen Senate Office Building", https://www.aoc.gov/explore-capitol-campus/buildings-grounds/senate-office-buildings/dirksen | current page | Eggers & Higgins; seven storeys; E-shaped; marble and limestone; site bounded by Constitution Ave, First St, Second St and C St NE; half the block between First and Second in 1958; occupancy 15 Oct 1958; 750,520 sq ft. "Tall ribbons of glass and dark panels alternated with marble to suggest a colonnade" | TEXT ONLY |
| E24 | SAH Archipedia DC-01-CH06, https://sah-archipedia.org/buildings/DC-01-CH06 | current page | "Synthesis of the classical and contemporary". **First St** is the principal elevation, with a **pilastered central bay, entablature and pediment**. Windows alternate with wall strips of equal width (a colonnade rhythm), with matching basement and attic windows. **Entries are on Constitution Ave**, through doors in the centre of **three-bay wall projections at each end**. Danby marble and Chelmsford granite on the street fronts; limestone on the court fronts | TEXT ONLY |
| E25 | Search summary of the AOC art record for the Dirksen spandrel reliefs (search hit only; the record URL was not surfaced) | — | **51 bronze reliefs** on the spandrels between the 3rd- and 4th-floor windows. Five subjects: shipping, farming, manufacturing, mining, lumbering. Figures 2'2" square set in 3'4" square panels; Eggers design, modelled by Rochette & Parzini, cast by Flour City Ornamental Iron. 1958 work, so **rights unconfirmed**. Use labelled simplified stand-ins (stage standard §7) | TEXT ONLY |
| E26 | Visit the Capitol, "Preliminary Design for the Dirksen Senate Office Building", Eggers & Higgins, 1948, https://www.visitthecapitol.gov/artifact/preliminary-design-dirksen-senate-office-building-eggars-higgins-1948 | 1948 drawing | Design intent only. The 1948 scheme differs from the building as constructed in 1956–58 | LEAD (not opened) |
| E27 | LoC P&P 2023631785, "Back exterior of the Hart Senate Office Building with the Dirksen Senate Office Building in the background, Second St and C St NE", https://www.loc.gov/pictures/item/2023631785/ | post-1982 | C St / Second St side of the NSOB. Shows later context (Hart), so the date mismatch must be noted | LEAD (not opened) |
| E28 | AOC Dirksen photo gallery and the senate.gov Dirksen page, https://www.senate.gov/about/historic-buildings-spaces/office-buildings/dirksen-building.htm | current | Modern and possibly 1958 construction or dedication photos | LEAD (not opened) |

### Conflicts and gaps (must be resolved before the v004 build)

1. **Frontage dimensions.** No length or height figures were found. The footprint needs the DC-R02
   card or a dated plan.
2. **First St portico.** E17 (memory of an earlier session's inspection) shows a "central pedimented
   portico with columns". E24 says "pilastered central bay ... pediment". Columns or pilasters? Only a
   photo settles this.
3. **Constitution Ave entrances.** E24 says "three-bay projections at each end". E17 noted "a corner
   entrance". Compatible, but bay counts and door forms are unverified.
4. **The 1963 east end.** The Hart site was vacant or used for other things in 1963. What stood there
   (parking, other buildings) is unknown.
5. **Window and spandrel pattern.** "Tall ribbons of glass and dark panels" plus bronze spandrels
   between floors 3 and 4: the dark panel material and mullion layout need a photo.

### Photo pack wanted (put permitted images in References / DC-F02, or send them in chat)

- A 1958–65 view of the Constitution Ave front (or the earliest available), showing the end
  projections and the entrances.
- A First St front view of the central bay, to answer columns vs pilasters.
- A close view of a window bay with spandrel reliefs, to measure the glass/panel/marble rhythm.
- Any dated plan or elevation (AOC) for the footprint and height.

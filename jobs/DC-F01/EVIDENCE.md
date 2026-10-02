# DC-F01 v001 — EVIDENCE (C10 hard-locks: Library of Congress Annex, Folger, Cannon)

Target state: **October–November 1963**. Compiled 2026-10-02 by claude-cloud-agent.

## How the evidence was gathered — and its limits (read first)

- This cloud environment's network policy is an **allowlist**. loc.gov, tile.loc.gov,
  Wikimedia (commons/upload), Wikipedia, NARA, NPS/NPGallery, AOC, house.gov, DC Planning,
  SAH Archipedia, folger.edu, archive.org, HathiTrust, Flickr and OSM all returned HTTP 403
  from the policy proxy for both curl and WebFetch. **No reference image could be opened,
  inspected or saved in this run.**
- **Update, second run (2026-10-02, same claim):** the Drive connector now returns image
  data, so the two starter photos in `References/DC-F01` were downloaded, inspected and
  measured (see "Photo inspection" below). The outside photo archives are still blocked
  (HTTP 000 from loc.gov, tile.loc.gov, Wikimedia and NARA), so no 1963-dated photo has been
  inspected yet.
- Facts come from **WebSearch result text** quoting the named pages. Three research agents
  ran ~170 searches before the session's 200-search cap ran out. Full fact sheets, with
  every quote and source key, are in `research/*_factsheet_agent_2026-10-02.md`.
- The **DC-R02 v001** approved footprint/height dataset is the placement authority. Its data
  package is on Matt's PC only (the Drive folder holds just the handoff), so v001 footprints
  come from published dimensions. They must be re-checked against the R02 evidence cards
  before placement.
- Only the Folger north facade has now been checked against a photo, and that photo is from
  2025. **Annex and Cannon facade rhythm details (bay counts not stated in text, window sizes,
  heights, mouldings) are still APPROXIMATE**. The renders show the actual exported
  output, ready for Matt to compare with the photo records listed per building.

Labels: **VERIFIED** = stated by a named authoritative source (as quoted in search text) ·
**PROBABLE** = secondary source or consistent inference · **APPROXIMATE** = reasoned
estimate, unverified · **FICTIONALISED** = invented (none of the building identities are
fictional; only stand-in sculpture and placeholder landscape are invented forms, labelled below).

## Photo inspection (second run, 2026-10-02)

Ref 01 (Folger, Commons 2025, CC BY-SA 4.0, Ser Amantio di Nicolao) is taken from the **NE corner** (the Adams Building
shows behind the east end). Review camera `photo01_ne` in render_review.py roughly matches this vantage. The
side-by-side is `renders/review/CMP_ref01_vs_photo01_ne.png`. It supports the following (all north facade; carved
stone is unchanged since 1932, so it is valid for 1963):
nine bays ✓ · reliefs directly under the windows at terrace level ✓ · wide fluted pilasters with sunk window fields
running up to the frieze (fixed) · rectilinear grilles (fixed) · window heads at ~9 m and the frieze on them (fixed) ·
canopy entrances with masks (fixed) · inscriptions in the attic over the window row (fixed) · upper dentil band and
slight recession at the top ✓. Excluded as post-2019: the "FOLGER THEATRE" letters on the terrace wall, the planters
and the modern lamp.

## Drive starter photos (References/DC-F01, collected 2026-09-22)

| File | Source / ID | Date | Creator | Rights | What it could support | Limitation |
|---|---|---|---|---|---|---|
| 01_Exterior_view_Folger_Shakespeare_Library_June_2025_166991267.jpg | commons.wikimedia.org/wiki/File:Exterior_view,_Folger_Shakespeare_Library,_June_2025.jpg | 2025-06-03 (EXIF) | Ser Amantio di Nicolao | CC BY-SA 4.0 | Folger north facade composition | Post-2024 renovation (new entrances/landscape must be excluded). **Inspected and measured 2026-10-02 (second run).** |
| 02_Adams_Building_Exterior_Stairs_32044495186_54993551.jpg | commons.wikimedia.org/wiki/File:Adams_Building_Exterior_Stairs_(32044495186).jpg | 2017-01-03 | USCapitol | Public domain | Annex entrance stair detail | Modern view. **Inspected 2026-10-02:** close-up of the white marble treads with tan/grey veining and soiling; it supports the material and tone only, not geometry. |

Moodbook: `SAVE_JFK_Visual_Benchmark_Moodbook.pdf` (Drive 11YkCsfarp_oZ-ylqn0sN3ahHHr-G5QNr). Pages
10–12 were read as **text only**; the page images could not be viewed here (see CONTEXT_ACK.json).

---

## 1. Library of Congress Annex (1963 name; "John Adams Building" from 1980)

Sources (all accessed 2026-10-02 via search text): AOC building page (aoc.gov/explore-capitol-campus/buildings-grounds/library-of-congress/john-adams-building) ·
AOC roof replacement project page · LoC blog "The Annex — 400 feet by 225 feet" (blogs.loc.gov/inside_adams/2019/04/, quoting the *Evening Star*, 20 Sep 1936) ·
LoC "Art and architecture of the John Adams Building" · SAH Archipedia DC-01-CH13 · J. Y. Cole, *On These Walls* (loc.gov/loc/walls/adams.html) ·
LoC blog "Know your marble" (2011-06-09) · LoC blogs "Our bronze doors" (2009-12) and "Labors in bronze" (2023-09) · LoC floor plans page · DC HPO Folger reports.

### Evidence card

| Item | Value used | Label | Source |
|---|---|---|---|
| Name in 1963 | Library of Congress Annex | VERIFIED | LoC blog (renamed Adams 1980); Road Plans canon v002 locks |
| Site | Block between 2nd St SE (west) and 3rd St SE (east), Independence Ave (south); private drive/service area on the north separating it from the Folger | VERIFIED | LoC floor plans; DC HPO Folger reports |
| Built | 1935–38; occupied Dec 1938; opened 3 Jan 1939. Architects Pierson & Wilson, consultant Alexander B. Trowbridge | VERIFIED | AOC |
| Footprint | **400 ft (E–W) × 225 ft (N–S)** = 121.92 × 68.58 m | VERIFIED | Evening Star 1936 via LoC blog |
| Storeys | five above ground over the cellar; **5th storey set back 35 ft (10.67 m)** on all sides | VERIFIED | Evening Star 1936; AOC/LoC |
| Heights | ground floor at 1.35 m; floors 1–4 at 3.9 m; main parapet 24.0 m, pavilions 24.6 m; attic top 29.6 m; upper roof tier 31.2 m | APPROXIMATE | none found. Estimate from 12 stack tiers (cellar to 4th floor) ≈ 15 ft per level |
| Composition | rectangle with **corner and central pavilions linked by wide fenestrated curtains**, "terminated by a high recessed attic"; planar walls, **sunken window frames**, stylised **honeysuckle** ornament; "vertically linked window bays alternate with narrow strips of marble-clad walls" | VERIFIED (wording) | SAH Archipedia |
| Pavilion and curtain widths, bay counts | corner pavilions 11.6 m, central 24.4 m (N/S) / 19.5 m (E/W); 0.9 m projection; curtain bays 3.38 m (N/S, 10 each) and 3.24 m (E/W, 4 each) | APPROXIMATE | not stated in any source |
| Spandrels | **bronze panels** between windows, honeysuckle ornament cast in | PROBABLE (inference) | SAH contrasts "window bays" with "marble-clad" piers, so the bays are probably not marble; verify on Horydczak photos |
| Cladding | **Georgia white marble with a skirt of North Carolina pink granite**; matte finish | VERIFIED | LoC "Know your marble"; SAH |
| Doors | **Lee Lawrie bronze doors**, Flour City Ornamental Iron Co.: **three pairs west (2nd St), three east (3rd St), one south**, the south pair reached by a stair with **stylised owls and lamps** | VERIFIED (W/E/S counts PROBABLE: "seven pairs") | LoC blogs; Cole; SAH |
| Door figures | history of the written word, one figure per leaf (six per entrance); south doors show physical and intellectual labour | VERIFIED | Cole; LAB23 |
| Roof | original **copper** (replaced 2020s), three tiers | VERIFIED | AOC roof project |
| Window metal | bronze-toned frames | APPROXIMATE | not found |
| Exterior inscriptions | none found | NOT FOUND | (signage socket left PENDING) |

Excluded as post-1963: modern glass entry doors, security bollards/ramps, current signage, the 2020s roof replacement.

**Sculpture rights:** Lawrie's 1938–39 bronze doors were a private commission and their rights are unconfirmed. They are modelled as **labelled stand-ins**: one abstract figure per leaf, never a likeness. The owls and lamp standards are also simplified stand-ins.

**Photo records to inspect** (LoC control numbers): Horydczak 2019682846 "South side of Library of Congress annex I" (LC-H814-L03-071); 2019682853 "annex and Folger Library from northwest" (LC-H814-L03-078); 2019682843 / 2019682847 (from the roof of the main library); 2019676989 (roof); thc.5a38330 (south stairs and entrance); 2019676975 / 2019676978 (plastic models, good for massing); door photos 2019682824 and 2019682856. LOT 5760 (2004668869) includes the 1939 aerial 2012646221 (LC-DIG-ds-01526). Drawings: 94506196 (first floor plan), 94506200 (5th-floor reading rooms), 2002719444 (perspective). Highsmith 2007: 2007687067 (exterior), 2007687085, 2007687094–096, 2007687055 (owl).

---

## 2. Folger Shakespeare Library (201 East Capitol St SE)

Sources: DC HPO Landmark Nomination Staff Report, Case 17-07 (2019) · HPRB Staff Report HPA 19-332 (27 Jun 2019) · NRHP Registration Form amendment, Case 22-16 (DC Preservation League, 2022) ·
NRHP-form nomination "Folger Shakespeare Memorial Library" (DC HPO, c. 2017–19) · DC HPO Hartman-Cox addition report · SAH Archipedia DC-01-CH15 · Folgerpedia "A Monument to Shakespeare" and Timeline ·
folger.edu building history, the Collation posts "Creating John Gregory's Bas Reliefs" and "The 'Greco Deco' Folger", and "Why the Folger has two sculptures of Puck" · Folger "Excavating the Folger's Future" (2021) · CyArk / Open Heritage 3D (DOI 10.26301/3tpx-nd97).

### Evidence card

| Item | Value used | Label | Source |
|---|---|---|---|
| Site | full block on the south side of East Capitol St between 2nd and 3rd Sts SE; main facade north; west end faces 2nd St and the Capitol | VERIFIED | HPO / HPRB reports; Folger |
| Built | 1929–32, Paul P. Cret with consulting architect Alexander B. Trowbridge | VERIFIED | HPO; Folger |
| Footprint and height | **226 ft E–W × 111 ft N–S, 48 ft high** (68.88 × 33.83 × 14.63 m) | VERIFIED (excerpt) | NRHP amendment 2022 |
| Massing | "long, three-story building sits atop a raised plinth"; U-shaped with the courtyard on the south | VERIFIED | HPRB; HPO; SAH |
| North facade | smooth white marble, divided into **nine bays** of long narrow windows with **Art Deco aluminium grilles**, separated by **fluted pilasters** | VERIFIED (excerpt) | HPRB / NRHP; HPO addition report |
| Reliefs | **nine marble bas-reliefs by John Gregory**, carved 1932 by the Piccirilli Brothers, each **6 × 6 ft**, below the windows; left-to-right order MND, R&J, MoV, Macbeth, JC, Lear, R3, Hamlet, H4 | VERIFIED (order PROBABLE in the middle) | Folger Collation; Glenshaw |
| Top of the facade | "broad attic story broken only by inscriptions, a slight recession at the top, and an entablature of shallowly incised abstract classical ornament" | VERIFIED (excerpt) | SAH |
| Inscriptions | Ben Jonson "Thou art a monument, without a tombe …"; Samuel Johnson "This therefore is the praise of Shakespeare …"; First Folio spellings | VERIFIED text. **Positions VERIFIED by photo (ref 01):** both quotes are in the attic above the window row, with Johnson legible over the east half, so Jonson goes over the west half (v001 run 1 had them over the end doors, swapped) | folger.edu inscriptions page; ref 01 |
| West end | "treated more prominently, as the main approach is from the west"; "two similar façades" | VERIFIED / PROBABLE | SAH; Folger podcast |
| Puck | Brenda Putnam, 1932, **marble**, on a fountain facing west; "Lord, what fooles these mortals be!" (marble original in place in 1963; aluminium copy only from 2001–02) | VERIFIED | Folger |
| East end | "a blank wall broken only by masks of comedy and tragedy"; the theatre is in the east wing | VERIFIED (excerpt) | SAH; NRHP |
| Front terrace | terrace with a shallow lawn about 25 × 135 ft along the north elevation; marble staircases, a wall along the front, marble and bluestone paving | VERIFIED (lawn per a 2017–22 document; 1932 match PROBABLE) | NRHP-form nomination; Folger 2021 |
| Rear in 1963 | U-shaped plan; the courtyard was filled by the **1958–59 one-storey addition** (present in 1963) | VERIFIED | HPO addition report; Folgerpedia |
| Materials | white **Georgia marble** ashlar in "alternating rows of larger and smaller panels"; marble plinth; **all exterior metal aluminium**; glazed brick on non-primary walls | VERIFIED (brick location PROBABLE) | NRHP; Folger Collation |
| Bay spacing, window size, heights | 15 ft bays (9 × 15 ft = the 135 ft lawn) APPROXIMATE; **glass 1.83 × 5.26 m (3.99–9.25 m), sunk window field 2.4 m wide up to the frieze, fluted pilasters 1.4 m with 8 flutes, incised frieze 9.85–10.75 m**, attic to 14.0 m | **PROBABLE** (photo-measured on ref 01; run 1 had the windows 1.2 m too tall and the pilasters 0.86 m) | ref 01 measured along vertical lines on the facade plane, scaled from the attic line and the 1.83 m relief panels (±0.4 m) |
| Rear wing widths, reading-room block, 1958 addition height | 15/17 m wings; 4.3 m addition | APPROXIMATE | not stated |
| Doors | north-facade end entrances: grille door about 2.2 × 4.5 m in a tall sunk panel; mask cartouche just above the door inside the panel; fluted strips each side; **projecting flat canopy** whose top meets the frieze, with a pendant lantern | **PROBABLE** (ref 01; lantern form APPROXIMATE) | ref 01; Folger page excerpt |
| Window grilles | cast aluminium, **rectilinear interlocking-rectangle fret** over the full height (run 1 used chevron heads, which was wrong) | VERIFIED type (ref 01) / APPROXIMATE exact pattern | ref 01 |
| East end door (ref 01) | the 2025 photo shows a door with steps and a vertical break in the east wall | **NOT MODELLED. CONFLICT:** SAH describes "a blank wall broken only by masks"; the door may be a 2019–24 change. Needs a pre-2019 photo (Horydczak / CyArk 2020) | ref 01 vs SAH |

Excluded as post-1963: the Hartman-Cox reading room (1983); the Elizabethan Garden (1989); the aluminium Puck (2001–02); the 2019–24 KieranTimberlake/OLIN works (Adams Pavilion under the lawn, sunken entry plazas and ramps, tapestry gardens, poem wall, new Puck fountain, aluminium quotation letters).

**Sculpture rights:** John Gregory's 1932 reliefs and Brenda Putnam's Puck may still be in copyright (renewal and notice status are undetermined). Both are modelled as **labelled simplified stand-ins**: smooth abstract figure masses and an abstract standing figure, never likenesses. The comedy/tragedy masks are stand-in medallions.

**Photo records to inspect:** Gottscho-Schleisner, 22 Jun 1932 (LOT 12401, gsc 5a00146; 2018734345, "Vertical of four panels"); Horydczak 2019673381 (colour transparency of the front, thc.5a51349), 2019682862 (west end), 2019684231 (Puck fountain), 2019681567, thc1995013111 (Hamlet carving); LoC 2006678488 (Puck with the Capitol dome, 1932), 2018717226; Highsmith 2010641652 / 2010641655; CyArk point cloud (Aug 2020, pre-renovation). Drawings: Cret working drawings 1926–31, ADE - UNIT 1963 (LCCN 95860220); ironwork 95860219 / 95860218.

---

## 3. Cannon House Office Building (named 21 May 1962; "Old House Office Building" 1933–62)

Sources: AOC Cannon building, history, "Cannon courtyard as intended" (c. 2025), "Doric columns" and Cannon Renewal pages · House Historian pages on the original building opening and on the naming of the House office buildings ·
Congressional Directory, GPO, 15 Jun 1999 · SAH Archipedia DC-01-CH02 (Cannon), DC-01-CH03 (Russell) and essay DC-01-0002 · US Senate Historical Office (Russell) · MTFA Architecture (Renewal preservation architect).

### Evidence card

| Item | Value used | Label | Source |
|---|---|---|---|
| Name in 1963 | Cannon House Office Building (P.L. 87-453, signed 21 May 1962) | VERIFIED | House Historian |
| Site | Square 690: Independence Ave (N; "B Street" on the 1905–07 drawings), First St SE (E), C St SE (S), **New Jersey Ave SE (W, diagonal)** | VERIFIED | AOC; LoC 97506876 |
| Plan | **hollow trapezoid**, four wings around a central court; closed quadrangle from 1908 | VERIFIED / PROBABLE | AOC; MTFA; Senate |
| Court | "300-foot-wide opening encompassing **70,000 sq ft**"; **1955 garage under the court**, so in 1963 the court was a garage deck, not the 1908 garden | VERIFIED | AOC |
| Footprint | north (Independence) **440 ft**, N–S **380 ft**, New Jersey Ave at **13.5°** east of south (south side ≈ 349 ft); wings 65 ft | APPROXIMATE. Cross-check: these give a court ≈ 300 ft wide and **≈ 69,500 sq ft**, matching AOC's 70,000 sq ft | derived |
| Main entrance | NW corner (Independence × New Jersey), rotunda behind: 57 ft 4 in diameter, three storeys | VERIFIED | AOC; MTFA; House Historian |
| Corner form | chamfered NW entrance face, 14 m, with arched portal and a large window above | APPROXIMATE (exterior form not found) | — |
| Built | 1905–08, Carrère & Hastings (Thomas Hastings); 5th storey added **1913–14 "by raising the roof"** | VERIFIED | AOC; GPO |
| Storeys in 1963 | basement plus five | VERIFIED | AOC; WP |
| Elevation | **rusticated base carrying a colonnade with entablature and balustrade**, "reminiscent of the Colonnade du Louvre"; the base is "long rusticated arcades" with the order rising "through two stories" | VERIFIED | SAH; WP |
| Colonnade | **34 fluted Doric columns** on Independence Ave | VERIFIED | AOC "Doric columns"; House Historian |
| Column pairing | **coupled** (17 pairs) | PROBABLE (SAH "doubled fluted columns … doubled pilasters"; Louvre analogy). **HIGH-PRIORITY photo check**: `CANNON["n_pairs"]` and `pair_cc` switch it | SAH |
| Secondary fronts | coupled pilasters ("pilastrade") on New Jersey Ave; pilasters continue on First St and C St | VERIFIED / PROBABLE | SAH; AOC |
| Heights | base 9.0 m (+0.4 stylobate); order 9.6 m (column Ø 1.2 m); entablature 19.0–21.4 m; balustrade to 22.6 m; attic (4th + 5th storeys) set back 2.4 m, roof 28.0, coping 28.4 m | APPROXIMATE | typological; not stated |
| Stone | **South Dover, NY marble** on the Independence and New Jersey fronts; **Georgia marble** on the C St and First St fronts; **Bedford, Indiana limestone** on the court fronts | VERIFIED | AOC history |
| Granite | low granite plinth course | APPROXIMATE (MTFA lists granite; location not found) | — |
| Window sash | dark painted | APPROXIMATE | not found |
| Court archway | location not found; socket left PENDING | NOT FOUND | — |

Excluded as post-1963: the 2015–c. 2025 Cannon Renewal (court lawn and new fountain, restored finishes, modern security). "White Vermont marble" (Wikipedia) contradicts AOC and is **not** used.

**Context in Nov 1963** (not built here): the Rayburn building was under construction (cornerstone 24 May 1962, opened 1965), and the future Madison site east across First St was still standing rows (Road Plans RG03, unresolved).

**Photo records to inspect:** LoC 2016646401 (Trikosko aerial, 11 Mar 1964, closest to target); LoC 97506876 (Carrère & Hastings drawing set 1905–07, 101 sheets with elevations and sections, pre-1913 roof); HABS DC-2 (LoC dc0471, HABS DC,WASH,401-; Boucher photos 1976 plus data pages); Horydczak 2019672849 (Nov 1938, LC-H824-1144-004) and 2019684694; history.house.gov 15032399787 (Harris & Ewing postcard, New Jersey Ave side); LoC 2024639980 (aerial 1967), 2016815564 (Detroit Publishing 1910–20), 2007683626 (Fawcett 1908).

---

## Open research gates (carried into PASS_PLAN / HANDOFF)

1. Inspect the photo records above, then correct bay counts, window sizes, heights and moulding profiles where they differ (all three buildings).
2. Re-snap all three footprints to the DC-R02 v001 evidence cards (R02 data not reachable here).
3. Cannon: coupled vs single columns; the NW corner exterior; how the 5th storey reads from the street; court archway location.
4. Annex: spandrel material (bronze PROBABLE); bay counts; attic cladding; entrance stair rises.
5. Folger: inscription positions; west facade composition; terrace layout in 1932–63; 1958–59 addition appearance.
6. Sculpture rights (Lawrie doors, Gregory reliefs, Putnam's Puck): until confirmed, stand-ins stay.

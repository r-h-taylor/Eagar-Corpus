# Case Index — Lecture 7KFTHxDcJwY (Codes and Standards, Summer 2012, session 5/7)

*Citation format: layer 3 paragraph anchor (e.g. `§1.p3`). Click-through reveals the corresponding layer 2 passage with timestamp range.*

This lecture is structured around inspection regimes (NDT vs. radiography, NDT vs. NDE, inspector levels) and how design specifications and codes evolve through failure. Center of gravity is the **60 Wall Street air conditioning riser pipe failure** (§3) and the **Boeing 747-400 catalytic converter titanium welding spec** (§4), used to teach the gap between what inspection contracts buy and what good engineering requires.

## Major cases

### 60 Wall Street (JP Morgan building) air conditioning riser pipe failure
- **Anchor:** `§3.p4`–`§3.p9`
- **canonical_cluster_id:** "60 Wall Street (JP Morgan building) air conditioning riser pipe failure"
- **Frame in this lecture:** Rush erection of a 40-story building with 16-inch air conditioning riser pipes welded in place by welders hanging off I-beams with no inspector access. Welds passed visual inspection from outside but had no penetration past about a quarter inch. Ten years later, JP Morgan spent $7M to relocate an air conditioning compressor to the 10th-floor ledge to protect the 7th-floor trading computers (which could lose ~$1B/minute), and $20M+ more to repair the riser pipe — a $100K inspection problem turned into a $60M+ lawsuit. Used to anchor the "you only get what you pay for" principle.
- **Materials/systems:** 16-inch carbon steel water pipe, vertical field welds, visual-only inspection contract
- **Era:** building erected ~1990s; failure discovered ~10 years later
- **Related clusters in canon:** Refinery A106 pipe failure and consultant study

### Boeing 747-400 catalytic converter titanium welding failure
- **Anchor:** `§4.p5`–`§4.p14`
- **canonical_cluster_id:** "Boeing 747-400 catalytic converter titanium welding failure"
- **Frame in this lecture:** Engelhard was building a titanium catalytic converter (for cabin-air ozone removal) for the 747-400 long-haul jet, replacing a stainless steel design to save weight. Boeing's spec disallowed any flaw larger than 10 thousandths of an inch — about four human hairs — which Tom shows was a CYA spec written by someone who set acceptance criteria at the limit of x-ray detectability rather than at any engineering-based size. With a 50% reject rate on four required welds and one repair allowed, statistics doomed throughput. Tom's diagnosis: 55-gallon-drum acetone left an oil film causing hydrogen porosity; switching to reagent-grade acetone dropped rejects from 50% to 10%. Engelhard reverted to old practice twice and had to be re-told three times.
- **Materials/systems:** 1/16" titanium sheet, GTAW welding, 360° x-ray inspection, acetone cleaning
- **Era:** ~early 1990s
- **Related clusters in canon:** Titanium welding porosity at aerospace contractor; General Electric titanium compressor case electron beam welding porosity

### Hyatt Regency walkway collapse
- **Anchor:** `§7.p1`–`§7.p10`
- **canonical_cluster_id:** "Hyatt Regency walkway collapse"
- **Frame in this lecture:** Suspended walkway in Kansas City Hyatt lobby. As-designed: single threaded rods through the C-channels of multiple walkway levels, requiring a nut threaded up many stories during erection. Erection changed it to extended/doubled rods, converting straight tension on the threaded rod into shear loading on the box-beam C-channel — a connection never sized for shear. Procedure existed for sign-off on changes; it was not followed. 114 dead, 200 injured; the building lobby was subsequently reduced to two stories.
- **Materials/systems:** Steel threaded rod, welded C-channel box beam, shear vs. tension loading
- **Era:** 1981 collapse
- **Related clusters in canon:** 1988 nor'easter structural collapses (New Jersey/Pennsylvania)

### Ford Taurus air conditioner compressor production failure
- **Anchor:** `§8.p4`–`§8.p9`
- **canonical_cluster_id:** "Ford Taurus air conditioner compressor"
- **Frame in this lecture:** Single-shuttle-piston compressor design — two cylinders, one piston, sub-thousandth clearance. Engineers specified prototype fixturing; the machinist silently used a different fixture because he knew the engineer's design wouldn't hold tolerance. Prototype worked; Ford built a $100M production line to the original (bad) fixture spec; production parts didn't fit. Tom personally affected — bought a Taurus in February, no working A/C until June, dealer had no compressors because all new ones went to assembly. Moral: communicate with hourly workers.
- **Materials/systems:** Aluminum compressor cylinders, precision machining/lapping/reaming
- **Era:** ~early 1990s
- **Related clusters in canon:** Ford air conditioner compressor production failure; Ford Taurus air conditioner compressor

## Cases referenced in passing

### 1988 nor'easter structural collapses (New Jersey/Pennsylvania)
- **Anchor:** `§7.p6`–`§7.p9`
- **canonical_cluster_id:** "1988 nor'easter structural collapses (New Jersey/Pennsylvania)"
- **Frame in this lecture:** "300-year storm" Pennsylvania snowstorm collapsed mall/shopping-center roofs supported by mini-mill bar joists. Mini-mills had competed by varying truss member thickness using mid-1980s PCs (128K RAM, 20MB disk) — but the computer models assumed symmetric concurrence at joints, while as-built joints had small offsets producing shear loading. Steel sheared just like Hyatt Regency. Tom got two years of forensic work from this storm.
- **Materials/systems:** Steel bar joist trusses, welded angle/rod members
- **Era:** 1980s; storm referenced as ~1985

### Salem Harbor steam generator explosion
- **Anchor:** `§5.p8`
- **canonical_cluster_id:** "Salem Harbor steam generator explosion"
- **Frame in this lecture:** Forty-year-old utility boiler. Massachusetts state inspector deferred the required corrosion-under-ash inspection of the manifold header for ~15 years because removing several feet of ash was too much trouble. The boiler eventually exploded, killing four. Used to illustrate that boiler/PV code inspection intervals exist for reason and that "money under the table" defeats them.
- **Materials/systems:** Carbon steel boiler tubes/header, corrosion-under-ash
- **Era:** ~2000s

### Manwich hot water tank stress corrosion cracking
- **Anchor:** `§5.p10`–`§5.p11`
- **canonical_cluster_id:** "Manwich hot water tank stress corrosion cracking"
- **Frame in this lecture:** Tennessee food plant making Manwich sauce. Stainless steel hot-water hold tank held below 210°F (so excluded from boiler & pressure vessel code scope). Bleach cleaning chemical migrated under insulation, producing chloride SCC that no inspector saw because no one removed insulation. Tank "looked like a dried riverbed" of cracks when it failed; people killed.
- **Materials/systems:** Austenitic stainless steel, chloride SCC under insulation
- **Era:** unspecified

### Liberty ships and SS Schenectady
- **Anchor:** `§9.p2`–`§9.p6`
- **canonical_cluster_id:** "Liberty ships and SS Schenectady"
- **Frame in this lecture:** Tom reads from the 1946 Maritime Commission report: 4,694 welded merchant vessels investigated, 970 with fracture casualties, 24 complete strength-deck fractures, 8 vessels lost (4 broke in two, 4 abandoned), 26 lives lost. Schenectady famous photo (split at dock); SS Manhattan more dramatic (mid–North Atlantic). Three postwar investigation centers: NRL (Pellini), British Welding Institute, MIT metallurgy (Cohen, Averbach). Outcome includes the Pellini explosion bulge test.
- **Materials/systems:** WWII welded ship steel, brittle fracture
- **Era:** 1941–1946 failures; 1946 report
- **Related clusters in canon:** 1940s welded ship cracking; T2 tanker fracture (1952); WWII Welded Merchant Vessel Structural Failures (Fleet-Wide); Explosion bulge test (Pellini underwater weld testing)

### USS Belknap collision and fire
- **Anchor:** `§9.p11`–`§9.p12`
- **canonical_cluster_id:** "USS Belknap collision and fire"
- **Frame in this lecture:** Destroyer Belknap collided with carrier JFK, hit below hangar deck; jet fuel landed on Belknap's aluminum superstructure and gutted the ship. Combined with HMS Sheffield (Exocet hit, Falklands) this drove ~$100M NAVSEA program at David Taylor Annapolis on waffle-steel superstructure to replace aluminum. Note in editorial register: Tom calls Sheffield "a cruiser"; it was a Type 42 destroyer — preserved as Tom said it.
- **Materials/systems:** 5xxx-series aluminum superstructure, jet fuel fire, high-strength waffle steel alternative
- **Era:** Belknap 1975; Sheffield 1982; remediation program mid-1980s
- **Related clusters in canon:** HMS Sheffield; LCS (Littoral Combat Ship) aluminum alloy redesign; Navy topside weight reduction composite structures study

### Tacoma Narrows Bridge
- **Anchor:** `§9.p1`
- **canonical_cluster_id:** "Tacoma Narrows Bridge"
- **Frame in this lecture:** Cited as exemplar within Petroski's *To Engineer is Human* thesis that engineering progresses through failure. "Galloping Gertie"; "only the dog died."
- **Materials/systems:** Suspension bridge aeroelastic flutter
- **Era:** 1940

### Refinery A106 pipe failure and consultant study
- **Anchor:** `§3.p9`, `§4.p1`
- **canonical_cluster_id:** "Refinery A106 pipe failure and consultant study"
- **Frame in this lecture:** Tom's backward reference to a case from prior session: refinery found one leaking pipe out of 600, manager ordered all 600 ripped out and sued contractor, turning a ~$100K inspection problem into a $60M lawsuit. Used in parallel with 60 Wall Street to illustrate "rip-it-all-out" manager pathology.
- **Materials/systems:** ASTM A106 carbon steel refinery piping, hydrostatic test
- **Era:** unspecified

### Massachusetts lemon-law case against General Motors
- **Anchor:** `§8.p7`
- **canonical_cluster_id:** "Massachusetts lemon-law case against General Motors"
- **Frame in this lecture:** Single-sentence parenthetical aside — Tom mentions he previously took a car to MA lemon-law arbitration and won against GM. Used as backdrop to threatening Ford with the same.
- **Materials/systems:** —
- **Era:** 1980s

## Figures referenced

- **1995 / ~mid-1990s:** approximate date NAVSEA permitted ultrasonics in lieu of radiography in shipyards (§1.p5–p8)
- **2011 NFPA lightning protection standard:** ~70 pages (§2.p1)
- **Boiler & pressure vessel code exclusion:** below 210°F operating temperature; 180°F bacterial threshold for Manwich hold tank (§5.p9–p11)
- **60 Wall Street:** 40 stories, ~400 ft, 0.44 psi/ft, several hundred psi at base; 16-inch riser pipe; 7 A/C compressors (designers said 2); $7M to relocate one compressor; $20M+ to repair riser; $60M lawsuit (§3.p4–p9)
- **Boeing 747-400 spec:** 10 thousandths of an inch maximum flaw size = ~4 human hairs; 50% reject rate on 4 welds with 1 repair allowed; aircraft cost ~$100M at the time, ~$250M today (§4.p7–p9)
- **Hyatt Regency:** 114 dead, ~200 injured (§7.p10)
- **Pennsylvania roof collapse era PCs:** 128K RAM, 20MB disk drives (§7.p7)
- **Floor load standards:** 100 psf human-occupancy typical; 150–200 psf manufacturing; ~300 psf MIT historical concrete buildings (§6.p16)
- **Building safety factor:** 1.67 (§7.p6)
- **Stata Center:** budget $150M, came in at $430M; pay freeze 2003–2004 (§6.p10)
- **Liberty ships:** 4,694 vessels, 970 fracture casualties (~20.7%), 24 complete strength-deck fractures, 1 complete bottom fracture, 8 vessels lost (4 broke in two, 4 abandoned), 26 lives lost (§9.p4)
- **Explosion bulge test:** dome formation at 160°F transition temperature (§9.p6); ~$100K per qualification today
- **NDT/NDE inspector levels:** Level I operator, Level II highest technical proficiency, Level III paperwork/management (§8.p1–p3)
- **Sheffield / Belknap remediation program:** ~$100M NAVSEA waffle-steel program (§9.p12)

## Open questions

- §6.p11–p12: A second student turn at the Stata Center discussion is unrecoverable from raw transcript; the case content is unaffected but no case attaches to this gap.
- §6.p23: The "seven inches longer" building-dimension anecdote is recoverable only from Tom's reply; insufficient detail to identify a canonical case. No cluster assignment made.
- §7.p2: The student description of the Hyatt Regency rod redesign is reconstructed from Tom's reply; case identification (Hyatt Regency walkway collapse) is unambiguous.
- §8.p7: Captioner garble ("aluminum") cut from "I did take a car in once"; the Massachusetts lemon-law case is attached but details (year, model, outcome) are sparse.
- §9.p11: Tom calls HMS Sheffield "a cruiser"; it was a Type 42 destroyer. Per constitution, Tom's misstatement is preserved on tape; the canonical cluster name "HMS Sheffield" is used unchanged.
# Case Index — Lecture 20

*Citation format: layer 3 paragraph anchor (e.g. `§5.p3`). Click-through in the static site reveals the corresponding layer 2 passage with timestamp range.*

This is a procedurally-oriented lecture on welding codes, with the metallurgical content concentrated in §6–§8. Most "cases" here are illustrative anecdotes rather than developed forensic studies; the principal forensic case is the Seawolf hydrogen-cracking failure in §8.

## Cases referenced

### Pentium 2 two-chip package (residual stress limit on chip size)
- **Anchor:** `§1.p4`
- **canonical_cluster_id:** PROPOSED: Pentium 2 two-chip package and one-centimeter joining limit
- **Frame in this lecture:** Tom's tour of an Intel plant in the late 1990s revealed that the Pentium 2, unlike the original Pentium, was actually two chips in one package — because you couldn't join something more than about one centimeter on a side without cracking from residual soldering/brazing stresses. Used to undermine the redefinition of Moore's Law.
- **Era:** late 1990s
- **Materials/systems:** silicon chip joining, residual stress, solder/braze

### Bell Helicopter mast electroplating and hydrogen bakeout
- **Anchor:** `§5.p3`
- **canonical_cluster_id:** Bell Helicopter mast hydrogen cracking prevention
- **Frame in this lecture:** Critical non-welded high-strength steel part. Electroplated for corrosion resistance; within five minutes of leaving the plating bath it goes into the hydrogen bakeout oven, because the steel is high-strength and there's no redundancy — mast failure means loss of blades and no possibility of auto-rotation.
- **Materials/systems:** high-strength steel mast, electroplating, hydrogen embrittlement, bakeout
- **Era:** unspecified (Tom has flown the Bell 407, so contemporary)

### Auto-rotation training on the Bell 407
- **Anchor:** `§5.p5`
- **canonical_cluster_id:** PROPOSED: Bell 407 ground school auto-rotation training
- **Frame in this lecture:** Tom's personal recollection of doing an auto-rotation under a test pilot's supervision during ground school for the Bell 407. Used to ground the auto-rotation explanation in concrete experience. Harrison Ford is mentioned as having gone through the same training the week before.
- **Era:** unspecified
- **Note:** This is a Tom-the-pilot anecdote, not a forensic case. May not warrant promotion to canonical case status — flag for editor.

### Hovering helicopter engine-loss fatalities
- **Anchor:** `§5.p6`
- **canonical_cluster_id:** PROPOSED: hovering helicopter engine-loss fatalities and operating-envelope litigation
- **Frame in this lecture:** Tom references "a couple of situations" where pilots lost engines while hovering with no forward momentum, dropped, and died, leading to lawsuits over whether they should have been in the dead-zone of the operating envelope. Used to make the point that hovering is more dangerous than flying.
- **Era:** unspecified
- **Note:** Tom is plural ("a couple of situations") — this may aggregate multiple individual consulting cases. Flag for editor.

### Seawolf submarine hydrogen cracking
- **Anchor:** `§8.p2`
- **canonical_cluster_id:** Seawolf submarine hydrogen cracking
- **Frame in this lecture:** The principal forensic case of the lecture. The Seawolf was supposed to be welded with HY-100 (100 ksi) steel, but high-side chemistry on every alloying element (carbon, manganese, chromium) drove the weld metal strength to 130 ksi with martensitic rather than acicular-ferrite structure. Hydrogen cracking ensued. Repair cost an additional $2 billion, doubling the submarine's price; Congress was unhappy. Only one Seawolf-class was built, partly for this reason and partly because the Cold War ended.
- **Materials/systems:** HY-100 steel, martensite, acicular ferrite, hydrogen embrittlement
- **Era:** late 1980s / early 1990s
- **Related canonical clusters:** Seawolf-class submarine keel beam bending; SSN-21 Sea Wolf hull cracking problem; USS Seawolf HY-100 hydrogen cracking; HY-130 Seawolf submarine welds — these are likely all the same case under different framings; reconciliation needed.

### America's Cup 4340 yacht welding (foreshadowed)
- **Anchor:** `§8.p3`
- **canonical_cluster_id:** America's Cup 4340 welding procedure development
- **Frame in this lecture:** Foreshadowed at the end of the layer 2 cut — Tom is about to launch into the case where a client wanted to use 4340 (a high-hardenability, >180 ksi steel requiring 600°F preheat and post-weld heat treatment) for racing yacht components. Will be developed in the next portion of the lecture.

## Figures referenced

- **Person-hours / industrial productivity:** not invoked in this lecture.
- **Safety factors:** 1.67 (five-thirds) for building base material; 3.3 for building welds; 2 for fatigue-loaded structures like bridges. (`§4.p5`)
- **Allowable defect sizes:** 1/8 inch routine; up to 1 inch in 12 inch for undercut depending on code. (`§4.p7`)
- **Strength regimes:**
  - Acicular ferrite ceiling: ~120 ksi (`§7.p5`)
  - Martensite range with post-weld heat treatment: 120–180 ksi (`§8.p1`)
  - Hard martensite, requires 600°F preheat: >180 ksi (`§8.p3`)
- **Hardness ceilings:** Rockwell C 30 (welding general); Rockwell C 22 (petroleum industry preference). (`§8.p3`)
- **Oxygen content:** base metal 20–30 ppm O; weld metal 300–2,000 ppm O — the source of acicular ferrite nucleation sites. (`§6.p3`)
- **Moore's Law inflection:** "pooped out around 2002 or 2005"; feature sizes ~0.12 nm (Tom's figure; actual is ~14 nm at the time of recording — flag as Tom's misstatement, but preserve). (`§1.p2`)

## Open questions for the case index methodology

- The Seawolf hydrogen cracking case appears in the canonical cluster list under at least four different names. Recommend collapsing to a single canonical name during reconciliation.
- Tom's claim of "0.12 nanometers" for chip feature sizes (`§1.p2`) is a misstatement (he likely means 14 nm or 22 nm process node). Per the constitutional constraint, this is preserved on tape and not corrected in layer 3, but flagged here for the editor.
- The Pentium 2 one-centimeter joining limit (`§1.p4`) is a specific technical claim about silicon die size and bonding stress that would benefit from independent verification before being cited downstream.
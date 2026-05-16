# Case Index — Lecture 14 (PM6Qc720MgA)

*Citation format: layer 3 paragraph anchor (e.g. `§3.p5`). Note: this lecture is delivered by a guest lecturer (Belmar), not by Tom Eagar. Case framings reflect the guest's perspective, not Tom's.*

The lecture is structured around two extended teaching cases (aircraft wing rib casting; roof joist weld failures), with several secondary cases referenced in passing.

## Primary teaching cases

### Aircraft wing rib — titanium casting substitution
- **Anchor:** `§2.p1` through `§3.p10` (extended treatment)
- **canonical_cluster_id:** `Aircraft wing casting substitution project`
- **Frame in this lecture:** The guest lecturer's own work at a Canadian regional-jet manufacturer (Bombardier, by inference from "Canadian company competing with the Brazilians"). The wing's heated leading-edge rib was originally machined from a 3.5-inch wrought titanium plate down to ⅛-inch web thickness — extremely wasteful. The cost-reduction question was whether the rib could be cast instead. The teaching point: castings introduce a "casting factor of safety" penalty (Boeing's value cited as 1.25) that can be eliminated only by 100% NDT inspection of the casting. The argument unfolds into which surfaces (tension vs. compression) need full inspection.
- **Materials/systems:** Ti-alloy plate, Ti-alloy casting, aluminum skin (riveted), liquid penetrant testing, fracture toughness testing
- **Era:** roughly mid-1990s to early 2000s (10-year-old design at time of speaker's involvement; lecture given Fall 2012)

### Regional jet landing gear torsion crack
- **Anchor:** `§4.p3` through `§4.p4`
- **canonical_cluster_id:** `Landing gear torsional cracking failure`
- **Frame in this lecture:** A parallel project at the same Canadian aircraft company. During qualification testing at twice service load, a heavy steel landing-gear structural component cracked rapidly because of a torsional loading mode that had not been analyzed (tension and bending had been; torsion had not). The teaching point: even with thorough stress analysis, full-assembly testing reveals loading modes the analysis missed, and a redesign late in the program is enormously expensive because weight is already accounted for elsewhere.
- **Materials/systems:** heavy-section steel landing gear, possible titanium substitution
- **Era:** roughly mid-1990s to early 2000s

### Roof joist weld failure collapses
- **Anchor:** `§7.p5` through `§8.p7` (extended treatment)
- **canonical_cluster_id:** `Roof joist collapse from poor welding during snow storms`
- **Frame in this lecture:** The guest's forensic experience: of nine roof-joist collapses he investigated over about a year, eight involved welding defects at the diagonal-to-chord connections. The teaching points are (1) the demand side of the design is well-specified by code (snow loads, drift loads, etc.), but (2) the capacity side depends on weld quality, which is variable in practice, and (3) the design choice of single-sided vs. two-sided welds, and of fillet welds vs. round-tube-to-flat-bar welds, materially affects both inspectability and redundancy.
- **Materials/systems:** structural steel joists, fillet welds, round-tube-to-flat-bar joints, rectangular tube chords
- **Era:** speaker's own forensic practice, ~late 2000s through 2012

### Greenhouse / tomato warehouse weld failure
- **Anchor:** `§8.p2`
- **canonical_cluster_id:** `Tomato greenhouse/warehouse weld failure`
- **Frame in this lecture:** A specific instance from the guest's forensic work, illustrating low-convexity fillet welds that pulled off the chord surface rather than ripping the parent metal. Used as a concrete example of the convexity / contact-angle teaching point.
- **Materials/systems:** structural steel joist fillet welds

## Secondary references

### Boston molasses flood
- **Anchor:** `§1.p3`
- **canonical_cluster_id:** `Boston Molasses Flood`
- **Frame in this lecture:** Cited briefly as a historical example of why large stored-liquid structures in populated areas need code-governed design. The speaker explicitly distinguishes this from the Boiler and Pressure Vessel Code lineage but uses it for the same "structures near populations need oversight" argument.

### Propeller shaft designed to fail at 400 hours
- **Anchor:** `§9.p3` (with brief recall at `§9.p4`)
- **canonical_cluster_id:** `Shaft designed to fail within 400 hours`
- **Frame in this lecture:** Cited from an earlier session in the same course (the speaker says "we had that propeller shaft example") as the canonical illustration that the acceptable safety factor depends on intended service life — a shaft designed for 400 hours has a safety factor less than one against a 10-year life, and that's intentional.

### Speaker's trailer design
- **Anchor:** `§1.p4`
- **canonical_cluster_id:** PROPOSED: `Belmar custom trailer design (3.371 teaching example)`
- **Frame in this lecture:** Backward-reference only — "when I talked about my trailer." The speaker is recalling an earlier session in this same course. Not developed in §14. Likely overlaps with one of the existing trailer-design cases in the canon (`Custom firewood trailer design and overload incident`, `Custom race car trailer design`, `Custom-built trailer design and field testing`, etc.) but cannot be assigned without listening to the earlier session.

### ATV design
- **Anchor:** `§1.p4`
- **canonical_cluster_id:** `Honda ATV design optimization history` (provisional — may also map to `ATV exhaust and water ingress assembly failures`)
- **Frame in this lecture:** Backward-reference only. Not developed in §14.

### Helicopter blade (torsion)
- **Anchor:** `§4.p6`
- **canonical_cluster_id:** *unclear* — possibly `Helicopter blade spar stress evaluation case` or one of several other helicopter-blade cases
- **Frame in this lecture:** Backward-reference to "last week's" lecture on helicopter blade design, used to extend the torsion-loading argument from fixed-wing aircraft to rotorcraft. The teaching point: helicopter blades carry torsion loads that must be carried in shear by the skin-to-honeycomb interface, and excess torsional rotation changes the attack angle.

### Pressure vessel factor of safety = 4
- **Anchor:** `§9.p1`
- **canonical_cluster_id:** *framing figure, not a case*
- **Frame in this lecture:** The speaker's recurring example from earlier sessions: the BPVC safety factor of four absorbs water hammer and other unaccounted loads. Cited as the cleanest example of how a single nominal safety factor encodes multiple unmodeled load cases.

## Figures referenced

- "Aerospace is about 1000× more willing to accept a failure than dam-scale structures" (`§1.p2`) — framing statistic for industry-specific safety-factor variation
- Boeing casting factor of safety = 1.25 (`§3.p8`) — specific number, may recur in other lectures
- ⅛ inch web thickness machined from 3.5-inch plate (`§3.p3`) — buy-to-fly ratio anchor; may align with `Air Force Buy-to-Fly Ratio in Aircraft Manufacturing`
- Aluminum softening above 200 °C (`§2.p4`) — material-property anchor
- 9 collapses / 8 with welding defects (`§7.p5`) — the guest's forensic frequency statistic for roof joist failures
- Wing bend test ≈ 3 feet of tip deflection (`§4.p1`) — testing-protocol anchor
- Propeller shaft 400-hour design life (`§9.p3`) — recurring figure from earlier in the course

## Notes on case-index methodology for this lecture

Because this lecture is delivered by a guest, several backward-references point to material in earlier sessions of 3.371 (Fall 2012) that may or may not have been Tom-delivered. The case index treats these as the speaker's references — i.e., as evidence that the case was treated somewhere in the course — without assigning them to a specific lecture. Cross-referencing against the rest of the Fall 2012 sequence will be needed to resolve the trailer and ATV references.
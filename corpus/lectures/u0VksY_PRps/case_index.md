# Case Index — Lecture 7 (u0VksY_PRps)

*Guest lecture by Simone Belmar on safety factor definitions and practice. The lecture's teaching is built around three physical-object demonstrations Belmar brings to class — the burst copper pipe, the speedboat propeller shaft, and the jet ski fuel-tank fitting — plus a tour of industry-by-industry safety factor norms.*

## Cases referenced in this lecture

### Frozen copper pipe (residential)
- **Anchor:** `§1.p2`, `§3.p2`
- **canonical_cluster_id:** "Frozen copper water pipe failure"
- **Frame in this lecture:** Belmar's opening prop. A burst copper pipe shown to motivate the discussion of why even a safety factor of six to ten isn't enough when the failure mode (4% volume expansion on freezing) is outside the design envelope.
- **Materials/systems:** Copper plumbing pipe; water; freezing cycles.

### Large condominium riser pipe failure
- **Anchor:** `§3.p4`, `§3.p5`, `§3.p6`
- **canonical_cluster_id:** "Tall condominium riser pipe failure"
- **Frame in this lecture:** Used to illustrate that allowable load calculations don't include thermal expansion of vertical risers in 10-story buildings, even though the code requires it.
- **Materials/systems:** Copper or steel piping in tall residential buildings.

### New Orleans levee failure (Katrina)
- **Anchor:** `§5.p1`, `§5.p2`
- **canonical_cluster_id:** "New Orleans Canal Levee Failure"
- **Frame in this lecture:** A 1.3 safety factor design where the actual shear strength of saturated soil was the unknown — the failure was a material-property estimation error, not a safety-factor-too-low error.
- **Materials/systems:** Soil shear strength under saturation.

### Speedboat propeller shaft fatigue failure
- **Anchor:** `§6` (entire section)
- **canonical_cluster_id:** "Speedboat propeller shaft fatigue failure"
- **Frame in this lecture:** Belmar's consulting case, circa 2007. A nickel-based (Inconel) shaft, half-submerged in operation, designed for 400 hours of service. Failed by bending fatigue with beach marks from a corner-initiated crack growing to the centerline. Used to show that "safety factor of three on yield" collapses to "1.5 on fatigue strength," and that acceptance criteria (400-hour service life) drive the safety factor calculation.
- **Materials/systems:** Inconel shaft; marine environment; bending fatigue under half-submerged rotation.
- **Era:** ~2007 (consulting engagement).
- **Note:** This may map to "High-speed boat propeller shaft failure" or "Propeller shaft fatigue failure (boat/sport unit)" in the canonical list — both candidates appear plausible. Suggest reconciliation against aggregate v2.

### Jet ski fuel hose fitting
- **Anchor:** `§7` (entire section)
- **canonical_cluster_id:** "Jet ski fuel cap hose adapter failure"
- **Frame in this lecture:** Molded nylon fuel-tank fitting connected by hose to the engine. The load is not internal pressure but the mismatch displacement between hull and engine platform. Used to illustrate that safety factor analysis breaks down for assembly-driven loads — the design comes from prototype experience, not from finite element analysis.
- **Materials/systems:** Molded nylon fitting; hose clamp connection; jet ski hull/engine platform.

### Aircraft landing gear design
- **Anchor:** `§5.p4`, `§5.p5`
- **canonical_cluster_id:** PROPOSED: Aircraft landing gear safety factor design
- **Frame in this lecture:** Used as a counter-intuitive example — landing gear has a 1.2 safety factor (lower than building piping at 1.5–2), but is more reliable, because the load is well-determined, the material is forged and weld-free, and quality control is high.
- **Materials/systems:** Aircraft landing gear (high-strength steel forgings).
- **Note:** Not clearly mapped to an existing cluster; recurring landing-gear material discussion across the corpus may warrant a dedicated cluster.

### ATV / four-wheeler design philosophy
- **Anchor:** `§5.p11`
- **canonical_cluster_id:** PROPOSED: ATV design philosophy and deformability tradeoff
- **Frame in this lecture:** Belmar mentions having worked "quite a bit with ATVs, the four-wheelers" and uses them to make the design-for-deformation point. Brief reference, not developed.
- **Note:** Possibly related to "Honda ATV design optimization history" or "ATV exhaust and water ingress assembly failures" but the framing here is distinct (crashworthiness rather than assembly defects). Proposed as new.

## Figures referenced

### Automotive weight cost ratio
- **Anchor:** `§5.p8`
- **Figure:** "The cost of adding a pound of weight to an automotive is about two dollars for the life cycle."
- **Attribution in this lecture:** Belmar attributes the figure to Professor Eagar's material selection module.
- **Note:** This is a recurring corpus figure, not a case. Likely appears in Eagar's own material selection lectures.

### Boiler and pressure vessel code safety factor
- **Anchor:** `§1.p3`, `§4.p1`, `§5.p7`
- **Figure:** Safety factor of four for the boiler and pressure vessel code, of which a substantial portion accounts for water hammer (pressure multiplication of 2–3×).
- **Note:** Recurring corpus figure. Belmar attributes the underlying explanation to Eagar's prior lecture.

## Open questions
- The speedboat shaft case — is this Belmar's case alone, or does Eagar also reference it elsewhere? If Belmar-specific, the cluster_id should probably note the source.
- Belmar's "ATV" mention is so brief it may not warrant a cluster entry; flagged for editor judgment.
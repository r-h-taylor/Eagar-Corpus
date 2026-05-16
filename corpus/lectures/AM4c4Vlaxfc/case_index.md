# Case Index — Lecture AM4c4Vlaxfc

*Citation format: layer 3 paragraph anchor (e.g. `§1.p2`). Click-through in the static site reveals the corresponding layer 2 passage with timestamp range.*

This lecture is the fourth session of 3.371 Codes and Standards, transitioning from measurement science into codes and standards proper. The teaching architecture is: two opening case stories about stainless steel grade mix-ups → bonding/properties theory → Ashby plots → Concorde as a limits case → introduction to ASTM standards via the Alberta refinery dispute.

## Cases referenced

### Ballpark Franks hot dog cooker stainless steel failure
- **Anchor:** `§1.p1`–`§1.p9`
- **canonical_cluster_id:** Hot dog cooker corrosion failure
- **Related cluster:** 316 stainless steel heat exchanger tube pitting failure (parallel mechanism)
- **Frame in this lecture:** Opening story. 304 stainless steel replacement parts substituted in a 316 cooker; chloride attack from hot dog salt content caused rapid crumbling failure. Shows how 2% molybdenum doubles cost but is essential for chloride service.
- **Materials/systems:** 304 vs. 316 stainless steel; chloride corrosion.

### Desalination pump bearing 302/304 substitution
- **Anchor:** `§2.p1`–`§2.p3`
- **canonical_cluster_id:** Desalination pump bearing failure
- **Frame in this lecture:** Parallel current case to the hot dog cooker. 302 stainless steel inserts substituted in a 316 pump bearing destined for Middle East desalination service. Failed within a year; destroyed company reputation.
- **Materials/systems:** 302/304/316 stainless steel; chloride attack on bearings.

### Woods Hole house spray foam fire
- **Anchor:** `§6.p4`
- **canonical_cluster_id:** Woods Hole house spray foam fire
- **Frame in this lecture:** Polyurethane spray foam insulation installed incorrectly along eaves caused a house fire. Used to illustrate that polymer foams are the lowest-thermal-conductivity material in the world — but the same property makes them dangerous if installed where heat can build up internally. Tom shows a charred sample.
- **Materials/systems:** Polyurethane foam insulation; thermal conductivity.

### Concorde supersonic transport operations and economics
- **Anchor:** `§7.p1`–`§7.p3`
- **canonical_cluster_id:** Concorde supersonic transport operations and economics
- **Frame in this lecture:** Personal anecdote of flying Concorde in the early 1990s ($2500 fare upgrade). Used to illustrate the practical limits of engineering — Concorde retired after a tarmac-debris crash, restricted routes due to sonic boom regulations, expensive maintenance with no slack time. Includes a side note on a king/tycoon who chartered British Airways for round-the-world weekend trips.
- **Materials/systems:** N/A — operations and economics case.
- **Era:** Early 1990s personal flight; 1980s-2003 Concorde service.

### Alberta refinery hydrostatic test pipe failure
- **Anchor:** `§8.p5`
- **canonical_cluster_id:** Alberta refinery pipe hydrostatic test failure
- **Frame in this lecture:** Foreshadowed for tomorrow's lecture. $500M Alberta refinery construction project; during recession, pipe sourced from non-standard supplier; hydrostatic test produced a crack; client demanded $2M-$6M back. Tom's framing: "the fight arose because people don't know how to read a standard in plain English." Used to motivate the codes-and-standards material to follow.
- **Materials/systems:** Carbon steel pipe (ASTM A106 seamless context); hydrostatic test; ASTM standard interpretation.
- **Era:** Tom doesn't specify the year but references a recession; likely early 1980s or early 1990s.

## Figures and concepts referenced (not cases)

### Stainless steel grade pricing
- **Anchor:** `§1.p7`–`§1.p8`
- 316 has 2% molybdenum, adds ~$4,000/ton at $50-100/lb Mo
- 317 has 4% Mo (medical implants — body salinity ≈ seawater)
- 6% Mo Navy submarine grade — ~$12,000/ton premium

### Steel productivity / pricing framework
- N/A in this lecture — not invoked.

### Ashby plots
- **Anchor:** `§6.p1`–`§6.p5`
- Mike Ashby (Cambridge, Lorna Gibson's professor); founded Granta; Acta Materialia gold medal.
- Strength-vs-modulus plot; thermal conductivity on 45° line; polymer foams as lowest-thermal-conductivity material in the world.

### Diamond-graphite bonding contrast
- **Anchor:** `§3.p2`–`§3.p10`
- Same composition, different bonding (sp3 vs sp2) produces opposite properties on every measurable axis: density, transparency, conductivity, thermal conductivity, hardness, abundance, machinability.

### Lennard-Jones potential
- **Anchor:** `§4.p1`–`§4.p3`
- Equilibrium bond distance; ~3-4 atomic distances of attractive range; cube-root-of-1000 ≈ 10 atomic spacings between molecules in room-temperature air.

### Heisenberg uncertainty in measurement
- **Anchor:** `§5.p2`–`§5.p4`
- UV breaks primary bonds (suntan); 5 MeV electron beams transmute elements.

## Open questions for the case index methodology

- The Ballpark Franks case and the desalination pump case share a mechanism (304/302 substituted for 316 in chloride service). They appear to be canonical clusters in the aggregate. Verify both cluster_ids resolve cleanly.
- "Alberta refinery pipe hydrostatic test failure" is in the aggregate; this lecture is Tom's setup, with the full case scheduled for the next session (lecture 5/14). The cluster may need to merge across both lectures' instances.
- The king/tycoon British Airways anecdote within §7.p3 is a sub-case of Concorde operations; not separately clustered.
# Lecture 21 — High-Strength Steel Welds and Fatigue Design

*3.371 Welding Metallurgy, Spring 2014, session 21 of 29.*
*Source video: `Jh5DokU5lSU`.*

---

## §1. Welding ultra-high-strength steel [00:04]

`§1.p1` More than 180 ksi, four-inch-thick or eight-inch-thick material — I think it's like eight-inch-thick material — yeah, you can buy the steel and you can weld it, but you've got to really know what you're doing. You're going to have to put the whole thing in an oven, preheat it to 600 degrees, and pull it out. The welders are going to be welding next to a huge massive tons of steel at 600 degrees Fahrenheit. It's like welding on an oven.

`§1.p2` They use it in the keel of the America's Cup yacht. This was about ten or fifteen years ago. In the America's Cup yacht keel beam, they'd used HY130, which was what the Navy wanted to use for submarines. But they built one and they went out and tested it and it bent. 130 ksi, like four feet wide, eight inches thick — a lot of force on those things, a lot of sail area, and you concentrate it all in a bending moment with a big knot. And I say keel — it's actually the piece that sticks down. It's not the rudder, but it's the centerpiece, and you want a bunch of weight in the bottom, down low.

`§1.p3` In fact they used to put lead in the bottoms of the ships, even though you're trying to make them lightweight. They put lead in so the thing wouldn't tip over. But you only put it in the bottom. You'd like to have a gradient of density — high density in the bottom and low density at the top.

`§1.p4` Anyway, so we do know how to weld these steels. We can do it if you're willing to pay the price. I often say we can weld almost anything if you're willing to pay the price. But the price for these really high-strength steels gets prohibitive very quickly, okay.

## §2. Fatigue of welded steel: the stress-concentration trap [01:56]

`§2.p1` I think we've got a little bit of time to talk about fatigue design. In fatigue design of weldments, the problem has burned people many times — Santayana, anybody know who George Santayana was? He was a philosopher at Harvard. Santayana said, those who cannot remember the past are condemned to repeat it.

`§2.p2` In the design of fatigue of steel structures, the stress for a million-cycle life in the base material — or the base material with a hole — increases as the ultimate strength of the steel. If you put a weld in there, you get no advantage for high-strength steel in fatigue if it's welded. The reason is the weld produces a notch. It's a stress concentration. And it turns out, in terms of fatigue, that notch is going to give you the same fatigue strength whether you're a low-strength steel or whether you're a high-strength steel.

`§2.p3` Now General Motors and Ford sort of ran into this in the mid-80s when they were trying to lightweight automobiles. They said, oh, we'll save weight on the cars, we'll use high-strength steel. And they did, and they spot-welded the high-strength steel, and they assumed that they would get the same proportional strength increase in the weld as they got in the base metal strength. But you don't. You get the same proportional strength in the solid piece of base metal, but if you have a stress concentration like just a simple hole, you don't get a 45 degree slope — you get something less. That's just the base metal, just the stress concentration. You put in a weld, you have an even sharper stress concentration. It turns out there's no advantage.

`§2.p4` So they designed these things with the same fatigue criteria but thinner, as they'd always used, assuming that the weld strength would increase proportional to the ultimate strength of the steel. They just assumed they would get higher fatigue strength out of the welds. Well, they didn't. And people buying minivans in the mid-80s were unhappy when, after a couple years, they started hearing extra rattles, because the spot welds were fading, okay.

`§2.p5` Well, it happens in bridges, it happens in buildings. So you have to be careful using high-strength steels in a fatigue-loaded situation. You pay extra attention to the stress concentrations, or you put the welds in locations where the stress is low. Because in general we just willy-nilly put the welds in the highest stress locations, because we expect the welds to be wonderful. And they are wonderful — I've made a whole career out of it, okay.

`§2.p6` **Student:** [question about weld placement at corners]

`§2.p7` Right. And when I get to aluminum welds I'm going to show you how to avoid putting the welds at the corners. There's lots of ways to do it, and we know how to do it. It's a design detail, it's not a metallurgical thing. The metallurgy kills you, and you have to solve it with design. So there are solutions. It's just that those solutions add weight, unfortunately. The best weld is one where you just make a simple butt weld and it's like continuous base material. Doesn't work in fatigue situations.

## §3. The AISC fatigue tables [06:02]

`§3.p1` And this applies to aluminum too — you actually have some of these things. This is a much busier thing than you really want to worry about right now. But if you go to the AISC manual — the American Institute of Steel Construction, the civil engineers — they have a section on fatigue design, a whole chapter in the book on design for fatigue structures. They have allowable stresses, and you can go to table B3 which is probably on the next page, and it will tell you what stresses you're allowed as a percentage of the base metal strength. And then the weld safety factors — they have loading conditions depending on the number of cycles, because the fatigue curve goes down with the number of cycles, so basically loading condition is where you are on the fatigue curve. That's the way the civil engineers do it.

`§3.p2` Then they say: if I've got base material, plain material rolled and cleaned, it's a stress category A. If I have built-up members that are made with some welds, it could be a B, C, or an E. And there are all kinds of fillet welds, mechanically fastened — that's like rivets and bolts and things like that — with different stress conditions. The illustration of those stress conditions is a series of pages. This is condition one, just straight base material. Here's an I-beam. Here's a welded built-up member, here's another built-up member. These one, two, three and four are things that if you look back on the other table it will tell you, but you get more and more complex structures, where the welds are, or worse, where the plug welds or slot welds are. And these will have different fatigue criteria.

`§3.p3` People have gone out and made these things and broken them. They were doing this all the time back in the 1930s through the 1960s. Today you go and simulate it in a computer if you want. In the old days they'd just go out and make the whole thing, get a great big machine, vibrate them, and see when they broke. That's not the way we study fatigue today, okay. But that's the way they did it. That's how these charts came about, and we have similar charts whether it's aluminum or steel.

`§3.p4` Now this may be useful. This is the allowable stress from the category A, B, C, D, E, F loading conditions. The allowable stress could be 60 ksi for the base material. But in fact you may only be allowed for base material category A, 36 ksi. So loading condition one may be the maximum capability of the material, and 36 — maybe 24 is really the design stress for most base metal in the structural welding code. But in these other conditions the maximum allowable stress in your design drops depending on the category of the joint and other things.

`§3.p5` It's a whole chapter, it gets very messy. But essentially we reduce — or, if you want to say, we increase the safety factor on these more complex joints by requiring a lower permissible stress level. That's how we handle fatigue, okay.

## §4. LRFD and the Northridge earthquake [10:00]

`§4.p1` There actually is a new thing in the last ten years called load — what is it, Small, do you remember? Load-based moment design or something. It kind of came out of the Northridge earthquake in southern California in the early 90s, and it's so complex I've tried to look at it a few times. I need to take a course in it, okay.

`§4.p2` **Student:** [explains LRFD — safety factor on the material side, separate safety factor on the load side, then you compare them without additional factors]

`§4.p3` Right. Well, the American Institute of Steel Construction for the last ten years has preferred this load moment resistant approach. It's four initials, LMRD [LRFD] or something like that. Like I said, I'm too old, I never learned it as a student. You helped me understand that they're actually bringing a safety factor from a design side and from a material side, and you see if they match. They learned a lot of this by looking at the failures of buildings in the Northridge earthquake. A lot of this came out of Northridge, but it was coming out of other research and other things too.

## §5. Mouse holes, hard spots, and the King Street Bridge [11:29]

`§5.p1` The codes don't generally get smaller. When we get to aluminum, I will show you an example perhaps tomorrow of how the welds — the American Welding Society code got simpler in aluminum. You worry about joint design details, like the stress concentrations — they call them hard spots in tanks. If you're talking about ship construction where you have beams going different ways, you may have little — they call them mouse holes, you can see why they call them a mouse hole — you cut out so you don't have three welds coming together giving you a lot of triaxial constraint at an intersection of three welds, okay.

`§5.p2` So there's lots of little details and games that we have learned to do, because we have learned that some little details are terrible. There is a story of the King Street Bridge in Melbourne, Australia back in the 60s. They had a plate on top of another plate. So this plate was on another plate, and they made the weld all the way around. This might be four inches, this might be twelve inches over here. They just made a fillet weld all the way around. Fatigue crack came along, the bridge fell down, a bunch of cars went in the river. I don't think anybody got killed, I don't remember, but in any case it's a fairly famous failure.

`§5.p3` Now you're not allowed to put the closure weld on there. You have to leave it open. It doesn't really add any strength. In fact, it tremendously reduces the fatigue strength. And if you look at all those geometries I showed you, you'll find that one's not allowed, or it's category F, or whatever the stress you can put on that weld is the nearest zip. So we learn — one of the things in codes is we learn from our failures. So, see you tomorrow.

`§5.p4` **Student:** Load factor resistance design.

`§5.p5` Yep, okay. Load factor resistance design. The title didn't even make sense anyway. Sorry, okay, thanks.
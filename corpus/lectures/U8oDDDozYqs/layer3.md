# Lecture 2 — Measurement: From the Sublime to the Ridiculous

*3.371 Codes and Standards, Fall 2012, session 2 of 14.*
*Source video: `U8oDDDozYqs`.*

---

## §1. LIGO: the most precise measurement ever attempted [00:01]

`§1.p1` I have a short article on the history of codes and standards — lightning codes and standards. I'll hand it out because we talked about CSST and how lightning can perforate it.

`§1.p2` Any questions? If not, I'll go back to what we were talking about, which was observables. We were going from the sublime to what I call the ridiculous. The sublime is the NIST F1 atomic clock — one part in 10 to the 15th accuracy, which is one second in 30 million years. So we have a pretty good handle on time today.

`§1.p3` But I want to give you a case study on the most accurate measurement ever attempted: the laser interferometric gravitational observatory. LIGO. It's a joint MIT-Caltech project. Back in 1992, Ray Weiss, a scientist in the MIT physics department who had started as a technician and then got his PhD in physics, proposed to the National Science Foundation, together with two people from Caltech, what has become the largest NSF project in terms of cost ever attempted. They built two interferometers.

`§1.p4` If you remember the Michelson-Morley experiment from freshman physics, they had a little interferometer where you split light on two perpendicular axes, send part of the light down one way and part the other, with mirrors at each end. The beams come back and you see the beating frequency, and you can measure the length very precisely along the interferometer arms.

`§1.p5` These interferometers are 4 km long. One is in Hanford, Washington — which is a desert — and the other is in Lafayette, Louisiana, surrounded by a swamp. It's about a half-billion-dollar project. You can't take a picture of the whole thing except from space.

`§1.p6` I read an article in *Science* saying this was supposed to measure one part in 10 to the 23rd. I'd worked with Ray on the welding of the beam tubes — about a 4-foot diameter tube, 4 km long. He came down to my office to explain this, and in his own handwriting wrote down what they were trying to measure: 10 to the minus 23rd per square root of hertz.

`§1.p7` Anybody have an idea why square root of hertz? It's how frequently you sample the measurement. You could call it Nyquist frequency, but whenever you're dealing with a Gaussian distribution — remember the precision plot, the bell curve — you're trying to make a measurement. Here they're trying to measure gravity waves from space to confirm Einstein's general theory of relativity.

`§1.p8` Gravity waves are created when a supernova occurs, sending waves out through space that change the weight of everything. So you're gaining and losing weight twenty times a second. If you could just combine all the weight loss and not the weight gain — anyway. What they do is square root of hertz because if you sample for a longer period, you get better accuracy; if you sample for a shorter period, you get more measurements. There's a trade-off. If you sample over too long a period, the waves average out.

`§1.p9` So Ray said the length is 4 km — he wrote it as meters, he's a physicist, he doesn't put units down. The change in length you're trying to measure, if it's 10 to the minus 23rd over 4 km, is 4 times 10 to the minus 20 meters per square root of hertz. If you sample ten times a second, you lose threefold in accuracy because you're sampling faster than a second. So it's 1 times 10 to the minus 19 meters that you're trying to measure.

`§1.p10` They have 12-inch diameter tungsten spheres with mirrors on them in the building where the two lines come together, and a mirror at the other end. They had to align these tubes within about 3/16 of an inch over 4 km. No one had ever surveyed anything that accurately. Civil engineers didn't know how to do it — at 4 km, you actually have to start accounting for the curvature of the earth.

`§1.p11` They ended up using the GPS system with their own base stations to increase the accuracy. Civil engineers use GPS for surveying all the time now, but they had to develop the technique to even align these things on their foundations.

`§1.p12` They had to do it in vacuum, because light changes speed in a vacuum. They're down at about 10 to the minus 12 atmospheres. The primary impurity is hydrogen, and one of the things they worked on — they had undergraduates working on this — was developing the right way to oxidize the surface of the stainless steel vacuum chamber so it wouldn't outgas hydrogen. At 10 to the minus 12 atmospheres, when you're dealing with 10 to the minus 19, it doesn't take much contamination to throw you off.

`§1.p13` There's a little helium in there too. If they had done it the conventional vacuum technology way, they would have spent twenty or thirty million dollars a year just in energy cost pulling the vacuum. So they had to develop a vacuum system so hermetically sealed that they could do it with a couple of vacuum pumps that would fit in this room — for the whole beam tube. That was a whole new technology. So they pushed the limits on surveying, vacuum technology, and outgassing of surfaces.

`§1.p14` This is when I learned, fifteen or twenty years ago, that some of the best engineering at MIT is done in the School of Science. I'd like to say some of the best science is done in the School of Engineering, but I'm not sure I can say that. When you get to these half-billion-dollar projects, the problems they have to solve are real engineering problems — as mundane as pushing the limits of surveying technology.

`§1.p15` So that's LIGO — sublime measurements. 10 to the minus 19 meters is how much gravity waves change the location of that tungsten sphere holding the mirror. That's significantly smaller than the diameter of the nucleus — the nucleus is around 10 to the minus 13 meters. We're five or six orders of magnitude smaller than the nucleus. That's the distance they're trying to measure.

`§1.p16` It's not something everyone wants to do. It's almost equal to the NIST annual budget. And then NIST has a precision measurement group, which is one or two percent of their annual budget, to make the most precise measurements of time and length.

---

## §2. The ridiculous: spark testing for steel composition [10:01]

`§2.p1` That's what we do for big science. Now let's talk about the ridiculous. Does anybody know what I'm going to do with my grinder and my steel rods? We're going to do spark testing. Chemical analysis à la 1900s steel.

`§2.p2` Different compositions of steel produce different amounts of sparking. This is 1018 steel — regular old carbon steel. When I worked for a steel company forty years ago, which is almost an eternity, there were guys who'd been spark-testing in the yard for thirty years. They had big yards full of rolled steel bars. The bars were supposed to be labeled, but they didn't have fancy laser marking, and they didn't have nice battery-operated grinders forty years ago either.

`§2.p3` *[Tom takes a grinder to a steel rod.]* If I take a grinder to this, I get sparks. Those sparks are different than if I take another piece of steel — this happens to be 440C. You can see the difference: hardly any sparks. This is a stainless steel; that was a carbon steel.

`§2.p4` I have a bunch of other steels here. This is 1045, which has a little more carbon — medium carbon, that one was low carbon. If I grind this one versus that one, the difference is in the little sparks at the end. High-carbon steel: lots of sparks. Mild steel: very few secondary sparks. Do you see the secondary sparks on that one? There are some on this one too, but they're not as intense.

`§2.p5` I can't tell the difference if you put two of these in front of me. But if you'd been doing it for thirty years, you could. These guys had 99.9% accuracy out in the yard. I have some alloy steels here too — tungsten steels, molybdenum steels. The most dramatic is stainless versus carbon. Stainless doesn't spark much because it doesn't oxidize well. This is all a question of how the steel oxidizes.

`§2.p6` Pretty ridiculous way to do things, right? The people who could do this have all retired or died. What we do now is use a $15,000 gun. CMSE has one. It's got a little radioisotope that generates gamma rays, and you put it up to a piece of steel and it gives you a digital display of ten different elements within plus or minus a few tenths of a percent. So you don't need a guy who can look at sparks. But that's how people used to do it.

---

## §3. The ball identification exercise [13:59]

`§3.p1` There are complex ways to do things like LIGO, and simple ways to do things. So we're going to give you a test — an in-class lab. I have four sets of these balls. Each one of you can do this. There are about eleven or twelve balls in each bag, but there are nineteen things the balls could be. You've got four or five minutes to see how many you can figure out.

`§3.p2` Last time I did this, people only got four or five out of nineteen. See how many you can do without the magnet, then use the magnet to see if you can figure out any others. Some of them you may only be able to narrow down to A or B — like, most of you can figure out you have a rubber ball, but there are two different types of rubber and you probably can't tell the difference.

`§3.p3` If you think you've gotten as many as you can, then use the magnet. Make a note of how many you distinguished with the magnet's help. You can distinguish certain types of stainless steel by magnetism. There are some carbon steel balls in there too. Unless they're rusty, you can't tell the difference between carbon steel and stainless. There are no duplicates in the bag.

`§3.p4` Okay, let's talk about it. It's not necessarily easy, but what properties were you using to distinguish the materials? That's a measurement. Everyone got the first one — brass. What property did you use? Color. Color is a property.

`§3.p5` I bet most people got the second one. What property did you use to find the aluminum ball aside from color? Density. Most of you found it first on density. Some on color. Either way, that's another property.

`§3.p6` Low-carbon steel — did anybody figure out which steel ball is low carbon? It's not easy unless it's rusty. If it's a little rusty, you got it by corrosion resistance. You couldn't tell it on density, and you couldn't easily tell it on color — unless you were really good, like the guys with the spark testers who'd been at it every day for thirty years.

`§3.p7` Go into a machine shop, and a machinist can look at those balls and tell you whether they're 9/16, 7/16, or 1/2 inch. They all happen to be 1/2 inch. If I just put a 7/16 and a 9/16 ball on the table and asked you the diameter without telling you, the average person would be about 50/50. But a machinist who deals with these dimensions every day will get it right 98% of the time. So a lot of it is experience.

`§3.p8` The stainless steels — you were able to distinguish that one of them was magnetic and the other two were not. That's because the 300-series stainless steels are austenitic, 18-8, non-magnetic.

`§3.p9` *[Tom takes a magnet to a Farberware pot.]* I use this Farberware pot in a lot of lectures. It's non-magnetic down here because it's 18-8 stainless — actually 304. Up here it's quite magnetic. That little red magnet — whoever ended up with it — sticks great up here.

`§3.p10` I use this in my forming course, deformation processing, and in other courses. Students complain I use the same props in different classes. Well, I only know certain things. We're all limited. **Student:** What were these bought for? I bought them for 3.014, and I don't know if we ever got to use them in 3.014, but I did buy them for 3.014. I may have talked in 3.014 about doing it, but the little labs always ran over. This was always going to be a fill-in if we had a couple of minutes at the end. I made these up.

`§3.p11` If you know enough about stainless steels, you could separate the 440C. The tool steel — M50 — is also magnetic. So the low-carbon steel, the M50, and the 440C are all magnetic. You got three magnetic balls — I saw you picking up three with the cow magnet. By the way, that's a cow magnet. The two of you in the front row got the cow magnet.

`§3.p12` Do you know what a cow magnet is? It's a stainless steel magnet — made out of 400-series stainless. You stuff it in a cow's mouth and make them swallow it. It goes into the cow's belly because cows tend to eat a lot of scrap metal, and the scrap metal can tear up their intestines. If you have something that holds the metal in the belly, the hydrochloric acid in the stomach will digest the steel before it gets to the intestines. So dairy cows get to eat a magnet. They're called cow magnets, they're cheap, they're stainless steel, and they don't rust. So I bought a couple. Don't worry — they've never been in a cow.

`§3.p13` The tool steel — to identify that you'd have to do a spark test, something destructive. I was asking you to do this non-destructively and without a lot of tools. You used density, color, you might have tried hardness — and you used coefficient of restitution. Did you know that? You were bouncing the balls. That's the coefficient of restitution.

`§3.p14` There were two rubbers. I can't tell the difference, but Viton is a fluoroelastomer. If I wanted to do it non-destructively and I had a scanning electron microscope, I could put it in the SEM and see which one has fluorine. Non-destructive. All I need is a quarter-million-dollar instrument. Easy.

`§3.p15` Torlon — anybody get Torlon? That's color again, but you have to know something about plastics. Acrylic — you probably got acrylic. The acrylic and the polystyrene are a little difficult because they're both crystal clear.

`§3.p16` There's a simple destructive test to tell acrylic from polystyrene. If I'd given you a plumber's torch or a match, you could have slightly burned them and told from the smell. Same thing for polyethylene. You wouldn't know what polyethylene smells like when it burns, but this is a standard trick — take a little razor blade, take a piece of the plastic if you don't know whether it's polypropylene or polyethylene versus some other milky white plastic, drop it in the flame. Polyethylene smells like paraffin wax.

`§3.p17` Why does polyethylene smell like paraffin wax? It has the exact same chemical formula — C_n H_{2n+2}. It's just a longer chain piece of paraffin wax. Polypropylene smells almost the same — it's got methyl groups rather than hydrogens off the side.

`§3.p18` Anybody get tungsten carbide? Heavy, right? Density. Also, if you had something to scratch it with, you wouldn't scratch the tungsten carbide. Anybody get aluminum oxide or silicon nitride? Two of you have silicon nitride and two have tungsten carbide. That's because those balls cost about fifty bucks apiece. They're high-tech ceramics.

`§3.p19` The low-carbon stainless steel balls were like three dollars for a bag of 100, and I couldn't buy less than 100. The tungsten carbide balls you buy one at a time at fifty bucks a pop. These all came from McMaster-Carr.

`§3.p20` Aluminum oxide — nobody got it? Hard, white, dense — but not very dense. Light, like aluminum. Aluminum oxide is a little heavier than aluminum, but not much. Nylon — some people might have gotten nylon by color. It's a different milky white. If you burn it, it smells slightly putrid.

`§3.p21` How many did you get? Let's see the competitiveness of MIT students. **Students:** Five. Six. Seven. Three. Four. Did you count the rubber? Yeah, count the rubber. **Student:** I got five. One of you was getting about ten — that's because you've been working in a lab with a lot of these different things for a couple of years. So there's the experience factor.

`§3.p22` The point is, we analyze things all the time without really analyzing them. When I'm teaching a communications lecture, I sometimes hold up a tensile bar — an aluminum tensile bar — and ask, "What is this?" A civil engineer will say it's a piece of metal, or a tensile bar. A mechanical engineer will say it's a piece of aluminum. A materials engineer might say it's 6061-T6. Everybody has a different lexicon and a different level of specificity, even though we're speaking English.

---

## §4. Practical measurement of length [31:54]

`§4.p1` Now you've learned a little about how we measure properties. Let's talk about the practical side. Mass, length, and time — let's start with length.

`§4.p2` *[Tom holds up a tape measure.]* A tape measure might give you one part in 20. You don't do too much with a tape. A ruler — this type isn't much better than a tape. A machinist ruler with 64ths of an inch can give you about one part in 100 or 200.

`§4.p3` A micrometer, or in this case a vernier caliper with a dial gauge, gives you about one part in 1,000 just from mechanical movement. An electronic one will give you about one part in 2,000 — half a thousandth of an inch.

`§4.p4` Then there are gauge blocks. Have you seen gauge blocks? These are the good ones — chromium carbide, rather than tool steel, so they won't scratch.

`§4.p5` Gauge blocks have been used by machinists for about 100 years to precisely measure length. They're ground so precisely on the end that they actually stick together by adhesion — just the bit of grease on them is the adhesive. Take my adhesive bonding course and you'll learn about ringing gauge blocks together.

`§4.p6` These come with a certificate of calibration. They're called Webber blocks because they're made by Starrett, but the traditional name is Johansson blocks, or Joe blocks, because those were the first.

`§4.p7` The certificate tells you these were measured using the international inch, because there are different inches — different calibration societies. One inch equals 25.4 mm exactly. That's a defined definition of an inch back in terms of millimeters, which are defined in terms of the speed of light. So when you're talking about calibrations, you actually have to define what standard you're calibrating to.

`§4.p8` Calibrated at 68° Fahrenheit, 20° C, 45% relative humidity maximum. The accuracy for 1-inch gauge blocks is about 0.02 microns, which is 0.8 micro-inches — eight tenths of a millionth of an inch. For 2-to-4-inch blocks, double that.

`§4.p9` You can get them in different levels. If you pay enough, you can get master blocks calibrated back to NIST — the company makes them and sends them to NIST, and NIST measures them to their standards.

`§4.p10` So there are all kinds of ways to measure length. If you control the temperature, you can easily measure to 50 millionths of an inch. You can get down to 10 micro-inches.

`§4.p11` Why do you have to specify the temperature? The coefficient of thermal expansion. Steel has a coefficient of thermal expansion of about 10 to the minus 5 per degree C — go look it up, it's just material properties. That means if your room isn't constant within 1° C, that 10 micro-inches becomes another 10 micro-inches per degree.

`§4.p12` Years ago I stole from my wife's sewing kit — she got it from her mother — a cloth tape measure on a roll. I liked it because I could take it with me and it rolled up the size of a dime. Now I can get small metal tape measures, and they don't stretch much because they're metal. That cloth tape, if you stretched it, you changed the length.

`§4.p13` So whether it's temperature or just the modulus of the material, plastic rulers are not as accurate as metal rulers because they have ten times the coefficient of thermal expansion. But many times, one part in 20 is plenty. If you're cutting a dressmaking pattern, that's all my mother-in-law needed. Who cares if it's off by a 16th of an inch — you're going to sew a seam over it.

`§4.p14` So you can improve things by a factor of two by going from a mechanical dial to an electronic dial. Electronic dials are cheap now — as cheap as mechanical ones — because of improvements in semiconductors.

---

## §5. Chips to ships: extremes of manufacturing precision [38:30]

`§5.p1` That's measurement of length. But let's think more about length. What are the most precise things we manufacture? After all, this is supposed to be a course on manufacturing. In parts per thousand or parts per billion, what are the most precise things we make? When someone asks a question like that, you have to go to the extremes. What's the extreme of a commonly manufactured product today in terms of small?

`§5.p2` **Student:** Microprocessor. A microprocessor — a semiconductor chip, about 1 cm squared. What tolerance do I have to hold on that? **Student:** Nanometers. About 10 to the minus 8 meters. The chip is 10 to the minus 2 meters. That's one part in 10 to the sixth.

`§5.p3` You have to worry about thermal expansion. They're actually doing lithography where they use masks to print the structures. Maybe it's within a nanometer, but really they're talking 20 nanometer feature lengths, or 13 — go look up on the Intel website where they are right now.

`§5.p4` I just bought some jump drives at Costco yesterday — a pack of three for twenty bucks, 16 gigabytes each. You can get 64 gigabytes for eighty bucks today. I threw them on my desk with my 2-gigabyte ones, and somewhere on my desk I have a 128-kilobyte jump drive, probably ten years old. They keep marching down in precision.

`§5.p5` Why are they limited to about a centimeter? Take my joining course and you'll learn — it's the same thermal expansion problem. If the chip gets too big, it has to be attached to a substrate with a different coefficient of thermal expansion, and they heat up 30, 40, 50 degrees C in service. You work out the delta T and you might crack them. The military has made them two inches on a side for super-duper applications, but you have to do all kinds of thermal management.

`§5.p6` What's the other extreme? The next largest thing we build that has no expansion joints? Highway bridges go for 20 miles, but they have expansion joints, so that doesn't count. Chips at one end — and the other end is ships. Chips to ships. A 300-meter, 1,000-foot ship. When you weld these together, how closely do you have to line up the ship plate before you weld it?

`§5.p7` That's three times 10 to the fifth. So who wins? It turns out Intel is winning now. A few years ago, ships were winning. Shipbuilding ten years ago was the most precise — in parts per million or billion — manufacturing we did. I now have to admit that the semiconductor guys are getting down there too. Build bigger ships.

`§5.p8` I told you about Catherine Gebbie [Katharine Gebbie] yesterday — the woman who went to Bryn Mawr and Harvard and MIT, PhD in physics, who heads up the atomic clock group at NIST. I caught her at a break and asked her — because she's now in the manufacturing group at NIST, but she's an experimental physicist — I asked, "Do you know what the most precise manufacturing there is?" They like to talk in parts per million, billion, trillion. She said no. I said, "It's shipbuilding." She looked at me, and I pointed to these numbers. "Oh." She could relate to one part in a million. She said, "How do they do it?" I said, "If the sun goes behind a cloud, the ship changes shape by half an inch — and you have to align them within a millimeter." She said, "Well, how do they do it?" I said, "Great big 100-ton jacks. They just squeeze them together."

`§5.p9` It shocked her, because she's been doing ultra-precise things. In shipbuilding, the practical answer is you just use a bigger hammer to pull it together. You don't use a bigger hammer when you're making semiconductors. So we're at two extremes — your quantum mechanical end and your astronomical end. Electrical readouts have improved our ability really only by about a factor of two.

---

## §6. Weight, time, and the limits of measurement [44:31]

`§6.p1` So that's length. We can do weight fairly quickly. A mechanical bathroom scale is probably good to plus or minus a pound — one part in 100. An electronic scale gets your weight to a tenth of a pound. Whether it's accurate or not, for precision and reproducibility, it's accurate.

`§6.p2` If you're weighing for chemical analysis — gravimetric analysis, weighing your sample, digesting it, measuring concentration — that's still one of the most precise, at about one part in 5,000.

`§6.p3` If I'm analyzing gold, they still use the fire assay technique. If you were in the materials department 120 years ago, you'd have taken a course in fire assay. There's a safe down in the basement where they used to keep the gold. The buildings were built in 1917, and they were probably still teaching fire assay as part of the undergraduate labs. You weigh the karat gold on a very precise balance — one part in about 5,000 if you do it properly.

`§6.p4` Then you digest it by throwing it into a bath of lead. You oxidize away the copper, the zinc, everything, and you're left with gold and silver. Lead and gold are immiscible — look at the phase diagram — so you get a little button of gold at the bottom with the lead floating on top. Gold's more dense than lead.

`§6.p5` You pop off that little button, roll it out in a little rolling mill, and put it in nitric acid. The nitric dissolves away the silver in this thin strip, and then you weigh the gold.

`§6.p6` By this process you're actually refining the gold to 99.999% pure, and you weigh it to one part in 5,000. It's still the most accurate way.

`§6.p7` Twenty-five or thirty years ago I was given the job of coming up with a better process than fire assay. We couldn't do it then. We're getting close now with inductively coupled plasma — probably one part in 2,000. But the standard, if you're doing a referee — a fight between people over the concentration of gold — is still fire assay. If you're dealing with fifty million dollars worth of gold, one part in 5,000 is $10,000. It's worth being accurate.

`§6.p8` The standard is still fire assay, which has been done for several thousand years. Over the last twenty-five years we've improved the other stuff by about ten times — the inductively coupled plasma is getting close.

`§6.p9` What are the limitations on weight? Wind, vibration, and fingerprints. If you've ever had to weigh something as precisely as possible, the balance — even if it's electronic — is sitting on a marble table with three-inch-thick legs of solid marble. Lots of mass to cut down vibration. It's inside a glass enclosure. Professor Allen has an old pan balance in his office with a glass enclosure. You have to wear white gloves — no fingerprints — and ideally lint-free gloves. Your fingerprint can set something off by one part in a thousand. Those are some of the limitations on weighing, but weighing is still one of the best.

`§6.p10` Time. What's the history of measuring time? We used to have mechanical clocks, and there are people who spend their lives buying antique clocks for fantastic amounts of money.

`§6.p11` Why did the Navy build the global positioning system? Knowing your longitude has always been the classic problem in ocean navigation. You can get your latitude from the sun, but you need to know time precisely to know longitude. So time has always mattered for navigation.

`§6.p12` A mechanical clock might be accurate to one second in a day — about one part in 10 to the fourth. Then quartz clocks came along — that's one part in 10 to the fifth. Quartz clocks didn't exist when I was born. We had mechanical clocks.

`§6.p13` A mechanical clock divides time into about 100 hertz. An electronic quartz clock divides it into 1/100,000 or 1/1,000,000 of a second. An atomic clock divides it into one part in 10 to the 10th seconds. NIST F1 does one part in 10 to the 15th. Time isn't really a problem in measurement right now. We've made tremendous strides over the last fifty years. So the three fundamental quantities — mass, length, and time — those are sort of the limitations.
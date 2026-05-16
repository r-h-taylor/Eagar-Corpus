# Lecture 9 — Safety Factors in Practice: Trailer and ATV Design

*3.371 Codes and Standards for Safety, Fall 2012, session 9 of 14.*
*Source video: `I9uRs8XywRk`.*
*Guest lecturer: Dr. Delmar. Prof. Eagar interjects in the second half.*

---

## §1. Continuing the safety factor: demand, capacity, and how use defines failure [00:02]

`§1.p1` Continuing on the safety factor. In the first lecture we talked about the definition and I started going through some examples. Today we're going to continue with a couple more. I want to talk mostly about different ways to look at and know the demand on a product. One of the reasons I'm doing this in the context of factor of safety is to show that depending on how conservative you are in determining the demand, your result will be different — you won't need as much of a safety factor.

`§1.p2` The safety factor we talked about was the failure load over the allowable load. Failure load varies depending on manufacturing, quality control, and the design itself. There is some uncertainty there unless you do a very precise and accurate design. For the allowable load, a lot of times it's more dependent on the application. If it turns out your structure is being used in ways it wasn't supposed to be used — an example of that is a car elevator. In a storage garage where people park cars for the winter, you have an elevator instead of a ramp between floors, like at the airport. Each car comes in, gets to a floor, and goes out, a little like a regular passenger elevator.

`§1.p3` If somebody comes and puts the same weight as a car but on one side of the elevator, that's not accounted for in the design. The code that governs the elevator says you only need to put the weight in the middle; you don't have to put it halfway on one side. In the case we were looking at, somebody came with a forklift fully loaded that was much lighter overall but had a much smaller wheel span, so they were able to put all the load on one side instead of more or less in the middle. And that came to be a problem.

`§1.p4` So is it fair to assume people know that this is meant to load big things as opposed to very small heavy things? It becomes a design question. By the time I ask for something that I know needs to be loaded in the middle, then obviously if I load it to the corner I don't have my safety factor anymore. I can actually fail some of the devices that take care of eccentricity. If this is loaded on the piston, you have railings to prevent it from turning. That railing is only so strong, depending on how much you say in your design that you're going to allow the load to be off center. So it's very simple in the first place, but you can start with an assumption that turned out not to be true all the time, when people don't use your structure the way you thought they would.

`§1.p5` The other definition, with yield stress and working stress, is very similar. When we were talking about the ASME code last week, saying it has a very high safety factor — that's based on the mean value of the pressure, as opposed to including pressure variation from closing valves, water hammers, everything you can have. So you could probably argue that ASME works with the second definition, where even by design you know that you will exceed your working stress sometimes.

---

## §2. Two examples without codes: trailers and ATVs [04:58]

`§2.p1` Demand and capacity. The two examples I'll talk about are a trailer design, which I did and I built, and then cars or ATVs — automotive type design. In both cases there are no real codes. If you go through the literature, nobody will tell you exactly how to design a trailer or a car as far as strength. The passenger car standards tell you that you have to put so many lights at this height, you need redundancy in your braking system. There are a lot of specifications, but when it comes to deciding how big the frame needs to be and how it gets connected and how it gets tested, the manufacturers are more or less left on their own to make sure it's strong enough. So today we don't really have a code or standard, but we're going to talk about ways to look at loads applied and capacity.

---

## §3. The trailer: designing from the wheels up [06:28]

`§3.p1` It's a relatively simple frame. *[Dr. Delmar draws the trailer frame on the board.]* Two beams that are eight feet long on each side. In the middle I have the tongue that goes about halfway from the middle going forward; it's also a beam. There are cross members here, a diagonal here, and some members for the floor to hold everything together. Single wheel on each side, on a torsional suspension.

`§3.p2` The way to design this is from the bottom up. Those wheels — if you start with a single wheel, you can only put so much load on them before you start wearing the tire or heating the tire. In this case they were rated for a thousand pounds each. Single axle, a thousand pounds. Are you going to put the whole load on one side of your trailer? Probably not. But that's where, in my case, I said that would be my safety factor. I'm going to put a thousand pounds on that beam and make sure it doesn't deform permanently in the middle. You can't have too much of a multiplication factor here because of the suspension. Say I allow for 500 pounds here and 500 pounds here, balanced by this. That gives me the size of this member.

`§3.p3` You can only buy these beams in increments of half an inch or one inch, so there's a point where one is not really good enough and the next is a little bigger, so I end up with a little bigger. In this case this one is three inches across. When I come to do the other side, it's the same size. This member here gets loaded if I end up putting the weight a little too far toward the front of the tray. In practice, having used this for eight years now, I know if I put the weight here, then instead of it all going into the suspension some of it goes on the ball. So I can put a little more weight.

`§3.p4` When I designed it, I put the weight right around here, and that made this cross member too weak. So I ended up strengthening these two in the middle, because of possible added force loading this way. That's all based on essentially not following the rule. You're supposed to have ninety percent of your weight on your wheels and ten percent on the tongue, but it's not always going to happen. So I ended up putting more here. These two outer members don't really do anything, so they are smaller in my design.

`§3.p5` Bottom line, if I think of this as a steady load, that's all I need. But in practice when I go through puddles and into the field, it's going to have to resist some torsion too. If I have more weight in that corner, this is going to bounce, and the whole plane of the trailer will try to rack. That's something that becomes a little more complicated to evaluate. But talking to people that have been building trailers for a long time, they told me that as long as I make my welded connections at the corner, they'll be more than sufficiently strong to resist the torsion.

`§3.p6` **Student:** [question about the planar deformation]

We start as a plane. It's eight feet by four feet, the size of this board a little bigger. If this wheel's pushing up very quickly, it wants to move up, and this one wants to stay. The only way you're going to prevent that deformation of your floor is by the resistance of the connections at the corner, or by bending.

`§3.p7` I went by their history mostly, because I thought it was going to be really hard to decide exactly how much force to put here and how much inertia. It's an inertia issue — it influences the transfer of force from one side to the other in a dynamic manner. In the end, I know it's not really oversized, because at some point this location deformed a little bit. I put on probably about three thousand pounds in it, instead of the two thousand pound design load. I was not going really fast, but I knew it was full of firewood, not the full height but a decent height.

---

## §4. Welds in compression, not tension [13:07]

`§4.p1` Afterwards I went back and checked. The reason I didn't get concerned with the overload is that in this connection here, I did not have welds on the tension side. I designed my connection so that this member was sitting under the cross member, and the welds were on the compression side. *[Dr. Delmar sketches the joint.]* The cross member comes right under and is welded together there, and on the sides there are some stiffening plates. The idea is, where I knew there was a risk of tension yielding, there are no welds at all. That tension yielding is something that, in my case, happened once. That's how I know I don't have any crack or any significant deterioration of that member.

`§4.p2` It would be a lot easier to design this in ways where you put more welding. But if you have welding in the tension zone and you start deforming it, then you're at risk of a premature failure depending on the weld quality. So I decided to put aside the uncertainty about the capacity of the metal by not having the connection where my highest stress was. I'm glad I did, because otherwise I don't know exactly what I would do with this trailer at this point. I'd probably have to stiffen it from underneath.

`§4.p3` If we look at it, this is the frame. You can see in the middle that the main member here is going under, because when I load this up it wants to push and this one wants to go up. That's why I want to have the cross member on top. That's really where the load is the highest, at the front cross member.

`§4.p4` This is how big it is today. If I let one of my friends use it and they're going to put something heavy in it, they need to be aware they can't fill it up. You can put maybe four tons of dirt in this trailer easily. It's only a one-ton capacity trailer. So it becomes common sense. There are things to look for — right here where the fenders are, when you go above 2,500 pounds and you hit some bumps, the wheels hit the fenders. So you know you're getting close. I had to raise them at some point because I wanted to put a little extra. But it's really custom-designed, and I can't say I'm going to go sell these things, because you'd need a much longer user manual than something you're supposed to go into Sears and buy and get on the road with.

---

## §5. The trailer's upper structure: aerodynamics and racking [17:05]

`§5.p1` I started more or less from scratch, and then I looked at what others would do for the same situation. For the upper portion, I ended up finding ways to make it lighter than most covered trailers. I have some composite beams — it's a composite structure with U-shapes going all around. I have diagonals. There's a very high safety factor for the whole thing to take off, because I've put enough steel connecting the roof all the way down. But at the same time there's not as much safety as far as starting to deform it on the way back, in a ductile way. Because of the redundancy, the amount of steel and bolted connections between the lower frame and the upper frame, it would bend over, it would not take off.

`§5.p2` That was pretty much my design criterion. If I have 2,000 pounds in it, and for whatever reason there's enough suction to take two thousand pounds, well, I don't want the whole thing to take off. So it's going to be able to take two thousand pounds of pulling — we can fill it up and lift it until the wheels untouch the ground — just with the idea that I didn't want to deal with all the aerodynamic issues. There's some basic aerodynamic calculation I did. At the front it has a pointed nose, but say you had a square nose: the baseline calculation if you're going to ride 65 miles an hour is to assume a force of 25 pounds per square foot for the wind pressure.

`§5.p3` That gives you a good idea. If I have 25 pounds on this panel here, 4 by 4 is 20, times 25 — I'm looking at about 500 pounds at least just pushing on it. You can double it because you don't really know. Am I really going to stay only at 65? Probably not. And then you have the effect when you're going around a truck and hitting the trailer, which isn't taken into account in that simple velocity calculation. That's pretty much the idea for the upper. I actually went stronger straight on, but it's still a relatively flexible structure. That's why it has a cross member two-thirds of the way along, so there's no issue of side forces — which are a little bit like the lower frame, you don't know exactly how much side force you're going to have. So there's a cross member in the middle, at the beginning, and at one-third. And the door in the back also prevents racking, the same type of twisting of the overall fuselage.

`§5.p4` **Student:** [question about fatigue or failure history]

There's no failure on it, even though I abused it. Somebody's asking: did you design for it, or you just ignored it? No. By taking the worst-case load here and not putting welds, with the safety factor, it includes the factor-of-two reduction due to fatigue. When I said I had a safety factor of two because I put the whole load on a single beam, that sort of included the long-term material properties. But it's still designed as an extreme load scenario, with the idea that extreme load is more than 60 percent of the working load that would generate fatigue.

---

## §6. Tom on the code: weld allowables and amateur builders [21:55]

`§6.p1` **Tom Eagar:** Another way to think about it: if you look at the structural welding code, the design allowable stress is only half of what your minimum yield stress is going to be. So you've already got a factor of safety on the members. But the design allowable stress for the welds is only thirty percent, okay. You have a higher factor of safety on the welds. He's saying that by not putting welds in tension, he doesn't have to worry about that. The code doesn't tell you that, but this is one place where the code's conservative. They can't control whether something's in tension or compression in the design. He can, as the designer.

`§6.p2` Plus, he doesn't come under anything. He can kill himself with this. Crash. Okay, no, seriously — the laws state that if you build your own airplane, you just can't fly anybody except your immediate family. Okay? You kill your family, you can't kill anyone else. If you start to fly anybody else, then you come under a different standard. He has a factor of safety inherent in using the design allowable stresses from the codes. That gives him a factor of two on the members. He got around the problem with the welds by putting them in compression rather than tension. You can't always do that.

`§6.p3` **Dr. Delmar:** It's a very good question, but it does bring up the general concept — when you go to ASME and design your pipe with a certain working pressure, you don't say, well, my pressure is going to vary, so I'm taking it down further. It's already built into those values that are there for shut-down and ramping up. Now, it doesn't mean that if you cycle multiple times per day, it's necessarily part of that application. That's what you need to check for.

`§6.p4` In my case, the other aspect is I'm dealing with structural steel, no welds, and I'm designing it so it doesn't yield. That's how I started. For fatigue, if I wanted to break this in say 10,000 cycles, those beams here without welds would have to go beyond the yield point. That's what it would take to break under those conditions. So we're not in a condition we call high-cycle fatigue, where you have millions of loading cycles. It's only when you hit a big bump on the road. There's nothing going on here with strength; you have some dynamic factors that add and could result in getting close to the yield strain.

---

## §7. Practical fabrication and the ladder cautionary tale [25:01]

`§7.p1` In retrospect — that's what I mean when I talk about practical design. This member here, if I wanted to optimize it and this was a race car, I would make it thicker here. I actually did that, because I made the tongue longer after I built it. It started as a 12-foot member and I made it 15 feet. So at the end here it's a smaller beam, a transition from a bigger beam to a smaller beam, mostly because I decided to make it longer after I had it.

`§7.p2` But the idea is, doing this is a lot more fabrication. If I start changing the section size as I'm moving along, I'm adding to the number of pieces of metal to put together. I could do the same for this member — the highest load is in the middle, so I could strengthen that section, but it's not always practical. I only had beams, and I wanted to put them together. I didn't really want to have to make longitudinal connections or lap joints just to optimize everything as if it were an airplane. It's not an airplane. So the practical way to make this stronger is to make the whole beam stronger, and that's why you become heavy very quickly.

`§7.p3` I analyzed this and arrived very quickly at the conclusion that I had a soft point right there. And maybe up above, but I didn't have any welded connection there either. I had some welded connection underneath to hook up the suspension, but not on top. That's how I came about doing this in practice. I overestimated the demand based on what I could put into this, and looked at other similar designs.

`§7.p4` In terms of looking at what could happen in a process — taking the trailer example again — if this were going to be built by somebody else after I came up with this design, I have to be very clear that there can't be any weld where I decided there was not going to be a tension weld. It looks very obvious, but we've seen cases: people have ladders that on the drawing just says "24-foot ladder," and then it turns out somebody put some welds in it because they only built it out of 16-foot-long members. There wasn't any requirement for the quality of those welds; they just made them the way they thought it was going to be okay. And it came out to be a very big problem.

`§7.p5` So in terms of fabrication, mine has no welds in the tension zone. And the inspection of the welds was mostly the welds that were going to prevent the twisting of the floor. Where I didn't have any weld, I used bolts to connect top and bottom. But if I had welds there, they'd have to be very well inspected, because they were going to work in tension or shear depending on the design. As for service history — it was my first one. That's why I didn't want to pretend like I knew everything from basic principles. I did go and see sizes of trailers of about the same capacity to make sure I wasn't far off.

---

## §8. The ATV: A-arms, ball joints, and complex loading [29:15]

`§8.p1` Now we're going to go to a little more complicated structure. We're looking at an ATV — quad or four-wheeler. What we're going to talk about for the front suspension here is more or less applicable to cars as well. They have what they call the control arms. *[Dr. Delmar refers to a diagram.]* We're looking at the wheel here. It has a knuckle that holds the wheel and the hub system. All the bearings are built into this one component, and you hold that knuckle with three points. This ball joint here is for the lower control arm. You have a little ball joint here — that's the tie rod that goes to the steering wheel, for holding sideways. And you have another ball joint on top to go into the upper control arm. So these are the only three ball joints holding the knuckle holding the wheel.

`§8.p2` In this case, the suspension is attached to the lower control arm, so we know that one's going to be loaded more. The only thing the upper ball joint does — you have bushings here and a ball joint there — is prevent the wheel from tipping back and forth. It's the lower arm that's going to make sure the wheel doesn't collapse, that the suspension doesn't collapse, that it stays on the ground. So the lower arm supports the ground force, which actually isn't that much.

`§8.p3` If you look at the shape of the arm, it's what we call an A-frame, or a triangle. It's stronger for forces that are back-to-front than for up-and-down. So for a force hitting an obstacle or applying the brakes, you can resist it by a combination of tension in this member, compression in this member. It's more or less a truss structure. For a force coming from the ground, that's resisted by the suspension we're going to put right here — the two tubes individually working in bending to resist the ground force.

`§8.p4` So if you design this, you have to think about both factors. How much force is going to come from applying the brakes versus from resisting the load from the ground? And maybe you're going to hit wood logs or stones with that member right here. You can see they put a little fender, a little protection that goes on top. There may be some dirt, some grass that will also hit this member.

`§8.p5` It's a complex loading. When you think about those rubber wheels going around a rough turn, you can arrive at worst-case scenarios. It would be really hard to put more than the whole weight of the vehicle on one wheel, because if you start really putting a whole lot more, that means you're landing really fast on one wheel, and that would typically get you to lose control. There are only so many worst-case forces you can think of for vertical load on that ball joint. And same for applying the brakes — if you arrive at a certain force for this, then what you need is a friction factor against the ground, and that gives you a good idea for this load going backward.

`§8.p6` For a load this way from turning, it's a little bit the same story. If you turn your wheels, there's only so much you're going to engage with the ground. Maybe the friction factor is one in the worst-case scenario, but most likely if you're on the road it's going to be 0.6, 0.7 for rubber. So you can work out these three forces.

---

## §9. Field testing, fatigue, and abuse tolerance [34:48]

`§9.p1` I don't know exactly how you handle the question of hitting stones and wood pieces. That's why they do a lot of field testing. They hire people to go out, and they put force transducers mounted right between the hub and the wheel itself, to capture all the vertical, torsional, and shear forces between the hub and the wheel for different driving conditions. Then you can go back to this type of analysis or to a finite element analysis and evaluate how close you are to these worst-case scenarios and how often they show up.

`§9.p2` We didn't talk about this yet, but compared to my trailer example, here you do have welds. You can't make this complex shape — these are hollow tubes with ball-joint forgings and everything together — in a practical sense without welding them or using a lot of rivets or bolts. The rivets or bolts are too expensive for this application. So it ends up being a lot of welding. And when we're talking about welding, the fatigue becomes more important. That ties back into our first example.

`§9.p3` We want the strength to be sufficient to handle these worst-case scenario loads. That's where the history comes in too — how many times would you expect somebody to ride it to this limit? There's no single answer. From working with these types of devices, even when you take these worst-case loads, the safety factor is still very high. They don't want the wheels to come apart just like that. It's designed to take a high amount of abuse.

`§9.p4` Now, that doesn't mean — and that's where some of my work comes in — that if you run into a tree it will still be the same after that. You become a crash situation, where we're not talking about these forces anymore. All of a sudden this force just went way up, and the whole unit spins around. At that point, you could think of it as a good thing if it's absorbing energy, because you really exceeded what you can tolerate for handling.

`§9.p5` That's where you want your design to be. You don't want to be in a condition where you're still in control, going around a curve in a car, and all of a sudden something deforms and you lose control. You want this to be able to sustain it as long as you're on your wheels and you're not in a rollover or skidding situation. But at the same time, you can't make it in such a way that if you drop it from 20 feet off the ground it's still going to be in the same condition.

`§9.p6` You can tell it's not completely random. There's been a lot of years of experience knowing you want to spread these members instead of having just one piece coming out, to take into account the back-and-forth force from applying the brakes. That's why it's spread into an A-frame, as opposed to just a piece sticking out. For the upper arm, the spreading between the two members is less — it becomes tighter — because when you're further from the ground, you don't have as much of that back-and-forth force.

`§9.p7` If we're looking at this — the ground, the two ball joints, the knuckle — the force ultimately comes from the ground, say backward. This lower ball joint needs to resist it by about twice as much. You reach equilibrium with about half the load on the upper one. That actually shows up in the design. It doesn't really come from testing; it comes from that simple analysis of moment.

`§9.p8` If I try to do the same for the size of this member versus this member, I end up with similar characteristics. If I'm looking at the knuckle, what I've seen lots of times is they make it stronger on the lower half. Sometimes it's just twice as wide, so you know exactly that it's stronger compared to the upper half, because they know it's not going to have to resist the same loads.

---

## §10. Manufacturing tolerances and segmented welds [40:52]

`§10.p1` A combination of worst-case scenario loads, field testing, and material testing. Taking all of this into account, if you go to fatigue for this, you don't have a safety factor of four anymore, because you've looked at it enough that you can tell it's not going to go much beyond your population. And it's the same for manufacturing. They make the welds in segments. If you have a weld around a round member — this one comes into the frame — they weld around in segments. If you have one that's not done correctly by mistake, you still have three-fourths of your circumference.

`§10.p2` That could be one way to look at it when you're saying, what would be my worst strength? Maybe I got one that's not done right and would still be able to meet your requirement. Not that you want that — because if you say we're going to do it for three-fourths, then you might end up with only half that's actually welded. But it's our way to make sure, from the manufacturing standpoint, that you have the strength you expect. If for my design I'm going to take the strength of three-quarters of it, I'm going to ask for four-quarters, no question, in the shop. But when it comes to what would be unacceptable, this will still be acceptable. Something that happens.

`§10.p3` From the loading scenario here, this is not really how I want people to drive my product. I need to put it in because they will abuse it. That's the capacity and that's the demand. The more you know from history about the two of them, or from field testing, the more you can reduce that factor of safety. I have seen some ways of calculating the useful life of these products that essentially end up with a safety factor of one. Because they've put it all in there — a lot of cycles of this, and that's all you get. If it can resist all these loads for so much time, taking the worst manufacturing case into account, and you have all that service history to verify that these loads are worst-case scenarios by putting sensors on your unit, then it's a little bit like your example with the landing gear: your safety factor is just going way down.

`§10.p4` One of the reasons you do that is you make a lot of them, and if you can make them 20 pounds lighter, 25 pounds lighter, they handle better. You get stuck in the snow, you can more easily take it out. So it's still a situation where not everything is optimized — these tubes are typically the same length all along, even though this one is loaded in compression, and you would want to have it more resistant to buckling, the way I drew it. But it's not practical. You're going to build out of straight tubes. So instead they have some cross members that help against the buckling capacity. We haven't really gone into each member, but they all have a very specific criterion you have to design against.

`§10.p5` If you want to take the weakest point of this, it would be a competition between a weld that's too small here and maybe this member being a little bent to begin with. That's where you start figuring out your design — calculations, testing.

---

## §11. Modifications in service: the nuclear-recovery deck holes [45:46]

`§11.p1` I'd like you to think about this in terms of demand and capacity for safety factors. If you know what it's going to be used for, if there's maintenance — are you going to drill some holes in your tubes? It happens in big structures.

`§11.p2` I worked on the erection of decking structural frames for nuclear recovery systems. The contractor came and put in some tubings, just conduits for the electrical, into the main frame that had to be resistant to seismic deformation. So the design of the member was to work in plasticity back and forth. If you have holes in it, it's not the same. The problem there was — now it's done. So what exactly are we going to do about it? The whole structure is there, they have walls, they have a roof, and this guy came and drilled some holes.

`§11.p3` The first thing I said — everyone was very surprised — was, don't plug-weld them, because you're actually going to make the situation worse. Welding will add residual stresses to the point where, when you get into plasticity, you're going to be more likely to initiate cracking than if you do nothing. So one way — these were round holes — was to sort of elongate the holes in this shape, that would be for loading this way. So you don't have as much of a stress riser at this location. Professor Eagar talked about a factor of three here; we can take it down to two and a half. That's for elasticity. When you get to plasticity, the stress concentration factor is less. But anyway, we could work on that geometry.

`§11.p4` What we ended up doing was to apply a stiffener that was welded away from the strengthened zone. It wasn't an easy fix, because it's the same situation where you have the code with all the requirements and the built-in safety factor. And now no matter what you do, you're not getting what you wanted in the first place. So you have to re-evaluate all the situations. If I stiffen the hole — I have a plate like this with the hole, and I come and put another member that I weld here and here — I don't want to increase the stiffness too much of this system, because it's still supposed to work by deforming back and forth. It needs to have compliance and energy absorption. That's the design requirement. So we did find a way, but it wasn't to make it look the same. In terms of property, that was really the worst-case scenario.

---

## §12. Safety factors in context: closing summary [49:01]

`§12.p1` We talked about the design situation. The safety factor — the number you see, four, two, three — is not really meaningful unless you put into context what exactly is the load you're looking at, the demand, and what exactly is the capacity. There will be an acceptable rate of failure. When we're talking about cars, in a crash situation obviously, and there may be other situations where you really abuse the car — it's 20 years old and the suspension has hit the bottom so many times that it can't take it anymore. I'm going to design it with a suspension. If I say, every car that comes off the road I want to design it so it's fine for 20 years even if the suspension is busted, that may not be practical. You may end up with a heavier car.

`§12.p2` There's always going to be variation in your capacity, and mostly when we talk about bolts, welds, any kind of connection, that's something that will reduce your capacity. The viability of that will depend on your inspection. We haven't talked about that a whole lot; we'll do that next class. After going through this, I think the answer is, we don't design things much stronger than they need to be at the very end.

`§12.p3` When we see a factor of safety of two, or four, it really doesn't mean you can put four times more demand on your structure. It's just that there are things that are variable, that you know about but you haven't gone through the process of quantifying. And that's fine. The most important thing is to be consistent. If you're making the design of a car in a certain way, and your history tells you it's strong enough, you can keep doing it this way, because you have your built-in history. You may be able to optimize it gradually. But you have to keep watching to see that you're not getting beyond what's acceptable in service. If you're relying on service history a lot, you have to keep track of it in a more detailed way. Any questions, any comments?

---

## §13. Tom's closing: tree-stand fatality, weld factors, and trailer welding bans [51:46]

`§13.p1` **Tom Eagar:** This idea that you've got at the top, of putting the weld in compression — it's pretty fundamental. I had a case down in Florida where a guy — you talked about designing your trailer, well, I had the exact same thing in a tree stand and it killed the guy. Because someone didn't think about: if you have a choice, if the loading is going to be this way, you put the weld up here so it's in compression. You don't put it this way so that you're pulling right through the weld, okay. When you're loading this way, your two members are just pushing against each other, and base steel has less variation than the weld.

`§13.p2` You asked a question about fatigue, just in general. The codes — whether it's ASME, which actually has higher factors of safety, but the structural welding code has on buildings a 1.67 safety factor, on bridges a 2.0 safety factor. That 2.0 basically assumes high cycle [cycles]. That's for the members. The welds, you assume, will have defects; they won't all be made perfectly. On the S-N curve for steel, at fifty percent of yield you'll have infinite life. And then Dr. Delmar was saying he knew he wasn't going to go two million cycles, okay. So he could actually have a lower safety factor because of the actual stress that's going on. If he's designing low-cycle fatigue, your safety factor is even more conservative. But they use the factor of two for fatigue for bridges and buildings.

`§13.p3` I've talked about some of the other stuff later, but — hey, I sit here and listen to it, I can think of other things I'll talk about. If you talk about bolting on trailers, the big heavy trailers going down the highway — tractor trailers — you are not allowed by code to weld on that frame, that steel frame. Too many trailers have had to be welded — given only welds. Okay, but we'll talk about that. Bolts are heavier, they're not as strong as welds. It takes longer to do — it has to do —
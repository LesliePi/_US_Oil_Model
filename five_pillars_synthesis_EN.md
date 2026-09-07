# Five Pillars, One Forced Path: What Actually Happens to Oil Before It Reaches the Pump

## The short version

We tend to think about oil as a yes/no question: you either have it, or you don't. Over the past week we built a five-part, interlocking model that shows this picture is incomplete. Finding the oil isn't enough — the *type* of oil (how heavy it is, its molecular makeup) determines how much of it is physically usable in the first place, and that fact quietly pushes a country onto a geopolitical path nobody actually chose.

All five pillars are built from real, primary sources (EIA, ExxonMobil crude assays, CrudeMonitor.ca, peer-reviewed literature), with every claim tagged by evidence strength (confirmed / derived / estimated). What follows is the headline result from each — the full source list and raw data will be on the GitHub repo.

## The model — not five separate stories, but one chain

The foundation is a conventional mass-and-energy balance: how much crude goes in, how much fuel comes out, how much energy the path from wellhead to wheel actually consumes. Where that conventional balance isn't precise enough — because, per the second law of thermodynamics, not all *retained* energy is equally *usable* — we added a finer, so-called exergy-based correction. That correction is a secondary refinement, not the backbone of the model.

**Pillar 1 — Refinery energy loss.** When crude is converted to diesel, beyond the conventional mass balance, some of the genuinely *usable* energy is also lost, at a rate that depends on crude type — this is what the finer, second-law-based correction measures. For light domestic crude the loss is small (about 91.3% of the usable input energy survives into the diesel), for Canadian dilbit it's larger (about 88.0%). The gap looks small — but it's only the first step.

**Pillar 2 — A molecular constraint.** Gasoline has a regulated vapor-pressure ceiling (EPA/ASTM standard). Domestic shale oil's molecular structure is simply too light to meet that on its own — so refiners are *chemically obligated* to blend in heavier, imported crude, no matter how much domestic oil is available. This isn't a market choice. It's a chemistry constraint.

**Pillars 3–4 — Wellhead to wheels.** The literature almost always stops the energy balance at the fuel pump. We carried it all the way to the engine — to the actual useful work delivered at the shaft, including the engine's own thermal-cycle efficiency. The result is **robust and surprising**: the chain for Canadian synthetic crude oil (SCO) **falls below an EROI of 1.0 even with the best commercial engine** (0.84–0.86), and the dilbit chain does too with a lab-test engine (0.96). In other words, for some imported crude types, the full extraction-refining-combustion chain **costs more energy than it delivers**, once you count all the way to the wheels rather than just to the tank.

**Pillar 5 — Geopolitical vulnerability.** This is where the constraints above turn into a concrete, measurable consequence. Between 2016 and 2026, heavy-crude imports into the U.S. Gulf Coast (PADD 3) collapsed dramatically — from 2,200 to 583 thousand barrels per day. Based on primary EIA microdata (our own processing, 1986–2026, complete monthly coverage, no gaps), **51.6% of that collapse is the 2019 U.S. sanctions on Venezuela**, and **25.8% is Mexico's structural production decline** — together, **77%** of the entire collapse. Canada grew over the same period (a partially offsetting factor), but not enough to compensate. Our own data confirms the sanctions timeline down to the year: Venezuelan imports go to zero between 2019 and 2022, then resume in 2023 (Chevron waiver).

## The combined effect

These five pillars aren't five separate observations — they're a closed loop:

> **The molecular constraint (Pillar 2) means domestic light oil can't actually displace heavy-crude imports → processing heavy crude already carries a bigger energy penalty (Pillars 1, 3–4), pushing some supply chains toward or below breakeven net energy return → and the remaining dependence is concentrated on a narrow set of suppliers (Venezuela, Mexico, Canada) whose politics (Pillar 5) then feed straight back into the physical reality of U.S. energy supply.**

In other words: you find the oil, you're relieved — but the *type* of oil you found locks you into a corridor that physics (what you can actually do with it) and geopolitics (who you now depend on for the missing piece) jointly close around you. This isn't a theory. Each of the five pillars, independently, backed by primary sources, points to the same pattern.

## What's still open — honestly

We're not claiming everything is settled:
- The wellhead-side energy input mix for dilbit/SCO (how much natural gas / diesel / electricity extraction actually takes) is properly sourced only for domestic shale (Bakken) so far — bitumen/dilbit/SCO remains an open question.
- On "which wellhead EROI value is authoritative," we have three sources that disagree with each other — we're treating this as a **parallel range of estimates**, not picking a "winner" until there's decisive evidence either way.
- Formally wiring country-level geopolitical stability into the model is still in progress.

## Connection to EIP

This work directly strengthens and extends the already-published **EIP (EnergyIntellect Pro) C12–C18 EROI_pump** framework (Zenodo DOI: 10.5281/zenodo.21381857) — Pillar 5's empirical result adds a new geopolitical layer to that companion model.

## Want in?

This has been a solo project so far, but it's outgrown what one person should carry alone. I'm looking for people interested in:
- energy economics / EROI analysis
- data processing, Python (the pipeline will be open source)
- oil-market / geopolitical expertise
- or just want to look, poke holes, and push it further

All sources, data, and code will be up on GitHub shortly — comment or DM if you'd like to be involved.

# Exergy-Molecular Oil Model

A source-disciplined, five-pillar analysis of U.S. crude oil supply chains, from wellhead to wheel: how much of the energy in a barrel of crude actually survives — as usable, shaft-delivered work — once you account for refinery losses, molecular/chemical constraints, engine thermodynamics, and the geopolitics of where the crude actually comes from.

**Author:** Tatai László · **Companion framework:** [EIP — C12–C18 Middle-Distillate EROI Framework](https://doi.org/10.5281/zenodo.21381857) (Zenodo DOI: 10.5281/zenodo.21381857)

---

## Start here

**[Five Pillars, One Forced Path](./five_pillars_synthesis_reddit_EN.md)** — the plain-language summary. Read this first.

For the full sourcing, equations, and derivations behind each claim, see [`/docs`](./docs).

---

## The core idea

You find the oil — but the *type* of oil you found determines how much of it is physically usable, and that fact quietly locks a country into a geopolitical corridor nobody chose. Five pillars trace this chain end to end:

| Pillar | Question | What it refines |
|---|---|---|
| 1 | How much usable energy does the refinery itself destroy, and does that depend on crude type? | Refinery exergy efficiency |
| 2 | Why can't light domestic tight oil simply replace heavy-crude imports? | Molecular distribution / vapor-pressure (RVP) constraint |
| 3–4 | How much of a barrel's energy actually reaches the wheels, not just the tank? | Well-to-wheels net EROI |
| 5 | Who does the U.S. actually depend on for the heavy-crude share it can't produce domestically, and how fragile is that? | Geopolitical / logistical vulnerability |

**Framing note:** the backbone of this model is a conventional mass-and-energy balance. Where that isn't precise enough, a second-law (exergy) correction is added as a secondary refinement — not as a rebranded standalone theory. Every claim in `/docs` is tagged by evidence strength:

- **GOF** — sourced / confirmed against a primary, citable source
- **DER** — derived from GOF inputs via an explicit formula or code path
- **EST** — estimate or interpolation, explicitly flagged as such
- **OPEN** — a question this project has not yet resolved

Negative and inconclusive results are recorded, not dropped. Where more than one defensible methodology exists, this project keeps them as parallel bounds rather than picking a winner prematurely.

---

## Repository structure

```
README.md              this file
five_pillars_synthesis_reddit_EN.md   plain-language summary (start here)
/docs                   full pillar-by-pillar briefs — sourcing, equations, epistemic tags
/code                   the data pipeline (download → process → derived series)
/data                   derived output series (our own computed results only —
                         see "On data and sources" below)
/assets                 diagrams
```

## On data and sources

This repository contains **our own derived results and our own code** — not third-party datasets or copyrighted papers. Where the model depends on external work, `/docs` cites it by DOI or official source link rather than redistributing it:

- **Government/institutional data** (EIA, EPA, DOE, World Bank, etc.) is publicly available from the issuing agency; `/docs` links directly to the specific series and tables used. The pipeline in `/code` can re-download the same source data on request — anyone is welcome to pull it fresh and reproduce the derived series independently.
- **Peer-reviewed literature** (e.g. Masnadi et al. 2018, *Science*; Elgowainy et al., *Environmental Science & Technology*) is cited by DOI. We do not host publisher-copyrighted PDFs or their supplementary files here.

`/data` therefore contains only series we ourselves computed from that public source data — e.g. the 1986–2026 PADD3 heavy-crude import series, derived from EIA Company-Level Imports microdata via the pipeline in `/code`.

## Contributing

This started as a solo project and has outgrown that. If you work in energy economics, EROI analysis, Python/data pipelines, or oil-market geopolitics — or just want to look, poke holes, and push it further — issues and pull requests are welcome.

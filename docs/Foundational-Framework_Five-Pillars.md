# The Five Pillars of the Synthesized Exergy-Molecular Oil Model

Our synthesized model rests on five distinct pillars. For the end result to hold up to scrutiny, each of the five pillars is anchored to its foundational literature, together with the exact mathematical / thermodynamic equations and datasets that go with it.

---

## Pillar 1 — The Second Law and Refinery Exergy Analysis

**Core idea:** A refinery is not a First-Law mass- and heating-value-conserving system, but a chemical-exergy-destroying plant.

**Foundational literature:**
- Antonio Valero & Alicia Valero — *Physical Geonomics / Exergy of Economic Goods*
- Göran Wall — *Exergy, Ecology and Economy*
- Rivero et al. — *Exergy analysis of crude oil distillation units*

**Exact mathematical basis** (B_refinery):

$$B_{in} = B_{crude} + B_{H2} + B_{own\text{-}heat} + B_{electric}$$

$$B_{out} = \sum m_i \cdot b_{i,chemical} = \sum m_i \left( LHV_i + T_0 \Delta S_{formation,i} \right)$$

$$\eta_{ex,\ refinery} = \frac{B_{out}}{B_{in}} = 1 - \frac{T_0 \cdot \dot{S}_{gen} + B_{heat\text{-}loss}}{B_{in}} \approx 0.78 - 0.84$$

---

## Pillar 2 — Molecular Distribution and the Vapor-Pressure Constraint (PADD 3)

**Core idea:** Refinery "top-end flooding" caused by tight oil's C₂–C₈ surplus and its C₁₂–C₃₀ shortfall, together with the resulting vapor-pressure constraint.

**Foundational literature:**
- Art Berman — *Petroleum Geology and Tight Oil Resource Limits*
- EIA (U.S. Energy Information Administration) — Crude Oil Input & Refinery Capacity Data (PADD 3)
- ASTM D323 — *Standard Test Method for Vapor Pressure of Petroleum Products (RVP)*

**Exact mathematical basis** (RVP and fraction matrix):

$$RVP_{blend} = \sum x_i \cdot \gamma_i \cdot P_i^{sat} \le RVP_{standard}$$

Because of tight oil's high x_C4–C6 share, blend RVP exceeds the permitted limit — forcing either flaring or below-market NGL offtake.

---

## Pillar 3 — Motive Exergy Extraction (C₅–C₈ vs. C₁₂–C₃₀)

**Core idea:** C₁₂–C₃₀ fractions enable high compression ratios (ε ≥ 18) and the higher-brake-thermal-efficiency Diesel/Seiliger cycle.

**Foundational literature:**
- John B. Heywood — *Internal Combustion Engine Fundamentals*
- Richard Stone — *Introduction to Internal Combustion Engines*

**Exact mathematical basis** (η_ex, engine):

$$\eta_{th,\ Seiliger} = 1 - \frac{1}{\varepsilon^{\kappa-1}} \left[ \frac{r_p r_c^\kappa - 1}{(r_p - 1) + \kappa r_p (r_c - 1)} \right]$$

$$W_{useful} = \eta_{th,\ Seiliger} \cdot B_{fuel} \cdot \left(1 - \frac{T_0}{T_{combustion}}\right)$$

This shows roughly a 1.5× exergetic gap between C₅–C₈ (Otto cycle, ε ≈ 10) and C₁₂–C₃₀ (Diesel cycle, ε ≈ 20).

---

## Pillar 4 — Well-to-Wheels Net EROI

**Core idea:** Refinery exergy loss, combined with steep wellhead decline rates, drastically degrades the socially useful EROI.

**Foundational literature:**
- Charles A.S. Hall & Kent Klitgaard — *Energy and the Wealth of Nations: An Introduction to Biophysical Economics*
- David Hughes — *Drilling Deeper: A Reality Check on U.S. Shale Production*

**Exact mathematical basis** (EROI_ext):

$$EROI_{soc} = \frac{E_{useful\ shaft\ exergy}}{E_{extraction} + E_{refining} + E_{infrastructure}} = EROI_{wellhead} \cdot \eta_{ex,\ refinery} \cdot \eta_{ex,\ engine}$$

---

## Pillar 5 — U.S. Geopolitical and Logistical Vulnerability

**Core idea:** The U.S. heavy-crude import requirement (Canadian WCS, Venezuela) needed to preserve the diesel-fraction supply chain.

**Foundational literature:**
- EIA — U.S. Imports by Country of Origin & Crude Type (Heavy vs. Light)
- Vaclav Smil — *Energy and Civilization: A History* / *Materials and Dematerialization*

**Datasets:** US PADD 3 heavy-crude import volumes vs. US domestic tight-oil production (2008–2026).

---

## Implementation Path

With this outline the structural architecture is in place. The following steps work through each pillar point by point:

1. **Data handling** — assemble the carbon-chain distribution matrix (C₁–C₄, C₅–C₈, C₉–C₁₁, C₁₂–C₁₈, C₁₉+) for a typical tight-oil proxy (Permian, 45° API) and a heavy-crude proxy (WCS, 20° API).
2. **Refinery balance** — compute the exergetic efficiency and energy loss of both crude types in U.S. Gulf Coast refineries.
3. **Final exergy derivation** — state the well-to-wheels exergetic efficiency for both pathways.

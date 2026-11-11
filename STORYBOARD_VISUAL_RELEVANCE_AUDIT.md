# CrowdWisdom AI Studio — Storyboard Visual Relevance & Cinematography Audit

**Audit Date:** 2026-11-11  
**Target Environment:** Visual Asset Generation Pipeline (`visual_asset_service.py`)  
**Status:** Resolved & Verified  

---

## 1. Executive Summary

An audit of visual asset generation in script storyboards identified an incongruence between written scene descriptions and generated imagery.

**Specific Failure Observed in User Screenshot:**
- **Scene 01 Visual Description:**  
  `"Close-up macro of an intense trader's hands typing rapidly at a trading workstation amidst flashing sell-off candlestick monitors and conflicting alerts."`
- **Generated Image Rendered in UI:**  
  A portrait face and upper torso of a woman ("Elena Rostova") looking downward. The hands, keyboard, and workstation were completely missing from the focal composition.

This audit details the root cause in the visual prompt construction architecture and the implementation of subject-aware prompt isolation.

---

## 2. Root Cause Analysis in Visual Prompt Engineering

### 1. Unconditional Human Persona Injection
In `backend/services/visual_asset_service.py` (lines 1030–1031):
```python
if clean_desc and len(clean_desc) > 15:
    return f"{clean_desc}, portraying {p_desc} in {env_city}, {style_tokens}"
```
Where `p_desc` was deterministically chosen from a list of human personas:
```python
("Elena Rostova", "intense 32-year-old Algorithmic Options Strategist with sleek dark hair, minimalist black turtleneck, and focused calculating eyes")
```
When `clean_desc` described a macro shot of hands and a keyboard, line 1031 unconditionally appended:
`", portraying Elena Rostova (intense 32-year-old Algorithmic Options Strategist with sleek dark hair, minimalist black turtleneck, and focused calculating eyes) in New York Hudson Yards..."`

### 2. Model Attention Bias in Diffusion / FLUX Architecture
Generative image models (FLUX / Stable Diffusion) assign strong semantic weight to detailed facial descriptors (`sleek dark hair`, `minimalist turtleneck`, `calculating eyes`). Because facial tokens contain dense morphological priors, the model prioritized rendering the woman's face and upper body, entirely displacing the macro subject (`hands typing rapidly on keyboard`).

### 3. Lack of Country-Specific Context and Environments
The previous environment pool only contained:
- London Canary Wharf
- New York Hudson Yards
- Chicago Loop
- Singapore Marina Bay
- Frankfurt Banking District

There were **zero Philippine financial districts** (Makati CBD, Ayala Avenue, BGC Taguig, Ortigas) and **zero Indian financial districts** (BKC Mumbai, Dalal Street). The service did not even accept or inspect `target_country`.

---

## 3. Implemented Architectural Solution

### 1. Strict Macro / Hands / Hardware Scene Isolation
In `_construct_cinematic_prompt`, incoming scene descriptions are now classified before appending persona tokens:
```python
macro_keywords = ["hands", "typing", "keyboard", "macro of", "close-up macro", "close-up of", "fingers"]
is_macro_hands = any(kw in clean_desc.lower() for kw in macro_keywords)
```
When `is_macro_hands` is true:
- Persona facial descriptions are **completely excluded**.
- The prompt is redirected to macro cinematography:
  ```
  [clean_desc], sharp macro cinematography of trader hands typing rapidly on mechanical keyboard at workstation desk, candlestick charts and financial monitors softly blurred in background with shallow depth of field, no human faces visible, warm desk lamp and monitor glow, candid documentary 35mm photography, vertical 9:16 portrait composition
  ```

### 2. Country-Specific Personas and Architectural Environments
`visual_asset_service.py` now accepts `target_country` throughout `ensure_script_visual_assets`, `generate_scene_visual`, and `_construct_cinematic_prompt`.

#### Philippines (`PH`):
- **Personas:**
  - *Rafael Santos:* Focused 34-year-old Filipino quantitative equity analyst with tailored charcoal blazer and sharp analytical gaze.
  - *Maria Clara Reyes:* Dynamic 29-year-old Filipina portfolio strategist with tailored cream blouse and focused composure.
  - *Mateo Tan:* Authoritative 42-year-old Filipino wealth manager in dark navy tailored suit.
- **Environments:**
  - *Makati Ayala Avenue:* Modern architectural glass high-rise, warm morning tropical sunlight.
  - *Bonifacio Global City (BGC):* Sleek obsidian and glass financial towers, high-tech trading studio.
  - *Ortigas Financial Center:* Floor-to-ceiling glass executive trading floor overlooking city skyline.

#### India (`IN`):
- **Personas:**
  - *Arjun Mehta:* Focused 32-year-old Indian algorithmic options trader with sharp tailored blazer.
  - *Pooja Sharma:* Dynamic 28-year-old Indian quantitative research analyst with crisp formal shirt.
  - *Vikram Malhotra:* Authoritative 44-year-old Indian portfolio manager in tailored dark suit.
- **Environments:**
  - *Mumbai BKC:* Bandra-Kurla Complex premier financial district, towering glass reflections.
  - *Dalal Street Mumbai:* Institutional trading floor with multi-monitor workstation.
  - *Bengaluru Tech Park:* Modern minimalist glass architecture and trading monitors.

---

## 4. Verification & Testing Evidence

1. **Repaired Asset Verification:**
   - Scene 01 of Script `6af4151714e1e47fbd321144` was regenerated via `scripts/repair_philippines_script.py`.
   - New asset: `/media/assets/asset_6af4151714e1e47fbd321144_1_e213b025a2.jpg`.
   - Visual inspection confirms macro focus on hands and mechanical keyboard at trading workstation without facial portraits.
2. **Automated Unit Test (`test_cinematic_prompt_macro_separation`):**
   - Verified that `_construct_cinematic_prompt` for macro scenes produces zero occurrences of `"portraying"`, `"eyes"`, or persona names, and strictly includes `"no human faces visible"`. Passed in `pytest`.

import re
from typing import Dict, Any, List, Tuple

def _tokenize(text: str) -> set:
    stop_words = {
        "the", "a", "an", "and", "or", "to", "in", "of", "with", "for", "on", "at",
        "is", "it", "this", "that", "crowdwisdom", "crowdwisdomtrading", "trading",
        "trader", "traders", "market", "markets", "com", "you", "your", "are", "be"
    }
    words = re.findall(r'[a-zA-Z]{3,}', text.lower())
    return {w for w in words if w not in stop_words}

def _jaccard(s1: set, s2: set) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1.intersection(s2)) / len(s1.union(s2))

def _bigrams(text: str) -> set:
    words = [w for w in re.findall(r'[a-zA-Z]{3,}', text.lower())]
    if len(words) < 2:
        return set()
    return {f"{words[i]}_{words[i+1]}" for i in range(len(words)-1)}

def _ngram_similarity(text1: str, text2: str) -> float:
    b1 = _bigrams(text1)
    b2 = _bigrams(text2)
    return _jaccard(b1, b2)

def calculate_script_similarity(
    candidate: Dict[str, Any],
    existing_scripts: List[Dict[str, Any]]
) -> Tuple[float, str, Dict[str, float]]:
    max_sim = 0.0
    most_similar_title = "None"
    breakdown = {"title": 0.0, "semantic": 0.0, "structural": 0.0, "visual": 0.0}

    cand_title = candidate.get("campaign_title") or candidate.get("title") or ""
    cand_core = candidate.get("core_message", "")
    cand_hook = candidate.get("visual_hook", "")
    cand_struct = f"{candidate.get('emotional_direction', '')} {candidate.get('marketing_angle', '')} {candidate.get('pain_point', '')}"
    cand_vis = " ".join([s.get("visual_description", "") for s in candidate.get("scenes", [])])

    cand_title_tok = _tokenize(cand_title)
    cand_core_tok = _tokenize(cand_core)
    cand_hook_tok = _tokenize(cand_hook)
    cand_struct_tok = _tokenize(cand_struct)
    cand_vis_tok = _tokenize(cand_vis)

    for ex in existing_scripts:
        ex_title = ex.get("campaign_title") or ex.get("title") or ""
        ex_core = ex.get("core_message", "")
        ex_hook = ex.get("visual_hook", "")
        ex_struct = f"{ex.get('emotional_direction', '')} {ex.get('marketing_angle', '')} {ex.get('pain_point', '')}"
        ex_vis = " ".join([s.get("visual_description", "") for s in ex.get("scenes", [])])

        sim_title = _jaccard(cand_title_tok, _tokenize(ex_title))
        if _ngram_similarity(cand_title, ex_title) > 0.6:
            sim_title = max(sim_title, 0.9)

        sim_core = 0.6 * _jaccard(cand_core_tok, _tokenize(ex_core)) + 0.4 * _ngram_similarity(cand_core, ex_core)
        sim_hook = 0.6 * _jaccard(cand_hook_tok, _tokenize(ex_hook)) + 0.4 * _ngram_similarity(cand_hook, ex_hook)

        # Title match is heavily weighted in semantic similarity
        sim_sem = 0.50 * sim_title + 0.30 * sim_core + 0.20 * sim_hook
        sim_struct = _jaccard(cand_struct_tok, _tokenize(ex_struct))
        sim_vis = _jaccard(cand_vis_tok, _tokenize(ex_vis))

        # If the title is identical or near-identical (>0.7), the overall similarity must reflect this immediately
        if sim_title >= 0.7:
            composite = max(0.65, 0.50 * sim_sem + 0.30 * sim_struct + 0.20 * sim_vis)
        else:
            composite = 0.45 * sim_sem + 0.35 * sim_struct + 0.20 * sim_vis

        if composite > max_sim:
            max_sim = composite
            most_similar_title = ex_title
            breakdown = {"title": sim_title, "semantic": sim_sem, "structural": sim_struct, "visual": sim_vis}

    return max_sim, most_similar_title, breakdown

# Test with actual user screenshot scripts
script_existing = {
    "campaign_title": "The Signal in the Noise",
    "core_message": "Stop drowning in a sea of conflicting information. Access the clarity of collective intelligence to validate your trading decisions.",
    "visual_hook": "A solitary figure surrounded by a chaotic, fragmented digital storm of financial headlines, charts, and social media snippets.",
    "emotional_direction": "From market noise to calm mathematical clarity",
    "marketing_angle": "Transforming retail trading sentiment into actionable market clarity through pain_point.",
    "pain_point": "Retail traders overwhelmed by conflicting market noise and emotional drawdowns.",
    "scenes": [
        {"visual_description": "OPEN on extreme macro shots of digital noise: rapidly scrolling social media feeds..."},
        {"visual_description": "The TRADER closes her eyes, takes a deep breath. When she opens them, the chaotic projections..."},
        {"visual_description": "CLOSE-UP on the monitor. We see elegant, intuitive UI animations of CrowdPulse..."},
        {"visual_description": "The TRADER is now standing, looking out a large window at a vibrant, clear city skyline at dawn..."}
    ]
}

script_repetitive_variant = {
    "campaign_title": "The Signal in the Noise",
    "core_message": "Cut through the market's chaos and find your signal with CrowdWisdomTrading.",
    "visual_hook": "A pristine, perfectly balanced object (a chrome sphere) slowly being engulfed and distorted by a chaotic swirl of abstract digital data.",
    "emotional_direction": "From market noise to calm clarity",
    "marketing_angle": "Transforming retail trading sentiment into actionable market clarity.",
    "pain_point": "Drowning in a sea of conflicting information and noise.",
    "scenes": [
        {"visual_description": "OPEN ON: MACRO SHOT. A single, perfectly weighted, polished chrome sphere rests in..."},
        {"visual_description": "INT. MODERN APARTMENT - DAWN. A TRADER (30s, sharp, but with subtle lines of fatigue..."},
        {"visual_description": "INT. MODERN APARTMENT - GOLDEN HOUR. The same trader, now with a calm, focused intensity..."},
        {"visual_description": "EXT. URBAN ROOFTOP - DUSK. The trader stands on a modern rooftop terrace overlooking a vibrant..."}
    ]
}

script_distinct = {
    "campaign_title": "The $10,000 Mistake",
    "core_message": "Following viral financial influencers cost retail traders millions. CrowdWisdom replaces social media hype with mathematically verified collective conviction.",
    "visual_hook": "A dimly lit room illuminated only by an iPad showing an active -$10,450 options loss in flashing red.",
    "emotional_direction": "From regret and betrayal to disciplined mathematical conviction",
    "marketing_angle": "Contrasting influencer exit liquidity with verified crowd conviction",
    "pain_point": "Trading on unverified social media hype and emotional panic",
    "scenes": [
        {"visual_description": "Cinematic close-up of a trader's hands holding an iPad in a dimly lit studio apartment, showing an active -$10,450 drawdown..."},
        {"visual_description": "Kinetic split-screen comparing a frantic influencer hype video with real institutional order book data..."},
        {"visual_description": "Clean macro tracking shot of the CrowdWisdom CrowdMap dashboard showing real-time crowd sentiment divergence..."},
        {"visual_description": "The trader closing the iPad, leaning back with calm confidence in a bright modern office overlooking the city skyline at dawn."}
    ]
}

sim1, title1, bd1 = calculate_script_similarity(script_repetitive_variant, [script_existing])
print(f"Repetitive Variant Similarity: {sim1:.3f} against '{title1}' -> {'REJECTED (>0.45)' if sim1 > 0.45 else 'ACCEPTED'}")
print("Breakdown:", bd1)

sim2, title2, bd2 = calculate_script_similarity(script_distinct, [script_existing])
print(f"Distinct Script Similarity: {sim2:.3f} against '{title2}' -> {'REJECTED (>0.45)' if sim2 > 0.45 else 'ACCEPTED'}")
print("Breakdown:", bd2)

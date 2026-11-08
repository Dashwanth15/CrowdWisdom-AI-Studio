import re

def _clean_on_screen_text(text: str) -> str:
    if not text:
        return ""
    meme_patterns = [
        r'\bBUY\s+NOW!?\b',
        r'\bDUMP\s+IT!?\b',
        r'\bFED\s+HAWKISH\??\b',
        r'\bTO\s+THE\s+MOON!?\b',
        r'\bHODL\b',
        r'\bLFG\b',
        r'\b100X\b',
    ]
    cleaned = text
    for pat in meme_patterns:
        cleaned = re.sub(pat, '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = cleaned.strip(' !?;:,-')

    words = cleaned.split()
    if len(words) > 6:
        cleaned = " ".join(words[:6])

    if len(words) >= 3 and cleaned.isupper():
        cleaned = cleaned.title()

    return cleaned

test_inputs = [
    "BUY NOW! DUMP IT! FED HAWKISH? TO THE MOON!",
    "INFORMATION OVERLOAD.",
    "CROWDPULSE. WEEKLY/DAILY WISDOM. CROWDMAP. PRO CROWD BARS.",
    "CROWDWISDOMTRADING.COM Find Your Signal.",
    "STOP DROWNING IN A SEA OF CONFLICTING MARKET NOISE AND CHAOS TODAY",
    "Consensus Entries • Verified Stops"
]

for t in test_inputs:
    print(f"Original: {t}")
    print(f"Cleaned:  {_clean_on_screen_text(t)}")
    print("-" * 40)


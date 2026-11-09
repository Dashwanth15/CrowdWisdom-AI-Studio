"""
CrowdWisdom AI Studio — Philippines Market Intelligence Profile
Evidence-based market intelligence, audience personas, regional dynamics,
and regulatory compliance frameworks for the Philippine retail trading and financial markets.
"""
from typing import Any, Dict, List

PHILIPPINES_MARKET_PROFILE: Dict[str, Any] = {
    "country_code": "PH",
    "country_name": "Philippines",
    "currency": {"code": "PHP", "symbol": "₱", "name": "Philippine Peso"},
    "timezone": "Asia/Manila",
    "market_hours": "09:30 - 15:00 PHT (Pre-open: 09:00 - 09:30 PHT)",

    # Financial Market Ecosystem
    "market_ecosystem": {
        "primary_exchanges": ["Philippine Stock Exchange (PSE)"],
        "benchmark_indices": ["PSEi (PSE Composite Index)", "All Shares Index", "PSE Financials", "PSE Property"],
        "market_structure": "Emerging retail market driven by mobile fintech democratisation. Over 1.9 million online stock trading accounts growing rapidly through digital wallet integrations.",
        "dominant_instruments": ["PSEi Equities & Dividend REITs", "Global US Equities (via fintech apps)", "Digital Asset / Crypto Crossover", "Mutual Funds/UITFs"],
        "key_domestic_platforms": ["COL Financial", "First Metro Securities", "BDO Securities", "DragonFi", "Philstocks", "GCash (GStocks)", "Maya (Maya Stocks)"],
    },

    # Core Audience Segments
    "audience_segments": [
        {
            "segment_id": "ph_active_equity_trader",
            "name": "Active PSE & Global US Equity Trader",
            "experience_level": "Intermediate to Advanced",
            "typical_age": "24-40",
            "primary_focus": ["PSEi Blue Chips & REITs", "High-growth US Tech Equities", "Technical Breakouts & Volume Flow"],
            "pain_points": [
                "Trapped by low liquidity in local small-cap stocks ('second-liners')",
                "Overwhelmed by noisy Facebook trading groups and unverified stock 'chismis' (rumors)",
                "Unable to identify where collective smart-money conviction sits before sudden pullbacks",
                "Struggles to balance local Philippine market hours with global US market swings",
            ],
            "content_preferences": "Real-time sentiment maps, crowd conviction levels, sector rotation breakdowns, objective data over rumors",
            "preferred_languages": ["Philippine English", "Taglish (Tagalog-English blend)"],
            "dominant_channels": ["Facebook Trading Groups", "YouTube", "Discord communities", "Viber/Telegram"],
        },
        {
            "segment_id": "ph_young_fintech_professional",
            "name": "Young Professional / Mobile-First FinEd Learner",
            "experience_level": "Beginner",
            "typical_age": "21-34",
            "primary_focus": ["Micro-investing via e-wallets (GCash/Maya)", "Dividend investing", "Building wealth beyond savings accounts"],
            "pain_points": [
                "Fear of falling for prevalent online investment scams and unregulated pyramiding schemes",
                "Lacking structured financial education in traditional schools",
                "Anxiety around market volatility and uncertainty on when to buy or sell",
            ],
            "content_preferences": "Approachable visual tutorials, relatable career-and-money storytelling, scam-prevention insights",
            "preferred_languages": ["Taglish", "Philippine English", "Tagalog"],
            "dominant_channels": ["TikTok (FinTok PH)", "Instagram", "YouTube Shorts", "Facebook Reels"],
        },
        {
            "segment_id": "ph_ofw_wealth_builder",
            "name": "OFW (Overseas Filipino Worker) Capital Allocator",
            "experience_level": "Beginner to Intermediate",
            "typical_age": "28-52",
            "primary_focus": ["Family retirement fund", "Passive dividend income in the Philippines", "Long-term capital preservation"],
            "pain_points": [
                "Working exhausting 12-14 hour shifts overseas with zero time to monitor live charts",
                "Remittance money squandered on family hype or predatory local schemes",
                "Demands proven, verifiable sentiment tools that can be reviewed in 60 seconds from anywhere in the world",
            ],
            "content_preferences": "Empathetic retirement narratives, weekly consensus briefings, clear risk management principles",
            "preferred_languages": ["Taglish", "Philippine English", "Tagalog", "Cebuano/Bisaya"],
            "dominant_channels": ["Facebook & Messenger", "YouTube", "Viber OFW Groups", "Zoom Webinars"],
        },
        {
            "segment_id": "ph_crypto_to_equity_crossover",
            "name": "Crypto-to-Equities Transitioner",
            "experience_level": "Intermediate",
            "typical_age": "22-35",
            "primary_focus": ["Diversifying volatile crypto gains into resilient equities", "Market sentiment velocity", "Algorithmic signals"],
            "pain_points": [
                "Burnt out by 24/7 crypto volatility and sudden rug-pulls",
                "Searching for traditional market consensus data that provides quantifiable conviction",
            ],
            "content_preferences": "Quantitative sentiment metrics, CrowdPulse momentum tracking, algorithmic risk-reward ratios",
            "preferred_languages": ["Philippine English", "Taglish"],
            "dominant_channels": ["Discord", "Twitter/X", "Telegram", "Reddit (r/PhInvest)"],
        },
        {
            "segment_id": "ph_provincial_emerging_investor",
            "name": "Provincial / Regional Emerging Investor",
            "experience_level": "Beginner",
            "typical_age": "25-45",
            "primary_focus": ["Localized wealth building outside NCR", "Agricultural & provincial business reinvestment", "Digital assets"],
            "pain_points": [
                "Geographic isolation from physical brokerage offices in Metro Manila",
                "Relies on mobile connectivity for all financial decision-making",
            ],
            "content_preferences": "Bite-sized mobile videos, relatable regional examples, step-by-step validation frameworks",
            "preferred_languages": ["Cebuano/Bisaya", "Taglish", "Tagalog", "Philippine English"],
            "dominant_channels": ["Facebook", "TikTok", "YouTube"],
        },
    ],

    # Regional & Demographic Dynamics
    "regional_intelligence": {
        "metropolitan_centers": [
            {"region": "Metro Manila (NCR)", "hubs": ["Makati CBD", "Bonifacio Global City (BGC)", "Ortigas Center", "Quezon City"], "cultural_context": "Core financial district, multinational corporations, sophisticated stock and crypto communities"},
            {"region": "Metro Cebu (Visayas)", "hubs": ["Cebu City", "Mandaue", "Cebu IT Park"], "cultural_context": "Rapidly expanding Southern economic powerhouse, entrepreneurial, strong Bisaya cultural identity"},
            {"region": "Metro Davao (Mindanao)", "hubs": ["Davao City"], "cultural_context": "Mindanao's commercial hub, agricultural-industrial wealth reinvested into financial assets"},
            {"region": "Central Luzon", "hubs": ["Clark Freeport", "Angeles", "San Fernando"], "cultural_context": "High overseas remittance density, real estate and retail investment growth"},
        ],
        "language_dynamics": {
            "primary_commercial": "Philippine English (Official business, institutional finance, banking)",
            "conversational_dominant": "Taglish (Essential for marketing: organic code-switching between Tagalog and English, creates instant trust and rapport)",
            "regional_native": "Tagalog / Filipino (National language), Cebuano / Bisaya (Widely spoken across Visayas and Mindanao)",
        },
    },

    # Marketing, Creative, and Narrative Hooks
    "marketing_intelligence": {
        "platforms": {
            "Facebook": {"role": "The primary digital town square; central hub for trading communities, live streams, and discussion groups", "format": "Feed videos (1:1 & 16:9), live commentary, community posts"},
            "TikTok": {"role": "High-growth discovery channel for young professionals and Gen Z", "format": "9:16 vertical short-form (15-60s), punchy hook in first 2 seconds"},
            "YouTube": {"role": "Primary long-form educational platform for in-depth chart reviews and tutorials", "format": "10-20 min tutorials and 60s Shorts"},
            "Viber/Telegram": {"role": "High-trust private investor groups and daily morning market alerts", "format": "Bullet-point market cards, sentiment snapshots"},
        },
        "creative_angles": [
            {
                "angle_name": "The Anti-Chismis Protocol",
                "core_narrative": "A Filipino trader stops gambling on social media rumors ('chismis') and replaces emotional trading with verified crowd consensus.",
                "opening_hook": "In Philippine stock groups, everyone has 'chismis' on the next breakout. But while retail trades on rumors, smart capital trades on verified consensus.",
                "cultural_reference": "Rejecting Facebook group rumors in favor of data-backed collective wisdom ('Bayanihan ng datos').",
            },
            {
                "angle_name": "The 6:00 AM BGC Sunrise Protocol",
                "core_narrative": "Calm morning coffee in Bonifacio Global City before the 9:30 AM PSE opening bell, analyzing sentiment velocity with CrowdPulse.",
                "opening_hook": "Dawn lighting across the skyscrapers of BGC. 9:15 AM. Before the Philippine Stock Exchange opens, I take sixty seconds with CrowdPulse.",
                "cultural_reference": "Minimalist modern professional morning routine in BGC or Makati.",
            },
            {
                "angle_name": "The OFW Hard-Earned Edge",
                "core_narrative": "An OFW worker in Dubai or Singapore protecting family remittances from hype cycles by using visual crowd maps.",
                "opening_hook": "You work 14 hours a day overseas sending remittances back to Manila. Don't let your hard-earned capital get trapped in social media hype.",
                "cultural_reference": "OFW sacrifice, protecting hard-earned family savings through disciplined tools.",
            },
            {
                "angle_name": "Diskarte Backed by Data",
                "core_narrative": "Elevating the Filipino spirit of 'diskarte' (resourceful problem solving) from street smarts to data-driven institutional intelligence.",
                "opening_hook": "In the Philippines, we take pride in our 'diskarte'. But in modern financial markets, the ultimate diskarte is having real-time data on where the crowd stands.",
                "cultural_reference": "Filipino 'diskarte' combined with mathematical precision.",
            },
        ],
        "local_terminology": [
            "PSEi", "Philippine Stock Exchange", "BGC", "Makati CBD", "Ayala", "Blue Chips",
            "Second-liners", "Chismis", "Diskarte", "Bayanihan", "OFW", "Remittance", "Piso (₱)",
            "GStocks", "Market opening 9:30 AM", "Dividend Yield", "PhInvest"
        ],
        "voiceover_specifications": {
            "locale": "en-PH",
            "recommended_voices": [
                {"voice_id": "en-PH-JamesNeural", "gender": "Male", "tone": "Warm, confident, articulate Philippine English narrator with professional cadence"},
                {"voice_id": "en-PH-RosaNeural", "gender": "Female", "tone": "Engaging, calm, trustworthy market commentator"},
            ],
            "pacing": "Moderate (140-155 WPM), friendly, accessible, conversational cadence without harsh technical jargon",
        },
    },

    # Strict Regulatory Safeguards (SEC Philippines)
    "regulatory_safeguards": {
        "regulator": "Securities and Exchange Commission of the Philippines (SEC Philippines)",
        "applicable_regulations": [
            "Securities Regulation Code (SRC - Republic Act No. 8799)",
            "SEC Memorandum Circulars on Public Solicitations and Unregistered Investment Schemes",
            "SRC Rule 56 on Registration of Investment Advisers and Advertising Conduct",
        ],
        "mandatory_disclaimers": [
            "Trading and investing in securities involves market risks and price fluctuations. Past performance is not indicative of future results.",
            "CrowdWisdomTrading is an analytical research and financial education technology platform. It is not an SEC-registered investment adviser or broker-dealer, and does not solicit investments or guarantee trading profits.",
        ],
        "strictly_prohibited_terms": [
            "guaranteed profit", "guaranteed income", "100% risk-free", "sure win",
            "passive income guarantee", "get rich quick", "surefire returns", "pyramid",
            "secret payout", "instant millionaire"
        ],
        "required_labeling": "For Financial Education & Market Sentiment Research Only",
    },
}


def get_philippines_market_profile() -> Dict[str, Any]:
    """Returns a deep copy of the Philippines Market Profile."""
    import copy
    return copy.deepcopy(PHILIPPINES_MARKET_PROFILE)

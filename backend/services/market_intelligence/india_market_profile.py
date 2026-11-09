"""
CrowdWisdom AI Studio — India Market Intelligence Profile
Evidence-based market intelligence, audience personas, regional dynamics,
and regulatory compliance frameworks for the Indian retail trading and financial markets.
"""
from typing import Any, Dict, List

INDIA_MARKET_PROFILE: Dict[str, Any] = {
    "country_code": "IN",
    "country_name": "India",
    "currency": {"code": "INR", "symbol": "₹", "name": "Indian Rupee"},
    "timezone": "Asia/Kolkata",
    "market_hours": "09:15 - 15:30 IST (Pre-market: 09:00 - 09:08 IST)",
    
    # Financial Market Ecosystem
    "market_ecosystem": {
        "primary_exchanges": ["National Stock Exchange (NSE)", "Bombay Stock Exchange (BSE)"],
        "benchmark_indices": ["Nifty 50", "Nifty Bank (Bank Nifty)", "BSE Sensex", "FinNifty"],
        "market_structure": "World's highest volume in equity index options (derivatives). Over 150 million registered demat accounts across CDSL and NSDL.",
        "dominant_instruments": ["Index Options (Nifty/BankNifty weekly contracts)", "Large & Mid-Cap Equities", "Mutual Funds/SIPs", "SME IPOs"],
        "key_domestic_platforms": ["Zerodha", "Groww", "Angel One", "Upstox", "ICICI Direct", "HDFC Sky"],
    },

    # Core Audience Segments
    "audience_segments": [
        {
            "segment_id": "in_options_derivative_trader",
            "name": "Active F&O / Index Options Trader",
            "experience_level": "Intermediate to Advanced",
            "typical_age": "24-42",
            "primary_focus": ["Nifty & Bank Nifty weekly options", "Intraday momentum", "Volatility spikes"],
            "pain_points": [
                "Overwhelmed by conflicting Telegram tip channels and fake P&L screenshots",
                "Revenge trading and emotional capital destruction on expiry days",
                "Lacking objective consensus data on where institutional order flow and market sentiment sit",
                "Suffering from severe whiplash in attention during volatile RBI policy or earnings days",
            ],
            "content_preferences": "Data-heavy visual heatmaps, consensus levels, stop-loss cluster maps, pre-market 60-second briefings",
            "preferred_languages": ["Indian English", "Hinglish", "Hindi"],
            "dominant_channels": ["YouTube Finance", "Twitter/X (FinTwit India)", "Telegram", "Instagram Reels"],
        },
        {
            "segment_id": "in_beginner_retail_investor",
            "name": "Aspirational Retail Investor / FinEd Learner",
            "experience_level": "Beginner to Novice",
            "typical_age": "20-32",
            "primary_focus": ["Bluechip stocks", "Mutual Fund SIPs", "Learning market fundamentals without gambling"],
            "pain_points": [
                "Intimidated by technical jargon, complex Greeks, and contradictory financial news",
                "Fear of losing hard-earned savings after seeing peers lose money in derivatives",
                "Unable to distinguish credible financial education from predatory get-rich-quick schemes",
            ],
            "content_preferences": "Relatable storytelling, visual explanations of market psychology, disciplined habit building",
            "preferred_languages": ["Hinglish", "Hindi", "Indian English", "Tamil", "Telugu", "Marathi"],
            "dominant_channels": ["Instagram Reels", "YouTube Shorts & Long-form", "Spotify Podcasts"],
        },
        {
            "segment_id": "in_disciplined_swing_trader",
            "name": "Disciplined Equity Swing Trader",
            "experience_level": "Intermediate",
            "typical_age": "28-48",
            "primary_focus": ["Nifty 500 equities", "Sectoral rotation", "Multi-day breakout setups"],
            "pain_points": [
                "Lack of time to monitor 500 stocks while working a full-time corporate job",
                "Missing early momentum shifts before the financial media reports them",
                "Difficulty gauging whether retail hype matches smart-money conviction",
            ],
            "content_preferences": "Actionable sector heatmaps, 30-day sentiment trajectory, clear multi-day consensus plans",
            "preferred_languages": ["Indian English", "Hinglish"],
            "dominant_channels": ["LinkedIn", "Twitter/X", "YouTube", "Trading Communities"],
        },
        {
            "segment_id": "in_tier2_tier3_emerging_investor",
            "name": "Tier-2/3 City Emerging Wealth Builder",
            "experience_level": "Beginner to Intermediate",
            "typical_age": "22-40",
            "primary_focus": ["Systematic equity wealth creation", "Localized stock discussions", "Mobile-first trading"],
            "pain_points": [
                "Limited access to institutional-quality trading tools in vernacular languages",
                "High vulnerability to unauthorized localized advisory networks",
                "Requires clear, simplified signals on mobile screens",
            ],
            "content_preferences": "Mobile-native vertical video, clear visual indicators, culturally grounded real-world metaphors",
            "preferred_languages": ["Hindi", "Hinglish", "Gujarati", "Marathi", "Bengali"],
            "dominant_channels": ["YouTube", "Instagram", "WhatsApp / Telegram channels"],
        },
        {
            "segment_id": "in_nri_global_investor",
            "name": "NRI (Non-Resident Indian) Wealth Allocator",
            "experience_level": "Intermediate to Advanced",
            "typical_age": "30-55",
            "primary_focus": ["Long-term India growth story", "NRE/NRO equity portfolios", "Macro sentiment tracking"],
            "pain_points": [
                "Living across time zones (Gulf, US, Singapore, UK) unable to track intraday Indian market moves",
                "Needing a consolidated summary of India market sentiment before opening trade positions",
            ],
            "content_preferences": "High-level macro synthesis, weekly consensus briefings, institutional-grade analytics",
            "preferred_languages": ["Global English", "Indian English"],
            "dominant_channels": ["LinkedIn", "YouTube", "Email Substack / Newsletters"],
        },
    ],

    # Regional & Demographic Dynamics
    "regional_intelligence": {
        "tier_1_metros": [
            {"city": "Mumbai", "region": "Maharashtra", "cultural_context": "Financial capital, deep Dalal Street equity culture, high risk tolerance"},
            {"city": "Bengaluru", "region": "Karnataka", "cultural_context": "Tech corridors, algorithmic and data-driven retail trading community"},
            {"city": "Delhi NCR", "region": "North India", "cultural_context": "High volume derivatives trading, entrepreneurial risk appetite"},
            {"city": "Hyderabad", "region": "Telangana", "cultural_context": "Rapidly growing tech and retail investor demographic"},
            {"city": "Chennai", "region": "Tamil Nadu", "cultural_context": "Conservative, value-driven equity and long-term dividend mindset"},
        ],
        "tier_2_3_growth_hubs": [
            {"city": "Ahmedabad & Surat", "region": "Gujarat", "cultural_context": "Pioneering trading culture, immense derivatives and equity participation"},
            {"city": "Pune", "region": "Maharashtra", "cultural_context": "Young IT workforce and students entering capital markets"},
            {"city": "Jaipur & Indore", "region": "Central/North India", "cultural_context": "Rapidly growing demat adoption, business-family retail investors"},
            {"city": "Kochi & Coimbatore", "region": "South India", "cultural_context": "High literacy, expanding direct equity and SIP penetration"},
        ],
        "language_dynamics": {
            "primary_commercial": "Indian English (Professional, tech-savvy)",
            "conversational_dominant": "Hinglish (Crucial for high conversion: conversational blend of Hindi and English)",
            "vernacular_growth": "Hindi (North/Central), Gujarati (Western trading belt), Tamil & Telugu (Southern tech belts)",
        },
    },

    # Marketing, Creative, and Narrative Hooks
    "marketing_intelligence": {
        "platforms": {
            "YouTube": {"role": "Primary deep-dive educational and pre-market analysis destination", "format": "Long-form 8-15 min and Shorts 30-60s"},
            "Instagram": {"role": "Top discovery channel for millennials and Gen Z", "format": "9:16 vertical video reels, hook-driven in first 2 seconds"},
            "Telegram/WhatsApp": {"role": "Community discussion, alerting, and daily morning briefings", "format": "Concise text summaries and visual cards"},
            "Twitter/FinTwit": {"role": "Real-time market reaction, sentiment debates, chart analysis", "format": "Short clips, data cards, threads"},
        },
        "creative_angles": [
            {
                "angle_name": "The Anti-Tipster Epiphany",
                "core_narrative": "A trader stops drowning in 50 noisy Telegram channels and switches to mathematical crowd consensus.",
                "opening_hook": "At 9:00 AM on Dalal Street, 40 Telegram tipsters will give you 40 contradictory trades. Here is how disciplined traders cut through the noise.",
                "cultural_reference": "Nifty pre-market opening, cutting the noise of chaotic messaging groups.",
            },
            {
                "angle_name": "The 60-Second Morning Chai Protocol",
                "core_narrative": "Minimalist pre-market routine: sipping cutting chai while CrowdPulse summarizes 30-day sentiment velocity before the 9:15 bell.",
                "opening_hook": "Steam rising from a morning chai in Mumbai. 9:14 AM. In sixty seconds, you know where real market conviction is positioned.",
                "cultural_reference": "Morning chai, calm focus before market opening bell.",
            },
            {
                "angle_name": "The SEBI 93% Reality Check",
                "core_narrative": "Acknowledging the official SEBI statistic that retail derivatives traders lose money on emotions, positioning CrowdWisdom as the disciplined consensus compass.",
                "opening_hook": "SEBI proved that 9 out of 10 retail traders lose money to emotional bias. The 10% who survive never trade on sentiment they can't verify.",
                "cultural_reference": "Rigorous data over emotional gambling.",
            },
            {
                "angle_name": "The CrowdMap Expiry Defense",
                "core_narrative": "Demonstrating how weekly expiry volatility wipes out retail stop-losses, and how CrowdMap visualizes collective price clusters.",
                "opening_hook": "Weekly expiry day. Nifty swings 200 points in three minutes. Do you know where the crowd's stop-losses are clustered?",
                "cultural_reference": "Zero-to-Hero expiry trap avoidance.",
            },
        ],
        "local_terminology": [
            "Dalal Street", "Nifty 50", "Bank Nifty", "Expiry Day", "Demat Account",
            "F&O", "Stop-loss", "Multi-bagger", "Pre-market 9:15 bell", "Support and Resistance",
            "Retail Quota", "Chai and Charts", "Option Greeks"
        ],
        "voiceover_specifications": {
            "locale": "en-IN",
            "recommended_voices": [
                {"voice_id": "en-IN-PrabhatNeural", "gender": "Male", "tone": "Confident, authoritative, intellectual financial narrator"},
                {"voice_id": "en-IN-NeerjaNeural", "gender": "Female", "tone": "Articulate, calm, professional market anchor"},
            ],
            "pacing": "Moderate-fast (145-160 WPM), crisp articulation, natural Indian cadence without exaggerated theatricality",
        },
    },

    # Strict Regulatory Safeguards (SEBI Advertising Code)
    "regulatory_safeguards": {
        "regulator": "Securities and Exchange Board of India (SEBI)",
        "applicable_regulations": [
            "SEBI Code of Conduct for Advertisements (Circular SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2023/43)",
            "SEBI Research Analyst (RA) and Investment Adviser (IA) Regulations",
            "Advertising Standards Council of India (ASCI) Guidelines for Virtual and Financial Products",
        ],
        "mandatory_disclaimers": [
            "Investment in securities market are subject to market risks. Read all the related documents carefully before investing.",
            "CrowdWisdomTrading is an analytical market sentiment research and educational tool. It does not provide SEBI-registered investment advice or guaranteed return recommendations.",
        ],
        "strictly_prohibited_terms": [
            "guaranteed return", "guaranteed profit", "100% win rate", "risk-free trade",
            "surefire call", "jackpot trade", "double your money", "become rich quick",
            "insider tips", "sure jackpot"
        ],
        "required_labeling": "Educational and Analytical Sentiment Research Only",
    },
}


def get_india_market_profile() -> Dict[str, Any]:
    """Returns a deep copy of the India Market Profile."""
    import copy
    return copy.deepcopy(INDIA_MARKET_PROFILE)


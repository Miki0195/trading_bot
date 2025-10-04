"""
Configuration Example
Copy this file and modify the constants in trading_bot.py directly,
or use this as a reference for different trading scenarios.
"""

# =============================================================================
# EXAMPLE CONFIGURATIONS
# =============================================================================

# CONSERVATIVE SETUP (Lower risk, smaller positions)
CONSERVATIVE = {
    "LOT_SIZE": 0.01,
    "TP_UNITS": 8.0,  # 80 pips
    "SCALE_LEVELS": [0.75, 0.50],  # Only 2 scale levels
}

# AGGRESSIVE SETUP (Higher risk, larger positions)
AGGRESSIVE = {
    "LOT_SIZE": 0.5,
    "TP_UNITS": 3.0,  # 30 pips
    "SCALE_LEVELS": [0.75, 0.50, 0.25, 0.10],  # 4 scale levels
}

# EUROPEAN HOURS (Different time zones)
EUROPEAN_HOURS = {
    "MORNING_RANGE_START": "08:00",
    "MORNING_RANGE_END": "08:15",
    "MORNING_ENTRY_START": "08:20",
    "AFTERNOON_RANGE_START": "14:30",
    "AFTERNOON_RANGE_END": "14:45",
    "AFTERNOON_ENTRY_START": "14:50",
}

# ASIAN SESSION
ASIAN_SESSION = {
    "MORNING_RANGE_START": "01:00",
    "MORNING_RANGE_END": "01:15",
    "MORNING_ENTRY_START": "01:20",
    "AFTERNOON_RANGE_START": "07:00",
    "AFTERNOON_RANGE_END": "07:15",
    "AFTERNOON_ENTRY_START": "07:20",
}

# MULTIPLE SYMBOLS (Run separate instances)
SYMBOLS_EXAMPLES = {
    "FOREX_MAJORS": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF"],
    "FOREX_MINORS": ["EURJPY", "GBPJPY", "EURGBP"],
    "INDICES": ["US30", "US500", "NAS100"],
    "GOLD": ["XAUUSD"],
}

# TIMEFRAME VARIATIONS
TIMEFRAME_OPTIONS = {
    "M1": "mt5.TIMEFRAME_M1",   # 1-minute (faster, more signals)
    "M5": "mt5.TIMEFRAME_M5",   # 5-minute (default)
    "M15": "mt5.TIMEFRAME_M15", # 15-minute (slower, fewer signals)
    "M30": "mt5.TIMEFRAME_M30", # 30-minute
}

# RISK MANAGEMENT EXAMPLES
RISK_MANAGEMENT = {
    "MICRO_ACCOUNT": {
        "LOT_SIZE": 0.01,
        "MAX_SLIPPAGE": 10,
    },
    "MINI_ACCOUNT": {
        "LOT_SIZE": 0.1,
        "MAX_SLIPPAGE": 20,
    },
    "STANDARD_ACCOUNT": {
        "LOT_SIZE": 1.0,
        "MAX_SLIPPAGE": 30,
    },
}

# =============================================================================
# BROKER-SPECIFIC ADJUSTMENTS
# =============================================================================

# For 3-digit brokers (e.g., some JPY pairs)
BROKER_3_DIGIT = {
    "TP_UNITS": 0.58,  # Adjust for different pip calculation
}

# For 5-digit brokers (most modern brokers)
BROKER_5_DIGIT = {
    "TP_UNITS": 5.8,  # Standard setting
}

# =============================================================================
# TESTING CONFIGURATIONS
# =============================================================================

# DEMO/BACKTEST MODE (Faster polling for testing)
TESTING = {
    "POLL_INTERVAL": 5,  # Check every 5 seconds
    "LOT_SIZE": 0.01,  # Small positions for testing
}

# LIVE PRODUCTION MODE
PRODUCTION = {
    "POLL_INTERVAL": 10,  # Standard 10 seconds
    "LOT_SIZE": 0.1,  # Adjust based on account size
}


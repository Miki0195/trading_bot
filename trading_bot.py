"""
MetaTrader5 Trading Bot - Range Breakout Strategy with Scaling
Production-ready implementation with vectorized operations
"""

import MetaTrader5 as mt5
import numpy as np
import pandas as pd
from datetime import datetime, time, timedelta
import logging
from typing import Tuple, Optional, Dict, List
import time as time_module

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

# Trading Parameters
SYMBOL = "XAUUSD"  # Trading instrument
LOT_SIZE = 0.1  # Standard lot size for entries
TP_UNITS = 5.8  # Take profit distance in units (58 pips for 5-digit broker)
MAGIC_NUMBER = 234567  # Unique identifier for bot's orders

# Range Definition Times
MORNING_RANGE_START = time(12, 0)  # Morning range start
MORNING_RANGE_END = time(12, 15)  # Morning range end (exclusive)
AFTERNOON_RANGE_START = time(18, 30)  # Afternoon range start
AFTERNOON_RANGE_END = time(18, 45)  # Afternoon range end (exclusive)x

# Entry Timing
MORNING_ENTRY_START = time(12, 15)  # Earliest morning entry
MORNING_ENTRY_CUTOFF = time(18, 29)  # No new morning entries after this
AFTERNOON_ENTRY_START = time(18, 45)  # Earliest afternoon entry
AFTERNOON_EXIT_TIME = time(23, 55)  # Force close all afternoon trades

# Scaling Levels (pullback percentages into the range)
SCALE_LEVELS = [0.75, 0.50, 0.25]  # 75%, 50%, 25% retracement levels

# Bot Settings
TIMEFRAME = mt5.TIMEFRAME_M5  # 5-minute candles
POLL_INTERVAL = 10  # Seconds between checks
MAX_SLIPPAGE = 20  # Maximum slippage in points

# Logging Configuration
LOG_FILE = "trading_bot.log"
LOG_LEVEL = logging.INFO

# =============================================================================
# LOGGING SETUP
# =============================================================================

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# GLOBAL STATE MANAGEMENT
# =============================================================================

class TradingState:
    """Manages the current state of the trading bot"""
    def __init__(self):
        self.morning_range: Optional[Dict] = None
        self.afternoon_range: Optional[Dict] = None
        self.morning_breakout: Optional[Dict] = None
        self.afternoon_breakout: Optional[Dict] = None
        self.morning_reversal_count: int = 0
        self.afternoon_reversal_count: int = 0
        self.morning_scale_levels: List[float] = []
        self.afternoon_scale_levels: List[float] = []
        self.morning_positions: List[int] = []  # Ticket numbers
        self.afternoon_positions: List[int] = []
        
    def reset_morning(self):
        """Reset morning session state"""
        self.morning_range = None
        self.morning_breakout = None
        self.morning_reversal_count = 0
        self.morning_scale_levels = []
        self.morning_positions = []
        
    def reset_afternoon(self):
        """Reset afternoon session state"""
        self.afternoon_range = None
        self.afternoon_breakout = None
        self.afternoon_reversal_count = 0
        self.afternoon_scale_levels = []
        self.afternoon_positions = []

state = TradingState()

# =============================================================================
# MT5 CONNECTION AND INITIALIZATION
# =============================================================================

def initialize_mt5() -> bool:
    """Initialize MetaTrader5 connection"""
    if not mt5.initialize():
        logger.error(f"MT5 initialization failed: {mt5.last_error()}")
        return False
    
    logger.info(f"MT5 initialized successfully. Version: {mt5.version()}")
    
    # Check if symbol is available
    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        logger.error(f"Symbol {SYMBOL} not found")
        return False
    
    if not symbol_info.visible:
        if not mt5.symbol_select(SYMBOL, True):
            logger.error(f"Failed to select {SYMBOL}")
            return False
    
    logger.info(f"Symbol {SYMBOL} selected and ready")
    return True

def shutdown_mt5():
    """Safely shutdown MT5 connection"""
    mt5.shutdown()
    logger.info("MT5 connection closed")

# =============================================================================
# DATA RETRIEVAL AND PROCESSING
# =============================================================================

def get_candles(symbol: str, timeframe: int, count: int = 100) -> Optional[np.ndarray]:
    """
    Retrieve historical candles using vectorized operations
    
    Args:
        symbol: Trading symbol
        timeframe: MT5 timeframe constant
        count: Number of candles to retrieve
        
    Returns:
        Structured numpy array with OHLC data or None on error
    """
    try:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None or len(rates) == 0:
            logger.error(f"Failed to get candles: {mt5.last_error()}")
            return None
        
        # Convert to numpy structured array for efficient operations
        return rates
        
    except Exception as e:
        logger.error(f"Error retrieving candles: {e}")
        return None

def candles_to_dataframe(candles: np.ndarray) -> pd.DataFrame:
    """Convert candles to pandas DataFrame for analysis"""
    df = pd.DataFrame(candles)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

# =============================================================================
# RANGE CALCULATION
# =============================================================================

def get_range(candles: np.ndarray, start_time: time, end_time: time, 
              current_date: datetime.date) -> Optional[Dict]:
    """
    Calculate the high/low range for the setup box using vectorized operations
    
    Args:
        candles: Numpy array of OHLC data
        start_time: Range start time
        end_time: Range end time (exclusive)
        current_date: Current trading date
        
    Returns:
        Dictionary with 'high', 'low', 'time_start', 'time_end' or None
    """
    try:
        df = candles_to_dataframe(candles)
        
        # Create datetime objects for filtering
        start_dt = datetime.combine(current_date, start_time)
        end_dt = datetime.combine(current_date, end_time)
        
        # Filter candles in range window (vectorized)
        mask = (df['time'] >= start_dt) & (df['time'] < end_dt)
        range_candles = df[mask]
        
        if len(range_candles) < 3:
            logger.warning(f"Insufficient candles for range: {len(range_candles)}")
            return None
        
        # Vectorized high/low calculation
        range_high = range_candles['high'].max()
        range_low = range_candles['low'].min()
        
        range_info = {
            'high': range_high,
            'low': range_low,
            'time_start': start_dt,
            'time_end': end_dt,
            'candles': len(range_candles)
        }
        
        logger.info(f"Range calculated: High={range_high:.5f}, Low={range_low:.5f}, Candles={len(range_candles)}")
        return range_info
        
    except Exception as e:
        logger.error(f"Error calculating range: {e}")
        return None

# =============================================================================
# BREAKOUT DETECTION
# =============================================================================

def check_breakout(candles: np.ndarray, range_info: Dict, 
                   entry_start_time: time, current_date: datetime.date) -> Optional[Dict]:
    """
    Detect breakout candle and direction using vectorized operations
    
    Args:
        candles: Numpy array of OHLC data
        range_info: Dictionary with range high/low
        entry_start_time: Earliest time for breakout detection
        current_date: Current trading date
        
    Returns:
        Dictionary with 'direction', 'price', 'time' or None
    """
    try:
        df = candles_to_dataframe(candles)
        
        # Filter candles after entry start time
        entry_dt = datetime.combine(current_date, entry_start_time)
        mask = df['time'] >= entry_dt
        entry_candles = df[mask]
        
        if len(entry_candles) == 0:
            return None
        
        range_high = range_info['high']
        range_low = range_info['low']
        
        # Vectorized breakout detection
        # Buy breakout: close above range high
        buy_breakout_mask = entry_candles['close'] > range_high
        # Sell breakout: close below range low
        sell_breakout_mask = entry_candles['close'] < range_low
        
        # Find first breakout
        buy_breakouts = entry_candles[buy_breakout_mask]
        sell_breakouts = entry_candles[sell_breakout_mask]
        
        first_buy = buy_breakouts.iloc[0] if len(buy_breakouts) > 0 else None
        first_sell = sell_breakouts.iloc[0] if len(sell_breakouts) > 0 else None
        
        # Determine which came first
        if first_buy is not None and first_sell is not None:
            if first_buy['time'] < first_sell['time']:
                direction = 'BUY'
                breakout_candle = first_buy
            else:
                direction = 'SELL'
                breakout_candle = first_sell
        elif first_buy is not None:
            direction = 'BUY'
            breakout_candle = first_buy
        elif first_sell is not None:
            direction = 'SELL'
            breakout_candle = first_sell
        else:
            return None
        
        breakout_info = {
            'direction': direction,
            'price': float(breakout_candle['close']),
            'time': breakout_candle['time'],
            'candle_high': float(breakout_candle['high']),
            'candle_low': float(breakout_candle['low'])
        }
        
        logger.info(f"Breakout detected: {direction} at {breakout_info['price']:.5f} @ {breakout_candle['time']}")
        return breakout_info
        
    except Exception as e:
        logger.error(f"Error checking breakout: {e}")
        return None

# =============================================================================
# POSITION MANAGEMENT
# =============================================================================

def get_symbol_info() -> Optional[Dict]:
    """Get symbol trading information"""
    info = mt5.symbol_info(SYMBOL)
    if info is None:
        return None
    
    return {
        'point': info.point,
        'digits': info.digits,
        'trade_contract_size': info.trade_contract_size,
        'volume_min': info.volume_min,
        'volume_max': info.volume_max,
        'volume_step': info.volume_step
    }

def open_position(direction: str, lot_size: float, tp_price: float, 
                  comment: str = "") -> Optional[int]:
    """
    Open a position with specified parameters
    
    Args:
        direction: 'BUY' or 'SELL'
        lot_size: Position size in lots
        tp_price: Take profit price
        comment: Order comment for tracking
        
    Returns:
        Order ticket number or None on failure
    """
    try:
        symbol_info = get_symbol_info()
        if symbol_info is None:
            logger.error("Failed to get symbol info")
            return None
        
        # Determine order type and price
        if direction == 'BUY':
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(SYMBOL).ask
        else:
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(SYMBOL).bid
        
        if price is None:
            logger.error("Failed to get current price")
            return None
        
        # Prepare request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": lot_size,
            "type": order_type,
            "price": price,
            "tp": round(tp_price, symbol_info['digits']),
            "deviation": MAX_SLIPPAGE,
            "magic": MAGIC_NUMBER,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send order
        result = mt5.order_send(request)
        
        if result is None:
            logger.error(f"Order send failed: {mt5.last_error()}")
            return None
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.retcode} - {result.comment}")
            return None
        
        logger.info(f"Position opened: {direction} {lot_size} lots @ {price:.5f}, TP={tp_price:.5f}, Ticket={result.order}")
        return result.order
        
    except Exception as e:
        logger.error(f"Error opening position: {e}")
        return None

def close_position(ticket: int) -> bool:
    """
    Close a specific position by ticket
    
    Args:
        ticket: Position ticket number
        
    Returns:
        True if closed successfully, False otherwise
    """
    try:
        # Get position info
        position = mt5.positions_get(ticket=ticket)
        if position is None or len(position) == 0:
            logger.warning(f"Position {ticket} not found")
            return False
        
        position = position[0]
        
        # Determine close parameters
        if position.type == mt5.ORDER_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(SYMBOL).bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(SYMBOL).ask
        
        if price is None:
            logger.error("Failed to get closing price")
            return False
        
        # Prepare close request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": position.volume,
            "type": order_type,
            "position": ticket,
            "price": price,
            "deviation": MAX_SLIPPAGE,
            "magic": MAGIC_NUMBER,
            "comment": "Close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Failed to close position {ticket}: {result.comment if result else mt5.last_error()}")
            return False
        
        logger.info(f"Position closed: Ticket={ticket} @ {price:.5f}")
        return True
        
    except Exception as e:
        logger.error(f"Error closing position {ticket}: {e}")
        return False

def close_all_positions(session: str = "ALL") -> int:
    """
    Close all positions (optionally filtered by session)
    
    Args:
        session: 'MORNING', 'AFTERNOON', or 'ALL'
        
    Returns:
        Number of positions closed
    """
    try:
        positions = mt5.positions_get(symbol=SYMBOL)
        if positions is None or len(positions) == 0:
            return 0
        
        closed_count = 0
        
        for position in positions:
            if position.magic != MAGIC_NUMBER:
                continue
            
            # Filter by session if needed
            if session == "MORNING" and position.ticket not in state.morning_positions:
                continue
            if session == "AFTERNOON" and position.ticket not in state.afternoon_positions:
                continue
            
            if close_position(position.ticket):
                closed_count += 1
        
        logger.info(f"Closed {closed_count} {session} positions")
        return closed_count
        
    except Exception as e:
        logger.error(f"Error closing all positions: {e}")
        return 0

# =============================================================================
# SCALING LOGIC
# =============================================================================

def calculate_scale_levels(range_info: Dict, direction: str, is_reversal: bool = False) -> List[float]:
    """
    Calculate scaling entry prices using vectorized operations
    
    Args:
        range_info: Dictionary with range high/low
        direction: 'BUY' or 'SELL'
        is_reversal: If True, only use 50% level for scaling
        
    Returns:
        List of price levels for scaling entries
    """
    range_high = range_info['high']
    range_low = range_info['low']
    range_size = range_high - range_low
    
    # For reversal trades, only scale at 50%
    # For initial breakout, scale at 75%, 50%, 25%
    if is_reversal:
        percentages = np.array([0.50])  # Only 50% level on reversal
    else:
        percentages = np.array(SCALE_LEVELS)  # All levels on initial breakout
    
    if direction == 'BUY':
        # For buy, scale levels are below range high going down
        levels = range_high - (percentages * range_size)
    else:
        # For sell, scale levels are above range low going up
        levels = range_low + (percentages * range_size)
    
    return levels.tolist()

def check_and_execute_scaling(candles: np.ndarray, range_info: Dict, 
                               breakout_info: Dict, scale_levels: List[float],
                               session: str) -> List[float]:
    """
    Check if price has hit any scale levels and execute entries
    
    Args:
        candles: Numpy array of OHLC data
        range_info: Range information
        breakout_info: Breakout information
        scale_levels: List of remaining scale levels to check
        session: 'MORNING' or 'AFTERNOON'
        
    Returns:
        Updated list of remaining scale levels
    """
    try:
        if not scale_levels:
            return scale_levels
        
        # Get latest candle
        latest_candle = candles[-1]
        candle_high = latest_candle['high']
        candle_low = latest_candle['low']
        direction = breakout_info['direction']
        
        # Calculate TP
        tp_price = calculate_tp(breakout_info)
        
        # Determine if we're in a reversal trade (use 2x lot size)
        if session == 'MORNING':
            is_reversal_trade = state.morning_reversal_count >= 1
        else:
            is_reversal_trade = state.afternoon_reversal_count >= 1
        
        # Use double lot size for reversal trades
        lot_size = LOT_SIZE * 2 if is_reversal_trade else LOT_SIZE
        
        # Check each scale level (vectorized)
        remaining_levels = []
        scale_levels_array = np.array(scale_levels)
        
        for level in scale_levels:
            triggered = False
            
            if direction == 'BUY':
                # For buy, trigger when candle LOW touches or goes below the level
                if candle_low <= level:
                    triggered = True
            else:
                # For sell, trigger when candle HIGH touches or goes above the level
                if candle_high >= level:
                    triggered = True
            
            if triggered:
                # Execute scale-in entry
                ticket = open_position(
                    direction=direction,
                    lot_size=lot_size,
                    tp_price=tp_price,
                    comment=f"{session}_SCALE_{level:.5f}"
                )
                
                if ticket:
                    if session == 'MORNING':
                        state.morning_positions.append(ticket)
                    else:
                        state.afternoon_positions.append(ticket)
                    
                    logger.info(f"Scale-in executed at {level:.5f} for {session} session")
            else:
                remaining_levels.append(level)
        
        return remaining_levels
        
    except Exception as e:
        logger.error(f"Error in scaling logic: {e}")
        return scale_levels

# =============================================================================
# REVERSAL MANAGEMENT
# =============================================================================

def check_reversal(candles: np.ndarray, range_info: Dict, 
                   breakout_info: Dict) -> Optional[str]:
    """
    Check if a reversal has occurred (opposite breakout)
    
    Args:
        candles: Numpy array of OHLC data
        range_info: Range information
        breakout_info: Current breakout information
        
    Returns:
        'BUY' or 'SELL' if reversal detected, None otherwise
    """
    try:
        latest_candle = candles[-1]
        close_price = latest_candle['close']
        current_direction = breakout_info['direction']
        
        range_high = range_info['high']
        range_low = range_info['low']
        
        # Check for opposite breakout
        if current_direction == 'BUY':
            # Check if price broke below range low
            if close_price < range_low:
                logger.info(f"REVERSAL DETECTED: Price broke below {range_low:.5f}")
                return 'SELL'
        else:
            # Check if price broke above range high
            if close_price > range_high:
                logger.info(f"REVERSAL DETECTED: Price broke above {range_high:.5f}")
                return 'BUY'
        
        return None
        
    except Exception as e:
        logger.error(f"Error checking reversal: {e}")
        return None

def handle_reversal(new_direction: str, range_info: Dict, candles: np.ndarray,
                    session: str) -> Optional[Dict]:
    """
    Handle reversal: close all positions and optionally open new ones
    
    Args:
        new_direction: New direction ('BUY' or 'SELL')
        range_info: Range information
        candles: Numpy array of OHLC data
        session: 'MORNING' or 'AFTERNOON'
        
    Returns:
        New breakout info if opened, None otherwise
    """
    try:
        # Increment reversal count
        if session == 'MORNING':
            state.morning_reversal_count += 1
            reversal_count = state.morning_reversal_count
        else:
            state.afternoon_reversal_count += 1
            reversal_count = state.afternoon_reversal_count
        
        logger.info(f"{session} REVERSAL #{reversal_count}: Closing all positions")
        
        # Close all existing positions for this session
        close_all_positions(session=session)
        
        # Clear position lists
        if session == 'MORNING':
            state.morning_positions = []
        else:
            state.afternoon_positions = []
        
        # If this is the second reversal, stop trading this session
        if reversal_count >= 2:
            logger.warning(f"{session} session: 2nd reversal detected - no more entries")
            return None
        
        # Open new position in opposite direction (only on first reversal)
        # Use double lot size for reversal trades
        latest_candle = candles[-1]
        breakout_info = {
            'direction': new_direction,
            'price': float(latest_candle['close']),
            'time': datetime.fromtimestamp(latest_candle['time']),
            'candle_high': float(latest_candle['high']),
            'candle_low': float(latest_candle['low'])
        }
        
        tp_price = calculate_tp(breakout_info)
        
        ticket = open_position(
            direction=new_direction,
            lot_size=LOT_SIZE * 2,  # Double lot size for reversal
            tp_price=tp_price,
            comment=f"{session}_REVERSAL_{new_direction}"
        )
        
        if ticket:
            if session == 'MORNING':
                state.morning_positions.append(ticket)
            else:
                state.afternoon_positions.append(ticket)
            
            logger.info(f"Reversal position opened: {new_direction}")
            return breakout_info
        
        return None
        
    except Exception as e:
        logger.error(f"Error handling reversal: {e}")
        return None

# =============================================================================
# TAKE PROFIT CALCULATION
# =============================================================================

def calculate_tp(breakout_info: Dict) -> float:
    """
    Calculate take profit price based on breakout
    
    Args:
        breakout_info: Breakout information
        
    Returns:
        TP price
    """
    direction = breakout_info['direction']
    breakout_price = breakout_info['price']
    
    symbol_info = get_symbol_info()
    if symbol_info is None:
        # Fallback: assume 5-digit pricing
        point_value = 0.00001
    else:
        point_value = symbol_info['point']
    
    tp_distance = TP_UNITS * point_value   # Convert units to actual distance
    
    if direction == 'BUY':
        tp_price = breakout_price + tp_distance
    else:
        tp_price = breakout_price - tp_distance
    
    return tp_price

# =============================================================================
# TIME MANAGEMENT
# =============================================================================

def get_current_time() -> time:
    """Get current time (using system time)"""
    return datetime.now().time()

def get_current_date() -> datetime.date:
    """Get current date"""
    return datetime.now().date()

def is_trading_day() -> bool:
    """Check if today is a trading day (Monday-Friday)"""
    weekday = datetime.now().weekday()
    return weekday < 5  # Monday=0, Friday=4

def should_calculate_morning_range() -> bool:
    """Check if we should calculate morning range"""
    current_time = get_current_time()
    return (current_time >= MORNING_RANGE_END and 
            current_time < time(23, 59) and
            state.morning_range is None)

def should_calculate_afternoon_range() -> bool:
    """Check if we should calculate afternoon range"""
    current_time = get_current_time()
    return (current_time >= AFTERNOON_RANGE_END and 
            current_time < time(23, 59) and
            state.afternoon_range is None)

def can_enter_morning_trade() -> bool:
    """Check if new morning trades can be entered"""
    current_time = get_current_time()
    return (current_time >= MORNING_ENTRY_START and 
            current_time <= MORNING_ENTRY_CUTOFF and
            state.morning_reversal_count < 2)

def can_enter_afternoon_trade() -> bool:
    """Check if new afternoon trades can be entered"""
    current_time = get_current_time()
    return (current_time >= AFTERNOON_ENTRY_START and 
            current_time < AFTERNOON_EXIT_TIME and
            state.afternoon_reversal_count < 2)

def should_force_close_afternoon() -> bool:
    """Check if we should force close afternoon positions"""
    current_time = get_current_time()
    return current_time >= AFTERNOON_EXIT_TIME

# =============================================================================
# MAIN TRADING LOOP
# =============================================================================

def process_morning_session(candles: np.ndarray):
    """Process morning trading session logic"""
    try:
        current_date = get_current_date()
        
        # Calculate range if needed
        if state.morning_range is None and should_calculate_morning_range():
            state.morning_range = get_range(
                candles, MORNING_RANGE_START, MORNING_RANGE_END, current_date
            )
            if state.morning_range:
                logger.info("Morning range calculated")
        
        # Check for breakout if range exists but no breakout yet
        if (state.morning_range is not None and 
            state.morning_breakout is None and 
            can_enter_morning_trade()):
            
            breakout = check_breakout(
                candles, state.morning_range, MORNING_ENTRY_START, current_date
            )
            
            if breakout:
                # Calculate TP and open initial position
                tp_price = calculate_tp(breakout)
                ticket = open_position(
                    direction=breakout['direction'],
                    lot_size=LOT_SIZE,
                    tp_price=tp_price,
                    comment="MORNING_INITIAL"
                )
                
                if ticket:
                    state.morning_breakout = breakout
                    state.morning_positions.append(ticket)
                    
                    # Calculate scale levels
                    state.morning_scale_levels = calculate_scale_levels(
                        state.morning_range, breakout['direction']
                    )
                    logger.info(f"Morning breakout: {breakout['direction']}, Scale levels: {state.morning_scale_levels}")
        
        # Manage existing morning trades
        if state.morning_breakout is not None:
            # Check for reversal
            reversal_direction = check_reversal(
                candles, state.morning_range, state.morning_breakout
            )
            
            if reversal_direction:
                new_breakout = handle_reversal(
                    reversal_direction, state.morning_range, candles, 'MORNING'
                )
                if new_breakout:
                    state.morning_breakout = new_breakout
                    # For reversal, only scale at 50%
                    state.morning_scale_levels = calculate_scale_levels(
                        state.morning_range, new_breakout['direction'], is_reversal=True
                    )
            else:
                # Check and execute scaling
                state.morning_scale_levels = check_and_execute_scaling(
                    candles, state.morning_range, state.morning_breakout,
                    state.morning_scale_levels, 'MORNING'
                )
        
    except Exception as e:
        logger.error(f"Error in morning session processing: {e}")

def process_afternoon_session(candles: np.ndarray):
    """Process afternoon trading session logic"""
    try:
        current_date = get_current_date()
        
        # Force close if past exit time
        if should_force_close_afternoon():
            if state.afternoon_positions:
                logger.info("22:55 - Force closing all afternoon positions")
                close_all_positions(session='AFTERNOON')
                state.afternoon_positions = []
            return
        
        # Calculate range if needed
        if state.afternoon_range is None and should_calculate_afternoon_range():
            state.afternoon_range = get_range(
                candles, AFTERNOON_RANGE_START, AFTERNOON_RANGE_END, current_date
            )
            if state.afternoon_range:
                logger.info("Afternoon range calculated")
        
        # Check for breakout if range exists but no breakout yet
        if (state.afternoon_range is not None and 
            state.afternoon_breakout is None and 
            can_enter_afternoon_trade()):
            
            breakout = check_breakout(
                candles, state.afternoon_range, AFTERNOON_ENTRY_START, current_date
            )
            
            if breakout:
                # Calculate TP and open initial position
                tp_price = calculate_tp(breakout)
                ticket = open_position(
                    direction=breakout['direction'],
                    lot_size=LOT_SIZE,
                    tp_price=tp_price,
                    comment="AFTERNOON_INITIAL"
                )
                
                if ticket:
                    state.afternoon_breakout = breakout
                    state.afternoon_positions.append(ticket)
                    
                    # Calculate scale levels
                    state.afternoon_scale_levels = calculate_scale_levels(
                        state.afternoon_range, breakout['direction']
                    )
                    logger.info(f"Afternoon breakout: {breakout['direction']}, Scale levels: {state.afternoon_scale_levels}")
        
        # Manage existing afternoon trades
        if state.afternoon_breakout is not None:
            # Check for reversal
            reversal_direction = check_reversal(
                candles, state.afternoon_range, state.afternoon_breakout
            )
            
            if reversal_direction:
                new_breakout = handle_reversal(
                    reversal_direction, state.afternoon_range, candles, 'AFTERNOON'
                )
                if new_breakout:
                    state.afternoon_breakout = new_breakout
                    # For reversal, only scale at 50%
                    state.afternoon_scale_levels = calculate_scale_levels(
                        state.afternoon_range, new_breakout['direction'], is_reversal=True
                    )
            else:
                # Check and execute scaling
                state.afternoon_scale_levels = check_and_execute_scaling(
                    candles, state.afternoon_range, state.afternoon_breakout,
                    state.afternoon_scale_levels, 'AFTERNOON'
                )
        
    except Exception as e:
        logger.error(f"Error in afternoon session processing: {e}")

def check_new_day():
    """Check if it's a new trading day and reset state"""
    current_date = get_current_date()
    
    # Simple new day detection (can be enhanced with proper tracking)
    current_time = get_current_time()
    
    # Reset at midnight
    if current_time < time(0, 5):  # Early morning reset window
        if state.morning_range is not None or state.afternoon_range is not None:
            logger.info("New trading day - resetting state")
            state.reset_morning()
            state.reset_afternoon()

def main_loop():
    """Main continuous trading loop"""
    logger.info("=" * 80)
    logger.info("Trading Bot Started")
    logger.info(f"Symbol: {SYMBOL}")
    logger.info(f"Lot Size: {LOT_SIZE}")
    logger.info(f"TP Units: {TP_UNITS}")
    logger.info("=" * 80)
    
    while True:
        try:
            # Check if it's a trading day
            if not is_trading_day():
                logger.info("Weekend - waiting for next trading day")
                time_module.sleep(3600)  # Check every hour
                continue
            
            # Check for new day
            check_new_day()
            
            # Get latest candles
            candles = get_candles(SYMBOL, TIMEFRAME, count=100)
            if candles is None:
                logger.warning("Failed to retrieve candles, retrying...")
                time_module.sleep(POLL_INTERVAL)
                continue
            
            # Process morning session
            process_morning_session(candles)
            
            # Process afternoon session
            process_afternoon_session(candles)
            
            # Wait before next iteration
            time_module.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            time_module.sleep(POLL_INTERVAL * 2)  # Wait longer on error

# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    """Main entry point"""
    try:
        # Initialize MT5
        if not initialize_mt5():
            logger.error("Failed to initialize MT5. Exiting.")
            return
        
        # Start main trading loop
        main_loop()
        
    except Exception as e:
        logger.critical(f"Critical error: {e}")
    finally:
        # Cleanup
        shutdown_mt5()
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    main()


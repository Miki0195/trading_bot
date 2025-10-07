"""
MetaTrader5 Trading Bot - Backtesting System
Simulates the range breakout strategy on historical data with comprehensive statistics
"""

import MetaTrader5 as mt5
import numpy as np
import pandas as pd
from datetime import datetime, time, timedelta
import logging
from typing import List, Dict, Tuple, Optional
import argparse
import json

# =============================================================================
# CONFIGURATION - Match trading_bot.py settings
# =============================================================================

# Trading Parameters
SYMBOL = "XAUUSD"
LOT_SIZE = 0.01 #0.1
TP_UNITS = 580.0 # 58.0
MAGIC_NUMBER = 234567

# Range Definition Times
MORNING_RANGE_START = time(10, 0)
MORNING_RANGE_END = time(10, 15)
AFTERNOON_RANGE_START = time(16, 30)
AFTERNOON_RANGE_END = time(16, 45)

# Entry Timing
MORNING_ENTRY_START = time(10, 15)
MORNING_ENTRY_CUTOFF = time(16, 29)
AFTERNOON_ENTRY_START = time(16, 45)
AFTERNOON_EXIT_TIME = time(23, 55)

# Scaling Levels
SCALE_LEVELS = [0.75, 0.50, 0.25]

# Backtesting Settings
TIMEFRAME = mt5.TIMEFRAME_M5
INITIAL_BALANCE = 10000.0  # Starting balance for simulation

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# TRADE CLASS
# =============================================================================

class Trade:
    """Represents a single trade"""
    def __init__(self, direction: str, entry_price: float, entry_time: datetime,
                 lot_size: float, tp_price: float, trade_type: str = "INITIAL",
                 session: str = "MORNING"):
        self.direction = direction
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.lot_size = lot_size
        self.tp_price = tp_price
        self.trade_type = trade_type  # INITIAL, SCALE, REVERSAL
        self.session = session
        self.exit_price: Optional[float] = None
        self.exit_time: Optional[datetime] = None
        self.exit_reason: Optional[str] = None  # TP, REVERSAL, TIME_EXIT
        self.profit: Optional[float] = None
        self.pips: Optional[float] = None
        
    def close(self, exit_price: float, exit_time: datetime, exit_reason: str, point: float):
        """Close the trade and calculate profit"""
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.exit_reason = exit_reason
        
        # Calculate pips
        if self.direction == "BUY":
            self.pips = (exit_price - self.entry_price) / point / 10
        else:
            self.pips = (self.entry_price - exit_price) / point / 10
        
        # Calculate profit (simplified: 1 pip = $1 per 0.01 lot)
        # For standard lot (100,000 units), 1 pip = $10
        # For 0.01 lot, 1 pip = $0.10
        pip_value = self.lot_size * 100  # $1 per 0.01 lot per pip
        self.profit = self.pips * pip_value
        
    def to_dict(self) -> Dict:
        """Convert trade to dictionary"""
        return {
            'direction': self.direction,
            'entry_price': self.entry_price,
            'entry_time': self.entry_time,
            'exit_price': self.exit_price,
            'exit_time': self.exit_time,
            'lot_size': self.lot_size,
            'tp_price': self.tp_price,
            'trade_type': self.trade_type,
            'session': self.session,
            'exit_reason': self.exit_reason,
            'profit': self.profit,
            'pips': self.pips,
            'duration': (self.exit_time - self.entry_time) if self.exit_time else None
        }

# =============================================================================
# SESSION STATE
# =============================================================================

class SessionState:
    """Manages state for a single trading session"""
    def __init__(self, session_type: str):
        self.session_type = session_type  # MORNING or AFTERNOON
        self.range_high: Optional[float] = None
        self.range_low: Optional[float] = None
        self.breakout_direction: Optional[str] = None
        self.breakout_price: Optional[float] = None
        self.tp_price: Optional[float] = None
        self.reversal_count: int = 0
        self.scale_levels: List[float] = []
        self.executed_scales: List[float] = []
        self.open_trades: List[Trade] = []
        self.session_start_balance: float = 0.0
        self.session_max_drawdown: float = 0.0
        self.session_peak_balance: float = 0.0
        self.initial_breakout_done: bool = False  # Track if initial breakout already happened
        self.breakout_candle_time: Optional[pd.Timestamp] = None  # Track when breakout candle closed
        
    def reset(self):
        """Reset session state"""
        self.range_high = None
        self.range_low = None
        self.breakout_direction = None
        self.breakout_price = None
        self.tp_price = None
        self.reversal_count = 0
        self.scale_levels = []
        self.executed_scales = []
        self.open_trades = []
        self.session_start_balance = 0.0
        self.session_max_drawdown = 0.0
        self.session_peak_balance = 0.0
        self.breakout_candle_time = None
        self.initial_breakout_done = False

# =============================================================================
# BACKTESTING ENGINE
# =============================================================================

class Backtester:
    """Main backtesting engine"""
    
    def __init__(self, symbol: str, start_date: datetime, end_date: datetime):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.point = 0.00001  # Will be set from symbol info
        self.digits = 5
        
        # Trading state
        self.morning_state = SessionState("MORNING")
        self.afternoon_state = SessionState("AFTERNOON")
        
        # Results tracking
        self.all_trades: List[Trade] = []
        self.closed_trades: List[Trade] = []
        self.daily_equity: List[Dict] = []
        self.balance = INITIAL_BALANCE
        
        # Session drawdown tracking
        self.morning_session_drawdowns: List[float] = []
        self.afternoon_session_drawdowns: List[float] = []
        
    def initialize(self) -> bool:
        """Initialize MT5 connection"""
        if not mt5.initialize():
            logger.error(f"MT5 initialization failed: {mt5.last_error()}")
            return False
        
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"Symbol {self.symbol} not found")
            return False
        
        self.point = symbol_info.point
        self.digits = symbol_info.digits
        
        logger.info(f"Backtester initialized for {self.symbol}")
        logger.info(f"Period: {self.start_date.date()} to {self.end_date.date()}")
        return True
    
    def get_historical_data(self) -> Optional[pd.DataFrame]:
        """Fetch historical data from MT5"""
        logger.info("Fetching historical data...")
        
        rates = mt5.copy_rates_range(
            self.symbol,
            TIMEFRAME,
            self.start_date,
            self.end_date
        )
        
        if rates is None or len(rates) == 0:
            logger.error(f"Failed to fetch historical data: {mt5.last_error()}")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df['date'] = df['time'].dt.date
        df['time_only'] = df['time'].dt.time
        df['weekday'] = df['time'].dt.day_name()
        
        logger.info(f"Loaded {len(df)} candles from {df['time'].min()} to {df['time'].max()}")
        return df
    
    def calculate_range(self, df: pd.DataFrame, date: datetime.date, 
                        start_time: time, end_time: time) -> Optional[Tuple[float, float]]:
        """Calculate range high/low for a session"""
        mask = (df['date'] == date) & (df['time_only'] >= start_time) & (df['time_only'] < end_time)
        range_candles = df[mask]
        
        if len(range_candles) < 3:
            logger.info(f"  Insufficient candles for range {start_time}-{end_time}: {len(range_candles)} candles (need 3+) - session skipped")
            return None
        
        range_high = range_candles['high'].max()
        range_low = range_candles['low'].min()
        
        return range_high, range_low
    
    def calculate_tp(self, breakout_price: float, direction: str) -> float:
        """Calculate take profit price"""
        tp_distance = TP_UNITS * self.point
        
        if direction == "BUY":
            return breakout_price + tp_distance
        else:
            return breakout_price - tp_distance
    
    def calculate_scale_levels(self, range_high: float, range_low: float, 
                               direction: str, is_reversal: bool = False) -> List[float]:
        """Calculate scaling entry prices"""
        range_size = range_high - range_low
        
        # For reversal trades, only scale at 50%
        # For initial breakout, scale at 75%, 50%, 25%
        if is_reversal:
            percentages = np.array([0.50])  # Only 50% level on reversal
        else:
            percentages = np.array(SCALE_LEVELS)  # All levels on initial breakout
        
        if direction == "BUY":
            levels = range_high - (percentages * range_size)
        else:
            levels = range_low + (percentages * range_size)
        
        return levels.tolist()
    
    def check_tp_hit(self, trade: Trade, candle: pd.Series) -> bool:
        """Check if take profit was hit"""
        if trade.direction == "BUY":
            return candle['high'] >= trade.tp_price
        else:
            return candle['low'] <= trade.tp_price
    
    def open_trade(self, direction: str, entry_price: float, entry_time: datetime,
                   tp_price: float, trade_type: str, session: str, lot_size: float = None) -> Trade:
        """Open a new trade"""
        if lot_size is None:
            lot_size = LOT_SIZE
        
        trade = Trade(
            direction=direction,
            entry_price=entry_price,
            entry_time=entry_time,
            lot_size=lot_size,
            tp_price=tp_price,
            trade_type=trade_type,
            session=session
        )
        self.all_trades.append(trade)
        return trade
    
    def close_trade(self, trade: Trade, exit_price: float, exit_time: datetime, 
                    exit_reason: str):
        """Close a trade"""
        trade.close(exit_price, exit_time, exit_reason, self.point)
        self.closed_trades.append(trade)
        self.balance += trade.profit
        
        logger.info(f"  Trade closed: {trade.direction} {trade.trade_type} | "
                   f"Entry: {trade.entry_price:.5f} | Exit: {exit_price:.5f} | "
                   f"Profit: ${trade.profit:.2f} ({trade.pips:.1f} pips) | {exit_reason}")
    
    def close_all_session_trades(self, state: SessionState, exit_price: float,
                                  exit_time: datetime, exit_reason: str):
        """Close all trades for a session"""
        for trade in state.open_trades:
            self.close_trade(trade, exit_price, exit_time, exit_reason)
        state.open_trades = []
    
    def calculate_floating_pnl(self, state: SessionState, current_price: float) -> float:
        """Calculate floating profit/loss for open trades in a session"""
        floating_pnl = 0.0
        for trade in state.open_trades:
            if trade.direction == "BUY":
                pips = (current_price - trade.entry_price) / self.point / 10
            else:
                pips = (trade.entry_price - current_price) / self.point / 10
            
            pip_value = trade.lot_size * 100
            profit = pips * pip_value
            floating_pnl += profit
        
        return floating_pnl
    
    def update_session_drawdown(self, state: SessionState, candle_high: float, candle_low: float, candle_close: float):
        """Update session drawdown based on floating P/L at WORST price point in candle"""
        # Check drawdown at BOTH high and low to capture worst moment for open positions
        # For BUY positions: worst is at candle LOW
        # For SELL positions: worst is at candle HIGH
        # We check both to get the most accurate drawdown
        
        prices_to_check = [candle_high, candle_low, candle_close]
        
        for price in prices_to_check:
            # Calculate current equity (balance + floating P/L at this price)
            floating_pnl = self.calculate_floating_pnl(state, price)
            current_equity = self.balance + floating_pnl
            
            # Update peak balance (only from close price, not intra-candle)
            if price == candle_close and current_equity > state.session_peak_balance:
                state.session_peak_balance = current_equity
            
            # Calculate drawdown from peak
            drawdown = current_equity - state.session_peak_balance
            
            # Update maximum drawdown (most negative value)
            if drawdown < state.session_max_drawdown:
                state.session_max_drawdown = drawdown
    
    def process_morning_session(self, df_day: pd.DataFrame, date: datetime.date):
        """Process morning trading session"""
        state = self.morning_state
        
        # Initialize session balance tracking
        state.session_start_balance = self.balance
        state.session_peak_balance = self.balance
        state.session_max_drawdown = 0.0
        
        # Calculate range if not done
        if state.range_high is None:
            range_result = self.calculate_range(df_day, date, MORNING_RANGE_START, MORNING_RANGE_END)
            if range_result:
                state.range_high, state.range_low = range_result
                logger.info(f"  Morning range: {state.range_high:.5f} - {state.range_low:.5f}")
        
        if state.range_high is None:
            return
        
        # Get candles after entry start time
        entry_candles = df_day[df_day['time_only'] >= MORNING_ENTRY_START].copy()
        
        for idx, candle in entry_candles.iterrows():
            current_time = candle['time']
            current_time_only = candle['time_only']
            
            # Check if past entry cutoff for new trades
            can_enter_new = current_time_only <= MORNING_ENTRY_CUTOFF
            
            # Check for initial breakout (only once per session!)
            if not state.initial_breakout_done and can_enter_new:
                # Check for buy breakout
                if candle['close'] > state.range_high:
                    state.breakout_direction = "BUY"
                    state.breakout_price = candle['close']
                    state.tp_price = self.calculate_tp(state.breakout_price, "BUY")
                    state.scale_levels = self.calculate_scale_levels(
                        state.range_high, state.range_low, "BUY"
                    )
                    state.initial_breakout_done = True  # Mark that initial breakout happened
                    state.breakout_candle_time = candle['time']  # Store breakout candle timestamp
                    
                    # DON'T open initial trade - only set up for scaling
                    logger.info(f"  Morning BREAKOUT: BUY @ {candle['close']:.5f}, TP: {state.tp_price:.5f} (NO INITIAL TRADE - scales only)")
                    # DON'T continue - allow scaling on subsequent candles
                
                # Check for sell breakout
                elif candle['close'] < state.range_low:
                    state.breakout_direction = "SELL"
                    state.breakout_price = candle['close']
                    state.tp_price = self.calculate_tp(state.breakout_price, "SELL")
                    state.scale_levels = self.calculate_scale_levels(
                        state.range_high, state.range_low, "SELL"
                    )
                    state.initial_breakout_done = True  # Mark that initial breakout happened
                    state.breakout_candle_time = candle['time']  # Store breakout candle timestamp
                    
                    # DON'T open initial trade - only set up for scaling
                    logger.info(f"  Morning BREAKOUT: SELL @ {candle['close']:.5f}, TP: {state.tp_price:.5f} (NO INITIAL TRADE - scales only)")
                    # DON'T continue - allow scaling on subsequent candles
            
            # Manage existing trades
            if state.breakout_direction is not None:
                # Check for TP hit (only if we have open trades)
                if state.open_trades:
                    tp_hit = False
                    for trade in state.open_trades[:]:
                        if self.check_tp_hit(trade, candle):
                            self.close_trade(trade, state.tp_price, current_time, "TP")
                            state.open_trades.remove(trade)
                            tp_hit = True
                    
                    if tp_hit:
                        # Close all trades when TP is hit
                        self.close_all_session_trades(state, state.tp_price, current_time, "TP")
                        # DON'T reset executed_scales - each level should only trigger once per session!
                        logger.info(f"  TP hit - positions closed, monitoring for remaining scale levels")
                        # DON'T continue - keep monitoring for pullbacks and reversals!
                
                # Check for scaling FIRST (before reversal check)
                # This ensures that if a candle sweeps through multiple levels and triggers reversal,
                # all scale positions are opened before being closed by the reversal
                # BUT: Only check scales if we're on a NEW candle (after breakout candle)
                can_check_scales = True
                if state.breakout_candle_time is not None:
                    if candle['time'] <= state.breakout_candle_time:
                        can_check_scales = False
                
                if can_check_scales:
                    for level_index, level in enumerate(state.scale_levels):
                        if level in state.executed_scales:
                            continue
                        
                        triggered = False
                        if state.breakout_direction == "BUY":
                            if candle['low'] <= level:
                                triggered = True
                        else:
                            if candle['high'] >= level:
                                triggered = True
                        
                        if triggered:
                            # Check if still within entry window for morning
                            if not can_enter_new:
                                logger.info(f"  Morning: Scale level {level:.5f} triggered but past entry cutoff ({MORNING_ENTRY_CUTOFF}) - skipping")
                                continue
                            
                            # Determine lot size based on scale order
                            if state.reversal_count >= 1:
                                # For reversal: only 1 scale (50%) with 4x lot size
                                lot_size = LOT_SIZE * 4
                                # lot_size = LOT_SIZE * 2
                            else:
                                # For initial breakout: 75%=4x, 50%=3x, 25%=2x
                                # Reverse the index so deepest pullback gets most size
                                lot_size = LOT_SIZE * (4 - level_index)  # 0->4x, 1->3x, 2->2x
                                # lot_size = LOT_SIZE

                            trade = self.open_trade(state.breakout_direction, level, current_time,
                                                   state.tp_price, "SCALE", "MORNING",
                                                   lot_size=lot_size)
                            state.open_trades.append(trade)
                            state.executed_scales.append(level)
                            trigger_price = candle['low'] if state.breakout_direction == "BUY" else candle['high']
                            logger.info(f"  Morning SCALE: {state.breakout_direction} @ {level:.5f} with {lot_size/LOT_SIZE:.1f}x lot (candle {'low' if state.breakout_direction == 'BUY' else 'high'}: {trigger_price:.5f})")
                
                # Check for reversal AFTER scaling (only if we have open trades OR no trades yet)
                reversal = False
                if state.breakout_direction == "BUY" and candle['close'] < state.range_low:
                    reversal = True
                    new_direction = "SELL"
                elif state.breakout_direction == "SELL" and candle['close'] > state.range_high:
                    reversal = True
                    new_direction = "BUY"
                
                if reversal:
                    # Close all existing trades (if any)
                    if state.open_trades:
                        self.close_all_session_trades(state, candle['close'], current_time, "REVERSAL")
                    
                    # Only allow reversals if within entry time window
                    if not can_enter_new:
                        logger.info(f"  Morning: Reversal detected but past entry cutoff ({MORNING_ENTRY_CUTOFF}) - positions closed, STOP TRADING")
                        state.breakout_direction = None  # Stop trading for this session
                        continue
                    
                    # Only allow ONE reversal per session with new positions
                    if state.reversal_count == 0:
                        # First reversal: set up for scaling in opposite direction (NO initial reversal trade)
                        logger.info(f"  Morning REVERSAL #1: {new_direction} @ {candle['close']:.5f}, TP: {self.calculate_tp(candle['close'], new_direction):.5f} (NO REVERSAL TRADE - scales only)")
                        state.reversal_count += 1
                        state.breakout_direction = new_direction
                        state.breakout_price = candle['close']
                        state.tp_price = self.calculate_tp(state.breakout_price, new_direction)
                        # For reversal, only scale at 50%
                        state.scale_levels = self.calculate_scale_levels(
                            state.range_high, state.range_low, new_direction, is_reversal=True
                        )
                        # Reset executed_scales for reversal - it's a NEW direction
                        # Even if 50% is same price, it's opposite direction so should be allowed
                        state.executed_scales = []
                        
                        # DON'T open reversal trade - only set up for scaling
                    else:
                        # Second (or more) opposite breakout: just close all and STOP trading
                        logger.info(f"  Morning: Second opposite breakout detected (candle closed @ {candle['close']:.5f}) - closing all positions, STOP TRADING")
                        state.reversal_count += 1
                        state.breakout_direction = None  # Stop trading for this session
                    continue
            
            # Update session drawdown tracking after processing each candle
            if state.open_trades:
                self.update_session_drawdown(state, candle['high'], candle['low'], candle['close'])
        
        # Store the maximum drawdown for this morning session
        if state.session_max_drawdown < 0:
            self.morning_session_drawdowns.append(state.session_max_drawdown)
    
    def process_afternoon_session(self, df_day: pd.DataFrame, date: datetime.date):
        """Process afternoon trading session"""
        state = self.afternoon_state
        
        # Initialize session balance tracking
        state.session_start_balance = self.balance
        state.session_peak_balance = self.balance
        state.session_max_drawdown = 0.0
        
        # Calculate range if not done
        if state.range_high is None:
            range_result = self.calculate_range(df_day, date, AFTERNOON_RANGE_START, AFTERNOON_RANGE_END)
            if range_result:
                state.range_high, state.range_low = range_result
                logger.info(f"  Afternoon range: {state.range_high:.5f} - {state.range_low:.5f}")
        
        if state.range_high is None:
            return
        
        # Get candles after entry start time
        entry_candles = df_day[df_day['time_only'] >= AFTERNOON_ENTRY_START].copy()
        
        for idx, candle in entry_candles.iterrows():
            current_time = candle['time']
            current_time_only = candle['time_only']
            
            # Force close at exit time
            if current_time_only >= AFTERNOON_EXIT_TIME:
                if state.open_trades:
                    logger.info(f"  Afternoon FORCE CLOSE at {AFTERNOON_EXIT_TIME}")
                    self.close_all_session_trades(state, candle['close'], current_time, "TIME_EXIT")
                break
            
            # Check for initial breakout (only once per session!)
            if not state.initial_breakout_done:
                if candle['close'] > state.range_high:
                    state.breakout_direction = "BUY"
                    state.breakout_price = candle['close']
                    state.tp_price = self.calculate_tp(state.breakout_price, "BUY")
                    state.scale_levels = self.calculate_scale_levels(
                        state.range_high, state.range_low, "BUY"
                    )
                    state.initial_breakout_done = True  # Mark that initial breakout happened
                    state.breakout_candle_time = candle['time']  # Store breakout candle timestamp
                    
                    # DON'T open initial trade - only set up for scaling
                    logger.info(f"  Afternoon BREAKOUT: BUY @ {candle['close']:.5f}, TP: {state.tp_price:.5f} (NO INITIAL TRADE - scales only)")
                    # DON'T continue - allow scaling on subsequent candles
                
                elif candle['close'] < state.range_low:
                    state.breakout_direction = "SELL"
                    state.breakout_price = candle['close']
                    state.tp_price = self.calculate_tp(state.breakout_price, "SELL")
                    state.scale_levels = self.calculate_scale_levels(
                        state.range_high, state.range_low, "SELL"
                    )
                    state.initial_breakout_done = True  # Mark that initial breakout happened
                    state.breakout_candle_time = candle['time']  # Store breakout candle timestamp
                    
                    # DON'T open initial trade - only set up for scaling
                    logger.info(f"  Afternoon BREAKOUT: SELL @ {candle['close']:.5f}, TP: {state.tp_price:.5f} (NO INITIAL TRADE - scales only)")
                    # DON'T continue - allow scaling on subsequent candles
            
            # Manage existing trades
            if state.breakout_direction is not None:
                # Check for TP hit (only if we have open trades)
                if state.open_trades:
                    tp_hit = False
                    for trade in state.open_trades[:]:
                        if self.check_tp_hit(trade, candle):
                            self.close_trade(trade, state.tp_price, current_time, "TP")
                            state.open_trades.remove(trade)
                            tp_hit = True
                    
                    if tp_hit:
                        # Close all trades when TP is hit
                        self.close_all_session_trades(state, state.tp_price, current_time, "TP")
                        # DON'T reset executed_scales - each level should only trigger once per session!
                        logger.info(f"  TP hit - positions closed, monitoring for remaining scale levels")
                        # DON'T continue - keep monitoring for pullbacks and reversals!
                
                # Check for scaling FIRST (before reversal check)
                # This ensures that if a candle sweeps through multiple levels and triggers reversal,
                # all scale positions are opened before being closed by the reversal
                # BUT: Only check scales if we're on a NEW candle (after breakout candle)
                can_check_scales = True
                if state.breakout_candle_time is not None:
                    if candle['time'] <= state.breakout_candle_time:
                        can_check_scales = False
                
                if can_check_scales:
                    for level_index, level in enumerate(state.scale_levels):
                        if level in state.executed_scales:
                            continue
                        
                        triggered = False
                        if state.breakout_direction == "BUY":
                            if candle['low'] <= level:
                                triggered = True
                        else:
                            if candle['high'] >= level:
                                triggered = True
                        
                        if triggered:
                            # Check if still within trading window for afternoon
                            if current_time_only >= AFTERNOON_EXIT_TIME:
                                logger.info(f"  Afternoon: Scale level {level:.5f} triggered but past exit time ({AFTERNOON_EXIT_TIME}) - skipping")
                                continue
                            
                            # Determine lot size based on scale order
                            if state.reversal_count >= 1:
                                # For reversal: only 1 scale (50%) with 4x lot size
                                lot_size = LOT_SIZE * 4
                                # lot_size = LOT_SIZE * 2
                            else:
                                # For initial breakout: 75%=4x, 50%=3x, 25%=2x
                                # Reverse the index so deepest pullback gets most size
                                lot_size = LOT_SIZE * (4 - level_index)  # 0->4x, 1->3x, 2->2x
                                # lot_size = LOT_SIZE
                            
                            trade = self.open_trade(state.breakout_direction, level, current_time,
                                                   state.tp_price, "SCALE", "AFTERNOON",
                                                   lot_size=lot_size)
                            state.open_trades.append(trade)
                            state.executed_scales.append(level)
                            trigger_price = candle['low'] if state.breakout_direction == "BUY" else candle['high']
                            logger.info(f"  Afternoon SCALE: {state.breakout_direction} @ {level:.5f} with {lot_size/LOT_SIZE:.1f}x lot (candle {'low' if state.breakout_direction == 'BUY' else 'high'}: {trigger_price:.5f})")
                
                # Check for reversal AFTER scaling (only if we have open trades OR no trades yet)
                reversal = False
                if state.breakout_direction == "BUY" and candle['close'] < state.range_low:
                    reversal = True
                    new_direction = "SELL"
                elif state.breakout_direction == "SELL" and candle['close'] > state.range_high:
                    reversal = True
                    new_direction = "BUY"
                
                if reversal:
                    # Close all existing trades (if any)
                    if state.open_trades:
                        self.close_all_session_trades(state, candle['close'], current_time, "REVERSAL")
                    
                    # Check if still within trading window for afternoon
                    if current_time_only >= AFTERNOON_EXIT_TIME:
                        logger.info(f"  Afternoon: Reversal detected but past exit time ({AFTERNOON_EXIT_TIME}) - positions closed, STOP TRADING")
                        state.breakout_direction = None  # Stop trading for this session
                        continue
                    
                    # Only allow ONE reversal per session with new positions
                    if state.reversal_count == 0:
                        # First reversal: set up for scaling in opposite direction (NO initial reversal trade)
                        logger.info(f"  Afternoon REVERSAL #1: {new_direction} @ {candle['close']:.5f}, TP: {self.calculate_tp(candle['close'], new_direction):.5f} (NO REVERSAL TRADE - scales only)")
                        state.reversal_count += 1
                        state.breakout_direction = new_direction
                        state.breakout_price = candle['close']
                        state.tp_price = self.calculate_tp(state.breakout_price, new_direction)
                        # For reversal, only scale at 50%
                        state.scale_levels = self.calculate_scale_levels(
                            state.range_high, state.range_low, new_direction, is_reversal=True
                        )
                        # Reset executed_scales for reversal - it's a NEW direction
                        # Even if 50% is same price, it's opposite direction so should be allowed
                        state.executed_scales = []
                        
                        # DON'T open reversal trade - only set up for scaling
                    else:
                        # Second (or more) opposite breakout: just close all and STOP trading
                        logger.info(f"  Afternoon: Second opposite breakout detected (candle closed @ {candle['close']:.5f}) - closing all positions, STOP TRADING")
                        state.reversal_count += 1
                        state.breakout_direction = None  # Stop trading for this session
                    continue
            
            # Update session drawdown tracking after processing each candle
            if state.open_trades:
                self.update_session_drawdown(state, candle['high'], candle['low'], candle['close'])
        
        # Force close any remaining open trades at end of afternoon session
        # (In case data doesn't have candles until AFTERNOON_EXIT_TIME)
        if state.open_trades:
            last_candle = entry_candles.iloc[-1]
            logger.info(f"  Afternoon FORCE CLOSE - End of session (data ended at {last_candle['time_only']}, {len(state.open_trades)} positions still open)")
            self.close_all_session_trades(state, last_candle['close'], last_candle['time'], "SESSION_END")
        
        # Store the maximum drawdown for this afternoon session
        if state.session_max_drawdown < 0:
            self.afternoon_session_drawdowns.append(state.session_max_drawdown)
    
    def run(self) -> Dict:
        """Run the backtest"""
        df = self.get_historical_data()
        if df is None:
            return {}
        
        # Group by date
        unique_dates = sorted(df['date'].unique())
        
        logger.info(f"\nStarting backtest simulation...")
        logger.info(f"Trading {len(unique_dates)} days\n")
        
        for date in unique_dates:
            # Skip weekends
            weekday = pd.Timestamp(date).day_name()
            if weekday in ['Saturday', 'Sunday']:
                continue
            
            logger.info(f"Trading day: {date} ({weekday})")
            
            # Reset daily state
            self.morning_state.reset()
            self.afternoon_state.reset()
            
            # Get day's data
            df_day = df[df['date'] == date].copy()
            
            if len(df_day) == 0:
                continue
            
            # Track balance at start of day
            balance_start = self.balance
            
            # Process sessions
            self.process_morning_session(df_day, date)
            self.process_afternoon_session(df_day, date)
            
            # Record daily equity
            daily_profit = self.balance - balance_start
            self.daily_equity.append({
                'date': date,
                'weekday': weekday,
                'balance': self.balance,
                'daily_profit': daily_profit,
                'trades_closed': len([t for t in self.closed_trades 
                                     if t.exit_time.date() == date])
            })
            
            logger.info(f"  End of day balance: ${self.balance:.2f} (Daily P/L: ${daily_profit:.2f})\n")
        
        return self.generate_statistics()
    
    def generate_statistics(self) -> Dict:
        """Generate comprehensive statistics"""
        if not self.closed_trades:
            return {'error': 'No trades executed'}
        
        trades_df = pd.DataFrame([t.to_dict() for t in self.closed_trades])
        
        # Basic statistics
        total_trades = len(self.closed_trades)
        winning_trades = len(trades_df[trades_df['profit'] > 0])
        losing_trades = len(trades_df[trades_df['profit'] < 0])
        breakeven_trades = len(trades_df[trades_df['profit'] == 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = trades_df['profit'].sum()
        gross_profit = trades_df[trades_df['profit'] > 0]['profit'].sum()
        gross_loss = abs(trades_df[trades_df['profit'] < 0]['profit'].sum())
        
        avg_win = trades_df[trades_df['profit'] > 0]['profit'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['profit'] < 0]['profit'].mean() if losing_trades > 0 else 0
        
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Day of week analysis
        trades_df['weekday'] = pd.to_datetime(trades_df['entry_time']).dt.day_name()
        weekday_stats = trades_df.groupby('weekday')['profit'].agg([
            ('total_profit', 'sum'),
            ('avg_profit', 'mean'),
            ('trade_count', 'count'),
            ('win_rate', lambda x: (x > 0).sum() / len(x) * 100)
        ]).round(2)
        
        # Reorder by weekday
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        weekday_stats = weekday_stats.reindex([d for d in weekday_order if d in weekday_stats.index])
        
        # Monthly analysis
        trades_df['month'] = pd.to_datetime(trades_df['entry_time']).dt.to_period('M')
        monthly_stats = trades_df.groupby('month')['profit'].agg([
            ('total_profit', 'sum'),
            ('trade_count', 'count')
        ]).round(2)
        
        # Equity curve
        equity_df = pd.DataFrame(self.daily_equity)
        
        # Drawdown analysis
        equity_df['cumulative_max'] = equity_df['balance'].cummax()
        equity_df['drawdown'] = equity_df['balance'] - equity_df['cumulative_max']
        equity_df['drawdown_pct'] = (equity_df['drawdown'] / equity_df['cumulative_max'] * 100)
        
        max_drawdown = equity_df['drawdown'].min()
        max_drawdown_pct = equity_df['drawdown_pct'].min()
        
        # Session analysis
        session_stats = trades_df.groupby('session')['profit'].agg([
            ('total_profit', 'sum'),
            ('avg_profit', 'mean'),
            ('trade_count', 'count'),
            ('win_rate', lambda x: (x > 0).sum() / len(x) * 100)
        ]).round(2)
        
        # Trade type analysis
        type_stats = trades_df.groupby('trade_type')['profit'].agg([
            ('total_profit', 'sum'),
            ('avg_profit', 'mean'),
            ('trade_count', 'count')
        ]).round(2)
        
        # Exit reason analysis
        exit_stats = trades_df.groupby('exit_reason')['profit'].agg([
            ('total_profit', 'sum'),
            ('trade_count', 'count')
        ]).round(2)
        
        # Session drawdown analysis
        morning_max_dd = min(self.morning_session_drawdowns) if self.morning_session_drawdowns else 0
        afternoon_max_dd = min(self.afternoon_session_drawdowns) if self.afternoon_session_drawdowns else 0
        overall_session_max_dd = min(morning_max_dd, afternoon_max_dd)
        
        morning_avg_dd = sum(self.morning_session_drawdowns) / len(self.morning_session_drawdowns) if self.morning_session_drawdowns else 0
        afternoon_avg_dd = sum(self.afternoon_session_drawdowns) / len(self.afternoon_session_drawdowns) if self.afternoon_session_drawdowns else 0
        
        # Calculate recommended starting balance (worst session * 3 for safety margin)
        recommended_balance = abs(overall_session_max_dd) * 3 if overall_session_max_dd < 0 else INITIAL_BALANCE
        safe_lot_multiplier = INITIAL_BALANCE / recommended_balance if recommended_balance > 0 else 1.0
        
        # Convert Period objects to strings for JSON serialization
        if 'month' in trades_df.columns:
            trades_df['month'] = trades_df['month'].astype(str)
        
        return {
            'summary': {
                'initial_balance': INITIAL_BALANCE,
                'final_balance': self.balance,
                'total_profit': total_profit,
                'return_pct': (total_profit / INITIAL_BALANCE * 100),
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'breakeven_trades': breakeven_trades,
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'gross_profit': gross_profit,
                'gross_loss': gross_loss,
                'max_drawdown': max_drawdown,
                'max_drawdown_pct': max_drawdown_pct,
                'avg_pips_per_trade': trades_df['pips'].mean(),
                # Session-specific drawdowns
                'morning_max_session_dd': morning_max_dd,
                'morning_avg_session_dd': morning_avg_dd,
                'afternoon_max_session_dd': afternoon_max_dd,
                'afternoon_avg_session_dd': afternoon_avg_dd,
                'worst_session_dd': overall_session_max_dd,
                'recommended_starting_balance': recommended_balance,
                'safe_lot_size': LOT_SIZE * safe_lot_multiplier,
            },
            'weekday_stats': weekday_stats.to_dict(),
            'monthly_stats': monthly_stats.to_dict(),
            'session_stats': session_stats.to_dict(),
            'trade_type_stats': type_stats.to_dict(),
            'exit_reason_stats': exit_stats.to_dict(),
            'equity_curve': equity_df.to_dict('records'),
            'all_trades': trades_df.to_dict('records')
        }

# =============================================================================
# REPORTING
# =============================================================================

def print_report(stats: Dict):
    """Print comprehensive backtest report"""
    if 'error' in stats:
        print(f"\n❌ Error: {stats['error']}\n")
        return
    
    summary = stats['summary']
    
    print("\n" + "=" * 80)
    print(" " * 25 + "BACKTEST RESULTS")
    print("=" * 80)
    
    # Summary
    print("\n📊 SUMMARY")
    print("-" * 80)
    print(f"Initial Balance:        ${summary['initial_balance']:,.2f}")
    print(f"Final Balance:          ${summary['final_balance']:,.2f}")
    print(f"Total Profit/Loss:      ${summary['total_profit']:,.2f}")
    print(f"Return:                 {summary['return_pct']:.2f}%")
    print(f"Max Drawdown:           ${summary['max_drawdown']:,.2f} ({summary['max_drawdown_pct']:.2f}%)")
    
    # Trade Statistics
    print("\n📈 TRADE STATISTICS")
    print("-" * 80)
    print(f"Total Trades:           {summary['total_trades']}")
    print(f"Winning Trades:         {summary['winning_trades']} ({summary['win_rate']:.2f}%)")
    print(f"Losing Trades:          {summary['losing_trades']}")
    print(f"Breakeven Trades:       {summary['breakeven_trades']}")
    print(f"Average Win:            ${summary['avg_win']:.2f}")
    print(f"Average Loss:           ${summary['avg_loss']:.2f}")
    print(f"Profit Factor:          {summary['profit_factor']:.2f}")
    print(f"Gross Profit:           ${summary['gross_profit']:,.2f}")
    print(f"Gross Loss:             ${summary['gross_loss']:,.2f}")
    print(f"Average Pips/Trade:     {summary['avg_pips_per_trade']:.1f}")
    
    # Session Drawdown Analysis (RISK MANAGEMENT)
    print("\n⚠️  SESSION DRAWDOWN ANALYSIS (RISK MANAGEMENT)")
    print("=" * 80)
    print(f"Morning Session:")
    print(f"  Max Drawdown:         ${summary['morning_max_session_dd']:,.2f}")
    print(f"  Avg Drawdown:         ${summary['morning_avg_session_dd']:,.2f}")
    print(f"\nAfternoon Session:")
    print(f"  Max Drawdown:         ${summary['afternoon_max_session_dd']:,.2f}")
    print(f"  Avg Drawdown:         ${summary['afternoon_avg_session_dd']:,.2f}")
    print(f"\n⚡ WORST SESSION DRAWDOWN: ${summary['worst_session_dd']:,.2f}")
    print(f"\n💡 RECOMMENDED SETTINGS:")
    print(f"  Minimum Starting Balance:  ${summary['recommended_starting_balance']:,.2f}")
    print(f"  Safe Lot Size (current):   {LOT_SIZE}")
    print(f"  OR use this lot size:      {summary['safe_lot_size']:.2f} (with ${INITIAL_BALANCE:,.2f})")
    print("\nℹ️  The recommended balance gives you a 3x safety margin against")
    print("   the worst session drawdown to avoid account wipeout.")
    print("=" * 80)
    
    # Day of Week Analysis
    print("\n📅 DAY OF WEEK ANALYSIS")
    print("-" * 80)
    print(f"{'Day':<12} {'Total Profit':<15} {'Avg Profit':<15} {'Trades':<10} {'Win Rate':<10}")
    print("-" * 80)
    
    weekday_stats = stats['weekday_stats']
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        if day in weekday_stats['total_profit']:
            total = weekday_stats['total_profit'][day]
            avg = weekday_stats['avg_profit'][day]
            count = int(weekday_stats['trade_count'][day])
            wr = weekday_stats['win_rate'][day]
            
            profit_color = "✅" if total > 0 else "❌"
            print(f"{day:<12} {profit_color} ${total:<12,.2f} ${avg:<12,.2f} {count:<10} {wr:.1f}%")
    
    # Best and Worst Days
    best_day = max(weekday_stats['total_profit'].items(), key=lambda x: x[1])
    worst_day = min(weekday_stats['total_profit'].items(), key=lambda x: x[1])
    
    print("\n🏆 BEST DAY TO TRADE:   " + best_day[0] + f" (${best_day[1]:,.2f})")
    print("⚠️  WORST DAY TO TRADE:  " + worst_day[0] + f" (${worst_day[1]:,.2f})")
    
    # Session Analysis
    print("\n🕐 SESSION ANALYSIS")
    print("-" * 80)
    print(f"{'Session':<12} {'Total Profit':<15} {'Avg Profit':<15} {'Trades':<10} {'Win Rate':<10}")
    print("-" * 80)
    
    session_stats = stats['session_stats']
    for session in session_stats['total_profit']:
        total = session_stats['total_profit'][session]
        avg = session_stats['avg_profit'][session]
        count = int(session_stats['trade_count'][session])
        wr = session_stats['win_rate'][session]
        
        print(f"{session:<12} ${total:<14,.2f} ${avg:<14,.2f} {count:<10} {wr:.1f}%")
    
    # Trade Type Analysis
    print("\n🎯 TRADE TYPE ANALYSIS")
    print("-" * 80)
    type_stats = stats['trade_type_stats']
    for trade_type in type_stats['total_profit']:
        total = type_stats['total_profit'][trade_type]
        avg = type_stats['avg_profit'][trade_type]
        count = int(type_stats['trade_count'][trade_type])
        
        print(f"{trade_type:<15} Total: ${total:<10,.2f}  Avg: ${avg:<10,.2f}  Count: {count}")
    
    # Exit Reason Analysis
    print("\n🚪 EXIT REASON ANALYSIS")
    print("-" * 80)
    exit_stats = stats['exit_reason_stats']
    for reason in exit_stats['total_profit']:
        total = exit_stats['total_profit'][reason]
        count = int(exit_stats['trade_count'][reason])
        
        print(f"{reason:<15} Total: ${total:<10,.2f}  Count: {count}")
    
    # Monthly Performance
    print("\n📆 MONTHLY PERFORMANCE")
    print("-" * 80)
    monthly_stats = stats['monthly_stats']
    for month in monthly_stats['total_profit']:
        profit = monthly_stats['total_profit'][month]
        count = int(monthly_stats['trade_count'][month])
        
        profit_icon = "📈" if profit > 0 else "📉"
        print(f"{profit_icon} {month}:  ${profit:,.2f}  ({count} trades)")
    
    print("\n" + "=" * 80 + "\n")

def save_results(stats: Dict, filename: str):
    """Save results to files"""
    # Save summary to JSON
    json_filename = filename.replace('.csv', '_summary.json')
    with open(json_filename, 'w') as f:
        # Convert Period objects to strings in monthly_stats
        monthly_stats_converted = {}
        for key, value in stats['monthly_stats'].items():
            monthly_stats_str = {str(k): v for k, v in value.items()}
            monthly_stats_converted[key] = monthly_stats_str
        
        # Convert to JSON-serializable format
        summary_export = {
            'summary': stats['summary'],
            'weekday_stats': stats['weekday_stats'],
            'monthly_stats': monthly_stats_converted,
            'session_stats': stats['session_stats'],
            'trade_type_stats': stats['trade_type_stats'],
            'exit_reason_stats': stats['exit_reason_stats']
        }
        json.dump(summary_export, f, indent=2, default=str)
    
    # Save trades to CSV
    trades_df = pd.DataFrame(stats['all_trades'])
    # Convert datetime and Period columns to strings for CSV
    for col in trades_df.columns:
        if pd.api.types.is_datetime64_any_dtype(trades_df[col]):
            trades_df[col] = trades_df[col].astype(str)
        elif hasattr(trades_df[col].dtype, 'name') and 'period' in trades_df[col].dtype.name.lower():
            trades_df[col] = trades_df[col].astype(str)
    trades_df.to_csv(filename, index=False)
    
    # Save equity curve
    equity_filename = filename.replace('.csv', '_equity.csv')
    equity_df = pd.DataFrame(stats['equity_curve'])
    # Convert date columns to strings
    for col in equity_df.columns:
        if pd.api.types.is_datetime64_any_dtype(equity_df[col]) or col == 'date':
            equity_df[col] = equity_df[col].astype(str)
    equity_df.to_csv(equity_filename, index=False)
    
    logger.info(f"\n💾 Results saved:")
    logger.info(f"   - Trades: {filename}")
    logger.info(f"   - Summary: {json_filename}")
    logger.info(f"   - Equity: {equity_filename}")

# =============================================================================
# MAIN
# =============================================================================

def main():
    # Declare globals at the start
    global SYMBOL, LOT_SIZE
    
    parser = argparse.ArgumentParser(description='Backtest the Range Breakout Strategy')
    parser.add_argument('--start', type=str, required=True, 
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, required=True,
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--symbol', type=str, default=SYMBOL,
                       help=f'Trading symbol (default: {SYMBOL})')
    parser.add_argument('--lot-size', type=float, default=LOT_SIZE,
                       help=f'Lot size (default: {LOT_SIZE})')
    parser.add_argument('--output', type=str, default='backtest_results.csv',
                       help='Output CSV filename')
    
    args = parser.parse_args()
    
    # Update global settings
    SYMBOL = args.symbol
    LOT_SIZE = args.lot_size
    
    # Parse dates
    try:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
    except ValueError:
        print("❌ Error: Invalid date format. Use YYYY-MM-DD")
        return
    
    # Initialize and run backtest
    backtester = Backtester(SYMBOL, start_date, end_date)
    
    if not backtester.initialize():
        print("❌ Failed to initialize backtester")
        return
    
    try:
        stats = backtester.run()
        
        if stats:
            print_report(stats)
            save_results(stats, args.output)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Backtest interrupted by user")
    except Exception as e:
        logger.error(f"Error during backtest: {e}", exc_info=True)
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()


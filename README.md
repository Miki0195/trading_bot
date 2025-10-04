# MetaTrader5 Range Breakout Trading Bot

A production-ready automated trading bot for MetaTrader5 that implements a range breakout strategy with scaling and reversal management.

## Features

- **Dual Session Trading**: Separate morning (9:00-9:15) and afternoon (15:30-15:45) range setups
- **Intelligent Scaling**: Automatic position scaling at 75%, 50%, and 25% retracement levels
- **Reversal Management**: Automatic position flip on opposite breakouts (max 2 reversals)
- **Time Restrictions**: Enforces entry cutoffs and forced exits
- **Vectorized Operations**: Uses numpy for efficient candle analysis
- **Production Ready**: Comprehensive error handling, logging, and state management
- **📊 Backtesting System**: Test strategy on historical data with comprehensive statistics

## Installation

### ⚠️ Important: Windows Required

**MetaTrader5 Python API only works on Windows.** 

- **macOS users:** See **[MACOS_SETUP.md](MACOS_SETUP.md)** for solutions (VPS, VM, or dual boot)
- **Linux users:** Use Wine or Windows VM

### Windows Installation

1. **Install MetaTrader5 Terminal** (if not already installed)

2. **Install Python Dependencies**:
```bash
pip install -r requirements.txt
```

### macOS Installation

```bash
# macOS users: Install development dependencies only
pip install -r requirements-mac.txt

# Then follow MACOS_SETUP.md for running the bot on Windows (VM/VPS)
```

## Backtesting

Before going live, test your strategy on historical data:

```bash
# Test strategy on 2023 data
python backtest.py --start 2023-01-01 --end 2023-12-31

# Test different symbol
python backtest.py --start 2023-01-01 --end 2023-12-31 --symbol GBPUSD

# Test with specific lot size
python backtest.py --start 2023-01-01 --end 2023-12-31 --lot-size 0.01
```

**The backtest provides:**
- Total profit/loss and return %
- Win rate and profit factor
- **Best/worst days of week to trade** ⭐
- Session performance (morning vs afternoon)
- Monthly breakdown
- Detailed trade log exported to CSV
- Equity curve for visualization

See **[BACKTESTING_GUIDE.md](BACKTESTING_GUIDE.md)** for complete documentation.

## Configuration

All settings are configurable at the top of `trading_bot.py`:

### Trading Parameters
- `SYMBOL`: Trading instrument (default: "EURUSD")
- `LOT_SIZE`: Position size in lots (default: 0.1)
- `TP_UNITS`: Take profit distance in units/10 pips (default: 5.8 = 58 pips)
- `MAGIC_NUMBER`: Unique identifier for bot's orders

### Time Windows
- **Morning Range**: 9:00 - 9:15 (3 candles)
- **Morning Entry**: From 9:20 onwards
- **Morning Cutoff**: 15:29 (no new entries after)
- **Afternoon Range**: 15:30 - 15:45 (3 candles)
- **Afternoon Entry**: From 15:50 onwards
- **Afternoon Exit**: 22:55 (force close all)

### Scaling Levels
- 75% retracement into range
- 50% retracement into range
- 25% retracement into range

## Trading Strategy

### Range Setup
1. **Morning Session**: Range defined by high/low of 9:00-9:15 (three 5m candles)
2. **Afternoon Session**: Range defined by high/low of 15:30-15:45 (three 5m candles)

### Entry Rules
- First 5m candle close outside the range triggers entry
- **Buy**: Close above range high
- **Sell**: Close below range low
- Initial position: LOT_SIZE (default 0.1)

### Scaling In
When price pulls back into the range:
- Add position at 75% level
- Add position at 50% level
- Add position at 25% level
- All positions in same direction as original breakout

### Take Profit
- TP = Breakout close price ± TP_UNITS
- All positions share the same TP
- TP is static once set

### Reversal Handling
If price breaks out in the opposite direction:
1. Close all existing positions
2. Open new position in opposite direction
3. Apply same scaling logic
4. If reversal happens again (2nd flip), close everything and stop

### Time Restrictions
- **Morning trades**: No new entries after 15:29, existing can run
- **Afternoon trades**: Force close all at 22:55

## Usage

### Basic Run
```bash
python trading_bot.py
```

### Background Run (Linux/Mac)
```bash
nohup python trading_bot.py > bot.log 2>&1 &
```

### Windows Service
Use Task Scheduler or run in a terminal:
```cmd
python trading_bot.py
```

## Monitoring

### Log File
All trading activity is logged to `trading_bot.log`:
- Range calculations
- Breakout detections
- Position entries/exits
- Scaling operations
- Reversals
- Errors and warnings

### Real-time Monitoring
```bash
tail -f trading_bot.log
```

## Important Notes

### MetaTrader5 Setup
1. **Enable Algo Trading**: Tools → Options → Expert Advisors → "Allow automated trading"
2. **Login**: Ensure you're logged into your MT5 account
3. **Symbol**: Verify EURUSD (or your chosen symbol) is available in Market Watch

### Risk Management
- Start with small lot sizes (0.01 - 0.1)
- Test on demo account first
- Monitor the bot regularly
- Understand the strategy before deploying

### Timezone Considerations
- The bot uses **system time**
- Ensure your system timezone matches your broker's server time
- Adjust time constants if needed for your timezone

### Error Handling
The bot includes comprehensive error handling:
- Connection loss recovery
- Order rejection handling
- Invalid candle data protection
- Automatic retry mechanisms

## Troubleshooting

### Bot won't connect to MT5
- Ensure MT5 terminal is running
- Check that algo trading is enabled
- Verify you're logged into your account

### No trades being placed
- Check if it's a trading day (Monday-Friday)
- Verify time windows in configuration
- Check log file for errors
- Ensure symbol is available and visible in Market Watch

### Orders being rejected
- Check margin requirements
- Verify lot size is within broker limits
- Check if trading is allowed for the symbol
- Review `MAX_SLIPPAGE` setting

## Customization

### Changing Trading Hours
Edit these constants in `trading_bot.py`:
```python
MORNING_RANGE_START = time(9, 0)
MORNING_RANGE_END = time(9, 15)
AFTERNOON_RANGE_START = time(15, 30)
AFTERNOON_RANGE_END = time(15, 45)
```

### Adjusting Take Profit
```python
TP_UNITS = 5.8  # 58 pips for 5-digit broker
```

### Modifying Scale Levels
```python
SCALE_LEVELS = [0.75, 0.50, 0.25]  # As percentages
```

## Architecture

### Modular Design
- **Data Retrieval**: Efficient candle fetching with numpy arrays
- **Range Calculation**: Vectorized high/low computation
- **Breakout Detection**: Fast boolean array operations
- **Position Management**: Robust order sending and tracking
- **Scaling Logic**: Automatic pullback monitoring
- **Reversal Handler**: Smart position flip management
- **Time Manager**: Session and time restriction enforcement

### State Management
The `TradingState` class maintains:
- Current range data (morning/afternoon)
- Active breakout information
- Reversal counts
- Scale levels remaining
- Position ticket numbers

## Safety Features

1. **Magic Number**: Only manages its own orders
2. **Session Isolation**: Morning and afternoon trades tracked separately
3. **Reversal Limit**: Maximum 2 reversals per session
4. **Force Exit**: Automatic close at 22:55 for afternoon trades
5. **Error Recovery**: Graceful handling of connection issues

## Performance

- **Efficient Operations**: Numpy vectorized calculations for speed
- **Low Latency**: 10-second polling interval (configurable)
- **Memory Efficient**: Structured arrays for candle data
- **CPU Light**: Minimal processing per iteration

## License

This is a custom trading bot. Use at your own risk. Past performance does not guarantee future results.

## Support

For issues or questions:
1. Check the log file for detailed error messages
2. Verify MT5 connection and settings
3. Test on demo account first
4. Review the strategy documentation

## Version History

**v1.0** - Initial release
- Dual session trading
- Range breakout with scaling
- Reversal management
- Time restrictions
- Comprehensive logging


# Quick Start Guide

Get your MetaTrader5 trading bot up and running in 5 minutes!

## Step 1: Prerequisites

### Install MetaTrader5 Terminal
- **Windows**: Download from [metaquotes.net](https://www.metaquotes.net/en/metatrader5)
- **Mac**: Use Wine or run on Windows VM
- **Linux**: Use Wine

### Open a Trading Account
- Demo account (recommended for testing)
- Live account (for real trading)

## Step 2: Install Python Dependencies

```bash
# Make sure you're in the trading_bot directory
cd /Users/buchsbaummiklos/Documents/trading_bot

# Install required packages
pip install -r requirements.txt
```

## Step 3: Configure MetaTrader5

### Enable Algo Trading
1. Open MT5 Terminal
2. Go to **Tools → Options**
3. Click **Expert Advisors** tab
4. Check ✅ **"Allow automated trading"**
5. Check ✅ **"Allow DLL imports"** (if available)
6. Click **OK**

### Login to Your Account
1. File → Login to Trade Account
2. Enter your credentials
3. Select your broker's server
4. Click **Login**

### Add Symbol to Market Watch
1. Right-click **Market Watch** window
2. Click **Symbols**
3. Search for **EURUSD** (or your chosen symbol)
4. Click **Show** to enable it
5. Close the window

## Step 4: Verify Setup

Run the verification script to check everything is working:

```bash
python verify_setup.py
```

You should see:
```
✅ SUCCESS: Connected to MetaTrader5
✅ SUCCESS: Symbol EURUSD is available
✅ SUCCESS: Retrieved 50 candles
✅ SUCCESS: Trading is allowed for EURUSD
✅ SUCCESS: Lot size 0.1 is valid
✅ ALL TESTS PASSED!
```

If any tests fail, follow the troubleshooting instructions displayed.

## Step 5: Configure the Bot (Optional)

Edit `trading_bot.py` at the top to customize:

```python
# Trading Parameters
SYMBOL = "EURUSD"          # Change symbol here
LOT_SIZE = 0.1             # Start with 0.01 for demo
TP_UNITS = 5.8             # Take profit in units
MAGIC_NUMBER = 234567      # Unique identifier

# Time Windows (adjust for your timezone)
MORNING_RANGE_START = time(9, 0)
MORNING_RANGE_END = time(9, 15)
AFTERNOON_RANGE_START = time(15, 30)
AFTERNOON_RANGE_END = time(15, 45)
```

### Important Timezone Note
The bot uses **system time**. Make sure your computer's timezone matches your broker's server time, or adjust the time constants accordingly.

## Step 6: Start the Bot

### Test Mode (Demo Account)
```bash
python trading_bot.py
```

The bot will:
- Connect to MT5
- Wait for the morning range window (9:00-9:15)
- Calculate the range
- Monitor for breakouts
- Execute trades automatically

### Monitor the Bot
Watch the console output and log file:

```bash
# In another terminal
tail -f trading_bot.log
```

### Stop the Bot
Press `Ctrl+C` in the terminal

## Step 7: Monitor Your First Trade

### What to Expect

#### Morning Session (9:00-9:15)
1. Bot calculates range from 9:00-9:15 candles
2. Waits for breakout at 9:20 or later
3. Enters position when price closes outside range
4. Monitors for pullbacks to scale in
5. Manages take profit automatically

#### Afternoon Session (15:30-15:45)
1. Bot calculates range from 15:30-15:45 candles
2. Waits for breakout at 15:50 or later
3. Same process as morning
4. Force closes all at 22:55 if still open

### Check Your Trades in MT5
1. Open **Toolbox** panel (View → Toolbox)
2. Click **Trade** tab
3. See active positions
4. Check **History** tab for closed trades

## Common First-Time Issues

### "MT5 initialization failed"
**Solution:**
- Ensure MT5 is running
- Check you're logged in
- Enable algo trading in settings

### "Symbol EURUSD not found"
**Solution:**
- Add EURUSD to Market Watch
- Right-click Market Watch → Symbols → Search → Show

### "Order failed: Not enough money"
**Solution:**
- Reduce LOT_SIZE (try 0.01)
- Check account balance
- Verify margin requirements

### "No trades being placed"
**Solution:**
- Check if it's a trading day (Monday-Friday)
- Verify current time is within trading windows
- Look at log file for errors

### "Trading is disabled"
**Solution:**
- Enable algo trading in MT5
- Check if symbol allows trading
- Verify market is open

## Best Practices

### For Testing (Demo Account)
```python
LOT_SIZE = 0.01           # Very small positions
POLL_INTERVAL = 5         # Faster updates for testing
```

### For Production (Live Account)
```python
LOT_SIZE = 0.1            # Adjust based on account size
POLL_INTERVAL = 10        # Standard polling
```

### Risk Management
1. **Start Small**: Use 0.01 lots initially
2. **Demo First**: Test for at least 1 week on demo
3. **Monitor Daily**: Check bot and trades regularly
4. **Set Limits**: Know your maximum risk per trade
5. **Understand Strategy**: Read the full README.md

## Next Steps

1. ✅ Run on demo account for 1+ week
2. ✅ Review all trades in the log file
3. ✅ Understand the strategy fully
4. ✅ Adjust configuration to your preference
5. ✅ Consider running on VPS for 24/7 operation
6. ✅ When ready, switch to live account with small lots

## Getting Help

### Check Logs
```bash
cat trading_bot.log | grep ERROR
cat trading_bot.log | grep WARNING
```

### Verify Connection
```bash
python verify_setup.py
```

### Test Strategy Manually
1. Watch the bot during range time (9:00-9:15 or 15:30-15:45)
2. Check if range is calculated correctly
3. Verify breakout detection works
4. Monitor scaling and reversals

## Safety Reminders

⚠️ **IMPORTANT**:
- This bot trades with real money on live accounts
- Always test thoroughly on demo first
- Never risk more than you can afford to lose
- Monitor the bot regularly
- Understand the strategy before deploying
- Use appropriate lot sizes for your account
- Set up proper VPS if running 24/7

---

## Quick Command Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Verify setup
python verify_setup.py

# Start bot
python trading_bot.py

# Monitor logs (separate terminal)
tail -f trading_bot.log

# Stop bot
Ctrl+C

# Check for errors
grep "ERROR" trading_bot.log

# View recent trades
tail -50 trading_bot.log
```

---

**Ready to Start?**

1. ✅ MT5 installed and running
2. ✅ Dependencies installed (`pip install -r requirements.txt`)
3. ✅ Setup verified (`python verify_setup.py`)
4. ✅ Bot configured (edit `trading_bot.py` if needed)
5. ✅ Demo account ready

**Run:** `python trading_bot.py`

Happy Trading! 🚀


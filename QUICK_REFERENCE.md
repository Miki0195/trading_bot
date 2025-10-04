# Quick Reference Card

## 🚀 Essential Commands

### First Time Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Verify MT5 connection
python verify_setup.py
```

### Backtesting (Test Strategy First!)
```bash
# Test on 2023 data
python backtest.py --start 2023-01-01 --end 2023-12-31

# Test multiple years at once
./run_backtests.sh

# Test different symbol
python backtest.py --start 2023-01-01 --end 2023-12-31 --symbol GBPUSD
```

### Live Trading
```bash
# Start the bot
python trading_bot.py

# Monitor logs (in another terminal)
tail -f trading_bot.log

# Stop the bot
Press Ctrl+C
```

## 📊 Backtest Output Key Metrics

**Look for these in the output:**

✅ **Return %** - Above 15% per year is good  
✅ **Win Rate** - Above 55% is good  
✅ **Profit Factor** - Above 1.5 is excellent  
✅ **Max Drawdown** - Under 15% is good  
✅ **Best Day** - Focus on profitable days  
❌ **Worst Day** - Consider skipping these days  

## 🔧 Configuration Quick Edit

Edit `trading_bot.py` (top of file):

```python
SYMBOL = "EURUSD"          # Line ~23
LOT_SIZE = 0.1             # Line ~24
TP_UNITS = 5.8             # Line ~25 (58 pips)

MORNING_RANGE_START = time(9, 0)    # Line ~30
MORNING_RANGE_END = time(9, 15)     # Line ~31

SCALE_LEVELS = [0.75, 0.50, 0.25]   # Line ~47
```

## 📁 Important Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `verify_setup.py` | Check MT5 connection | Before first run |
| `backtest.py` | Test strategy | Before going live |
| `trading_bot.py` | Live trading bot | After backtesting |
| `BACKTESTING_GUIDE.md` | Backtest docs | To understand results |
| `QUICKSTART.md` | Setup guide | First time setup |

## 🎯 Typical Workflow

### 1. Initial Setup (Once)
```bash
pip install -r requirements.txt
python verify_setup.py
```

### 2. Backtest Strategy (Before Live)
```bash
python backtest.py --start 2023-01-01 --end 2023-12-31
# Review results and optimize
```

### 3. Live Trading (Demo First!)
```bash
# Switch MT5 to DEMO account
python verify_setup.py  # Verify it's demo
python trading_bot.py   # Start bot
```

### 4. Monitor
```bash
tail -f trading_bot.log
# Check MT5 Trade tab
```

## 📈 Backtest Analysis Checklist

After running backtest, check:

- [ ] Total return positive?
- [ ] Win rate above 50%?
- [ ] Profit factor above 1.0?
- [ ] Which days are profitable?
- [ ] Which session performs better?
- [ ] Is drawdown acceptable?
- [ ] Are results consistent across years?

## ⚙️ Common Configuration Changes

### Change Trading Hours
```python
# Line ~30-40 in trading_bot.py
MORNING_RANGE_START = time(8, 0)   # Earlier
AFTERNOON_RANGE_START = time(14, 30)  # Earlier
```

### Change Take Profit Distance
```python
# Line ~25
TP_UNITS = 8.0  # Larger TP (80 pips)
TP_UNITS = 3.0  # Smaller TP (30 pips)
```

### Change Scaling Behavior
```python
# Line ~47
SCALE_LEVELS = [0.50]              # Only one scale level
SCALE_LEVELS = [0.75, 0.50]        # Two scale levels
SCALE_LEVELS = []                  # No scaling
```

### Change Lot Size
```python
# Line ~24
LOT_SIZE = 0.01  # Micro lot (safe)
LOT_SIZE = 0.1   # Mini lot (standard)
LOT_SIZE = 1.0   # Standard lot (high risk)
```

## 🚨 Safety Reminders

⚠️ **ALWAYS:**
1. Test on demo account first
2. Start with small lot sizes (0.01-0.1)
3. Verify setup with `verify_setup.py`
4. Backtest before live trading
5. Monitor the bot regularly
6. Keep MT5 terminal running
7. Have stable internet connection

⚠️ **NEVER:**
1. Run unverified on live account
2. Use large lot sizes without testing
3. Leave bot unattended for weeks
4. Trade without understanding the strategy
5. Ignore backtest warnings

## 📞 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "MT5 initialization failed" | Check MT5 is running, algo trading enabled |
| "Symbol not found" | Add symbol to Market Watch in MT5 |
| "No trades being placed" | Check if trading day, verify time windows |
| "Order rejected" | Check margin, reduce lot size |
| "Connection lost" | Check internet, restart MT5 |
| Backtest no data | MT5 needs to download historical data |

## 📊 Files Generated

### By Backtest
- `backtest_results.csv` - All trades (open in Excel)
- `backtest_results_summary.json` - Statistics
- `backtest_results_equity.csv` - Equity curve

### By Live Bot
- `trading_bot.log` - All activity logs

## 🎓 Learning Resources

1. **First time?** → Read `QUICKSTART.md`
2. **Want to backtest?** → Read `BACKTESTING_GUIDE.md`
3. **Need details?** → Read `README.md`
4. **Want overview?** → Read `PROJECT_OVERVIEW.md`

## 💡 Pro Tips

1. **Always backtest 2-3 years** to verify consistency
2. **Skip unprofitable days** based on backtest results
3. **Start with 0.01 lots** on live account
4. **Monitor first week closely** on live
5. **Use VPS** for 24/7 operation
6. **Keep detailed records** of all changes
7. **Review weekly** to ensure strategy is working

## 🔄 Update Configuration Workflow

```bash
# 1. Edit configuration
nano trading_bot.py  # or your editor

# 2. Test with backtest
python backtest.py --start 2023-01-01 --end 2023-12-31

# 3. If good, test on demo
python trading_bot.py

# 4. Monitor for a week

# 5. If still good, consider live with small lots
```

## 📞 Need Help?

1. Check log file: `cat trading_bot.log | grep ERROR`
2. Verify setup: `python verify_setup.py`
3. Review documentation: `README.md`, `BACKTESTING_GUIDE.md`
4. Check backtest results for insights

---

**Quick Commands Summary:**

```bash
# Setup
pip install -r requirements.txt && python verify_setup.py

# Backtest
python backtest.py --start 2023-01-01 --end 2023-12-31

# Run Bot
python trading_bot.py

# Monitor
tail -f trading_bot.log
```

**Remember:** Test → Demo → Live (small) → Scale Up


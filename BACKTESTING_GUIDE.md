# Backtesting Guide

Complete guide to backtesting your trading strategy using historical MT5 data.

## 📋 What the Backtesting Does

The backtesting system:
- ✅ Connects to MT5 API to fetch historical data
- ✅ Simulates your exact trading strategy on past data
- ✅ Tracks every trade (entries, exits, scaling, reversals)
- ✅ Calculates comprehensive statistics
- ✅ Analyzes best/worst days of the week
- ✅ Shows monthly performance
- ✅ Exports results to CSV for further analysis

## 🚀 Quick Start

### Basic Usage

Test strategy for 1 year (2023):
```bash
python backtest.py --start 2023-01-01 --end 2023-12-31
```

Test for 2 years:
```bash
python backtest.py --start 2022-01-01 --end 2023-12-31
```

Test for 6 months:
```bash
python backtest.py --start 2024-01-01 --end 2024-06-30
```

## 📊 Command-Line Options

### Required Arguments

**`--start`** - Start date in YYYY-MM-DD format
```bash
--start 2023-01-01
```

**`--end`** - End date in YYYY-MM-DD format
```bash
--end 2023-12-31
```

### Optional Arguments

**`--symbol`** - Trading symbol (default: XAUUSD)
```bash
--symbol GBPUSD
```

**`--lot-size`** - Position size (default: 0.1)
```bash
--lot-size 0.01
```

**`--output`** - Output filename (default: backtest_results.csv)
```bash
--output my_backtest_2023.csv
```

## 💡 Example Commands

### Test Different Years

```bash
# Test 2020
python backtest.py --start 2020-01-01 --end 2020-12-31

# Test 2021
python backtest.py --start 2021-01-01 --end 2021-12-31

# Test 2022
python backtest.py --start 2022-01-01 --end 2022-12-31

# Test 2023
python backtest.py --start 2023-01-01 --end 2023-12-31
```

### Test Different Symbols

```bash
# GBPUSD
python backtest.py --start 2023-01-01 --end 2023-12-31 --symbol GBPUSD --output gbpusd_2023.csv

# USDJPY
python backtest.py --start 2023-01-01 --end 2023-12-31 --symbol USDJPY --output usdjpy_2023.csv

# EURJPY
python backtest.py --start 2023-01-01 --end 2023-12-31 --symbol EURJPY --output eurjpy_2023.csv
```

### Test Different Lot Sizes

```bash
# Small lot size
python backtest.py --start 2023-01-01 --end 2023-12-31 --lot-size 0.01 --output test_micro.csv

# Medium lot size
python backtest.py --start 2023-01-01 --end 2023-12-31 --lot-size 0.1 --output test_mini.csv

# Large lot size
python backtest.py --start 2023-01-01 --end 2023-12-31 --lot-size 1.0 --output test_standard.csv
```

### Full Example

```bash
python backtest.py \
  --start 2023-01-01 \
  --end 2023-12-31 \
  --symbol EURUSD \
  --lot-size 0.1 \
  --output eurusd_2023_results.csv
```

## 📈 Understanding the Output

### Console Output

The backtest will display:

#### 1. Summary Statistics
```
📊 SUMMARY
─────────────────────────────────────────
Initial Balance:        $10,000.00
Final Balance:          $12,450.00
Total Profit/Loss:      $2,450.00
Return:                 24.50%
Max Drawdown:           -$345.00 (-3.12%)
```

#### 2. Trade Statistics
```
📈 TRADE STATISTICS
─────────────────────────────────────────
Total Trades:           145
Winning Trades:         87 (60.00%)
Losing Trades:          58
Average Win:            $45.23
Average Loss:           -$28.50
Profit Factor:          1.85
```

#### 3. Day of Week Analysis ⭐ IMPORTANT
```
📅 DAY OF WEEK ANALYSIS
─────────────────────────────────────────
Day          Total Profit    Avg Profit      Trades    Win Rate
─────────────────────────────────────────
Monday       ✅ $450.00      $12.50          36        58.3%
Tuesday      ✅ $380.00      $15.20          25        64.0%
Wednesday    ✅ $520.00      $17.33          30        66.7%
Thursday     ❌ -$120.00     -$4.00          30        43.3%
Friday       ✅ $220.00      $9.17           24        54.2%

🏆 BEST DAY TO TRADE:   Wednesday ($520.00)
⚠️  WORST DAY TO TRADE:  Thursday (-$120.00)
```

**Use this to decide which days to trade!**

#### 4. Session Analysis
```
🕐 SESSION ANALYSIS
─────────────────────────────────────────
Session      Total Profit    Avg Profit      Trades    Win Rate
─────────────────────────────────────────
MORNING      $1,200.00       $18.46          65        61.5%
AFTERNOON    $1,250.00       $15.63          80        58.8%
```

#### 5. Monthly Performance
```
📆 MONTHLY PERFORMANCE
─────────────────────────────────────────
📈 2023-01:  $245.00  (12 trades)
📈 2023-02:  $180.00  (10 trades)
📉 2023-03:  -$45.00  (11 trades)
📈 2023-04:  $320.00  (14 trades)
...
```

### Generated Files

The backtest creates 3 files:

#### 1. `backtest_results.csv` - All Trades
Contains every single trade with details:
- Entry/exit prices
- Entry/exit times
- Direction (BUY/SELL)
- Trade type (INITIAL/SCALE/REVERSAL)
- Session (MORNING/AFTERNOON)
- Profit/loss
- Pips
- Exit reason (TP/REVERSAL/TIME_EXIT)

**Open in Excel or Google Sheets for detailed analysis.**

#### 2. `backtest_results_summary.json` - Statistics
JSON file with all statistics:
- Summary metrics
- Day of week stats
- Monthly stats
- Session stats
- Trade type stats

**Use for programmatic analysis or data visualization.**

#### 3. `backtest_results_equity.csv` - Equity Curve
Daily equity progression:
- Date
- Balance
- Daily profit
- Cumulative max
- Drawdown

**Plot in Excel to visualize account growth.**

## 🔍 Analyzing Results

### Step 1: Review Console Output

Look at:
1. **Total Return** - Is it profitable?
2. **Win Rate** - Above 50% is good
3. **Profit Factor** - Above 1.5 is excellent
4. **Max Drawdown** - How much can you lose?

### Step 2: Check Day of Week Stats ⭐

**Key Questions:**
- Which days are most profitable?
- Which days are losing money?
- Should you avoid trading on certain days?

**Action:** Modify `trading_bot.py` to skip bad days:
```python
# In main_loop(), add:
if datetime.now().strftime('%A') == 'Thursday':
    continue  # Skip Thursday if it's unprofitable
```

### Step 3: Analyze Session Performance

**Questions:**
- Is morning or afternoon better?
- Should you trade only one session?

**Action:** Comment out unprofitable session in `trading_bot.py`:
```python
# If afternoon session loses money, comment out:
# process_afternoon_session(candles)
```

### Step 4: Review Monthly Performance

**Questions:**
- Are there seasonal patterns?
- Which months to avoid?

### Step 5: Open CSV Files in Excel

**All Trades CSV:**
1. Open `backtest_results.csv` in Excel
2. Create pivot tables
3. Filter by session, trade type, etc.
4. Calculate custom metrics

**Equity Curve CSV:**
1. Open `backtest_results_equity.csv`
2. Create a line chart of `balance` column
3. Visualize drawdowns
4. Identify winning/losing streaks

## 📊 Excel Analysis Tips

### Create Pivot Table from Trades CSV

1. Open `backtest_results.csv` in Excel
2. Select all data → Insert → PivotTable
3. Drag fields to analyze:
   - **Rows:** `weekday`
   - **Values:** Sum of `profit`
   - **Filters:** `session`, `trade_type`

### Chart Equity Curve

1. Open `backtest_results_equity.csv`
2. Select `date` and `balance` columns
3. Insert → Line Chart
4. See your account growth over time

### Calculate More Metrics

Add columns in Excel:
```
# Win/Loss indicator
=IF(profit>0,"WIN","LOSS")

# Trade duration in hours
=(exit_time-entry_time)*24

# Risk/Reward ratio
=IF(direction="BUY", (exit_price-entry_price)/(entry_price-range_low), ...)
```

## 🎯 Optimization Workflow

### 1. Run Baseline Backtest

```bash
python backtest.py --start 2023-01-01 --end 2023-12-31
```

Note the results.

### 2. Identify Weak Points

From the output:
- Worst day of week?
- Unprofitable session?
- Which trade types lose money?

### 3. Modify Strategy

Edit `trading_bot.py` constants:
```python
# Change TP distance
TP_UNITS = 8.0  # Try larger TP

# Change scale levels
SCALE_LEVELS = [0.50]  # Try fewer scales

# Change times
MORNING_RANGE_START = time(8, 0)  # Try earlier
```

### 4. Re-run Backtest

```bash
python backtest.py --start 2023-01-01 --end 2023-12-31 --output test_v2.csv
```

### 5. Compare Results

- Did return improve?
- Is drawdown lower?
- Is win rate higher?

### 6. Repeat Until Satisfied

Keep tweaking and testing until you find optimal parameters.

## 🚨 Important Notes

### Data Requirements

**MT5 must have historical data available:**
- Right-click chart in MT5
- Select "Refresh"
- MT5 will download data
- You need data for the date range you're testing

**Missing Data:**
If you get errors, MT5 may not have data for that period.

### Realistic Simulation

The backtest assumes:
- ✅ Orders execute at candle close price
- ✅ TP is hit at exact TP price
- ✅ No slippage
- ✅ No spread (simplified)
- ⚠️ Real trading may differ slightly

**Bottom line:** Backtest is optimistic. Real results may be 10-20% worse.

### Overfitting Warning

⚠️ **Don't over-optimize!**

If you tweak parameters too much to fit historical data:
- It won't work on future data
- You're curve-fitting

**Best practice:**
- Test on multiple years
- Use different symbols
- Keep strategy simple

## 📝 Example Analysis Session

### Goal: Find Best Days to Trade

```bash
# Step 1: Run backtest
python backtest.py --start 2023-01-01 --end 2023-12-31

# Step 2: Look at output
# Day of Week Analysis shows:
# Monday: $450 ✅
# Tuesday: $380 ✅
# Wednesday: $520 ✅
# Thursday: -$120 ❌
# Friday: $220 ✅

# Step 3: Decision
# Don't trade on Thursdays!

# Step 4: Modify trading_bot.py
# Add check in main_loop():
if datetime.now().strftime('%A') == 'Thursday':
    logger.info("Skipping Thursday - unprofitable day")
    time_module.sleep(3600)
    continue

# Step 5: Test live on demo account
```

## 🔄 Comparing Multiple Backtests

```bash
# Test different years
python backtest.py --start 2021-01-01 --end 2021-12-31 --output 2021.csv
python backtest.py --start 2022-01-01 --end 2022-12-31 --output 2022.csv
python backtest.py --start 2023-01-01 --end 2023-12-31 --output 2023.csv

# Compare in Excel:
# 1. Open all 3 CSV files
# 2. Compare total profit, win rate, drawdown
# 3. Check if strategy is consistent across years
```

## 💾 Saving Your Analysis

Create a folder structure:
```
trading_bot/
├── backtests/
│   ├── 2023/
│   │   ├── eurusd_2023.csv
│   │   ├── eurusd_2023_summary.json
│   │   └── eurusd_2023_equity.csv
│   ├── 2022/
│   │   └── ...
│   └── analysis.xlsx  ← Your Excel analysis
```

## 🎓 Learning from Results

### Good Results (Example)
```
Return: 35%
Win Rate: 62%
Profit Factor: 2.1
Max Drawdown: -8%
```
✅ Strategy is solid - consider live testing

### Mediocre Results (Example)
```
Return: 8%
Win Rate: 51%
Profit Factor: 1.15
Max Drawdown: -15%
```
⚠️ Strategy needs improvement - optimize more

### Bad Results (Example)
```
Return: -12%
Win Rate: 42%
Profit Factor: 0.85
Max Drawdown: -25%
```
❌ Strategy doesn't work - major changes needed

## 🚀 Next Steps

1. **Run your first backtest:**
   ```bash
   python backtest.py --start 2023-01-01 --end 2023-12-31
   ```

2. **Analyze the results:**
   - Look at day of week stats
   - Check session performance
   - Review monthly breakdown

3. **Make decisions:**
   - Which days to skip?
   - Which session to focus on?
   - Any parameter changes?

4. **Optimize strategy:**
   - Modify `trading_bot.py`
   - Run backtest again
   - Compare results

5. **Test live:**
   - Once satisfied, test on demo account
   - Monitor for 1-2 weeks
   - If good, consider live with small lots

## ❓ FAQ

**Q: How far back can I test?**
A: Depends on MT5 data. Usually 1-5 years available.

**Q: Can I test multiple symbols at once?**
A: Run separate backtests for each symbol.

**Q: How long does a backtest take?**
A: 1 year usually takes 30-60 seconds.

**Q: Why are results different from live trading?**
A: Backtest doesn't include spread, slippage, or execution delays.

**Q: What's a good return?**
A: 15-30% per year is excellent. 50%+ is exceptional (but verify it's real).

**Q: What if I lose money in backtest?**
A: Don't trade live! Optimize strategy first.

---

**Ready to backtest?**

```bash
python backtest.py --start 2023-01-01 --end 2023-12-31
```

Analyze, optimize, and profit! 📈


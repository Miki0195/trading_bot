# macOS Setup Guide

## ⚠️ Important: MetaTrader5 Limitation

**The MetaTrader5 Python API is Windows-only.** This means you cannot run the trading bot directly on macOS.

## 🔧 Solutions for macOS Users

You have **4 options** to run this trading bot on macOS:

---

## Option 1: Windows Virtual Machine (RECOMMENDED)

Run Windows in a VM on your Mac.

### Using UTM (Free, Apple Silicon Native)

**For Apple Silicon Macs (M1/M2/M3):**

1. **Download UTM:**
   - Visit: https://mac.getutm.app/
   - Install UTM (free)

2. **Install Windows 11 ARM:**
   - Download Windows 11 ARM from Microsoft
   - Create new VM in UTM
   - Install Windows 11

3. **Inside Windows VM:**
   ```cmd
   pip install MetaTrader5 numpy pandas
   ```

4. **Copy trading bot files to VM:**
   - Use shared folders or copy files manually
   - Run bot inside Windows VM

**Pros:** Free, native performance on Apple Silicon  
**Cons:** Requires Windows license, uses Mac resources

### Using Parallels Desktop (Paid, Best Performance)

**Best option for both Intel and Apple Silicon:**

1. **Purchase Parallels Desktop:**
   - Visit: https://www.parallels.com/
   - ~$100/year subscription

2. **Install Windows 11:**
   - Parallels makes this easy
   - Includes Windows download

3. **Inside Windows:**
   - Install Python
   - Install requirements:
     ```cmd
     pip install MetaTrader5 numpy pandas
     ```
   - Run bot

**Pros:** Best performance, seamless integration  
**Cons:** Costs money

---

## Option 2: Remote Windows VPS (RECOMMENDED FOR SERIOUS TRADING)

Run bot on a Windows cloud server.

### Services to Use:

**1. Forex VPS Providers (Best for Trading):**
- **FXVM** - https://www.fxvm.com/ (~$30/month)
- **ForexVPS** - https://www.forexvps.net/ (~$25/month)
- **Commercial Network Services** (~$30/month)

**Pros:**
- ✅ 24/7 uptime (bot never stops)
- ✅ Fast connection to broker servers
- ✅ Don't need to keep Mac on
- ✅ Professional trading setup

**Cons:**
- 💰 Monthly cost (~$25-30)

### Setup:

1. **Sign up for Forex VPS**
2. **Connect via Remote Desktop:**
   ```bash
   # On Mac, use Microsoft Remote Desktop (free from App Store)
   ```
3. **Install MT5 on VPS**
4. **Install Python on VPS:**
   ```cmd
   # Download Python from python.org
   pip install MetaTrader5 numpy pandas
   ```
5. **Upload bot files to VPS**
6. **Run bot 24/7:**
   ```cmd
   python trading_bot.py
   ```

**This is what professional traders use!**

---

## Option 3: Dual Boot Windows (Advanced)

Install Windows alongside macOS.

### Using Boot Camp (Intel Macs Only):

1. **Open Boot Camp Assistant** (in Utilities)
2. **Partition your drive** (allocate 50GB+ for Windows)
3. **Install Windows 10/11**
4. **Restart and hold Option** to choose OS
5. **In Windows, install requirements:**
   ```cmd
   pip install MetaTrader5 numpy pandas
   ```

**Pros:** Native Windows performance  
**Cons:** Need to restart to switch OS, Intel Macs only

---

## Option 4: Wine/CrossOver (Complex, Not Recommended)

Run Windows apps on macOS using Wine.

### Using CrossOver:

1. **Purchase CrossOver** (~$60) - https://www.codeweavers.com/crossover
2. **Install MT5 through CrossOver**
3. **Install Windows Python in CrossOver bottle**

**Pros:** No Windows license needed  
**Cons:** Complex, may have compatibility issues, not reliable for trading

**⚠️ Not recommended for live trading**

---

## 🎯 Recommended Approach

### For Testing/Development:
**Use Parallels or UTM** - Keep everything on your Mac

### For Live Trading:
**Use Forex VPS** - Professional, reliable, 24/7 uptime

---

## 💡 Temporary Solution: Development on Mac, Testing on Windows

You can **edit the code on your Mac** but **run it on Windows**:

### Workflow:

1. **Edit files on Mac** (in Cursor/VS Code)
2. **Sync files to Windows** (Dropbox, Google Drive, GitHub)
3. **Run bot on Windows** (VM or VPS)

### Setup:

**On Mac:**
```bash
# Install only numpy/pandas for code editing
pip install numpy pandas

# Edit files in Cursor
```

**On Windows (VM/VPS):**
```cmd
# Install full requirements
pip install MetaTrader5 numpy pandas

# Run bot
python trading_bot.py
```

---

## 🚀 Quick Start (My Recommendation)

### Immediate Solution:

**Use a Forex VPS** - it's the professional approach:

1. **Sign up:** https://www.fxvm.com/ (~$30/month)
2. **Connect via Remote Desktop** (free app on Mac App Store)
3. **Install MT5 on VPS**
4. **Install Python:**
   ```cmd
   # Download from python.org inside VPS
   ```
5. **Copy bot files to VPS** (drag & drop in Remote Desktop)
6. **Install requirements:**
   ```cmd
   pip install MetaTrader5 numpy pandas
   ```
7. **Run bot:**
   ```cmd
   python verify_setup.py
   python backtest.py --start 2023-01-01 --end 2023-12-31
   python trading_bot.py
   ```
8. **Disconnect** - bot keeps running 24/7!

---

## 📊 Backtesting on Mac

**Good news:** You CAN backtest if you have MT5 data!

If you have MT5 running (via any method above), you can:

1. **Connect to MT5 from Mac** (if MT5 is accessible)
2. **Or copy historical data** from MT5 to Mac
3. **Run backtests locally** (backtesting doesn't need live connection)

But the easiest is to just run everything on Windows (VM/VPS).

---

## 🆘 Still Need Help?

### Option A: Use My VPS Recommendation
Sign up for FXVM or similar, and run everything there.

### Option B: Use Parallels Desktop
Best integration with macOS, worth the cost.

### Option C: Ask for Help
If you have specific constraints, let me know and I can suggest alternatives.

---

## 📝 What to Do Now

**Choose your path:**

### 🎯 Path 1: Serious Trader → Get Forex VPS
```bash
# Sign up for FXVM, run everything there
# Professional, reliable, 24/7
```

### 🎯 Path 2: Testing First → Use Parallels
```bash
# Install Parallels Desktop
# Run Windows on Mac
# Test strategy before committing to VPS
```

### 🎯 Path 3: Free Option → Use UTM
```bash
# Install UTM (free)
# Install Windows 11 ARM
# Run bot in VM
```

---

## 💡 My Personal Recommendation

**For you specifically:**

1. **Right now:** Use **Parallels Desktop** ($100/year)
   - Get Windows running in 30 minutes
   - Test everything
   - Keep your Mac workflow

2. **After testing:** Switch to **Forex VPS** ($30/month)
   - 24/7 uptime
   - Professional setup
   - Don't need to keep Mac on

**Total cost:** ~$100 setup + $30/month = Worth it for serious trading

---

## ✅ Installation Summary

### On Windows (VM/VPS):

```cmd
# Install Python 3.9+ from python.org

# Install requirements
pip install MetaTrader5 numpy pandas

# Verify
python -c "import MetaTrader5 as mt5; print('Success!')"

# Run bot
python trading_bot.py
```

### On Mac (Development Only):

```bash
# Install numpy/pandas only
pip install numpy pandas

# Edit code in Cursor
# Sync to Windows to run
```

---

**Questions? Ask me which option is best for your situation!**


#!/bin/bash
# Quick Backtest Runner - Test multiple years at once

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Trading Bot - Multi-Year Backtest Runner          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
SYMBOL="EURUSD"
LOT_SIZE=0.1

# Create output directory
mkdir -p backtest_results

echo "Running backtests for $SYMBOL..."
echo "Lot size: $LOT_SIZE"
echo ""

# Test 2021
echo "📊 Testing 2021..."
python backtest.py \
  --start 2021-01-01 \
  --end 2021-12-31 \
  --symbol $SYMBOL \
  --lot-size $LOT_SIZE \
  --output backtest_results/${SYMBOL}_2021.csv \
  > backtest_results/${SYMBOL}_2021_report.txt

echo "   ✅ 2021 complete"
echo ""

# Test 2022
echo "📊 Testing 2022..."
python backtest.py \
  --start 2022-01-01 \
  --end 2022-12-31 \
  --symbol $SYMBOL \
  --lot-size $LOT_SIZE \
  --output backtest_results/${SYMBOL}_2022.csv \
  > backtest_results/${SYMBOL}_2022_report.txt

echo "   ✅ 2022 complete"
echo ""

# Test 2023
echo "📊 Testing 2023..."
python backtest.py \
  --start 2023-01-01 \
  --end 2023-12-31 \
  --symbol $SYMBOL \
  --lot-size $LOT_SIZE \
  --output backtest_results/${SYMBOL}_2023.csv \
  > backtest_results/${SYMBOL}_2023_report.txt

echo "   ✅ 2023 complete"
echo ""

# Test 2024 (partial year)
echo "📊 Testing 2024..."
python backtest.py \
  --start 2024-01-01 \
  --end 2024-12-31 \
  --symbol $SYMBOL \
  --lot-size $LOT_SIZE \
  --output backtest_results/${SYMBOL}_2024.csv \
  > backtest_results/${SYMBOL}_2024_report.txt

echo "   ✅ 2024 complete"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "✅ All backtests complete!"
echo ""
echo "Results saved to: backtest_results/"
echo ""
echo "View reports:"
echo "  cat backtest_results/${SYMBOL}_2023_report.txt"
echo ""
echo "Analyze in Excel:"
echo "  open backtest_results/${SYMBOL}_2023.csv"
echo ""
echo "════════════════════════════════════════════════════════════"


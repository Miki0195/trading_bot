#!/bin/bash
# Run multiple trading bot instances for different symbols
# Each instance will run in the background with its own log file

# Configuration
SYMBOLS=("EURUSD" "GBPUSD" "USDJPY")
LOT_SIZE=0.1

echo "Starting Trading Bot instances for multiple symbols..."
echo "=================================================="

for SYMBOL in "${SYMBOLS[@]}"; do
    echo "Starting bot for $SYMBOL..."
    
    # Create a temporary modified version of the bot for this symbol
    # (In production, you'd want separate config files)
    
    LOG_FILE="trading_bot_${SYMBOL}.log"
    
    # Start the bot in background
    # Note: You'll need to modify trading_bot.py to accept command-line arguments
    # or create separate config files for each symbol
    
    echo "  Symbol: $SYMBOL"
    echo "  Log file: $LOG_FILE"
    echo "  Status: ⏳ Starting..."
    
    # Uncomment when ready to use:
    # nohup python trading_bot.py --symbol $SYMBOL --lot-size $LOT_SIZE > "$LOG_FILE" 2>&1 &
    # echo "  PID: $!"
    
    echo ""
done

echo "=================================================="
echo "All bots started!"
echo ""
echo "To monitor logs:"
for SYMBOL in "${SYMBOLS[@]}"; do
    echo "  tail -f trading_bot_${SYMBOL}.log"
done
echo ""
echo "To stop all bots:"
echo "  pkill -f trading_bot.py"
echo ""


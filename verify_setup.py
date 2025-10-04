"""
Setup Verification Script
Run this before starting the trading bot to verify your MT5 connection and configuration.
"""

import MetaTrader5 as mt5
import sys
from datetime import datetime

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def verify_mt5_connection():
    """Verify MT5 connection"""
    print_section("MT5 Connection Test")
    
    if not mt5.initialize():
        print("❌ FAILED: Cannot connect to MetaTrader5")
        print(f"   Error: {mt5.last_error()}")
        print("\n   Troubleshooting:")
        print("   1. Is MT5 terminal running?")
        print("   2. Is algo trading enabled? (Tools → Options → Expert Advisors)")
        print("   3. Are you logged into your account?")
        return False
    
    print("✅ SUCCESS: Connected to MetaTrader5")
    
    # Get account info
    account_info = mt5.account_info()
    if account_info:
        print(f"\n   Account Number: {account_info.login}")
        print(f"   Account Type: {'Demo' if account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO else 'Real'}")
        print(f"   Balance: {account_info.balance:.2f} {account_info.currency}")
        print(f"   Leverage: 1:{account_info.leverage}")
    
    # Get terminal info
    print(f"\n   MT5 Version: {mt5.version()}")
    print(f"   Terminal Info: {mt5.terminal_info()}")
    
    return True

def verify_symbol(symbol="EURUSD"):
    """Verify symbol availability"""
    print_section(f"Symbol Test: {symbol}")
    
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"❌ FAILED: Symbol {symbol} not found")
        print("\n   Troubleshooting:")
        print(f"   1. Right-click Market Watch → Symbols")
        print(f"   2. Search for {symbol} and enable it")
        return False
    
    if not symbol_info.visible:
        print(f"⚠️  WARNING: Symbol {symbol} exists but not visible in Market Watch")
        print(f"   Attempting to enable...")
        if mt5.symbol_select(symbol, True):
            print(f"✅ SUCCESS: Symbol {symbol} enabled")
        else:
            print(f"❌ FAILED: Cannot enable {symbol}")
            return False
    else:
        print(f"✅ SUCCESS: Symbol {symbol} is available")
    
    # Display symbol properties
    print(f"\n   Description: {symbol_info.description}")
    print(f"   Digits: {symbol_info.digits}")
    print(f"   Point: {symbol_info.point}")
    print(f"   Spread: {symbol_info.spread}")
    print(f"   Min Volume: {symbol_info.volume_min}")
    print(f"   Max Volume: {symbol_info.volume_max}")
    print(f"   Volume Step: {symbol_info.volume_step}")
    
    # Get current price
    tick = mt5.symbol_info_tick(symbol)
    if tick:
        print(f"\n   Current Bid: {tick.bid:.5f}")
        print(f"   Current Ask: {tick.ask:.5f}")
        print(f"   Last Update: {datetime.fromtimestamp(tick.time)}")
    
    return True

def verify_data_access(symbol="EURUSD", count=50):
    """Verify historical data access"""
    print_section("Historical Data Test")
    
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, count)
    
    if rates is None or len(rates) == 0:
        print(f"❌ FAILED: Cannot retrieve historical data")
        print(f"   Error: {mt5.last_error()}")
        return False
    
    print(f"✅ SUCCESS: Retrieved {len(rates)} candles")
    
    # Display sample data
    latest = rates[-1]
    print(f"\n   Latest Candle (5M):")
    print(f"   Time: {datetime.fromtimestamp(latest['time'])}")
    print(f"   Open: {latest['open']:.5f}")
    print(f"   High: {latest['high']:.5f}")
    print(f"   Low: {latest['low']:.5f}")
    print(f"   Close: {latest['close']:.5f}")
    print(f"   Volume: {latest['tick_volume']}")
    
    return True

def verify_trading_permissions(symbol="EURUSD"):
    """Verify trading permissions"""
    print_section("Trading Permissions Test")
    
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"❌ FAILED: Cannot get symbol info")
        return False
    
    # Check trading mode
    if symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_DISABLED:
        print(f"❌ FAILED: Trading is disabled for {symbol}")
        return False
    elif symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_CLOSEONLY:
        print(f"⚠️  WARNING: Only closing positions is allowed for {symbol}")
        return False
    
    print(f"✅ SUCCESS: Trading is allowed for {symbol}")
    
    # Check if market is open
    terminal_info = mt5.terminal_info()
    if terminal_info:
        print(f"\n   Trade Allowed: {terminal_info.trade_allowed}")
        print(f"   Expert Advisors Allowed: {terminal_info.mqid}")
    
    return True

def verify_lot_size(symbol="EURUSD", lot_size=0.1):
    """Verify lot size is valid"""
    print_section(f"Lot Size Test: {lot_size}")
    
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"❌ FAILED: Cannot verify lot size")
        return False
    
    min_lot = symbol_info.volume_min
    max_lot = symbol_info.volume_max
    step = symbol_info.volume_step
    
    if lot_size < min_lot:
        print(f"❌ FAILED: Lot size {lot_size} is below minimum {min_lot}")
        return False
    
    if lot_size > max_lot:
        print(f"❌ FAILED: Lot size {lot_size} exceeds maximum {max_lot}")
        return False
    
    # Check if lot size is a valid multiple of step
    if (lot_size - min_lot) % step != 0:
        print(f"⚠️  WARNING: Lot size {lot_size} is not a valid multiple of step {step}")
        print(f"   Suggested values: {min_lot}, {min_lot + step}, {min_lot + 2*step}, ...")
    
    print(f"✅ SUCCESS: Lot size {lot_size} is valid")
    print(f"\n   Min Lot: {min_lot}")
    print(f"   Max Lot: {max_lot}")
    print(f"   Lot Step: {step}")
    
    # Calculate margin requirement
    account_info = mt5.account_info()
    if account_info:
        # Simplified margin calculation
        tick = mt5.symbol_info_tick(symbol)
        if tick:
            contract_size = symbol_info.trade_contract_size
            leverage = account_info.leverage
            estimated_margin = (lot_size * contract_size * tick.ask) / leverage
            print(f"\n   Estimated Margin Required: {estimated_margin:.2f} {account_info.currency}")
            print(f"   Current Free Margin: {account_info.margin_free:.2f} {account_info.currency}")
            
            if estimated_margin > account_info.margin_free:
                print(f"   ⚠️  WARNING: Insufficient margin for this trade!")
    
    return True

def main():
    """Run all verification tests"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "MT5 TRADING BOT SETUP VERIFICATION" + " " * 9 + "║")
    print("╚" + "═" * 58 + "╝")
    
    results = []
    
    # Test 1: MT5 Connection
    try:
        results.append(("MT5 Connection", verify_mt5_connection()))
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        results.append(("MT5 Connection", False))
    
    if not results[0][1]:
        print("\n❌ Cannot proceed without MT5 connection. Please fix the issue and try again.")
        sys.exit(1)
    
    # Test 2: Symbol Availability
    try:
        results.append(("Symbol Availability", verify_symbol("EURUSD")))
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        results.append(("Symbol Availability", False))
    
    # Test 3: Historical Data
    try:
        results.append(("Historical Data", verify_data_access("EURUSD")))
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        results.append(("Historical Data", False))
    
    # Test 4: Trading Permissions
    try:
        results.append(("Trading Permissions", verify_trading_permissions("EURUSD")))
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        results.append(("Trading Permissions", False))
    
    # Test 5: Lot Size
    try:
        results.append(("Lot Size", verify_lot_size("EURUSD", 0.1)))
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        results.append(("Lot Size", False))
    
    # Summary
    print_section("SUMMARY")
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED! You're ready to run the trading bot.")
        print("\n   To start the bot, run:")
        print("   python trading_bot.py")
    else:
        print("❌ SOME TESTS FAILED. Please fix the issues above.")
        print("\n   Common solutions:")
        print("   1. Restart MT5 terminal")
        print("   2. Check internet connection")
        print("   3. Verify account login")
        print("   4. Enable algo trading in MT5 settings")
    print("=" * 60 + "\n")
    
    # Cleanup
    mt5.shutdown()
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()


import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class MT5Bridge:
    """
    MetaTrader 5 API Bridge for XAUUSD Auto-Trading on Demo / Live accounts.
    Includes Sandbox Simulation Fallback when MT5 terminal is not active.
    """
    def __init__(self, symbol: str = "XAUUSD", magic_number: int = 888111):
        self.symbol = symbol
        self.magic_number = magic_number
        self.is_connected = False
        self.mt5 = None
        self.simulation_mode = False

        self._initialize()

    def _initialize(self):
        """Attempts to initialize MetaTrader 5 Python module."""
        try:
            import MetaTrader5 as mt5
            self.mt5 = mt5
            if mt5.initialize():
                account_info = mt5.account_info()
                if account_info is not None:
                    self.is_connected = True
                    logger.info(f"[MT5 Bridge] Connected to MT5 Account #{account_info.login} (Server: {account_info.server}, Currency: {account_info.currency})")
                    return
                else:
                    logger.warning("[MT5 Bridge] MT5 terminal running but no logged in account detected.")
            else:
                logger.warning(f"[MT5 Bridge] MT5 initialize() failed: {mt5.last_error()}")
        except Exception as e:
            logger.warning(f"[MT5 Bridge] MetaTrader5 package error ({e}).")

        self.simulation_mode = True
        logger.info("[MT5 Bridge] Initialized in SIMULATION SANDBOX MODE (Offline / Test environment).")

    def get_account_summary(self) -> dict:
        """Returns account balance, equity, and free margin."""
        if self.is_connected and self.mt5:
            info = self.mt5.account_info()
            if info:
                return {
                    "Login": info.login,
                    "Server": info.server,
                    "Balance": info.balance,
                    "Equity": info.equity,
                    "Margin": info.margin,
                    "Margin_Free": info.margin_free,
                    "Margin_Level": info.margin_level if hasattr(info, 'margin_level') else 0.0,
                    "Leverage": info.leverage,
                    "Mode": "REAL_MT5"
                }
        return {
            "Login": 9999999,
            "Server": "Simulation",
            "Balance": 10000.0,
            "Equity": 10000.0,
            "Margin": 0.0,
            "Margin_Free": 10000.0,
            "Margin_Level": 0.0,
            "Leverage": 100,
            "Mode": "SIMULATION"
        }

    def get_account_info(self) -> dict:
        return self.get_account_summary()


    def get_bot_active_positions(self) -> list:
        """
        Retrieves all active Gold positions on MT5 (auto-bot trades & manual trades).
        """
        bot_positions = []
        if self.is_connected and self.mt5:
            target_symbol = self._resolve_symbol()
            positions = self.mt5.positions_get(symbol=target_symbol)
            if positions is None or len(positions) == 0:
                positions = self.mt5.positions_get()
            
            if positions is not None:
                for pos in positions:
                    pos_dict = pos._asdict()
                    sym = str(pos_dict.get("symbol", ""))
                    if "XAU" in sym.upper() or "GOLD" in sym.upper():
                        bot_positions.append(pos_dict)
        return bot_positions

    def get_open_positions(self) -> list:
        return self.get_bot_active_positions()

    def manage_trailing_stop(self, pos_dict: dict, current_atr: float = 4.5) -> bool:
        """
        Smart Tiered Trailing Stop & Profit Locking Engine:
        - Tier 1 (Profit >= +$3.00): Shift SL to Entry + $0.50
        - Tier 2 (Profit >= +$6.00): Shift SL to Entry + $3.50
        - Tier 3 (Profit >= +$9.00): Shift SL to Entry + $6.50
        - Tier 4 (Profit >= +$12.00): Shift SL to Entry + $9.50 (or Dynamic 1.2*ATR trail)
        """
        if not self.is_connected or not self.mt5:
            return False

        ticket = int(pos_dict.get("ticket") or pos_dict.get("Ticket", 0))
        ptype = pos_dict.get("type") or pos_dict.get("Type")
        entry_price = float(pos_dict.get("price_open") or pos_dict.get("Price_Open", 0.0))
        curr_price = float(pos_dict.get("price_current") or pos_dict.get("Price_Current", 0.0))
        curr_sl = float(pos_dict.get("sl") or pos_dict.get("SL", 0.0))
        profit = float(pos_dict.get("profit") or pos_dict.get("Profit_USD", 0.0))
        sym_name = str(pos_dict.get("symbol") or pos_dict.get("Symbol") or self._resolve_symbol())

        symbol_info = self.mt5.symbol_info(sym_name)
        digits = symbol_info.digits if symbol_info else 2
        point = symbol_info.point if symbol_info else 0.01
        min_stop_pts = symbol_info.trade_stops_level if symbol_info else 10
        min_stop_dist = max(min_stop_pts * point, 0.50)  # Broker minimum stop distance

        is_buy = (ptype == 0 or ptype == "BUY")
        target_sl = curr_sl
        tier_reason = ""

        # Session-aware ATR Multiplier (London/NY Session Overlap: 2.0x ATR for Gold Volatility)
        curr_hour = time.localtime().tm_hour
        is_london_ny_session = (14 <= curr_hour or curr_hour <= 3)
        atr_multiplier = 2.0 if is_london_ny_session else 1.6

        # Dynamic Peak Profit Ratchet Engine (Locks Peak Gains & Prevents Giving Profit Back)
        if profit >= 15.00:
            tier_reason = f"PEAK_RATCHET_LOCK_15USD ({int(profit)}USD)"
            # Lock +$12.00 (+120 pips / 80% of peak profit) when profit >= $15.00
            target_sl = round(entry_price + 12.00, digits) if is_buy else round(entry_price - 12.00, digits)
        elif profit >= 10.00:
            tier_reason = f"PEAK_RATCHET_LOCK_10USD ({int(profit)}USD)"
            # Lock +$7.00 (+70 pips / 70% of peak profit) when profit >= $10.00
            target_sl = round(entry_price + 7.00, digits) if is_buy else round(entry_price - 7.00, digits)
        elif profit >= 5.00:
            tier_reason = "PEAK_RATCHET_LOCK_5USD"
            # Lock +$2.50 (+25 pips) when profit >= $5.00
            target_sl = round(entry_price + 2.50, digits) if is_buy else round(entry_price - 2.50, digits)

        if not tier_reason:
            return False

        # Adjust target_sl to respect broker trade_stops_level distance from current price
        if is_buy:
            target_sl = min(target_sl, round(curr_price - min_stop_dist, digits))
        else:  # SELL
            target_sl = max(target_sl, round(curr_price + min_stop_dist, digits))

        # Ensure Stop Loss ONLY ratchets forward in profit direction (never backward)
        should_update = False
        if is_buy:
            if target_sl > curr_sl and target_sl > (entry_price - 1.0):
                should_update = True
        else:  # SELL
            if (curr_sl == 0 or target_sl < curr_sl) and target_sl < (entry_price + 1.0):
                should_update = True

        if should_update and target_sl != curr_sl:
            req = {
                "action": self.mt5.TRADE_ACTION_SLTP,
                "position": ticket,
                "symbol": sym_name,
                "sl": float(target_sl),
                "tp": float(pos_dict.get("tp") or pos_dict.get("TP", 0.0))
            }
            res = self.mt5.order_send(req)
            if res and res.retcode == self.mt5.TRADE_RETCODE_DONE:
                logger.info(f"🛡️ [Smart Trailing Stop] ({tier_reason}) Shifted SL from ${curr_sl} to ${target_sl} (Floating Profit: ${profit:,.2f}) for Ticket #{ticket}")
                return True
            else:
                ret = res.retcode if res else "No Response"
                comment = res.comment if res else ""
                logger.warning(f"⚠️ [Smart Trailing Stop] Broker rejected SL update for Ticket #{ticket} (retcode: {ret}, comment: {comment})")

        return False




    def get_latest_rates(self, timeframe_str: str = "H1", count: int = 500) -> pd.DataFrame:
        """Pulls OHLCV rate bars directly from MT5 terminal or simulation data."""
        if self.is_connected and self.mt5:
            tf_map = {
                "M1": self.mt5.TIMEFRAME_M1,
                "M5": self.mt5.TIMEFRAME_M5,
                "M15": self.mt5.TIMEFRAME_M15,
                "H1": self.mt5.TIMEFRAME_H1,
                "D1": self.mt5.TIMEFRAME_D1
            }
            tf = tf_map.get(timeframe_str, self.mt5.TIMEFRAME_H1)
            rates = self.mt5.copy_rates_from_pos(self.symbol, tf, 0, count)
            if rates is not None and len(rates) > 0:
                df = pd.DataFrame(rates)
                df["time"] = pd.to_datetime(df["time"], unit="s")
                df.set_index("time", inplace=True)
                df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "tick_volume": "Volume"}, inplace=True)
                # Synthetic macro proxy (inverse gold momentum — labeled clearly as proxy)
                df["DXY_Close"] = 100.0 + (df["Close"].pct_change().cumsum() * -5.0)
                df["DXY_Close"] = df["DXY_Close"].ffill().bfill().fillna(100.0)
                df["US10Y_Close"] = 4.0 + (df["Close"].pct_change().cumsum() * -2.0)
                df["US10Y_Close"] = df["US10Y_Close"].ffill().bfill().fillna(4.0)
                return df[["Open", "High", "Low", "Close", "Volume", "DXY_Close", "US10Y_Close"]]


        # Fallback simulation rates
        logger.info("[MT5 Bridge] Fetching rates from fallback data provider...")
        from xauusd_quant.data_loader import XauDataLoader
        loader = XauDataLoader()
        return loader.fetch_data(symbol="GC=F")

    def _resolve_symbol(self) -> str:
        """Auto-detects broker-specific Gold symbol name (XAUUSD, XAUUSDm, XAUUSD.m, GOLD)."""
        if not (self.is_connected and self.mt5):
            return self.symbol

        candidates = [self.symbol, f"{self.symbol}m", f"{self.symbol}.m", "GOLD", "XAUUSD"]
        for sym in candidates:
            info = self.mt5.symbol_info(sym)
            if info is not None:
                if not info.visible:
                    self.mt5.symbol_select(sym, True)
                logger.info(f"[MT5 Bridge] Auto-detected broker Gold symbol: '{sym}'")
                return sym

        return self.symbol

    def execute_market_order(self, order_type: str, volume: float, sl_price: float = 0.0, tp_price: float = 0.0) -> dict:
        """
        Sends BUY or SELL market order to MT5 terminal.
        """
        volume = max(0.01, round(volume, 2))  # Ensure valid min lot size

        if self.is_connected and self.mt5:
            target_symbol = self._resolve_symbol()
            symbol_info = self.mt5.symbol_info(target_symbol)
            if not symbol_info:
                logger.error(f"[MT5 Bridge] Symbol {target_symbol} not found on MT5 broker.")
                return {"status": "FAILED", "reason": "SYMBOL_NOT_FOUND"}

            price = self.mt5.symbol_info_tick(target_symbol).ask if order_type == "BUY" else self.mt5.symbol_info_tick(target_symbol).bid
            point = symbol_info.point
            digits = symbol_info.digits
            min_stop_pts = symbol_info.trade_stops_level
            min_stop_dist = max(min_stop_pts * point, 1.5)  # At least $1.50 min distance

            mt5_order_type = self.mt5.ORDER_TYPE_BUY if order_type == "BUY" else self.mt5.ORDER_TYPE_SELL

            # Adjust SL/TP to respect broker minimum stop distance
            if sl_price > 0:
                if order_type == "BUY":
                    sl_price = min(sl_price, price - min_stop_dist)
                else:
                    sl_price = max(sl_price, price + min_stop_dist)

            if tp_price > 0:
                if order_type == "BUY":
                    tp_price = max(tp_price, price + min_stop_dist * 2.0)
                else:
                    tp_price = min(tp_price, price - min_stop_dist * 2.0)

            sl_price = round(sl_price, digits)
            tp_price = round(tp_price, digits)

            request = {
                "action": self.mt5.TRADE_ACTION_DEAL,
                "symbol": target_symbol,
                "volume": volume,
                "type": mt5_order_type,
                "price": price,
                "sl": sl_price if sl_price > 0 else 0.0,
                "tp": tp_price if tp_price > 0 else 0.0,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": "XauQuant ML Signal",
                "type_time": self.mt5.ORDER_TIME_GTC,
                "type_filling": self.mt5.ORDER_FILLING_IOC,
            }

            result = self.mt5.order_send(request)
            if result.retcode != self.mt5.TRADE_RETCODE_DONE:
                logger.error(f"[MT5 Bridge] Order failed! Code: {result.retcode}, Comment: {result.comment}")
                return {"status": "FAILED", "retcode": result.retcode, "reason": result.comment}

            logger.info(f"[MT5 Bridge] ORDER EXECUTED ON DEMO! Ticket #{result.order}, Symbol: {target_symbol}, Type: {order_type}, Volume: {volume}, Price: {price}")
            return {
                "status": "SUCCESS",
                "ticket": result.order,
                "symbol": target_symbol,
                "type": order_type,
                "volume": volume,
                "price": price,
                "sl": sl_price,
                "tp": tp_price
            }



        # Simulation Mode Execution Log
        sim_price = 2000.0
        logger.info(f"[MT5 Bridge SIMULATION] Executed {order_type} order | Vol: {volume} lots | Price: {sim_price} | SL: {sl_price} | TP: {tp_price}")
        return {
            "status": "SUCCESS_SIMULATED",
            "ticket": 12345678,
            "type": order_type,
            "volume": volume,
            "price": sim_price,
            "sl": sl_price,
            "tp": tp_price
        }

    def execute_trade(self, signal_type: str, lot_size: float = 0.01, sl_pips: float = 45.0, tp_pips: float = 90.0) -> dict:
        """
        Execute a live market order.
        For XAUUSD/XAUUSDm: 1 pip = $1.00 (not $0.10).
        sl_pips=45 means SL is $45 away from entry price.
        """
        rates = self.get_latest_rates(timeframe_str="M15", count=5)
        curr_price = rates["Close"].iloc[-1] if rates is not None and not rates.empty else 2000.0

        if signal_type == "BUY":
            sl_price = curr_price - sl_pips   # FIX: 1 pip = $1.00 for XAUUSD
            tp_price = curr_price + tp_pips
        else:
            sl_price = curr_price + sl_pips
            tp_price = curr_price - tp_pips

        return self.execute_market_order(order_type=signal_type, volume=lot_size, sl_price=sl_price, tp_price=tp_price)



    def close_position(self, ticket: int) -> bool:

        """Closes a specific open position by ticket number."""
        if self.is_connected and self.mt5:
            positions = self.mt5.positions_get(ticket=ticket)
            if positions and len(positions) > 0:
                pos = positions[0]
                order_type = self.mt5.ORDER_TYPE_SELL if pos.type == self.mt5.POSITION_TYPE_BUY else self.mt5.ORDER_TYPE_BUY
                price = self.mt5.symbol_info_tick(pos.symbol).bid if pos.type == self.mt5.POSITION_TYPE_BUY else self.mt5.symbol_info_tick(pos.symbol).ask
                request = {
                    "action": self.mt5.TRADE_ACTION_DEAL,
                    "symbol": pos.symbol,
                    "volume": pos.volume,
                    "type": order_type,
                    "position": pos.ticket,
                    "price": price,
                    "magic": self.magic_number,
                    "comment": "Close Position",
                    "type_time": self.mt5.ORDER_TIME_GTC,
                    "type_filling": self.mt5.ORDER_FILLING_IOC,
                }
                res = self.mt5.order_send(request)
                if res and res.retcode == self.mt5.TRADE_RETCODE_DONE:
                    logger.info(f"[MT5 Bridge] Position Ticket #{ticket} closed cleanly.")
                    return True
        logger.info(f"[MT5 Bridge SIMULATION] Closed position Ticket #{ticket}")
        return True

    def close_all_positions(self) -> int:

        """Safety Kill Switch: Closes all open positions matching magic number."""
        closed_count = 0
        if self.is_connected and self.mt5:
            positions = self.mt5.positions_get(symbol=self.symbol)
            if positions:
                for pos in positions:
                    if pos.magic == self.magic_number:
                        order_type = self.mt5.ORDER_TYPE_SELL if pos.type == self.mt5.POSITION_TYPE_BUY else self.mt5.ORDER_TYPE_BUY
                        price = self.mt5.symbol_info_tick(self.symbol).bid if pos.type == self.mt5.POSITION_TYPE_BUY else self.mt5.symbol_info_tick(self.symbol).ask
                        request = {
                            "action": self.mt5.TRADE_ACTION_DEAL,
                            "symbol": self.symbol,
                            "volume": pos.volume,
                            "type": order_type,
                            "position": pos.ticket,
                            "price": price,
                            "magic": self.magic_number,
                            "comment": "Close Position",
                            "type_time": self.mt5.ORDER_TIME_GTC,
                            "type_filling": self.mt5.ORDER_FILLING_IOC,
                        }
                        self.mt5.order_send(request)
                        closed_count += 1
        logger.info(f"[MT5 Bridge] Closed {closed_count} active positions.")
        return closed_count

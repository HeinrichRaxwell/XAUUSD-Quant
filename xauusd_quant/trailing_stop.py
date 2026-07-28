import logging
import numpy as np

logger = logging.getLogger(__name__)

class TrailingStopManager:
    """
    Manages Break-Even and ATR Trailing Stop Loss for active bot positions.
    """
    def __init__(self, bridge, breakeven_profit_usd: float = 3.50, atr_trail_mult: float = 1.5):
        self.bridge = bridge
        self.breakeven_profit_usd = breakeven_profit_usd
        self.atr_trail_mult = atr_trail_mult

    def manage_positions(self, current_atr: float) -> list:
        """
        Evaluates open bot positions.
        - Moves SL to Break-Even if floating profit >= breakeven_profit_usd.
        - Trails SL behind price as profit expands.
        Returns list of updated position event dicts.
        """
        updates = []
        bot_positions = self.bridge.get_bot_active_positions()
        if not bot_positions:
            return updates

        mt5 = self.bridge.mt5
        if not (self.bridge.is_connected and mt5):
            return updates

        for pos in bot_positions:
            ticket = pos["Ticket"]
            symbol = pos["Symbol"]
            pos_type = pos["Type"]
            entry = pos["Price_Open"]
            current_price = pos["Price_Current"]
            current_sl = pos["SL"]
            current_tp = pos["TP"]
            profit = pos["Profit_USD"]

            new_sl = current_sl
            modified = False
            event_reason = ""

            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                continue

            spread = symbol_info.spread * symbol_info.point
            digits = symbol_info.digits

            # 1. Minimum Profit Lock (Move SL to Entry + $2.50 when profit >= $5.00)
            if profit >= 5.00:
                if pos_type == "BUY":
                    target_be = round(entry + 2.50, digits)
                    if current_sl < target_be:
                        new_sl = target_be
                        modified = True
                        event_reason = "PROFIT_LOCK_25PIPS"
                elif pos_type == "SELL":
                    target_be = round(entry - 2.50, digits)
                    if current_sl > target_be or current_sl == 0:
                        new_sl = target_be
                        modified = True
                        event_reason = "PROFIT_LOCK_25PIPS"

            # 2. Dynamic ATR Trailing Stop (Trail behind current price)
            if modified or profit >= (self.breakeven_profit_usd * 1.5):
                trail_dist = max(current_atr * self.atr_trail_mult, 2.0)
                if pos_type == "BUY":
                    trail_sl = round(current_price - trail_dist, digits)
                    if trail_sl > new_sl:
                        new_sl = trail_sl
                        modified = True
                        event_reason = "TRAILING_STOP"
                elif pos_type == "SELL":
                    trail_sl = round(current_price + trail_dist, digits)
                    if new_sl == 0 or trail_sl < new_sl:
                        new_sl = trail_sl
                        modified = True
                        event_reason = "TRAILING_STOP"

            if modified and new_sl != current_sl:
                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": symbol,
                    "position": ticket,
                    "sl": new_sl,
                    "tp": current_tp,
                    "magic": pos["Magic"]
                }
                result = mt5.order_send(request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"[Trailing Stop] Updated SL to ${new_sl} for Ticket #{ticket} ({event_reason})")
                    updates.append({
                        "Ticket": ticket,
                        "Type": pos_type,
                        "Reason": event_reason,
                        "Old_SL": current_sl,
                        "New_SL": new_sl,
                        "Profit_USD": profit
                    })
                else:
                    logger.warning(f"[Trailing Stop] Failed to update SL for #{ticket}: {result.comment if result else 'Unknown error'}")

        return updates

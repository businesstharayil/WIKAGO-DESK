"""Helpers for business-scoped queries."""
from datetime import datetime, timezone
from fastapi import HTTPException
from .db import get_sb
from .auth import CurrentUser


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def assert_business(business_id: str, user: CurrentUser) -> dict:
    """Verify the business belongs to the current user; return the row."""
    sb = get_sb()
    res = sb.table("businesses").select("*").eq("id", business_id).eq("owner_id", user.id).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Business not found")
    return res.data[0]


def calc_order_totals(o: dict) -> dict:
    """Calculate revenue, total_cost, net_profit from order fields."""
    qty = float(o.get("qty") or 0)
    selling_price = float(o.get("selling_price") or 0)
    cost_per_unit = float(o.get("cost_per_unit") or 0)
    shipping = float(o.get("shipping") or 0)
    cod_fee = float(o.get("cod_fee") or 0)
    platform_fee = float(o.get("platform_fee") or 0)
    ad_spend = float(o.get("ad_spend") or 0)
    returns = float(o.get("returns") or 0)
    other = float(o.get("other_deductions") or 0)
    gst_pct = float(o.get("gst_pct") or 0)
    gst_mode = o.get("gst_mode") or "exclusive"

    gross = qty * selling_price
    # GST: if inclusive, the gross already contains GST -> revenue = gross / (1 + g/100). If exclusive, revenue = gross (GST is added on top from customer but not affecting our net).
    if gst_mode == "inclusive" and gst_pct > 0:
        revenue = gross / (1 + gst_pct / 100.0)
    else:
        revenue = gross

    product_cost = qty * cost_per_unit
    total_cost = product_cost + shipping + cod_fee + platform_fee + ad_spend + returns + other
    net_profit = revenue - total_cost

    return {
        "revenue": round(revenue, 2),
        "total_cost": round(total_cost, 2),
        "net_profit": round(net_profit, 2),
    }


def adjust_inventory_stock(business_id: str, inventory_id: str, delta: float, reason: str, note: str | None = None):
    """Increment/decrement stock and append history entry."""
    sb = get_sb()
    inv = sb.table("inventory").select("*").eq("id", inventory_id).eq("business_id", business_id).limit(1).execute()
    if not inv.data:
        return None
    item = inv.data[0]
    new_stock = float(item.get("stock") or 0) + delta
    history = item.get("stock_history") or []
    history.append({
        "ts": now_iso(),
        "delta": delta,
        "new_stock": new_stock,
        "reason": reason,
        "note": note,
    })
    sb.table("inventory").update({
        "stock": new_stock,
        "stock_history": history,
        "updated_at": now_iso(),
    }).eq("id", inventory_id).execute()
    return new_stock

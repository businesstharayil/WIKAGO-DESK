"""Pydantic models for WIKAGO API.
All models use simple field names matching Supabase table columns.
"""
from datetime import date, datetime
from typing import Any, Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------------- AUTH ----------------
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleSessionRequest(BaseModel):
    session_id: str


class AuthResponse(BaseModel):
    token: str
    user: dict


# ---------------- BUSINESS ----------------
class BusinessCreate(BaseModel):
    name: str
    business_type: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    default_gst_pct: Optional[float] = 0
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc: Optional[str] = None
    upi_id: Optional[str] = None
    currency_symbol: Optional[str] = "₹"
    accent_color: Optional[str] = "indigo"
    fixed_monthly_costs: Optional[float] = 0
    theme: Optional[str] = "light"


class BusinessUpdate(BusinessCreate):
    name: Optional[str] = None  # type: ignore


# ---------------- INVENTORY ----------------
class InventoryCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    selling_price: float = 0
    retail_price: float = 0
    cost_price: float = 0
    stock: float = 0
    low_alert: float = 5
    supplier_name: Optional[str] = None
    supplier_phone: Optional[str] = None
    supplier_lead_days: Optional[int] = 0
    supplier_moq: Optional[int] = 0
    supplier_notes: Optional[str] = None


class InventoryUpdate(InventoryCreate):
    name: Optional[str] = None  # type: ignore


class StockAdjustRequest(BaseModel):
    delta: float
    note: Optional[str] = None
    reason: Optional[str] = "Adjustment"


# ---------------- ORDERS ----------------
class OrderCreate(BaseModel):
    inventory_id: Optional[str] = None
    product_name: str
    qty: float = 1
    selling_price: float = 0
    cost_per_unit: float = 0
    payment_type: str = "COD"
    shipping: float = 0
    cod_fee: float = 0
    platform_fee: float = 0
    ad_spend: float = 0
    returns: float = 0
    other_deductions: float = 0
    gst_pct: float = 0
    gst_mode: str = "exclusive"
    channel: str = "Other"
    aggregator: Optional[str] = ""
    courier: Optional[str] = ""
    customer_name: Optional[str] = None
    awb: Optional[str] = None
    notes: Optional[str] = None
    order_date: Optional[date] = None


class OrderUpdate(OrderCreate):
    product_name: Optional[str] = None  # type: ignore


class BulkOrderCreate(BaseModel):
    order: OrderCreate
    count: int = Field(ge=1, le=100)


# ---------------- PURCHASES ----------------
class PurchaseItem(BaseModel):
    inventory_id: Optional[str] = None
    name: str
    qty: float = 1
    cost: float = 0


class PurchaseCreate(BaseModel):
    supplier_name: Optional[str] = None
    supplier_phone: Optional[str] = None
    supplier_gstin: Optional[str] = None
    invoice_number: Optional[str] = None
    purchase_date: Optional[date] = None
    address: Optional[str] = None
    items: List[PurchaseItem] = []
    shipping_total: float = 0
    other_charges: float = 0
    gst_pct: float = 0
    payment_mode: str = "Paid"
    amount_paid: float = 0
    notes: Optional[str] = None


# ---------------- REMITTANCE ----------------
class RemittanceCreate(BaseModel):
    channel: str = "Other"
    amount: float = 0
    reference: Optional[str] = None
    status: str = "Pending"
    remit_date: Optional[date] = None
    notes: Optional[str] = None


class RemittanceUpdate(BaseModel):
    channel: Optional[str] = None
    amount: Optional[float] = None
    reference: Optional[str] = None
    status: Optional[str] = None
    remit_date: Optional[date] = None
    notes: Optional[str] = None


# ---------------- MISC ----------------
class MiscCreate(BaseModel):
    name: str
    type: str = "expense"  # income | expense
    category: str = "Other"
    amount: float = 0
    entry_date: Optional[date] = None
    notes: Optional[str] = None


# ---------------- TEMPLATE / DRAFT ----------------
class TemplateCreate(BaseModel):
    name: str
    config: dict


class DraftCreate(BaseModel):
    config: dict


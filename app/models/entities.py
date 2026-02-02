
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class InventoryItem:
    id: int
    part_name: str
    category: str
    brand: str = ""
    model_number: str = ""
    quantity: int = 0
    cost_price: float = 0.0
    selling_price: float = 0.0
    supplier_id: Optional[int] = None
    supplier_name: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def profit_margin(self) -> float:
        if self.cost_price == 0:
            return 0
        return ((self.selling_price - self.cost_price) / self.cost_price) * 100
    
    @property
    def total_value(self) -> float:
        return self.quantity * self.selling_price
    
    @property
    def total_cost(self) -> float:
        return self.quantity * self.cost_price


@dataclass
class User:

    id: int
    username: str
    full_name: str
    email: str = ""
    role: str = "staff"
    password_hash: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Sale:
    id: int
    total: float
    user_id: Optional[int] = None
    vat_amount: float = 0.0
    payment_mode: str = "Cash"
    amount_received: float = 0.0
    change_amount: float = 0.0
    sale_date: Optional[datetime] = None
    items: list = field(default_factory=list)  


@dataclass
class SaleItem:
    id: int
    sale_id: int
    item_id: int
    quantity: int
    price: float
    item_name: str = ""


@dataclass
class Supplier:
    id: int
    name: str
    contact_person: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    city: str = ""
    country: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class StockMovement:

    id: int
    item_id: int
    movement_type: str
    quantity: int
    reason: str
    notes: str = ""
    user_id: Optional[int] = None
    movement_date: Optional[datetime] = None
    item_name: str = ""
    username: str = ""


@dataclass
class Category:
    id: int
    name: str
    description: str = ""


@dataclass
class ReportData:
    title: str
    data: list = field(default_factory=list)
    headers: list = field(default_factory=list)
    filters: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)

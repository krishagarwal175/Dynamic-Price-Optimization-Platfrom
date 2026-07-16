"""Idempotent demo seed for a fresh deployment.

Populates a believable catalog plus ~24 months of price-varying sales so the read-only
console shows real analytics (elasticity, forecasts, optimization) out of the box. Skips
entirely if any product already exists, so it is safe to run on every container start.

This is deployment/ops tooling — not application logic. Run: ``python scripts/seed.py``.
"""

from __future__ import annotations

import math
import random
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.database import create_db_engine, create_session_factory
from app.models.category import Category
from app.models.historical_sale import HistoricalSale
from app.models.product import Product

_CENTS = Decimal("0.01")
_MONTHS = 24

# sku, name, category, unit_cost, base_price, elasticity, reference monthly demand
_CATALOG = [
    ("NX-2200", "Titan Pro Sensor", "Industrial Sensors", "148.00", "249.00", -1.42, 1050),
    ("PL-900", "Pressure Logger", "Industrial Sensors", "210.00", "365.00", -1.05, 470),
    ("TS-410", "Thermal Shield", "Industrial Sensors", "19.50", "41.00", -1.30, 5200),
    ("HX-940", "Helix Actuator", "Motion Control", "820.00", "1290.00", -0.88, 180),
    ("MG-05", "Magnetic Coupler", "Motion Control", "33.00", "58.00", -1.75, 3100),
    ("AX-3", "Axis Encoder", "Motion Control", "95.00", "159.00", -1.55, 880),
    ("QV-118", "Quantum Valve", "Fluidics", "52.00", "89.50", -2.31, 2400),
    ("CR-77", "Cryo Regulator", "Fluidics", "260.00", "412.00", -1.10, 340),
]

_PRICE_FACTORS = [1.0, 1.0, 1.0, 0.9, 0.95, 1.05, 1.1, 0.85]


def _money(value: float) -> Decimal:
    return Decimal(str(value)).quantize(_CENTS, rounding=ROUND_HALF_UP)


def _month_start(anchor: date, months_back: int) -> date:
    total = anchor.year * 12 + (anchor.month - 1) - months_back
    return date(total // 12, total % 12 + 1, 1)


def main() -> None:
    settings = get_settings()
    engine = create_db_engine(settings)
    session = create_session_factory(engine)()
    rng = random.Random(42)
    try:
        existing = session.scalar(select(func.count()).select_from(Product)) or 0
        if existing:
            print(f"Seed skipped: {existing} product(s) already present.")
            return

        # Write in bulk (a handful of round-trips) so the seed stays fast even over a
        # high-latency database connection: categories → flush, products → flush, sales → commit.
        categories: dict[str, Category] = {}
        for _sku, _name, category_name, *_rest in _CATALOG:
            categories.setdefault(category_name, Category(name=category_name))
        session.add_all(list(categories.values()))
        session.flush()

        products: list[tuple[Product, float, int, float]] = []
        for sku, name, category_name, unit_cost, base_price, elasticity, ref_demand in _CATALOG:
            product = Product(
                category_id=categories[category_name].id,
                sku=sku,
                name=name,
                unit_cost=Decimal(unit_cost),
                base_price=Decimal(base_price),
                currency="USD",
            )
            products.append((product, elasticity, ref_demand, float(base_price)))
        session.add_all([product for product, _e, _rd, _base in products])
        session.flush()  # assign product ids

        anchor = date.today().replace(day=1)
        sales: list[HistoricalSale] = []
        for product, elasticity, ref_demand, base in products:
            for i in range(_MONTHS):
                factor = _PRICE_FACTORS[(i + hash(product.sku)) % len(_PRICE_FACTORS)]
                price = _money(base * factor)
                ratio = float(price) / base
                seasonal = 1.0 + 0.08 * math.sin(i / 2.0)
                demand = ref_demand * (ratio**elasticity) * seasonal * rng.uniform(0.9, 1.1)
                sales.append(
                    HistoricalSale(
                        product_id=product.id,
                        sale_date=_month_start(anchor, _MONTHS - 1 - i),
                        quantity=max(0, int(round(demand))),
                        unit_price=price,
                    )
                )
        session.add_all(sales)
        session.commit()
        products = session.scalar(select(func.count()).select_from(Product)) or 0
        sales = session.scalar(select(func.count()).select_from(HistoricalSale)) or 0
        print(f"Seeded {products} products and {sales} sales records.")
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    main()

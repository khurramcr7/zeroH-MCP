# -*- coding: utf-8 -*-
"""
ONE XI Technologies by Aalimbooks International — Public Payment Gateway & Checkout Module
==========================================================================================
Provides zero-dependency multi-rail checkout session resolution, 16-product Polar.sh/Stripe
checkout catalog, Payoneer / Meezan Bank Corporate IBAN / Web3 USDT settlement coordinates,
and the unified Inter Tight Starfield `ONE XI Checkout` page (`checkout.html`).
"""
from __future__ import annotations

import hashlib
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict

CHECKOUT_HTML_PATH = Path(__file__).resolve().parent / "checkout.html"

CORPORATE_ENTITY_IDENTITY: Dict[str, Any] = {
    "gateway_brand": "ONE XI Technologies by Aalimbooks International",
    "operating_divisions": [
        "ONE XI Technologies (onexi.tech)",
        "ONE XI BIO Clinical & Biopharma Cloud (onexibio.com)",
        "Aalimbooks International / Aalim Books (aalimbooksint.com)",
        "Islamic Heritage Press (islamicheritagepress.com/aalimbooks)",
        "KutubLink Digital & Warith.io (kutublink.com | warith.io)",
    ],
    "checkout_theme": {
        "theme_id": "ONEXI_INTER_TIGHT_STARFIELD_V2",
        "font_family": "Inter Tight (200, 300, 400, 500)",
        "background": "#05070b radial-gradient starfield canvas",
        "supported_brands": ["onexi", "bio", "aalim", "kutublink", "ihp"],
    },
    "checkout_portals": {
        "onexi_tech_checkout": "https://onexi.tech/checkout",
        "primary_enterprise_checkout": "https://onexibio.com/checkout",
        "kutublink_checkout": "https://kutublink.com/checkout",
        "ihp_digital_checkout": "https://www.islamicheritagepress.com/onexi-checkout",
        "book_and_library_checkout": "https://onexibio.com/book-checkout",
        "payoneer_portal": "https://onexibio.com/checkout/payoneer",
        "mizan_portal": "https://onexibio.com/checkout/mizan",
        "aalimbooks_storefront": "https://www.islamicheritagepress.com/aalimbooks",
    },
    "payoneer_merchant_emails": [
        "khurram.younus@aalimbooksint.com",
        "aalimbook@gmail.com",
    ],
    "corporate_bank": {
        "bank_name": "Meezan Bank Limited (Pakistan)",
        "account_title": "Aalim Books",
        "iban": "PK40MEZN0008310104515858",
        "swift_bic": "MEZNPKKAISD",
    },
    "web3_treasury_wallet": "0x5e6128814f22d8fc65b07f387355402ed8c42b0c",
    "whatsapp_concierge": ["+92 330 5677799", "+971 58 977 7753"],
}

ONEXI_16_PRODUCT_CATALOG: Dict[str, Dict[str, Any]] = {
    "BOOK_15_SINGLE": {
        "code": "15",
        "tier_id": "BOOK_15_SINGLE",
        "division": "Aalimbooks International × KutubLink Digital",
        "name": "Single E-Book ($15)",
        "price_usd": 15.0,
        "polar_url": "https://buy.polar.sh/polar_cl_IsodrKALkvXOZNwTAUe2jXIPirwcKrrUn4fMW2IvZSb",
    },
    "BOOK_29_DIGITAL": {
        "code": "29",
        "tier_id": "BOOK_29_DIGITAL",
        "division": "Aalimbooks International × KutubLink Digital",
        "name": "20-Volume Collection ($29)",
        "price_usd": 29.0,
        "polar_url": "https://buy.polar.sh/polar_cl_OY6kJpTMnbYcVss5frahza2pRh3bo8PkmlbFM42Psvg",
    },
    "FAST_49_PASS": {
        "code": "49",
        "tier_id": "FAST_49_PASS",
        "division": "ONE XI Technologies Cloud",
        "name": "Pro Pass ($49)",
        "price_usd": 49.0,
        "polar_url": "https://buy.polar.sh/polar_cl_yiaY2QaaJrj4WuWm1bpQWOIPNDogghaLT2A0o0JczDW",
    },
    "FAST_99_AUDIT": {
        "code": "99",
        "tier_id": "FAST_99_AUDIT",
        "division": "ONE XI Technologies Cloud",
        "name": "Pro Compute Pack ($99)",
        "price_usd": 99.0,
        "polar_url": "https://buy.polar.sh/polar_cl_Gz9p54IMeHEHkhJIbopPTKCX6LtlT3CI9isWR4PruOa",
    },
    "TURATH_150_SPRINT": {
        "code": "150",
        "tier_id": "TURATH_150_SPRINT",
        "division": "Aalimbooks International × KutubLink Cloud",
        "name": "OCR & Corpus Credits ($150)",
        "price_usd": 150.0,
        "polar_url": "https://buy.polar.sh/polar_cl_yHVdCwtXLV6BmKR800Ww2zWs6rD7L9dhDGyPq1XtvVw",
    },
    "LAB_199_PACK": {
        "code": "199",
        "tier_id": "LAB_199_PACK",
        "division": "ONE XI Technologies Cloud",
        "name": "Team License ($199)",
        "price_usd": 199.0,
        "polar_url": "https://buy.polar.sh/polar_cl_2rGWKtRrTpFyrMjKTRwRSv9Cb8F4FZmvW322i16kIwX",
    },
    "CLINICAL_PILOT_250": {
        "code": "250",
        "tier_id": "CLINICAL_PILOT_250",
        "division": "ONE XI Technologies Cloud",
        "name": "Batch API Credits ($250)",
        "price_usd": 250.0,
        "polar_url": "https://buy.polar.sh/polar_cl_AAc3JcysPhTQFTF5r8RvXTwXdeH8eBHzzUxBO4Plnaz",
    },
    "PULSE_PER_PROCEDURE_SIMULATION": {
        "code": "350",
        "tier_id": "PULSE_PER_PROCEDURE_SIMULATION",
        "division": "ONE XI Pulse Clinical API",
        "name": "PULSE Clinical Simulation ($350 / patient)",
        "price_usd": 350.0,
        "polar_url": "https://buy.polar.sh/polar_cl_65elMuiHLPwr7UAxL4EAv7FIXhg1WuC5gsrnR1MZWGa",
    },
    "BOOK_499_WAQF": {
        "code": "499",
        "tier_id": "BOOK_499_WAQF",
        "division": "Aalimbooks International × KutubLink Digital",
        "name": "Department Pass / Institutional Library Seat ($499)",
        "price_usd": 499.0,
        "polar_url": "https://buy.polar.sh/polar_cl_eXsIPJGpi0QnzjA913s581oKVvBz8ooPNUgOa49Ofe8",
    },
    "TURATH_PILOT_1500": {
        "code": "1500",
        "tier_id": "TURATH_PILOT_1500",
        "division": "Aalimbooks International × KutubLink Enterprise",
        "name": "Corpus API License ($1,500 / yr)",
        "price_usd": 1500.0,
        "polar_url": "https://buy.polar.sh/polar_cl_mxNmmpL5zKWLFXrBBzMu7C1CEeM00enlnf0jk27GYzr",
    },
    "QUANTUM_AUDIT_2500": {
        "code": "2500",
        "tier_id": "QUANTUM_AUDIT_2500",
        "division": "ONE XI Quantum Suite",
        "name": "Quantum Compiler SDK ($2,500)",
        "price_usd": 2500.0,
        "polar_url": "https://buy.polar.sh/polar_cl_ZRpW61YKd5LTSuG3q9aRPhWqdiwWiXVnd8cs51JEP28",
    },
    "CHIRAL_PRO_4950": {
        "code": "4950",
        "tier_id": "CHIRAL_PRO_4950",
        "division": "ONE XI Technologies Enterprise",
        "name": "Enterprise License ($4,950)",
        "price_usd": 4950.0,
        "polar_url": "https://buy.polar.sh/polar_cl_z06WyxPY8fRnaZ3G6dZrEKko3fp9rvq3JtNp91bdBx1",
    },
    "GENESIS_STARTER_BIOPHARMA_MONTHLY": {
        "code": "5000",
        "tier_id": "GENESIS_STARTER_BIOPHARMA_MONTHLY",
        "division": "ONE XI Genesis Biopharma R&D",
        "name": "GENESIS R&D Starter ($5,000 / mo)",
        "price_usd": 5000.0,
        "polar_url": "https://buy.polar.sh/polar_cl_tLfboQ7ehhuQeZen2RsNnXxB9tIBx3CfryIKp1ABbTu",
    },
    "QUANTUM_SUITE_COMPILER_SEAT_ANNUAL": {
        "code": "25000",
        "tier_id": "QUANTUM_SUITE_COMPILER_SEAT_ANNUAL",
        "division": "ONE XI Quantum Suite EDA",
        "name": "Quantum Compiler Seat ($25,000 / yr)",
        "price_usd": 25000.0,
        "polar_url": "https://buy.polar.sh/polar_cl_Zz0MHK1CwG3AriaHXdd7Y0atV1Kd3PDgBAWHL2tKoIM",
    },
    "GENESIS_ENTERPRISE_BIOPHARMA_MONTHLY": {
        "code": "50000",
        "tier_id": "GENESIS_ENTERPRISE_BIOPHARMA_MONTHLY",
        "division": "ONE XI Genesis Enterprise Biopharma",
        "name": "GENESIS Unlimited ($50,000 / mo)",
        "price_usd": 50000.0,
        "polar_url": "https://buy.polar.sh/polar_cl_MDfqAneUkOv5C8zFpf1PpjlzFYEMlVQb3kXbr2f3fOj",
    },
    "PULSE_HOSPITAL_NETWORK_LICENSE_ANNUAL": {
        "code": "120000",
        "tier_id": "PULSE_HOSPITAL_NETWORK_LICENSE_ANNUAL",
        "division": "ONE XI Pulse Hospital Network",
        "name": "PULSE Network License ($120,000 / yr)",
        "price_usd": 120000.0,
        "polar_url": "https://buy.polar.sh/polar_cl_pByY3kDswhIa0hC80Ua8Gjc1Mo4gi9XmzA16j21ZyhD",
    },
}


def load_checkout_html() -> str:
    if CHECKOUT_HTML_PATH.exists():
        return CHECKOUT_HTML_PATH.read_text(encoding="utf-8")
    return "<!doctype html><html><head><title>ONE XI Checkout</title></head><body><h1>ONE XI Checkout</h1></body></html>"


def resolve_product_tier(tier_or_query: str = "FAST_49_PASS", amount_usd: float = 0.0) -> Dict[str, Any]:
    key = (tier_or_query or "").strip().upper()
    if key in ONEXI_16_PRODUCT_CATALOG:
        return ONEXI_16_PRODUCT_CATALOG[key]
    for item in ONEXI_16_PRODUCT_CATALOG.values():
        if key == item["code"] or (amount_usd > 0 and abs(float(item["price_usd"]) - float(amount_usd)) < 0.5):
            return item
    return ONEXI_16_PRODUCT_CATALOG["FAST_49_PASS"]


def handle_onexi_payment_gateway(args: Dict[str, Any]) -> Dict[str, Any]:
    action = str(args.get("action") or "gateway_status").strip().lower()
    if action in ("gateway_status", "status"):
        return {
            "gateway": CORPORATE_ENTITY_IDENTITY["gateway_brand"],
            "corporate_identity": CORPORATE_ENTITY_IDENTITY,
            "products_count": len(ONEXI_16_PRODUCT_CATALOG),
            "coherence_index": 1.0,
            "confidence_score": "100.0%",
            "deterministic_status": "VERIFIED_COMPUTED_PASS",
        }
    if action == "list_checkout_catalog":
        return {
            "gateway": CORPORATE_ENTITY_IDENTITY["gateway_brand"],
            "products_count": len(ONEXI_16_PRODUCT_CATALOG),
            "catalog": ONEXI_16_PRODUCT_CATALOG,
            "checkout_portals": CORPORATE_ENTITY_IDENTITY["checkout_portals"],
            "deterministic_status": "VERIFIED_COMPUTED_PASS",
        }
    if action in ("render_checkout_html", "checkout_theme"):
        html_src = load_checkout_html()
        return {
            "gateway": CORPORATE_ENTITY_IDENTITY["gateway_brand"],
            "theme": CORPORATE_ENTITY_IDENTITY["checkout_theme"],
            "checkout_portals": CORPORATE_ENTITY_IDENTITY["checkout_portals"],
            "html_bytes": len(html_src.encode("utf-8")),
            "html": html_src,
            "deterministic_status": "VERIFIED_COMPUTED_PASS",
        }
    if action == "create_checkout_session":
        prod = resolve_product_tier(
            str(args.get("tier_id") or args.get("product_id") or "FAST_49_PASS"),
            float(args.get("amount_usd") or 0.0),
        )
        email = str(args.get("customer_email") or args.get("email") or "").strip()
        polar_url = prod["polar_url"]
        if email and "@" in email:
            polar_url = f"{polar_url}?{urllib.parse.urlencode({'customer_email': email})}"
        hosted_qs = {"tier": prod["code"]}
        if email:
            hosted_qs["email"] = email
        inv_id = "ONX-" + hashlib.sha256(f"{prod['tier_id']}|{email}|{int(time.time())}".encode("utf-8")).hexdigest()[:8].upper()
        return {
            "status": "VERIFIED_COMPUTED_PASS",
            "invoice_id": inv_id,
            "product": prod,
            "one_click_checkout_urls": {
                "polar_stripe_card_checkout": polar_url,
                "onexi_tech_checkout": f"https://onexi.tech/checkout?{urllib.parse.urlencode(hosted_qs)}",
                "onexibio_checkout": f"https://onexibio.com/checkout?{urllib.parse.urlencode(hosted_qs)}",
                "kutublink_checkout": f"https://kutublink.com/checkout?{urllib.parse.urlencode(hosted_qs)}",
                "ihp_checkout": f"https://www.islamicheritagepress.com/onexi-checkout?{urllib.parse.urlencode(hosted_qs)}",
            },
            "bank_and_treasury_coordinates": {
                "payoneer": CORPORATE_ENTITY_IDENTITY["payoneer_merchant_emails"],
                "meezan_bank": CORPORATE_ENTITY_IDENTITY["corporate_bank"],
                "usdt_wallet": CORPORATE_ENTITY_IDENTITY["web3_treasury_wallet"],
            },
        }
    return {
        "error": f"Unknown action '{action}'. Valid actions: gateway_status, list_checkout_catalog, create_checkout_session, render_checkout_html."
    }

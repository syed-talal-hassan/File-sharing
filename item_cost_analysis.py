from __future__ import unicode_literals
from dataclasses import fields
from email.policy import default
import frappe
from frappe import _
from frappe.utils import flt
import erpnext


def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_data(filters):
    final_row = []

    # conditions = {}
    # if filters.get("docstatus"):
    #     conditions["status"]: filters.get("docstatus")
    # if filters.get("exc_non_exc"):
    #     conditions["exc_non_exc"] = filters.get("exc_non_exc")
    # if filters.get("department"):
    #     conditions["department"] = filters.get("department")
    # if filters.get("from_date"):
    #     conditions["start_date"] = filters.get("from_date")
    # if filters.get("to_date"):
    #     conditions["end_date"] = filters.get("to_date")
    # if filters.get("mode_of_payment"):
    #     conditions["mode_of_payment"] = filters.get("mode_of_payment")
    # if filters.get("employee"):
    #     conditions["employee"] = filters.get("employee")

    PR = frappe.db.get_all(
        "Purchase Receipt", fields=['name'])
    for pr in PR:
        data = frappe.get_doc("Purchase Receipt", pr.name)
        if data.items:
            for item in data.items:
                incoming_rate = frappe.db.get_value(
                    "Stock Ledger Entry", {"item_code": item.item_code}, 'incoming_rate')
                excr_euro = frappe.db.get_value("Currency Exchange", {"date":frappe.utils.getdate(), "for_buying": 1, "from_currency": "EUR"}, "exchange_rate")
                excr_dollar = frappe.db.get_value("Currency Exchange", {"date":frappe.utils.getdate(), "for_buying": 1, "from_currency": "USD"}, "exchange_rate")
                margin_profit_percent = frappe.db.get_value("Item Price", {"item_code": item.item_code, "buying": 1}, "margin_profit_percent")

                final_row.append({
                    # col 1
                    "item_code": item.item_code,
                    # col 2
                    "item_name": item.item_name,
                    # col 3
                    "item_group": item.item_group,
                    # col 4
                    "item_brand": item.brand,
                    # col 5
                    "voucher_type": "Purchase Receipt",
                    # col 6
                    "voucher_no": data.name,
                    # col 7
                    "voucher_cur": data.currency,
                    # col 8
                    "price_list_buying": round(item.buying_price_list, 2),
                    # col 9
                    "price_list_rate": round(item.price_list_rate, 2),
                    # col 10
                    "rate": round(item.rate, 2),
                    # col 11
                    "discount_percent": item.discount_percentage,
                    # col 12
                    "discount_amnt": round(item.discount_amount, 2),
                    # col 13 - [col 17 / col 15]
                    "lcv": round(item.landed_cost_voucher_amount, 2) / data.conversion_factor,
                    # col 14 - [col 18 / col 15]
                    "incoming_rate": round(incoming_rate, 2) / data.conversion_factor,
                    # col 15
                    "excr": data.conversion_factor,
                    # col 16
                    "rate_egp": round(item.base_rate, 2),
                    # col 17
                    "lcv_egp": round(item.landed_cost_voucher_amount, 2),
                    # col 18
                    "incoming_rate_egp": round(incoming_rate, 2),
                    # col 19
                    "valuation_rate": round(item.valuation_rate, 2),
                    # col 20 - [col 17 / col 16]
                    "cost": round(item.landed_cost_voucher_amount, 2) / round(item.base_rate, 2),
                    # col 21 - value from Currency Exchange
                    "excr_euro": round(excr_euro, 2),
                    # col 22 - value from Currency Exchange
                    "excr_dollar": round(excr_dollar, 2),
                    # col 23 - [value to be fetched from Item Price]
                    "profit_margin": margin_profit_percent,
                    # col 24 - [(col 10) * (1 + col 20) * (1 + col 23)]
                    "selling_price": round(item.rate, 2) * (1 + (round(item.landed_cost_voucher_amount, 2) / round(item.base_rate, 2))) * (1 + margin_profit_percent),
                    # col 25 - [if {col 7 = EUR} then {(col 10) * (1 + col 20) * (1 + col 23) * (col 21)} else if { col 7 = USD} then {(col 10) * (1 + col 20) * (1 + col 23) * (col 22)}]
                    "selling_price_egp": round(item.rate, 2) * (1 + (round(item.landed_cost_voucher_amount, 2) / round(item.base_rate, 2))) * (1 + margin_profit_percent) * (round(excr_euro, 2)) if data.currency == "EUR" else round(item.rate, 2) * (1 + (round(item.landed_cost_voucher_amount, 2) / round(item.base_rate, 2))) * (1 + margin_profit_percent) * (round(excr_dollar, 2)),
                    # col 26 - needs to update the value from Item Price [if {price list = selling & currency = EUR}]
                    "price_list_rate_euro": round(price_list_rate, 2),
                    # col 27 - needs to update the value from Item Price [if {price list = selling & currency = USD}]
                    "price_list_rate_dollar": round(price_list_rate, 2),
                    # col 28 - needs to update the value from Item Price [if {price list = selling & currency = EGP}]
                    "price_list_rate_egp": round(price_list_rate, 2),
                })

    return final_row


def get_columns(filters):
    columns = [
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150
        },
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 240
        },
        {
            "label": _("Item Group"),
            "fieldname": "item_group",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": _("Brand"),
            "fieldname": "item_brand",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": _("Voucher Type"),
            "fieldname": "voucher_type",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Voucher No."),
            "fieldname": "voucher_no",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Voucher Currency"),
            "fieldname": "voucher_cur",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Price List"),
            "fieldname": "price_list_buying",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Price"),
            "fieldname": "price_list_rate",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Rate"),
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Discount %"),
            "fieldname": "discount_percent",
            "fieldtype": "Data",
            "width": 70
        },
        {
            "label": _("Discount"),
            "fieldname": "discount_amnt",
            "fieldtype": "Currency",
            "width": 90
        },
        {
            "label": _("LCV"),
            "fieldname": "lcv",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Incoming Rate"),
            "fieldname": "incoming_rate",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("EXCR"),
            "fieldname": "excr",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Rate EGP"),
            "fieldname": "rate_egp",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("LCV EGP"),
            "fieldname": "lcv_egp",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("Incoming Rate EGP"),
            "fieldname": "incoming_rate_egp",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("Valuation Rate"),
            "fieldname": "valuation_rate",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("Cost"),
            "fieldname": "cost",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("EXCR Euro"),
            "fieldname": "excr_euro",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("EXCR Dollar"),
            "fieldname": "excr_dollar",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("Profit Margin"),
            "fieldname": "profit_margin",
            "fieldtype": "Data",
            "width": 50
        },
        {
            "label": _("Selling Price"),
            "fieldname": "selling_price",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("Selling Price EGP"),
            "fieldname": "selling_price_egp",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": _("Price List Rate Euro"),
            "fieldname": "price_list_rate_euro",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("Price List Rate Dollar"),
            "fieldname": "price_list_rate_dollar",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("Price List Rate EGP"),
            "fieldname": "price_list_rate_egp",
            "fieldtype": "Currency",
            "width": 140
        }
    ]
    return columns

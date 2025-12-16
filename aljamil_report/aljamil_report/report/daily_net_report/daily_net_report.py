# Copyright (c) 2025, abdopcnet@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "branch",
            "label": _("Branch"),
            "fieldtype": "Link",
            "options": "Branch",
            "width": 180,
        },
        {
            "fieldname": "total_sales",
            "label": _("Total Sales"),
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "total_purchases",
            "label": _("Total Purchases"),
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "fieldname": "net_amount",
            "label": _("Net Amount"),
            "fieldtype": "Currency",
            "width": 140,
        },
    ]


def get_data(filters):
    if not filters.get("from_date") or not filters.get("to_date"):
        frappe.throw(_("From Date and To Date are required."))

    conditions = ""
    if filters.get("branch"):
        conditions += " AND pe.branch = %(branch)s"

    query = f"""
        SELECT
            pe.branch AS branch,
            SUM(CASE WHEN pe.payment_type = 'Receive' THEN pe.paid_amount ELSE 0 END) AS total_sales,
            SUM(CASE WHEN pe.payment_type = 'Pay' THEN pe.paid_amount ELSE 0 END) AS total_purchases,
            (
                SUM(CASE WHEN pe.payment_type = 'Receive' THEN pe.paid_amount ELSE 0 END)
                - SUM(CASE WHEN pe.payment_type = 'Pay' THEN pe.paid_amount ELSE 0 END)
            ) AS net_amount
        FROM `tabPayment Entry` pe
        WHERE
            pe.docstatus = 1
            AND pe.posting_date >= %(from_date)s
            AND pe.posting_date <= %(to_date)s
            {conditions}
        GROUP BY pe.branch
        ORDER BY pe.branch
    """

    return frappe.db.sql(query, filters, as_dict=True)

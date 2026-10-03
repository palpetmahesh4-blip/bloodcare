from datetime import date
from html import escape

import streamlit.components.v1 as components

TEMPLATE = """
<html>
<head>
<style>
    body { font-family: Arial, Helvetica, sans-serif; color: #1B2A41; margin: 0; padding: 16px; }
    .brand { color: #B3122D; font-size: 20px; font-weight: 700; }
    h1 { font-size: 20px; margin: 4px 0 2px 0; }
    .meta { color: #6B7280; font-size: 12px; margin-bottom: 14px; }
    table.rep { width: 100%; border-collapse: collapse; font-size: 12px; }
    table.rep th { background: #1B2A41; color: #FFFFFF; text-align: left; padding: 6px 8px; }
    table.rep td { border-bottom: 1px solid #E5E7EB; padding: 6px 8px; }
    table.rep tr:nth-child(even) td { background: #F5F6F8; }
    thead { display: table-header-group; }
    tr { page-break-inside: avoid; }
    .btn {
        background: #B3122D; color: #FFFFFF; border: none; border-radius: 8px;
        padding: 8px 16px; font-size: 14px; font-weight: 600; cursor: pointer; margin-bottom: 12px;
    }
    @media print { .no-print { display: none; } }
</style>
</head>
<body>
    <button class="btn no-print" onclick="window.print()">🖨️ Print this report</button>
    <div class="brand">🩸 BloodBank Pro</div>
    <h1>%TITLE%</h1>
    <div class="meta">%META%</div>
    %TABLE%
</body>
</html>
"""


def render_print_view(df, title, date_from, date_to, blood_group, height=650):
    meta = (
        f"Period: {date_from} to {date_to} | Blood group: {blood_group} | "
        f"Records: {len(df)} | Generated on: {date.today().isoformat()}"
    )
    table_html = df.to_html(index=False, border=0, classes="rep", na_rep="-")
    html = (
        TEMPLATE
        .replace("%TITLE%", escape(title))
        .replace("%META%", escape(meta))
        .replace("%TABLE%", table_html)
    )
    components.html(html, height=height, scrolling=True)
#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
📊 COSTOMENU DATABASE ANALYTICS - PAGE 2: REVENUE ANALYSIS BY LICENSE TYPE
═══════════════════════════════════════════════════════════════════════════════

SQL Query Equivalent:
    SELECT 
      u.license_type,
      COUNT(p.id) as total_payments,
      SUM(p.amount) as total_revenue,
      ROUND(AVG(p.amount), 2) as avg_payment
    FROM users u
    JOIN payments p ON u.id = p.user_id
    GROUP BY u.license_type
    ORDER BY total_revenue DESC;

Purpose:
    Analyze revenue contribution by license type to identify highest-value
    customer segments and understand payment patterns.

Navigation:
    • Page 1: License Type Distribution
    • Page 2: Revenue Analysis (YOU ARE HERE)
    
Last Updated: 2026-01-26
═══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Configuration
USER_SUMMARY_CSV = Path(__file__).parent / "UserSummary_1769434497556.csv"
OUTPUT_JSON = Path(__file__).parent / "page_02_revenue_analysis.json"


def analyze_revenue():
    """Execute revenue analysis by license type."""
    
    print("=" * 80)
    print("📊 COSTOMENU DATABASE ANALYTICS - PAGE 2")
    print("=" * 80)
    print("ANALYSIS: Revenue Analysis by License Type")
    print("DATE:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    print()
    
    # Load data
    df = pd.read_csv(USER_SUMMARY_CSV)
    
    # Filter users with payment data
    df_with_payments = df[df['Total payments amount'].notna() & (df['Total payments amount'] > 0)].copy()
    
    total_revenue = df_with_payments['Total payments amount'].sum()
    total_users_with_payments = len(df_with_payments)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 1: REVENUE BY LICENSE TYPE
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("┌" + "─" * 78 + "┐")
    print("│ SQL QUERY RESULTS: Revenue by License Type" + " " * 33 + "│")
    print("├" + "─" * 78 + "┤")
    
    # Group by license type
    revenue_summary = df_with_payments.groupby('License').agg({
        'User id': 'count',
        'Total payments amount': ['sum', 'mean']
    }).round(2)
    
    revenue_summary.columns = ['total_payments', 'total_revenue', 'avg_payment']
    revenue_summary = revenue_summary.sort_values('total_revenue', ascending=False)
    
    # Display results
    print(f"│ {'License Type':<20} {'Payments':>12} {'Total Revenue':>15} {'Avg Payment':>15} │")
    print("├" + "─" * 78 + "┤")
    
    results_data = []
    for license_type, row in revenue_summary.iterrows():
        payments = int(row['total_payments'])
        revenue = row['total_revenue']
        avg = row['avg_payment']
        pct = (revenue / total_revenue * 100)
        
        print(f"│ {license_type:<20} {payments:>12,} €{revenue:>14,.2f} €{avg:>14,.2f} │")
        
        results_data.append({
            'license_type': license_type,
            'total_payments': payments,
            'total_revenue': round(revenue, 2),
            'avg_payment': round(avg, 2),
            'revenue_percentage': round(pct, 1)
        })
    
    print("├" + "─" * 78 + "┤")
    print(f"│ {'TOTAL':<20} {total_users_with_payments:>12,} €{total_revenue:>14,.2f} {' ':>15} │")
    print("└" + "─" * 78 + "┘")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 2: REVENUE CONTRIBUTION
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("┌" + "─" * 78 + "┐")
    print("│ REVENUE CONTRIBUTION BY LICENSE TYPE" + " " * 40 + "│")
    print("├" + "─" * 78 + "┤")
    
    for license_type, row in revenue_summary.iterrows():
        revenue = row['total_revenue']
        pct = (revenue / total_revenue * 100)
        bar_length = int(pct / 2)
        bar = "█" * bar_length
        
        print(f"│ {license_type:<20} {pct:>6.1f}% {bar:<30} │")
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 3: KEY INSIGHTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("┌" + "─" * 78 + "┐")
    print("│ 💡 KEY INSIGHTS" + " " * 61 + "│")
    print("├" + "─" * 78 + "┤")
    
    insights = []
    
    # Top revenue generator
    top_license = revenue_summary.index[0]
    top_revenue = revenue_summary.iloc[0]['total_revenue']
    top_pct = (top_revenue / total_revenue * 100)
    insight_1 = f"💰 {top_license} generates {top_pct:.1f}% of total revenue (€{top_revenue:,.2f})"
    insights.append(insight_1)
    print(f"│ {insight_1:<76} │")
    
    # Highest average payment
    highest_avg_license = revenue_summary['avg_payment'].idxmax()
    highest_avg = revenue_summary.loc[highest_avg_license, 'avg_payment']
    insight_2 = f"📈 {highest_avg_license} has highest avg payment: €{highest_avg:,.2f}"
    insights.append(insight_2)
    print(f"│ {insight_2:<76} │")
    
    # Payment concentration
    total_users = len(df)
    paying_pct = (total_users_with_payments / total_users * 100)
    insight_3 = f"👥 {paying_pct:.1f}% of users ({total_users_with_payments:,}/{total_users:,}) have made payments"
    insights.append(insight_3)
    print(f"│ {insight_3:<76} │")
    
    # Revenue per paying user
    revenue_per_user = total_revenue / total_users_with_payments
    insight_4 = f"💵 Average revenue per paying user: €{revenue_per_user:,.2f}"
    insights.append(insight_4)
    print(f"│ {insight_4:<76} │")
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXPORT TO JSON
    # ═══════════════════════════════════════════════════════════════════════════
    
    export_data = {
        "page": 2,
        "title": "Revenue Analysis by License Type",
        "analysis_date": datetime.now().isoformat(),
        "total_revenue": round(total_revenue, 2),
        "total_paying_users": total_users_with_payments,
        "total_users": total_users,
        "paying_user_percentage": round(paying_pct, 1),
        "avg_revenue_per_paying_user": round(revenue_per_user, 2),
        "revenue_by_license": results_data,
        "insights": insights,
        "sql_query": "SELECT u.license_type, COUNT(p.id) as total_payments, SUM(p.amount) as total_revenue, ROUND(AVG(p.amount), 2) as avg_payment FROM users u JOIN payments p ON u.id = p.user_id GROUP BY u.license_type ORDER BY total_revenue DESC"
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Analysis complete! Results exported to: {OUTPUT_JSON}")
    print()
    
    return export_data


if __name__ == "__main__":
    analyze_revenue()

#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
📊 COSTOMENU DATABASE ANALYTICS - PAGE 1: LICENSE TYPE DISTRIBUTION
═══════════════════════════════════════════════════════════════════════════════

SQL Query Equivalent:
    SELECT license_type, COUNT(*) as total_users 
    FROM users 
    GROUP BY license_type;

Purpose:
    Analyze the distribution of users across different license types (Beginner,
    Expert, Professional) to understand user segmentation and revenue potential.

Navigation:
    • Page 1: License Type Distribution (YOU ARE HERE)
    • Page 2: [Coming Soon] Cohort Retention Analysis
    • Page 3: [Coming Soon] User Activity Patterns
    
Last Updated: 2026-01-26
═══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Configuration
USER_SUMMARY_CSV = Path(__file__).parent / "UserSummary_1769434497556.csv"
OUTPUT_JSON = Path(__file__).parent / "page_01_license_types.json"


def analyze_license_types():
    """Execute license type distribution analysis."""
    
    print("=" * 80)
    print("📊 COSTOMENU DATABASE ANALYTICS - PAGE 1")
    print("=" * 80)
    print("ANALYSIS: License Type Distribution")
    print("DATE:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    print()
    
    # Load data
    df = pd.read_csv(USER_SUMMARY_CSV)
    total_users = len(df)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 1: PRIMARY QUERY RESULTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("┌" + "─" * 78 + "┐")
    print("│ SQL QUERY RESULTS: GROUP BY License Type" + " " * 35 + "│")
    print("├" + "─" * 78 + "┤")
    
    # Execute the SQL-equivalent query
    license_summary = df.groupby('License').agg({
        'User id': 'count'
    }).rename(columns={'User id': 'total_users'})
    
    license_summary = license_summary.sort_values('total_users', ascending=False)
    
    # Display results
    print(f"│ {'License Type':<25} {'Total Users':>15} {'Percentage':>15} {'Bar':>20} │")
    print("├" + "─" * 78 + "┤")
    
    results_data = []
    for license_type, row in license_summary.iterrows():
        count = row['total_users']
        percentage = (count / total_users * 100)
        bar_length = int(percentage / 5)
        bar = "█" * bar_length
        
        print(f"│ {license_type:<25} {count:>15,} {percentage:>14.1f}% {bar:>20} │")
        
        results_data.append({
            'license_type': license_type,
            'total_users': int(count),
            'percentage': round(percentage, 1)
        })
    
    print("├" + "─" * 78 + "┤")
    print(f"│ {'TOTAL':<25} {total_users:>15,} {100.0:>14.1f}% {' ':>20} │")
    print("└" + "─" * 78 + "┘")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 2: DETAILED BREAKDOWN (License Type + Status)
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("┌" + "─" * 78 + "┐")
    print("│ DETAILED BREAKDOWN: License Type × Status" + " " * 35 + "│")
    print("├" + "─" * 78 + "┤")
    
    detailed_summary = df.groupby(['License', 'License status']).agg({
        'User id': 'count'
    }).rename(columns={'User id': 'count'})
    
    print(f"│ {'License Type':<25} {'Status':<15} {'Count':>12} {'% of Type':>12} │")
    print("├" + "─" * 78 + "┤")
    
    detailed_data = []
    for (license_type, status), row in detailed_summary.iterrows():
        count = row['count']
        type_total = license_summary.loc[license_type, 'total_users']
        pct_of_type = (count / type_total * 100)
        
        print(f"│ {license_type:<25} {status:<15} {count:>12,} {pct_of_type:>11.1f}% │")
        
        detailed_data.append({
            'license_type': license_type,
            'status': status,
            'count': int(count),
            'percentage_of_type': round(pct_of_type, 1)
        })
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 3: KEY INSIGHTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("┌" + "─" * 78 + "┐")
    print("│ 💡 KEY INSIGHTS" + " " * 61 + "│")
    print("├" + "─" * 78 + "┤")
    
    insights = []
    
    # Insight 1: Dominant license type
    dominant = license_summary.index[0]
    dominant_pct = (license_summary.iloc[0]['total_users'] / total_users * 100)
    insight_1 = f"• {dominant} dominates with {dominant_pct:.1f}% of all users"
    insights.append(insight_1)
    print(f"│ {insight_1:<76} │")
    
    # Insight 2: Expiration rates
    for license_type in license_summary.index:
        type_df = df[df['License'] == license_type]
        expired_count = len(type_df[type_df['License status'] == 'EXPIRED'])
        total_count = len(type_df)
        exp_rate = (expired_count / total_count * 100) if total_count > 0 else 0
        
        if exp_rate > 50:
            emoji = "⚠️"
        elif exp_rate > 20:
            emoji = "⚡"
        else:
            emoji = "✅"
        
        insight = f"{emoji} {license_type}: {exp_rate:.1f}% expiration rate ({expired_count:,}/{total_count:,})"
        insights.append(insight)
        print(f"│ {insight:<76} │")
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXPORT TO JSON
    # ═══════════════════════════════════════════════════════════════════════════
    
    export_data = {
        "page": 1,
        "title": "License Type Distribution",
        "analysis_date": datetime.now().isoformat(),
        "total_users": total_users,
        "summary": results_data,
        "detailed_breakdown": detailed_data,
        "insights": insights,
        "sql_query": "SELECT license_type, COUNT(*) as total_users FROM users GROUP BY license_type"
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Analysis complete! Results exported to: {OUTPUT_JSON}")
    print()
    
    return export_data


if __name__ == "__main__":
    analyze_license_types()

#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
📊 COSTOMENU DATABASE ANALYTICS - PAGE 3: RENEWALS & CHURN PREVENTION
═══════════════════════════════════════════════════════════════════════════════

Purpose:
    Analyze upcoming renewals from Viva sales export and identify churn risks.
    Provide actionable insights for sales team to prioritize outreach.

Data Sources:
    - renewals_jan2026_VIVA_VERIFIED.csv (Viva sales export)
    - UserSummary_1769434497556.csv (Full user database)

Navigation:
    • Page 1: License Type Distribution
    • Page 2: Revenue Analysis
    • Page 3: Renewals & Churn Prevention (YOU ARE HERE)
    
Last Updated: 2026-01-26
═══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
VIVA_EXPORT = Path(__file__).parent / "renewals_jan2026_VIVA_VERIFIED.csv"
USER_SUMMARY = Path(__file__).parent / "UserSummary_1769434497556.csv"
OUTPUT_JSON = Path(__file__).parent / "page_03_renewals_churn.json"

# Average license values for revenue calculations
AVG_LICENSE_VALUE = {
    'Expert': 251.17,
    'Professional': 248.50,
    'Beginner': 10.94
}


def analyze_renewals():
    """Execute renewals and churn prevention analysis."""
    
    print("=" * 80)
    print("📊 COSTOMENU DATABASE ANALYTICS - PAGE 3")
    print("=" * 80)
    print("ANALYSIS: Renewals & Churn Prevention")
    print("DATE:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    print()
    
    # Load data
    viva_df = pd.read_csv(VIVA_EXPORT)
    users_df = pd.read_csv(USER_SUMMARY)
    
    # Clean email for matching
    viva_df['Email_Clean'] = viva_df['Email_Clean'].str.lower().str.strip()
    users_df['Email_Clean'] = users_df['Email'].str.lower().str.strip()
    
    # Merge datasets
    merged = viva_df.merge(
        users_df,
        on='Email_Clean',
        how='left',
        suffixes=('_viva', '_db')
    )
    
    total_renewals = len(viva_df)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 1: OVERVIEW METRICS
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("┌" + "─" * 78 + "┐")
    print("│ RENEWALS OVERVIEW" + " " * 60 + "│")
    print("├" + "─" * 78 + "┤")
    
    # Risk distribution
    risk_counts = viva_df['Churn_Risk'].value_counts()
    
    high_risk = risk_counts.get('🔴 High', 0)
    medium_risk = risk_counts.get('🟡 Medium', 0)
    low_risk = risk_counts.get('🟢 Low', 0)
    
    print(f"│ Total Renewals Due:        {total_renewals:>3}                                         │")
    print(f"│ 🔴 High Risk:               {high_risk:>3} ({high_risk/total_renewals*100:>5.1f}%)                                 │")
    print(f"│ 🟡 Medium Risk:             {medium_risk:>3} ({medium_risk/total_renewals*100:>5.1f}%)                                 │")
    print(f"│ 🟢 Low Risk:                {low_risk:>3} ({low_risk/total_renewals*100:>5.1f}%)                                 │")
    print("└" + "─" * 78 + "┘")
    print()
    
    # Calculate revenue at risk
    viva_df['estimated_value'] = viva_df['License'].map(AVG_LICENSE_VALUE)
    total_revenue_at_risk = viva_df['estimated_value'].sum()
    high_risk_revenue = viva_df[viva_df['Churn_Risk'] == '🔴 High']['estimated_value'].sum()
    
    print("┌" + "─" * 78 + "┐")
    print("│ REVENUE IMPACT" + " " * 63 + "│")
    print("├" + "─" * 78 + "┤")
    print(f"│ Total Revenue at Risk:     €{total_revenue_at_risk:>8,.2f}                                  │")
    print(f"│ High-Risk Revenue:         €{high_risk_revenue:>8,.2f} ({high_risk_revenue/total_revenue_at_risk*100:>5.1f}%)                          │")
    print("└" + "─" * 78 + "┘")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 2: USER SEGMENT ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("┌" + "─" * 78 + "┐")
    print("│ USER SEGMENT BREAKDOWN" + " " * 54 + "│")
    print("├" + "─" * 78 + "┤")
    print(f"│ {'Segment':<20} {'Count':>8} {'High Risk':>12} {'Med Risk':>12} {'Low Risk':>12} │")
    print("├" + "─" * 78 + "┤")
    
    segment_data = []
    for segment in viva_df['User_Segment'].unique():
        seg_df = viva_df[viva_df['User_Segment'] == segment]
        count = len(seg_df)
        high = len(seg_df[seg_df['Churn_Risk'] == '🔴 High'])
        med = len(seg_df[seg_df['Churn_Risk'] == '🟡 Medium'])
        low = len(seg_df[seg_df['Churn_Risk'] == '🟢 Low'])
        
        print(f"│ {segment:<20} {count:>8} {high:>12} {med:>12} {low:>12} │")
        
        segment_data.append({
            'segment': segment,
            'total': count,
            'high_risk': high,
            'medium_risk': med,
            'low_risk': low
        })
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 3: ACTION LISTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def generate_action(row):
        """Generate suggested action based on user segment and risk."""
        segment = row['User_Segment']
        risk = row['Churn_Risk']
        recipes = row['Recipe count']
        
        if risk == '🔴 High':
            if recipes < 20:
                return "📞 Urgent: Schedule onboarding call"
            elif segment == 'Power User':
                return "👔 Executive check-in call"
            else:
                return "💰 Offer loyalty discount"
        elif risk == '🟡 Medium':
            if recipes < 30:
                return "📚 Send training resources"
            else:
                return "✨ Highlight premium features"
        else:  # Low risk
            return "🎁 Upsell annual plan"
    
    viva_df['suggested_action'] = viva_df.apply(generate_action, axis=1)
    
    # High-risk action list
    print("┌" + "─" * 78 + "┐")
    print("│ 🔴 HIGH-RISK ACTION LIST (Top 10)" + " " * 44 + "│")
    print("├" + "─" * 78 + "┤")
    
    high_risk_df = viva_df[viva_df['Churn_Risk'] == '🔴 High'].sort_values('Recipe count')
    
    high_risk_actions = []
    for idx, row in high_risk_df.head(10).iterrows():
        name = row['Fullname'][:20] if pd.notna(row['Fullname']) else 'N/A'
        email = row['Email_Clean'][:25]
        expires = row['ExpirationDate']
        recipes = row['Recipe count']
        action = row['suggested_action']
        
        print(f"│ {name:<20} {email:<25} {expires:>10} {recipes:>3} recipes │")
        
        high_risk_actions.append({
            'name': row['Fullname'],
            'company': row['Company'] if pd.notna(row['Company']) else '',
            'email': row['Email_Clean'],
            'expiration_date': row['ExpirationDate'],
            'license': row['License'],
            'recipe_count': int(recipes),
            'user_segment': row['User_Segment'],
            'suggested_action': action
        })
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # Medium and low risk lists
    medium_risk_actions = []
    for idx, row in viva_df[viva_df['Churn_Risk'] == '🟡 Medium'].iterrows():
        medium_risk_actions.append({
            'name': row['Fullname'],
            'company': row['Company'] if pd.notna(row['Company']) else '',
            'email': row['Email_Clean'],
            'expiration_date': row['ExpirationDate'],
            'license': row['License'],
            'recipe_count': int(row['Recipe count']),
            'user_segment': row['User_Segment'],
            'suggested_action': row['suggested_action']
        })
    
    low_risk_actions = []
    for idx, row in viva_df[viva_df['Churn_Risk'] == '🟢 Low'].iterrows():
        low_risk_actions.append({
            'name': row['Fullname'],
            'company': row['Company'] if pd.notna(row['Company']) else '',
            'email': row['Email_Clean'],
            'expiration_date': row['ExpirationDate'],
            'license': row['License'],
            'recipe_count': int(row['Recipe count']),
            'user_segment': row['User_Segment'],
            'suggested_action': row['suggested_action']
        })
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 4: KEY INSIGHTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("┌" + "─" * 78 + "┐")
    print("│ 💡 KEY INSIGHTS" + " " * 61 + "│")
    print("├" + "─" * 78 + "┤")
    
    insights = []
    
    # Insight 1: High-risk percentage
    insight_1 = f"⚠️ {high_risk} users ({high_risk/total_renewals*100:.1f}%) are at high risk - immediate action required"
    insights.append(insight_1)
    print(f"│ {insight_1:<76} │")
    
    # Insight 2: Light users
    light_users = len(viva_df[viva_df['User_Segment'] == 'Light User'])
    light_high_risk = len(viva_df[(viva_df['User_Segment'] == 'Light User') & (viva_df['Churn_Risk'] == '🔴 High')])
    if light_users > 0:
        insight_2 = f"📉 {light_high_risk}/{light_users} Light Users are high-risk - need onboarding support"
        insights.append(insight_2)
        print(f"│ {insight_2:<76} │")
    
    # Insight 3: Revenue impact
    insight_3 = f"💰 €{high_risk_revenue:,.0f} in revenue at risk from high-risk renewals"
    insights.append(insight_3)
    print(f"│ {insight_3:<76} │")
    
    # Insight 4: Power users
    power_users_high_risk = len(viva_df[(viva_df['User_Segment'] == 'Power User') & (viva_df['Churn_Risk'] == '🔴 High')])
    if power_users_high_risk > 0:
        insight_4 = f"👔 {power_users_high_risk} Power Users at risk - executive attention needed"
        insights.append(insight_4)
        print(f"│ {insight_4:<76} │")
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXPORT TO JSON
    # ═══════════════════════════════════════════════════════════════════════════
    
    export_data = {
        "page": 3,
        "title": "Renewals & Churn Prevention",
        "analysis_date": datetime.now().isoformat(),
        "total_renewals": total_renewals,
        "high_risk_count": int(high_risk),
        "medium_risk_count": int(medium_risk),
        "low_risk_count": int(low_risk),
        "high_risk_percentage": round(high_risk/total_renewals*100, 1),
        "medium_risk_percentage": round(medium_risk/total_renewals*100, 1),
        "low_risk_percentage": round(low_risk/total_renewals*100, 1),
        "total_revenue_at_risk": round(total_revenue_at_risk, 2),
        "high_risk_revenue": round(high_risk_revenue, 2),
        "segment_breakdown": segment_data,
        "high_risk_actions": high_risk_actions,
        "medium_risk_actions": medium_risk_actions,
        "low_risk_actions": low_risk_actions,
        "insights": insights
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Analysis complete! Results exported to: {OUTPUT_JSON}")
    print()
    
    return export_data


if __name__ == "__main__":
    analyze_renewals()

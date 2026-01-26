#!/usr/bin/env python3
"""
Customer Acquisition Cost (CAC) Analysis for CostoMenu
Analyzes user acquisition patterns, costs, and cohort performance
"""

import pandas as pd
import json
from datetime import datetime
from collections import defaultdict

def load_user_data():
    """Load user summary data from CSV"""
    df = pd.read_csv('UserSummary_1769434497556.csv')
    
    # Convert date columns
    df['Registration date'] = pd.to_datetime(df['Registration date'], format='%d/%m/%Y', errors='coerce')
    df['ExpirationDate'] = pd.to_datetime(df['ExpirationDate'], format='%d/%m/%Y', errors='coerce')
    df['Last activity date'] = pd.to_datetime(df['Last activity date'], format='%d/%m/%Y', errors='coerce')
    
    # Convert numeric columns
    df['Total payments amount'] = pd.to_numeric(df['Total payments amount'], errors='coerce')
    df['Recipe count'] = pd.to_numeric(df['Recipe count'], errors='coerce')
    
    return df

def calculate_cac_metrics(df):
    """Calculate Customer Acquisition Cost metrics"""
    
    # Extract year and month from registration date
    df['reg_year'] = df['Registration date'].dt.year
    df['reg_month'] = df['Registration date'].dt.month
    df['reg_year_month'] = df['Registration date'].dt.to_period('M')
    
    # Calculate metrics by cohort
    cohort_analysis = []
    
    for period in df['reg_year_month'].dropna().unique():
        cohort_df = df[df['reg_year_month'] == period]
        
        total_users = len(cohort_df)
        paying_users = len(cohort_df[cohort_df['Total payments amount'] > 0])
        total_revenue = cohort_df['Total payments amount'].sum()
        
        # Active users (those with activity or recipes)
        active_users = len(cohort_df[
            (cohort_df['Recipe count'] > 0) | 
            (cohort_df['Last activity date'].notna())
        ])
        
        # License type breakdown
        license_breakdown = cohort_df['License'].value_counts().to_dict()
        
        cohort_analysis.append({
            'period': str(period),
            'total_users': total_users,
            'paying_users': paying_users,
            'active_users': active_users,
            'total_revenue': round(total_revenue, 2),
            'avg_revenue_per_user': round(total_revenue / total_users if total_users > 0 else 0, 2),
            'avg_revenue_per_paying_user': round(total_revenue / paying_users if paying_users > 0 else 0, 2),
            'conversion_rate': round(paying_users / total_users * 100 if total_users > 0 else 0, 2),
            'activation_rate': round(active_users / total_users * 100 if total_users > 0 else 0, 2),
            'license_breakdown': license_breakdown
        })
    
    return sorted(cohort_analysis, key=lambda x: x['period'])

def calculate_cac_by_channel(df):
    """
    Estimate CAC by acquisition channel
    Note: Without explicit marketing spend data, we'll use revenue-based estimates
    """
    
    # Assumptions for CAC calculation
    # These should be replaced with actual marketing spend data
    ESTIMATED_MONTHLY_MARKETING_SPEND = {
        '2016': 500,  # Early stage, minimal marketing
        '2017': 800,
        '2018': 1200,
        '2019': 1500,
        '2020': 1000,  # COVID impact
        '2021': 1500,
        '2022': 2000,
        '2023': 2500,
        '2024': 3000,
        '2025': 3500,
        '2026': 4000
    }
    
    df['reg_year_str'] = df['Registration date'].dt.year.astype(str)
    
    cac_by_year = []
    
    for year in df['reg_year_str'].dropna().unique():
        year_df = df[df['reg_year_str'] == year]
        total_users = len(year_df)
        
        # Estimate annual marketing spend
        annual_spend = ESTIMATED_MONTHLY_MARKETING_SPEND.get(year, 2000) * 12
        
        # Calculate CAC
        cac = annual_spend / total_users if total_users > 0 else 0
        
        # Calculate Customer Lifetime Value (LTV)
        avg_revenue_per_user = year_df['Total payments amount'].mean()
        
        # Calculate LTV:CAC ratio
        ltv_cac_ratio = avg_revenue_per_user / cac if cac > 0 else 0
        
        cac_by_year.append({
            'year': year,
            'total_users': total_users,
            'estimated_marketing_spend': annual_spend,
            'cac': round(cac, 2),
            'avg_ltv': round(avg_revenue_per_user, 2),
            'ltv_cac_ratio': round(ltv_cac_ratio, 2),
            'payback_period_months': round(cac / (avg_revenue_per_user / 12) if avg_revenue_per_user > 0 else 0, 1)
        })
    
    return sorted(cac_by_year, key=lambda x: x['year'])

def analyze_user_segments(df):
    """Analyze CAC and LTV by user segment"""
    
    segments = {
        'Professional': df[df['License'] == 'Professional'],
        'Expert': df[df['License'] == 'Expert'],
        'Active_Users': df[df['Recipe count'] > 10],
        'Power_Users': df[df['Recipe count'] > 50],
        'Paying_Users': df[df['Total payments amount'] > 0],
        'Free_Users': df[df['Total payments amount'] == 0]
    }
    
    segment_analysis = []
    
    for segment_name, segment_df in segments.items():
        if len(segment_df) == 0:
            continue
            
        total_revenue = segment_df['Total payments amount'].sum()
        total_users = len(segment_df)
        
        segment_analysis.append({
            'segment': segment_name,
            'total_users': total_users,
            'total_revenue': round(total_revenue, 2),
            'avg_revenue_per_user': round(total_revenue / total_users, 2),
            'avg_recipes': round(segment_df['Recipe count'].mean(), 1),
            'pct_of_total_users': round(total_users / len(df) * 100, 2)
        })
    
    return segment_analysis

def generate_cac_insights(cohort_data, cac_by_year, segment_data):
    """Generate actionable insights from CAC analysis"""
    
    insights = {
        'summary': {
            'total_users': sum(c['total_users'] for c in cohort_data),
            'total_revenue': sum(c['total_revenue'] for c in cohort_data),
            'overall_conversion_rate': round(
                sum(c['paying_users'] for c in cohort_data) / 
                sum(c['total_users'] for c in cohort_data) * 100, 2
            ),
            'avg_cac_recent_years': round(
                sum(y['cac'] for y in cac_by_year[-3:]) / 3, 2
            ) if len(cac_by_year) >= 3 else 0
        },
        'key_findings': [],
        'recommendations': []
    }
    
    # Analyze trends
    if len(cac_by_year) >= 2:
        recent_cac = cac_by_year[-1]['cac']
        previous_cac = cac_by_year[-2]['cac']
        cac_change = ((recent_cac - previous_cac) / previous_cac * 100) if previous_cac > 0 else 0
        
        insights['key_findings'].append({
            'finding': f"CAC {'increased' if cac_change > 0 else 'decreased'} by {abs(round(cac_change, 1))}% year-over-year",
            'impact': 'high' if abs(cac_change) > 20 else 'medium'
        })
    
    # LTV:CAC ratio analysis
    avg_ltv_cac = sum(y['ltv_cac_ratio'] for y in cac_by_year) / len(cac_by_year) if cac_by_year else 0
    
    if avg_ltv_cac < 3:
        insights['recommendations'].append({
            'priority': 'high',
            'action': 'Improve LTV:CAC ratio',
            'details': f"Current ratio is {round(avg_ltv_cac, 2)}. Target should be 3:1 or higher. Consider increasing pricing or reducing acquisition costs."
        })
    
    # Conversion rate analysis
    if insights['summary']['overall_conversion_rate'] < 50:
        insights['recommendations'].append({
            'priority': 'high',
            'action': 'Improve conversion rate',
            'details': f"Only {insights['summary']['overall_conversion_rate']}% of users are paying. Focus on onboarding and value demonstration."
        })
    
    # Segment analysis
    professional_segment = next((s for s in segment_data if s['segment'] == 'Professional'), None)
    expert_segment = next((s for s in segment_data if s['segment'] == 'Expert'), None)
    
    if professional_segment and expert_segment:
        if professional_segment['avg_revenue_per_user'] > expert_segment['avg_revenue_per_user']:
            insights['recommendations'].append({
                'priority': 'medium',
                'action': 'Focus on Professional tier acquisition',
                'details': f"Professional users generate €{professional_segment['avg_revenue_per_user']} vs €{expert_segment['avg_revenue_per_user']} for Expert tier"
            })
    
    return insights

def main():
    """Main execution function"""
    print("Loading user data...")
    df = load_user_data()
    
    print("Calculating CAC metrics...")
    cohort_data = calculate_cac_metrics(df)
    cac_by_year = calculate_cac_by_channel(df)
    segment_data = analyze_user_segments(df)
    
    print("Generating insights...")
    insights = generate_cac_insights(cohort_data, cac_by_year, segment_data)
    
    # Compile results
    results = {
        'analysis_date': datetime.now().isoformat(),
        'cohort_analysis': cohort_data,
        'cac_by_year': cac_by_year,
        'segment_analysis': segment_data,
        'insights': insights
    }
    
    # Save to JSON
    output_file = 'customer_acquisition_cost_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Analysis complete! Results saved to {output_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("CUSTOMER ACQUISITION COST ANALYSIS - SUMMARY")
    print("="*60)
    print(f"\nTotal Users: {insights['summary']['total_users']:,}")
    print(f"Total Revenue: €{insights['summary']['total_revenue']:,.2f}")
    print(f"Overall Conversion Rate: {insights['summary']['overall_conversion_rate']}%")
    print(f"Average CAC (Recent 3 Years): €{insights['summary']['avg_cac_recent_years']}")
    
    print("\n" + "-"*60)
    print("CAC BY YEAR")
    print("-"*60)
    for year_data in cac_by_year[-5:]:  # Last 5 years
        print(f"\n{year_data['year']}:")
        print(f"  Users Acquired: {year_data['total_users']}")
        print(f"  CAC: €{year_data['cac']}")
        print(f"  Avg LTV: €{year_data['avg_ltv']}")
        print(f"  LTV:CAC Ratio: {year_data['ltv_cac_ratio']}:1")
        print(f"  Payback Period: {year_data['payback_period_months']} months")
    
    print("\n" + "-"*60)
    print("TOP RECOMMENDATIONS")
    print("-"*60)
    for i, rec in enumerate(insights['recommendations'][:3], 1):
        print(f"\n{i}. [{rec['priority'].upper()}] {rec['action']}")
        print(f"   {rec['details']}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

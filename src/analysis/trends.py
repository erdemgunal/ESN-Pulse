import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
from sqlalchemy import create_engine
import numpy as np
from datetime import datetime
import calendar
from collections import Counter
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Database connection
def connect_to_db():
    """Connect to PostgreSQL database and return connection"""
    try:
        # Update these parameters with your actual database credentials
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="setgeb-vyjqa1-Sughop",
            host="localhost",
            port=5432
        )
        print("Connected to database successfully!")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Alternative connection using SQLAlchemy for pandas integration
def get_engine():
    """Create SQLAlchemy engine for pandas operations"""
    try:
        # Update these parameters with your actual database credentials
        engine = create_engine('postgresql://postgres:setgeb-vyjqa1-Sughop@localhost:5432/postgres')
        return engine
    except Exception as e:
        print(f"Error creating SQLAlchemy engine: {e}")
        return None

# Data Loading Functions
def load_data():
    """Load data from PostgreSQL tables"""
    try:
        engine = get_engine()
        if not engine:
            return None, None, None
        
        # Load data from the three tables
        organisations = pd.read_sql("SELECT * FROM \"organisations\"", engine)
        activities = pd.read_sql("SELECT * FROM \"activities\"", engine) 
        statistics = pd.read_sql("SELECT * FROM \"statistics\"", engine)
        
        print(f"Loaded {len(organisations)} organisations, {len(activities)} activities, and {len(statistics)} statistics records")
        return organisations, activities, statistics
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None

# Data Analysis Functions
def analyze_popular_activity_types(activities):
    """Analyze which activity types attract the most participants"""
    # Group by activity_type and calculate sum, mean, and count of participants
    activity_type_analysis = activities.groupby('activity_type').agg({
        'participant_count': ['sum', 'mean', 'count']
    }).reset_index()
    
    # Flatten the column hierarchy
    activity_type_analysis.columns = ['activity_type', 'total_participants', 'avg_participants', 'activity_count']
    
    # Sort by total participants descending
    activity_type_analysis = activity_type_analysis.sort_values('total_participants', ascending=False)
    
    print("Top activity types by total participants:")
    print(activity_type_analysis.head(10))
    
    # Create visualizations
    plt.figure(figsize=(12, 8))
    
    # Plot total participants by activity type
    plt.subplot(2, 1, 1)
    sns.barplot(x='activity_type', y='total_participants', data=activity_type_analysis.head(10), palette='viridis')
    plt.title('Top 10 Activity Types by Total Participants')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Plot average participants by activity type
    plt.subplot(2, 1, 2)
    sns.barplot(x='activity_type', y='avg_participants', data=activity_type_analysis.head(10), palette='magma')
    plt.title('Top 10 Activity Types by Average Participants')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    plt.savefig('popular_activity_types.png')
    
    return activity_type_analysis

def analyze_successful_organisations(organisations, activities, statistics):
    """Analyze which ESN organizations are most active and have highest participation"""
    # Join data from activities with organisations
    if 'organisation_id' in activities.columns and 'organisation_id' in organisations.columns:
        org_activity_counts = activities.groupby('organisation_id').agg({
            'activity_id': 'count',
            'participant_count': ['sum', 'mean']
        }).reset_index()
        
        # Flatten the column hierarchy
        org_activity_counts.columns = ['organisation_id', 'activity_count', 'total_participants', 'avg_participants']
        
        # Merge with organisation data
        org_analysis = pd.merge(
            org_activity_counts,
            organisations[['organisation_id', 'organisation_name', 'country']],
            on='organisation_id'
        )
        
        # Sort by total participants descending
        top_orgs_by_participants = org_analysis.sort_values('total_participants', ascending=False)
        
        # Sort by activity count descending
        top_orgs_by_activity_count = org_analysis.sort_values('activity_count', ascending=False)
        
        print("Top 10 organizations by total participants:")
        print(top_orgs_by_participants[['organisation_name', 'country', 'total_participants', 'activity_count']].head(10))
        
        print("\nTop 10 organizations by activity count:")
        print(top_orgs_by_activity_count[['organisation_name', 'country', 'activity_count', 'total_participants']].head(10))
        
        # Create visualizations
        plt.figure(figsize=(12, 10))
        
        # Plot top organizations by total participants
        plt.subplot(2, 1, 1)
        sns.barplot(y='organisation_name', x='total_participants', 
                   data=top_orgs_by_participants.head(10), palette='viridis')
        plt.title('Top 10 ESN Organizations by Total Participants')
        plt.tight_layout()
        
        # Plot top organizations by activity count
        plt.subplot(2, 1, 2)
        sns.barplot(y='organisation_name', x='activity_count', 
                   data=top_orgs_by_activity_count.head(10), palette='magma')
        plt.title('Top 10 ESN Organizations by Activity Count')
        plt.tight_layout()
        
        plt.savefig('successful_organisations.png')
        
        return top_orgs_by_participants, top_orgs_by_activity_count
    else:
        print("Required columns not found in the dataframes")
        return None, None

def analyze_seasonal_trends(activities):
    """Analyze which activity types are more popular by month/season"""
    # Extract month from activity_date
    if 'activity_date' in activities.columns:
        # Convert activity_date to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(activities['activity_date']):
            activities['activity_date'] = pd.to_datetime(activities['activity_date'], errors='coerce')
        
        # Extract month and season
        activities['month'] = activities['activity_date'].dt.month
        activities['month_name'] = activities['activity_date'].dt.month_name()
        
        # Define seasons
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Fall'
        
        activities['season'] = activities['month'].apply(get_season)
        
        # Monthly analysis
        monthly_activity_counts = activities.groupby(['month', 'month_name', 'activity_type']).agg({
            'activity_id': 'count',
            'participant_count': 'sum'
        }).reset_index()
        
        # Seasonal analysis
        seasonal_activity_counts = activities.groupby(['season', 'activity_type']).agg({
            'activity_id': 'count',
            'participant_count': 'sum'
        }).reset_index()
        
        # Get the top activity type for each month
        top_monthly_activities = monthly_activity_counts.sort_values(['month', 'participant_count'], ascending=[True, False])
        top_monthly_activities = top_monthly_activities.groupby('month').first().reset_index()
        
        print("Top activity type by month:")
        for _, row in top_monthly_activities.iterrows():
            print(f"{row['month_name']}: {row['activity_type']} ({row['participant_count']} participants across {row['activity_id']} activities)")
        
        # Create visualizations
        plt.figure(figsize=(15, 10))
        
        # Plot activity count by month and season
        plt.subplot(2, 1, 1)
        monthly_totals = activities.groupby(['month', 'month_name']).size().reset_index(name='count')
        monthly_totals['month_name'] = pd.Categorical(monthly_totals['month_name'], 
                                                     categories=[calendar.month_name[i] for i in range(1, 13)], 
                                                     ordered=True)
        monthly_totals = monthly_totals.sort_values('month')
        sns.barplot(x='month_name', y='count', data=monthly_totals, palette='viridis')
        plt.title('Activity Count by Month')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Plot activity count by season
        plt.subplot(2, 1, 2)
        seasonal_totals = activities.groupby('season').size().reset_index(name='count')
        seasonal_totals['season'] = pd.Categorical(seasonal_totals['season'], 
                                                 categories=['Winter', 'Spring', 'Summer', 'Fall'], 
                                                 ordered=True)
        seasonal_totals = seasonal_totals.sort_values('season')
        sns.barplot(x='season', y='count', data=seasonal_totals, palette='magma')
        plt.title('Activity Count by Season')
        plt.tight_layout()
        
        plt.savefig('seasonal_trends.png')
        
        # Heatmap of activity types by month
        plt.figure(figsize=(16, 10))
        activity_month_pivot = pd.pivot_table(
            monthly_activity_counts,
            values='participant_count',
            index='activity_type',
            columns='month_name',
            aggfunc='sum'
        ).fillna(0)
        
        # Reorder columns by month
        month_order = [calendar.month_name[i] for i in range(1, 13)]
        available_months = [m for m in month_order if m in activity_month_pivot.columns]
        activity_month_pivot = activity_month_pivot[available_months]
        
        # Plot heatmap
        sns.heatmap(activity_month_pivot, cmap='viridis', annot=True, fmt='.0f', linewidths=.5)
        plt.title('Activity Type Popularity by Month (Participant Count)')
        plt.tight_layout()
        plt.savefig('activity_type_by_month.png')
        
        return monthly_activity_counts, seasonal_activity_counts
    else:
        print("activity_date column not found in the activities dataframe")
        return None, None

def analyze_demographic_distribution(statistics):
    """Analyze the distribution of international vs local student participation"""
    if all(col in statistics.columns for col in [
        'local_students_participants', 
        'international_students_participants',
        'coordinators_participants'
    ]):
        # Create a summary dataframe
        demographic_summary = pd.DataFrame({
            'Participant Type': ['Local Students', 'International Students', 'Coordinators'],
            'Total Count': [
                statistics['local_students_participants'].sum(),
                statistics['international_students_participants'].sum(),
                statistics['coordinators_participants'].sum()
            ]
        })
        
        # Calculate percentages
        total_participants = demographic_summary['Total Count'].sum()
        demographic_summary['Percentage'] = (demographic_summary['Total Count'] / total_participants * 100).round(2)
        
        print("Demographic distribution of participants:")
        print(demographic_summary)
        
        # Create visualization
        plt.figure(figsize=(10, 6))
        
        # Pie chart
        plt.subplot(1, 2, 1)
        plt.pie(demographic_summary['Total Count'], 
                labels=demographic_summary['Participant Type'], 
                autopct='%1.1f%%',
                startangle=90,
                colors=sns.color_palette('viridis', 3))
        plt.title('Participant Type Distribution')
        plt.axis('equal')
        
        # Bar chart
        plt.subplot(1, 2, 2)
        sns.barplot(y='Participant Type', x='Total Count', data=demographic_summary, palette='viridis')
        plt.title('Participant Counts by Type')
        
        plt.tight_layout()
        plt.savefig('demographic_distribution.png')
        
        # Analysis by organization
        org_demographics = statistics.copy()
        org_demographics['total_participants_calc'] = (
            org_demographics['local_students_participants'] + 
            org_demographics['international_students_participants'] + 
            org_demographics['coordinators_participants']
        )
        
        org_demographics['international_percentage'] = (
            org_demographics['international_students_participants'] / 
            org_demographics['total_participants_calc'] * 100
        ).round(2)
        
        org_demographics['local_percentage'] = (
            org_demographics['local_students_participants'] / 
            org_demographics['total_participants_calc'] * 100
        ).round(2)
        
        # Top 10 organizations with highest international student percentage
        top_international = org_demographics.sort_values('international_percentage', ascending=False).head(10)
        
        print("\nTop 10 organizations with highest international student percentage:")
        print(top_international[['organisation_id', 'international_percentage', 'total_participants_calc']])
        
        return demographic_summary, org_demographics
    else:
        print("Required demographic columns not found in the statistics dataframe")
        return None, None

def analyze_activity_causes(activities):
    """Analyze which activity causes/purposes attract more interest"""
    if 'activity_causes' in activities.columns:
        # The activity_causes column might be a JSON string, a list, or another format
        # Let's assume it's a string that can be parsed as JSON
        
        # Function to safely extract causes from the column
        def extract_causes(causes_data):
            if pd.isna(causes_data):
                return []
            try:
                if isinstance(causes_data, str):
                    return json.loads(causes_data)
                elif isinstance(causes_data, list):
                    return causes_data
                else:
                    return [str(causes_data)]
            except:
                return [str(causes_data)]
        
        # Extract all causes and count frequencies
        all_causes = []
        for causes in activities['activity_causes'].apply(extract_causes):
            all_causes.extend(causes)
        
        cause_counts = Counter(all_causes)
        
        # Convert to DataFrame for easier visualization
        cause_df = pd.DataFrame({
            'Cause': list(cause_counts.keys()),
            'Count': list(cause_counts.values())
        }).sort_values('Count', ascending=False)
        
        print("Most popular activity causes:")
        print(cause_df.head(10))
        
        # Calculate participant counts per cause
        # Create a new dataframe with one row per activity-cause combination
        cause_participant_rows = []
        for _, activity in activities.iterrows():
            causes = extract_causes(activity['activity_causes'])
            for cause in causes:
                cause_participant_rows.append({
                    'Cause': cause,
                    'Participants': activity['participant_count']
                })
        
        cause_participants_df = pd.DataFrame(cause_participant_rows)
        cause_participant_totals = cause_participants_df.groupby('Cause')['Participants'].sum().reset_index()
        cause_participant_totals = cause_participant_totals.sort_values('Participants', ascending=False)
        
        print("\nMost popular activity causes by total participants:")
        print(cause_participant_totals.head(10))
        
        # Create visualizations
        plt.figure(figsize=(12, 10))
        
        # Plot top causes by frequency
        plt.subplot(2, 1, 1)
        sns.barplot(y='Cause', x='Count', data=cause_df.head(10), palette='viridis')
        plt.title('Top 10 Activity Causes by Frequency')
        plt.tight_layout()
        
        # Plot top causes by participant count
        plt.subplot(2, 1, 2)
        sns.barplot(y='Cause', x='Participants', data=cause_participant_totals.head(10), palette='magma')
        plt.title('Top 10 Activity Causes by Total Participants')
        plt.tight_layout()
        
        plt.savefig('activity_causes.png')
        
        return cause_df, cause_participant_totals
    else:
        print("activity_causes column not found in the activities dataframe")
        return None, None

def create_interactive_dashboard(activities, organisations, statistics):
    """Create interactive Plotly visualizations for a dashboard"""
    # 1. Popular Activity Types
    activity_type_counts = activities.groupby('activity_type').agg({
        'activity_id': 'count',
        'participant_count': ['sum', 'mean']
    })
    activity_type_counts.columns = ['activity_count', 'total_participants', 'avg_participants']
    activity_type_counts = activity_type_counts.reset_index().sort_values('total_participants', ascending=False)
    
    # Plotly bar chart for activity types
    fig1 = px.bar(
        activity_type_counts.head(10),
        x='activity_type',
        y='total_participants',
        color='activity_count',
        title='Top 10 Activity Types by Total Participants',
        labels={'total_participants': 'Total Participants', 'activity_type': 'Activity Type', 'activity_count': 'Activity Count'},
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    # 2. Organizations Performance
    if 'organisation_id' in activities.columns:
        org_performance = activities.groupby('organisation_id').agg({
            'activity_id': 'count',
            'participant_count': 'sum'
        }).reset_index()
        
        org_performance = pd.merge(
            org_performance,
            organisations[['organisation_id', 'organisation_name', 'country']],
            on='organisation_id'
        )
        
        # Plotly scatter plot for organization performance
        fig2 = px.scatter(
            org_performance,
            x='activity_id',
            y='participant_count',
            size='participant_count',
            color='country',
            hover_name='organisation_name',
            title='ESN Organizations Performance',
            labels={
                'activity_id': 'Number of Activities',
                'participant_count': 'Total Participants',
                'country': 'Country'
            }
        )
    
    # 3. Seasonal Trends
    if 'activity_date' in activities.columns:
        # Ensure activity_date is datetime
        if not pd.api.types.is_datetime64_any_dtype(activities['activity_date']):
            activities['activity_date'] = pd.to_datetime(activities['activity_date'], errors='coerce')
        
        # Extract month and add month name
        activities['month'] = activities['activity_date'].dt.month
        activities['month_name'] = activities['activity_date'].dt.month_name()
        
        # Monthly activity counts
        monthly_activity = activities.groupby(['month', 'month_name']).agg({
            'activity_id': 'count',
            'participant_count': 'sum'
        }).reset_index()
        
        # Sort by month
        month_order = {month: i for i, month in enumerate(calendar.month_name[1:])}
        monthly_activity['month_sort'] = monthly_activity['month_name'].map(month_order)
        monthly_activity = monthly_activity.sort_values('month_sort')
        
        # Plotly line chart for monthly trends
        fig3 = px.line(
            monthly_activity,
            x='month_name',
            y=['activity_id', 'participant_count'],
            title='Monthly Activity and Participation Trends',
            labels={
                'month_name': 'Month',
                'value': 'Count',
                'variable': 'Metric'
            }
        )
    
    # 4. Demographic Distribution
    if all(col in statistics.columns for col in [
        'local_students_participants', 
        'international_students_participants',
        'coordinators_participants'
    ]):
        # Calculate totals
        demographic_totals = {
            'Local Students': statistics['local_students_participants'].sum(),
            'International Students': statistics['international_students_participants'].sum(),
            'Coordinators': statistics['coordinators_participants'].sum()
        }
        
        # Create data for pie chart
        pie_data = pd.DataFrame({
            'Participant Type': list(demographic_totals.keys()),
            'Count': list(demographic_totals.values())
        })
        
        # Plotly pie chart for demographics
        fig4 = px.pie(
            pie_data,
            values='Count',
            names='Participant Type',
            title='Participant Demographic Distribution',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
    
    # Save the interactive plots to HTML files
    fig1.write_html("popular_activity_types_interactive.html")
    if 'organisation_id' in activities.columns:
        fig2.write_html("organisation_performance_interactive.html")
    if 'activity_date' in activities.columns:
        fig3.write_html("monthly_trends_interactive.html")
    if all(col in statistics.columns for col in [
        'local_students_participants', 
        'international_students_participants',
        'coordinators_participants'
    ]):
        fig4.write_html("demographic_distribution_interactive.html")
    
    # Create a combined dashboard
    dashboard = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Top Activity Types', 
            'Organization Performance',
            'Monthly Trends', 
            'Demographic Distribution'
        ),
        specs=[
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "pie"}]
        ]
    )
    
    # Add traces from individual figures
    for trace in fig1.data:
        dashboard.add_trace(trace, row=1, col=1)
    
    if 'organisation_id' in activities.columns:
        for trace in fig2.data:
            dashboard.add_trace(trace, row=1, col=2)
    
    if 'activity_date' in activities.columns:
        for trace in fig3.data:
            dashboard.add_trace(trace, row=2, col=1)
    
    if all(col in statistics.columns for col in [
        'local_students_participants', 
        'international_students_participants',
        'coordinators_participants'
    ]):
        for trace in fig4.data:
            dashboard.add_trace(trace, row=2, col=2)
    
    # Update layout
    dashboard.update_layout(
        title_text="ESN Pulse Data Analysis Dashboard",
        height=1000,
        width=1200
    )
    
    dashboard.write_html("esn_pulse_dashboard.html")
    
    print("Interactive dashboard created successfully!")
    return dashboard

# Main function to run all analyses
def run_analysis():
    # Load data
    organisations, activities, statistics = load_data()
    
    if organisations is None or activities is None or statistics is None:
        print("Error: Could not load data. Analysis aborted.")
        return
    
    # Run analyses
    print("\n" + "="*50)
    print("ANALYZING POPULAR ACTIVITY TYPES")
    print("="*50)
    activity_type_analysis = analyze_popular_activity_types(activities)
    
    print("\n" + "="*50)
    print("ANALYZING SUCCESSFUL ORGANIZATIONS")
    print("="*50)
    top_orgs_by_participants, top_orgs_by_activity_count = analyze_successful_organisations(
        organisations, activities, statistics
    )
    
    print("\n" + "="*50)
    print("ANALYZING SEASONAL TRENDS")
    print("="*50)
    monthly_activity_counts, seasonal_activity_counts = analyze_seasonal_trends(activities)
    
    print("\n" + "="*50)
    print("ANALYZING DEMOGRAPHIC DISTRIBUTION")
    print("="*50)
    demographic_summary, org_demographics = analyze_demographic_distribution(statistics)
    
    print("\n" + "="*50)
    print("ANALYZING ACTIVITY CAUSES")
    print("="*50)
    cause_freq, cause_participants = analyze_activity_causes(activities)
    
    print("\n" + "="*50)
    print("CREATING INTERACTIVE DASHBOARD")
    print("="*50)
    dashboard = create_interactive_dashboard(activities, organisations, statistics)
    
    print("\n" + "="*50)
    print("ANALYSIS COMPLETE")
    print("="*50)
    print("All visualizations have been saved to the current directory.")
    
    # Return analysis results for potential further use
    return {
        'activity_type_analysis': activity_type_analysis,
        'top_orgs_by_participants': top_orgs_by_participants,
        'top_orgs_by_activity_count': top_orgs_by_activity_count,
        'monthly_activity_counts': monthly_activity_counts,
        'seasonal_activity_counts': seasonal_activity_counts,
        'demographic_summary': demographic_summary,
        'org_demographics': org_demographics,
        'cause_freq': cause_freq,
        'cause_participants': cause_participants,
        'dashboard': dashboard
    }

# Execute the analysis if this script is run directly
if __name__ == "__main__":
    analysis_results = run_analysis()
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Software Project Analytics",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("🚀 Software Project Management Analytics")
st.markdown("Analyze sprint performance, task delays, and bug trends to improve project efficiency")

# Load data
@st.cache_data
def load_data():
    tasks_df = pd.read_csv('software_tasks.csv')
    bugs_df = pd.read_csv('software_bugs.csv')
    sprints_df = pd.read_csv('sprints_data.csv')
    
    # Convert date columns to datetime
    tasks_df['start_date'] = pd.to_datetime(tasks_df['start_date'])
    tasks_df['due_date'] = pd.to_datetime(tasks_df['due_date'])
    tasks_df['end_date'] = pd.to_datetime(tasks_df['end_date'])
    bugs_df['date_reported'] = pd.to_datetime(bugs_df['date_reported'])
    sprints_df['start_date'] = pd.to_datetime(sprints_df['start_date'])
    sprints_df['end_date'] = pd.to_datetime(sprints_df['end_date'])
    
    # Calculate additional metrics
    tasks_df['duration'] = (tasks_df['end_date'] - tasks_df['start_date']).dt.days
    tasks_df['delay_days'] = (tasks_df['end_date'] - tasks_df['due_date']).dt.days
    tasks_df['is_delayed'] = tasks_df['delay_days'] > 0
    
    return tasks_df, bugs_df, sprints_df

try:
    tasks_df, bugs_df, sprints_df = load_data()
    
    # Sidebar filters
    st.sidebar.header("🔧 Filters")
    selected_sprint = st.sidebar.selectbox(
        "Select Sprint:",
        options=['All'] + list(tasks_df['sprint_id'].unique())
    )
    
    selected_assignee = st.sidebar.selectbox(
        "Select Team Member:",
        options=['All'] + list(tasks_df['assignee'].unique())
    )
    
    # Apply filters
    if selected_sprint != 'All':
        tasks_df = tasks_df[tasks_df['sprint_id'] == selected_sprint]
        bugs_df = bugs_df[bugs_df['related_task_id'].isin(tasks_df['task_id'])]
    
    if selected_assignee != 'All':
        tasks_df = tasks_df[tasks_df['assignee'] == selected_assignee]
        bugs_df = bugs_df[bugs_df['assignee'] == selected_assignee]
    
    # Key Metrics
    st.header("📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tasks = len(tasks_df)
        st.metric("Total Tasks", total_tasks)
    
    with col2:
        completed_tasks = len(tasks_df[tasks_df['status'] == 'Completed'])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    with col3:
        delayed_tasks = len(tasks_df[tasks_df['is_delayed'] == True])
        delay_rate = (delayed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        st.metric("Delayed Tasks", f"{delay_rate:.1f}%")
    
    with col4:
        total_bugs = len(bugs_df)
        st.metric("Total Bugs", total_bugs)
    
    # Main Analysis Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Task Analysis", "🐛 Bug Analysis", "⚡ Sprint Performance", "👥 Team Performance"])
    
    with tab1:
        st.subheader("Task Duration and Delays")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Average duration by task type
            st.write("**Average Duration by Task Type**")
            duration_by_type = tasks_df.groupby('task_type')['duration'].mean().sort_values(ascending=True)
            fig, ax = plt.subplots(figsize=(10, 6))
            duration_by_type.plot(kind='barh', ax=ax, color='skyblue')
            ax.set_xlabel('Average Duration (Days)')
            ax.set_ylabel('Task Type')
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            # Delay reasons
            st.write("**Reasons for Delay**")
            delay_reasons = tasks_df[tasks_df['delay_reason'] != 'None']['delay_reason'].value_counts()
            if not delay_reasons.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                delay_reasons.plot(kind='pie', autopct='%1.1f%%', ax=ax)
                ax.set_ylabel('')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No delays in the selected data")
    
    with tab2:
        st.subheader("Bug Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bugs by severity
            st.write("**Bugs by Severity**")
            severity_counts = bugs_df['severity'].value_counts()
            fig, ax = plt.subplots(figsize=(8, 8))
            severity_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
            ax.set_ylabel('')
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            # Bugs over time
            st.write("**Bugs Reported Over Time**")
            bugs_over_time = bugs_df.groupby('date_reported').size()
            fig, ax = plt.subplots(figsize=(10, 6))
            bugs_over_time.plot(kind='line', ax=ax, marker='o', color='red')
            ax.set_xlabel('Date')
            ax.set_ylabel('Number of Bugs')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
    
    with tab3:
        st.subheader("Sprint Performance")
        
        # Sprint velocity comparison
        st.write("**Planned vs Actual Story Points**")
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = range(len(sprints_df))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], sprints_df['planned_story_points'], 
               width, label='Planned', color='lightblue')
        ax.bar([i + width/2 for i in x], sprints_df['actual_story_points'], 
               width, label='Actual', color='lightgreen')
        
        ax.set_xlabel('Sprint')
        ax.set_ylabel('Story Points')
        ax.set_title('Sprint Velocity: Planned vs Actual')
        ax.set_xticks(x)
        ax.set_xticklabels(sprints_df['sprint_id'])
        ax.legend()
        
        plt.tight_layout()
        st.pyplot(fig)
    
    with tab4:
        st.subheader("Team Performance")
        
        # Tasks completed by each team member
        st.write("**Tasks Completed by Team Member**")
        tasks_by_assignee = tasks_df['assignee'].value_counts()
        fig, ax = plt.subplots(figsize=(10, 6))
        tasks_by_assignee.plot(kind='bar', ax=ax, color='orange')
        ax.set_xlabel('Team Member')
        ax.set_ylabel('Number of Tasks')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    
    # Raw Data Section
    with st.expander("📊 View Raw Data"):
        st.subheader("Raw Data Tables")
        
        data_tab1, data_tab2, data_tab3 = st.tabs(["Tasks Data", "Bugs Data", "Sprints Data"])
        
        with data_tab1:
            st.write("Tasks Data")
            st.dataframe(tasks_df)
        
        with data_tab2:
            st.write("Bugs Data")
            st.dataframe(bugs_df)
        
        with data_tab3:
            st.write("Sprints Data")
            st.dataframe(sprints_df)
    
    # Insights Section
    st.header("💡 Key Insights")
    
    # Generate automatic insights
    if not tasks_df.empty:
        most_common_delay = tasks_df[tasks_df['delay_reason'] != 'None']['delay_reason'].mode()
        avg_duration = tasks_df['duration'].mean()
        most_bugs_severity = bugs_df['severity'].mode().iloc[0] if not bugs_df.empty else "N/A"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Average Task Duration:** {avg_duration:.1f} days")
            if not most_common_delay.empty:
                st.warning(f"**Most Common Delay Reason:** {most_common_delay.iloc[0]}")
            st.success(f"**Completion Rate:** {completion_rate:.1f}%")
        
        with col2:
            if not bugs_df.empty:
                st.error(f"**Most Common Bug Severity:** {most_bugs_severity}")
            st.info(f"**Total Team Members:** {len(tasks_df['assignee'].unique())}")
            st.warning(f"**Delayed Tasks:** {delayed_tasks} out of {total_tasks}")

except FileNotFoundError:
    st.error("❌ Data files not found! Please make sure you have these files in the same folder:")
    st.code("""
    software_tasks.csv
    software_bugs.csv  
    sprints_data.csv
    """)
    
    st.info("💡 **Quick Fix:** Download the dataset files and place them in the same folder as this app.")
    
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your data files and try again.")

# Footer
st.markdown("---")
st.markdown("**Built with Streamlit** | Software Project Management Analytics Dashboard")
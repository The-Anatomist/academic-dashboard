import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(page_title="Teddy's Academic Dashboard", layout="wide", initial_sidebar_state="collapsed")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df_acad = pd.read_csv("academic_data.csv")
        df_behav = pd.read_csv("behavior_data.csv")
        df_behav['Date'] = pd.to_datetime(df_behav['Date'])
        return df_acad, df_behav
    except FileNotFoundError:
        st.error("Data files not found. Please run generate_mock_data.py first.")
        st.stop()

df_acad, df_behav = load_data()

# --- HELPER METRICS ---
current_mean = df_acad['Mark'].mean()
current_points = df_behav['Running_Balance'].iloc[-1] if not df_behav.empty else 100
attendance_rate = 96.5 # Mocked static metric for now

# --- TABS SETUP ---
tab_home, tab_exams, tab_analysis, tab_points = st.tabs(["🏠 Home", "📝 Exams", "📈 Analysis", "⭐️ Points"])

# ==========================================
# 1. HOME TAB
# ==========================================
with tab_home:
    st.title("Welcome back, Teddy Indetie. 🚀")
    st.markdown("Here is your personal academic command center.")
    
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Mean Mark", f"{current_mean:.1f}%")
    col2.metric("Total Active Points", current_points)
    col3.metric("Overall Attendance", f"{attendance_rate}%")
    
    st.divider()
    
    col_act, col_mot = st.columns([2, 1])
    with col_act:
        st.subheader("Recent Activity Feed")
        # Combine recent exams and behavior
        last_exam = df_acad['Exam_Name'].iloc[-1]
        last_behaviors = df_behav.tail(2)
        
        st.info(f"📚 **Latest Exam Cycle Completed:** {last_exam}")
        for _, row in last_behaviors.iterrows():
            if row['Points'] > 0:
                st.success(f"➕ **+{row['Points']} Points** ({row['Category']}): {row['Description']}")
            else:
                st.warning(f"➖ **{row['Points']} Points** ({row['Category']}): {row['Description']}")
                
    with col_mot:
        st.subheader("💡 Insights")
        # Find closest subject to an A (80%)
        latest_exam_id = df_acad['Exam_Order'].max()
        latest_marks = df_acad[df_acad['Exam_Order'] == latest_exam_id]
        close_to_a = latest_marks[(latest_marks['Mark'] >= 75) & (latest_marks['Mark'] < 80)]
        
        if not close_to_a.empty:
            sub = close_to_a.iloc[0]['Subject']
            mark = close_to_a.iloc[0]['Mark']
            gap = 80 - mark
            st.write(f"Keep pushing! You are only **{gap}%** away from an A average in **{sub}**!")
        else:
            st.write("Great work! Keep maintaining your current study habits.")

# ==========================================
# 2. EXAMS TAB
# ==========================================
with tab_exams:
    st.header("Granular Performance per Assessment")
    
    exam_list = df_acad.sort_values("Exam_Order")['Exam_Name'].unique()
    selected_exam = st.selectbox("Select Exam Cycle:", exam_list, index=len(exam_list)-1)
    
    # Filter Data
    exam_data = df_acad[df_acad['Exam_Name'] == selected_exam]
    current_order = exam_data['Exam_Order'].iloc[0]
    
    # Primary Visual
    fig_bar = px.bar(exam_data, x='Subject', y='Mark', color='Mark', 
                     color_continuous_scale='Viridis', range_y=[0, 100],
                     title=f"Subject Performance: {selected_exam}")
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Calculations
    best_sub = exam_data.loc[exam_data['Mark'].idxmax()]
    worst_sub = exam_data.loc[exam_data['Mark'].idxmin()]
    exam_mean = exam_data['Mark'].mean()
    mark_range = best_sub['Mark'] - worst_sub['Mark']
    ratio = best_sub['Mark'] / worst_sub['Mark'] if worst_sub['Mark'] > 0 else 0
    
    # Improved/Reduced Logic
    if current_order > 1:
        prev_data = df_acad[df_acad['Exam_Order'] == (current_order - 1)]
        merged = pd.merge(exam_data, prev_data, on='Subject', suffixes=('_curr', '_prev'))
        merged['Diff'] = merged['Mark_curr'] - merged['Mark_prev']
        most_improved = merged.loc[merged['Diff'].idxmax()]
        most_reduced = merged.loc[merged['Diff'].idxmin()]
    else:
        most_improved = {"Subject": "N/A (First Exam)", "Diff": 0}
        most_reduced = {"Subject": "N/A (First Exam)", "Diff": 0}

    st.subheader("Performance Insights")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Best Subject", best_sub['Subject'], f"{best_sub['Mark']}%")
    c2.metric("Worst Subject", worst_sub['Subject'], f"{worst_sub['Mark']}%")
    c3.metric("Most Improved", most_improved['Subject'], f"{most_improved['Diff']}%")
    c4.metric("Most Reduced", most_reduced['Subject'], f"{most_reduced['Diff']}%")
    
    st.subheader("Statistical Breakdown")
    cc1, cc2, cc3 = st.columns(3)
    cc1.metric("Exam Mean", f"{exam_mean:.1f}%")
    cc2.metric("Best-to-Worst Ratio", f"{ratio:.2f}:1")
    cc3.metric("Mark Range", f"{mark_range} points")

# ==========================================
# 3. ANALYSIS TAB
# ==========================================
with tab_analysis:
    st.header("Long-Term Macro Trends")
    
    # Graph A
    st.subheader("A. Overall Trend (Average Mark over Time)")
    trend_data = df_acad.groupby(['Exam_Order', 'Exam_Name'])['Mark'].mean().reset_index()
    fig_a = px.line(trend_data, x='Exam_Name', y='Mark', markers=True, range_y=[0, 100])
    st.plotly_chart(fig_a, use_container_width=True)
    
    # Graph B
    st.subheader("B. Subject Specific History")
    all_subjects = df_acad['Subject'].unique()
    selected_sub = st.selectbox("Select Subject to Isolate:", all_subjects)
    sub_data = df_acad[df_acad['Subject'] == selected_sub]
    fig_b = px.line(sub_data, x='Exam_Name', y='Mark', markers=True, range_y=[0, 100])
    fig_b.update_traces(line_color='cyan')
    st.plotly_chart(fig_b, use_container_width=True)
    
    # Graph C
    st.subheader("C. The Multi-Line Matrix")
    fig_c = px.line(df_acad, x='Exam_Name', y='Mark', color='Subject', markers=True, range_y=[0, 100])
    st.plotly_chart(fig_c, use_container_width=True)

# ==========================================
# 4. POINTS TAB
# ==========================================
with tab_points:
    st.header("Behavioral & Discipline Tracking")
    
    col_chart, col_pie = st.columns(2)
    
    with col_chart:
        st.subheader("Net Balance Chart")
        fig_bal = px.area(df_behav, x='Date', y='Running_Balance', title="Point Balance Over Time")
        st.plotly_chart(fig_bal, use_container_width=True)
        
    with col_pie:
        st.subheader("Infraction/Reward Breakdown")
        # Absolute values to count frequencies properly
        pie_data = df_behav.copy()
        pie_data['Abs_Points'] = pie_data['Points'].abs()
        fig_pie = px.pie(pie_data, names='Category', values='Abs_Points', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.subheader("Top Contributing Teacher")
    # Teacher who gave the most absolute points (positive or negative)
    teacher_impact = df_behav.groupby('Teacher')['Points'].sum().reset_index()
    top_pos_teacher = teacher_impact.loc[teacher_impact['Points'].idxmax()]
    top_neg_teacher = teacher_impact.loc[teacher_impact['Points'].idxmin()]
    
    t1, t2 = st.columns(2)
    t1.metric("Highest Rewarder", top_pos_teacher['Teacher'], f"+{top_pos_teacher['Points']} pts")
    t2.metric("Strictest Deductor", top_neg_teacher['Teacher'], f"{top_neg_teacher['Points']} pts")
    
    st.subheader("The Points Ledger")
    st.dataframe(df_behav[['Date', 'Teacher', 'Category', 'Points', 'Description', 'Running_Balance']], use_container_width=True)
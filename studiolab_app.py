import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Page config
st.set_page_config(page_title="StudioLab Data Dashboard", layout="wide")

# Styling
plt.rcParams['figure.dpi'] = 500
sns.set_theme(style="whitegrid", palette='rocket', font_scale=1.1)
st.set_option("client.showErrorDetails", True)

st.title("🦾 StudioLab Data Dashboard")
st.markdown("This dashboard displays some data analytics based on ID card check-ins and MPU Event check-ins to the StudioLab")

# --- 1. FILE UPLOADERS ---
with st.expander("📁 Upload CSV Files", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    
    # Custom CSS-styled headers to ensure equal height
    header_style = "<div style='height: 60px; font-size: 16px; line-height: 1.2;'>"
    
    with c1:
        st.markdown(f"{header_style}Attendance file (tap-ins)<br>[Date, Hour, ID]</div>", unsafe_allow_html=True)
        file_att = st.file_uploader("Upload Attendance", type="csv", label_visibility="collapsed")
        
    with c2:
        st.markdown(f"{header_style}Events file<br>[Event, Date, Hour, Registered, Waitlist, Attended]</div>", unsafe_allow_html=True)
        file_ev = st.file_uploader("Upload Events", type="csv", label_visibility="collapsed")
        
    with c3:
        st.markdown(f"{header_style}Trainings file<br>[Event, Date, Hour, Registered, Waitlist, Attended]</div>", unsafe_allow_html=True)
        file_tr = st.file_uploader("Upload Trainings", type="csv", label_visibility="collapsed")
        
    with c4:
        st.markdown(f"{header_style}Machine Reservations file<br>[Date, Machine, Name, Email, Project Type, Project Description]</div>", unsafe_allow_html=True)
        file_mr = st.file_uploader("Upload Reservations", type="csv", label_visibility="collapsed")
if not file_att:
    st.info("Please upload Attendance.csv to see the plots.")
    st.stop()

if not file_ev:
    st.info("Please upload Events.csv to see the plots.")
    st.stop()

if not file_tr:
    st.info("Please upload Trainings.csv to see the plots.")
    st.stop()

if not file_mr:
    st.info("Please upload Machine Reservations.csv to see the plots.")
    st.stop()

attendance = pd.read_csv(file_att)
trainings = pd.read_csv(file_tr)
events = pd.read_csv(file_ev)
machine_res = pd.read_csv(file_mr)
attendance['ID'] = attendance['ID'].astype('str')

# Parse dates
for df, col in [(attendance, "Date"), (trainings, "Date"), (events, "Date"), (machine_res, "Date")]:
    df[col] = pd.to_datetime(df[col], errors="coerce")

# --- 2. DATA QUALITY & INCOMPLETE DATA ---
#@st.cache_data
for df, name in [(trainings, "Trainings"), (events, "Events")]:
    for col in ["Registered", "Waitlist", "Attended"]:
        if col in df.columns:
            non_num = pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()

# Coerce numeric columns for Trainings/Events (treat non-numeric as NaN for later handling)
for df in [trainings, events]:
    for col in ["Registered", "Waitlist", "Attended"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

# Duplicate check-ins (same ID, same Date, same Hour) — could indicate double-tap or real re-entries
attendance = attendance.drop_duplicates(subset=["Date", "Hour", "ID"], keep="first")

# Drop rows with missing Date for attendance series
att_clean = attendance.dropna(subset=["Date"]).copy()
#att_clean["Date"] = att_clean["Date"].dt.date

# Daily check-in counts (raw rows; optional: dedupe by Date/Hour/ID for "unique check-ins per hour")
daily_checkins = att_clean.groupby("Date").size().reset_index(name="Check-ins")
daily_checkins["Date"] = pd.to_datetime(daily_checkins["Date"])

# How attendance varies: by day of week and by hour
att_clean["dow"] = pd.to_datetime(att_clean["Date"]).dt.day_name()
att_clean["hour"] = att_clean["Hour"]

# Specific adjustments for FRS129 and FRS177
# These classes meet every TTh and typically do not badge in.

# 1. Define the class details
classes_to_add = [
    {"name": "frs129", "count": 15, "hour": 13}, # 1:20 PM -> Hour 13
    {"name": "frs177", "count": 12, "hour": 10}, # 10:40 AM -> Hour 10
]

# 2. Identify all Tuesdays and Thursdays in the dataset range
all_dates = pd.to_datetime(att_clean["Date"]).unique()
class_days = [d for d in all_dates if pd.to_datetime(d).dayofweek in [1, 3]]

# 3. Generate synthetic check-ins
synthetic_rows = []
for day in class_days:
    for cls in classes_to_add:
        for _ in range(cls["count"]):
            synthetic_rows.append({
                "Date": day,
                "Hour": cls["hour"],
                "NetID": f"Adjustment_{cls['name']}",
                "Is_Student": True,
                "Project Type": "Class"  # Tagging them as Class usage
            })

# 4. Append to the main dataframe
adj_df = pd.DataFrame(synthetic_rows)
att_clean = pd.concat([att_clean, adj_df], ignore_index=True)

# 5. Refresh helper columns for downstream charts
att_clean["dow"] = pd.to_datetime(att_clean["Date"]).dt.day_name()
att_clean["hour"] = att_clean["Hour"]

# --- 4. THE PLOTS ---

tab_att, tab_event, tab_mr, tab_summary = st.tabs(["Attendance", "Trainings, Events, and Club Usage", "Machine Usage", "System Summary"])

# --- ATTENDANCE TAB ---
with tab_att:
    st.header("Attendance Overview")
    
    # Row 1: Daily and Cumulative (Requested swap to top)
    top_c1, top_c2 = st.columns(2)
    daily = att_clean.groupby(att_clean["Date"].dt.date).size().reset_index(name="Count")
    daily["Cumulative"] = daily["Count"].cumsum()
    total_served = daily['Cumulative'].max()
    
    with top_c1:
        fig1, ax1 = plt.subplots(figsize=(10, 7))
        sns.lineplot(data=daily, x="Date", y="Count", color="C2", ax=ax1)
        ax1.set_title("Daily Check-ins")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig1, use_container_width=True)
    
    with top_c2:
        fig5, ax5 = plt.subplots(figsize=(10, 7))
        ax5.fill_between(daily["Date"], daily["Cumulative"], color="C2", alpha=0.3)
        sns.lineplot(data=daily, x="Date", y="Cumulative", color="C2", ax=ax5)
        ax5.set_title("Cumulative Check-ins")
        ax5.text(0.02, 0.95, f'Total served by StudioLab: {total_served}', transform=ax5.transAxes, 
             fontsize=12, 
             fontweight='bold', 
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig5, use_container_width=True)

    # Row 2: Histograms (DOW and Hour)
    mid_c1, mid_c2 = st.columns(2)
    order_dow = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    with mid_c1:
        by_dow = att_clean.groupby("dow").size().reindex(order_dow).reset_index(name="Count")
        fig2, ax2 = plt.subplots()
        sns.barplot(data=by_dow, x="dow", y="Count", palette="rocket", ax=ax2)
        plt.xticks(rotation=45)
        ax2.set_title("Check-ins by Day of Week")
        ax2.set_xlabel("")
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)
    
    with mid_c2:
        by_hr = att_clean.groupby("Hour").size().reset_index(name="Count")
        fig3, ax3 = plt.subplots()
        sns.barplot(data=by_hr, x="Hour", y="Count", palette="rocket", ax=ax3)
        ax3.set_title("Check-ins by Hour")
        ax3.set_xlabel('Hour (24h)')
        plt.tight_layout()
        st.pyplot(fig3, use_container_width=True)

    # Heatmap Full Width
    st.subheader("Density Analysis")
    heat = att_clean.groupby(["dow", "Hour"]).size().unstack(fill_value=0).reindex(order_dow)

    annot_text = heat.astype(str)

    class_days = ['Tuesday', 'Thursday']
    class_hours = [10,13]

    for day in class_days:
        if day in annot_text.index:
            for hr in class_hours:
                if hr in annot_text.columns:
                    current_val = annot_text.loc[day, hr]
                    annot_text.loc[day, hr] = f"{current_val}*"
    
    fig4, ax4 = plt.subplots(figsize=(12, 5))
    sns.heatmap(heat, annot=annot_text, fmt="", cmap="rocket", ax=ax4, cbar=False)
    ax4.set_title("Check-ins by Day of Week and Hour (* indicates scheduled class time)")
    ax4.set_xlabel('Hour (24h)')
    ax4.set_ylabel('Day of the Week')
    st.pyplot(fig4, clear_figure=True, use_container_width=True)

# --- TRAININGS & EVENTS TAB (2x2 Grid) ---
with tab_event:
    st.header("Trainings, Events, & Club Usage")
    
    # Data Prep
    tr = trainings.dropna(subset=["Date"]).copy()
    tr["show_up_rate"] = np.where(tr["Registered"] > 0, tr["Attended"] / tr["Registered"], np.nan)
    ev = events.dropna(subset=["Date"]).copy()
    ev["show_up_rate"] = np.where(ev["Registered"] > 0, ev["Attended"] / ev["Registered"], np.nan)
    
    # Grid Row 1
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        fig_tr_rate, ax_tr_rate = plt.subplots(figsize=(10, 7))
        show_up = tr.groupby("Event")["show_up_rate"].mean().sort_values()
        sns.barplot(y=show_up.index, x=show_up.values, ax=ax_tr_rate, palette='rocket')
        ax_tr_rate.set_title("Training Show-up Rates")
        ax_tr_rate.axvline(x=1, linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig_tr_rate, use_container_width=True)
    
    with r1c2:
        fig_ev_rate, ax_ev_rate = plt.subplots(figsize=(10, 7))
        if not ev.empty:
            show_up_ev = ev.groupby("Event")["show_up_rate"].mean().sort_values()
            sns.barplot(y=show_up_ev.index, x=show_up_ev.values, ax=ax_ev_rate, palette='rocket')
        ax_ev_rate.set_title("Event Show-up Rates")
        ax_ev_rate.axvline(x=1, linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig_ev_rate, use_container_width=True)

    # Grid Row 2
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        # Combined Sessions Bar Chart
        tr["Type"] = "Training"
        ev["Type"] = "Event"
        combined = pd.concat([tr[["Date", "Attended", "Type"]], ev[["Date", "Attended", "Type"]]])
        combined["Month"] = combined["Date"].dt.to_period("M").apply(lambda x: x.to_timestamp())
        by_type = combined.groupby(["Month", "Type"]).size().reset_index(name="Sessions")
        fig_comp, ax_comp = plt.subplots()
        sns.barplot(data=by_type, x="Month", y="Sessions", hue="Type", ax=ax_comp, palette=['C0', 'C3'])
        plt.xticks(rotation=45)
        ax_comp.set_title("Trainings & Events per Month")
        plt.tight_layout()
        st.pyplot(fig_comp, use_container_width=True)

    with r2c2:
        # Club Usage
        att_clean["is_weekend"] = pd.to_datetime(att_clean["Date"]).dt.dayofweek.isin([5, 6])
        club_by_date = att_clean[att_clean["is_weekend"]].groupby("Date").size().reset_index(name="Check-ins")
        fig_club, ax_club = plt.subplots()
        if not club_by_date.empty:
            sns.barplot(data=club_by_date, x="Date", y="Check-ins", ax=ax_club, color="C2")
            plt.xticks(rotation=90)
        ax_club.set_title("Weekend Club Usage")
        plt.tight_layout()
        st.pyplot(fig_club, use_container_width=True)

# --- MACHINE USAGE TAB (2x2 Grid) ---
with tab_mr:
    st.header("Machine Usage Analytics")
    mr = machine_res.dropna(subset=["Date"]).copy()
    
    if not mr.empty:
        # Grid Row 1
        m1c1, m1c2 = st.columns(2)
        with m1c1:
            fig9, ax9 = plt.subplots()
            mr.groupby("Machine").size().sort_values().plot(kind='barh', color='C2', ax=ax9)
            ax9.set_title("Reservations by Machine Type")
            ax9.set_xlabel('Counts')
            plt.tight_layout()
            st.pyplot(fig9, use_container_width=True)
            
        with m1c2:
            pt_exp = mr["Project Type"].dropna().str.split(',').explode().str.strip()
            pt_counts = pt_exp.value_counts().reset_index(name="Reservations")
            fig10, ax10 = plt.subplots()
            sns.barplot(data=pt_counts, x="Project Type", y="Reservations", ax=ax10)
            ax10.set_title("Reservations by Project Type")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig10, use_container_width=True)

        # Grid Row 2
        m2c1, m2c2 = st.columns(2)
        with m2c1:
            mr_daily = mr.groupby(mr["Date"].dt.date).size().cumsum()
            fig11, ax11 = plt.subplots()
            mr_daily.plot(ax=ax11, color="C2", lw=3)
            ax11.set_title("Cumulative Machine Reservations")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig11, use_container_width=True)

        with m2c2:
            mr["Month"] = mr["Date"].dt.to_period("M").apply(lambda x: x.to_timestamp())
            cum_mach = mr.groupby(["Month", "Machine"]).size().unstack(fill_value=0).cumsum().stack().reset_index(name="Cumulative")
            fig13, ax13 = plt.subplots()
            sns.lineplot(data=cum_mach, x="Month", y="Cumulative", hue="Machine", palette=['C0', 'C3'], ax=ax13)
            ax13.set_title("Cumulative Machine Use by Type")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig13, use_container_width=True)

with tab_summary:
    # Plot 12, 14: The Final Aggregates
    st.subheader("Executive Summary Plots")
    
    # Summary: monthly check-ins, unique users, event+training attendance, machine reservations
    att_clean["Month"] = pd.to_datetime(att_clean["Date"]).dt.to_period("M")
    
    # 1. Total Check-ins
    monthly_checkins = att_clean.groupby("Month").size()
    monthly_checkins.index = monthly_checkins.index.to_timestamp()
    
    # 2. Unique Users (using 'ID' as requested, with a fallback to 'NetID')
    id_col = "ID" if "ID" in att_clean.columns else "NetID"
    monthly_unique = att_clean.groupby("Month")[id_col].nunique()
    monthly_unique.index = monthly_unique.index.to_timestamp()
    
    # 3. Event/Training Attendance
    monthly_events_att = combined.groupby(combined["Date"].dt.to_period("M"))["Attended"].sum()
    monthly_events_att.index = monthly_events_att.index.to_timestamp()
    
    # 4. Machine Reservations
    mr["Month"] = mr["Date"].dt.to_period("M")
    monthly_mr = mr.groupby("Month").size()
    monthly_mr.index = pd.to_datetime(monthly_mr.index.to_timestamp())
    
    # Create the expanded summary table
    summary = pd.DataFrame({
        "Check-ins": monthly_checkins,
        "Unique Users": monthly_unique + 27,
        "Event+Training attendance": monthly_events_att,
        "Machine reservations": monthly_mr,
    }).fillna(0).astype(int)

    st.write("### Monthly Summary Table")
    st.dataframe(summary, use_container_width=True)
    
    # Update the visualization
    summary_long = summary.reset_index().melt(id_vars="index", var_name="Metric", value_name="Count")
    summary_long = summary_long.rename(columns={"index": "Month"})
    
    fig12, ax12 = plt.subplots(figsize=(12, 6))
    # Using 'viridis' or another 4-color friendly palette
    sns.barplot(data=summary_long, x="Month", y="Count", hue="Metric", palette='rocket', ax=ax12)
    
    ax12.set_title("Monthly Usage")
    ax12.set_ylabel("Count")
    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.tight_layout()
    st.pyplot(fig12, clear_figure=True, use_container_width=True)


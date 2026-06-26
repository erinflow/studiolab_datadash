import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="StudioLab Data Dashboard", layout="wide")

# ── CST brand palette ─────────────────────────────────────────────────────────
CST = {
    "red":        "#D14112",
    "navy":       "#1E0944",
    "near_black": "#262626",
    "orange":     "#E77500",
    "purple":     "#5C43A8",
    "lime":       "#E1FF32",
    "slate":      "#A3ABB3",
    "lavender":   "#B39AFD",
    "pale_lime":  "#F0FD96",
    "light_gray": "#E9ECEF",
    "ghost":      "#EEECF6",
}

# Ordered multi-series palette (categorical charts)
CST_PALETTE = [CST["red"], CST["navy"], CST["orange"], CST["purple"],
               CST["slate"], CST["lavender"]]

# Sequential colormap for heatmaps: ghost → navy
CST_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "cst_seq", [CST["ghost"], CST["lavender"], CST["purple"], CST["navy"]]
)


def cst_colors(n):
    """Return n brand colors, cycling through the CST palette."""
    return [CST_PALETTE[i % len(CST_PALETTE)] for i in range(n)]

# ── Global matplotlib style ───────────────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi":         150,
    "figure.facecolor":   "white",
    "axes.facecolor":     "white",
    "axes.edgecolor":     CST["light_gray"],
    "axes.linewidth":     0.8,
    "axes.grid":          True,
    "grid.color":         CST["light_gray"],
    "grid.linewidth":     0.6,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.titleweight":   "bold",
    "axes.titlesize":     13,
    "axes.titlecolor":    CST["near_black"],
    "axes.labelcolor":    CST["near_black"],
    "axes.labelsize":     11,
    "xtick.color":        CST["slate"],
    "ytick.color":        CST["slate"],
    "xtick.labelsize":    9,
    "ytick.labelsize":    9,
    "legend.frameon":     False,
    "legend.fontsize":    9,
    "font.family":        "sans-serif",
})

sns.set_theme(style="white", rc={
    "axes.facecolor": "white",
    "figure.facecolor": "white",
})

st.set_option("client.showErrorDetails", True)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import Outfit — geometric sans close to Paralucent */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    color: #262626;
}

/* Page title */
h1 {
    font-weight: 700;
    font-size: 2rem;
    color: #262626;
    letter-spacing: -0.5px;
    padding-bottom: 0.25rem;
}

/* Section headers (st.header) */
h2 {
    font-weight: 600;
    font-size: 1.35rem;
    color: #262626;
    border-bottom: 3px solid #E77500;
    padding-bottom: 0.35rem;
    margin-bottom: 1rem;
}

/* Subheaders */
h3 {
    font-weight: 600;
    font-size: 1.1rem;
    color: #262626;
}

/* Expander label */
.streamlit-expanderHeader {
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #262626;
}

/* Tab labels */
[data-baseweb="tab"] {
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* Info / warning banners */
.stAlert {
    border-radius: 4px;
    border-left: 4px solid #D14112;
    background-color: #EEECF6;
}

/* Upload widget label */
.uploadLabel { font-size: 0.85rem; color: #A3ABB3; }

/* File uploader description text */
.stFileUploader label { font-size: 0.82rem; color: #262626; }

/* Metric value */
[data-testid="stMetricValue"] {
    font-size: 2rem;
    font-weight: 700;
    color: #D14112;
}

/* Dataframe header */
[data-testid="stDataFrameResizable"] th {
    background-color: #1E0944 !important;
    color: white !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("StudioLab Data Dashboard")
st.markdown(
    "<p style='color:#A3ABB3; font-size:0.95rem; margin-top:-0.5rem;'>"
    "ID card check-ins · MPU event attendance · Machine reservations"
    "</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── 1. FILE UPLOADERS ─────────────────────────────────────────────────────────
with st.expander("UPLOAD CSV FILES", expanded=True):
    c1, c2, c3, c4 = st.columns(4)

    label_style = (
        "font-size:0.8rem; font-weight:600; letter-spacing:0.05em; "
        "text-transform:uppercase; color:#A3ABB3; margin-bottom:4px;"
    )
    desc_style = "font-size:0.82rem; color:#262626; margin-bottom:8px; min-height:36px;"

    with c1:
        st.markdown(f"<p style='{label_style}'>Attendance</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='{desc_style}'>[Date, Hour, ID]</p>", unsafe_allow_html=True)
        file_att = st.file_uploader("Upload Attendance", type="csv", label_visibility="collapsed")

    with c2:
        st.markdown(f"<p style='{label_style}'>Events</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='{desc_style}'>[Event, Date, Hour, Registered, Waitlist, Attended]</p>", unsafe_allow_html=True)
        file_ev = st.file_uploader("Upload Events", type="csv", label_visibility="collapsed")

    with c3:
        st.markdown(f"<p style='{label_style}'>Trainings</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='{desc_style}'>[Event, Date, Hour, Registered, Waitlist, Attended]</p>", unsafe_allow_html=True)
        file_tr = st.file_uploader("Upload Trainings", type="csv", label_visibility="collapsed")

    with c4:
        st.markdown(f"<p style='{label_style}'>Machine Reservations</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='{desc_style}'>[Date, Machine, Name, Email, Project Type, Project Description]</p>", unsafe_allow_html=True)
        file_mr = st.file_uploader("Upload Reservations", type="csv", label_visibility="collapsed")

for f, name in [(file_att, "Attendance.csv"), (file_ev, "Events.csv"),
                (file_tr, "Trainings.csv"), (file_mr, "Machine Reservations.csv")]:
    if not f:
        st.info(f"Upload {name} to continue.")
        st.stop()

# ── 2. LOAD & CLEAN DATA ──────────────────────────────────────────────────────
attendance  = pd.read_csv(file_att)
trainings   = pd.read_csv(file_tr)
events      = pd.read_csv(file_ev)
machine_res = pd.read_csv(file_mr)

attendance["ID"] = attendance["ID"].astype("str")

for df, col in [(attendance, "Date"), (trainings, "Date"), (events, "Date"), (machine_res, "Date")]:
    df[col] = pd.to_datetime(df[col], errors="coerce")

for df in [trainings, events]:
    for col in ["Registered", "Waitlist", "Attended"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

attendance = attendance.drop_duplicates(subset=["Date", "Hour", "ID"], keep="first")
att_clean  = attendance.dropna(subset=["Date"]).copy()

daily_checkins        = att_clean.groupby("Date").size().reset_index(name="Check-ins")
daily_checkins["Date"] = pd.to_datetime(daily_checkins["Date"])

att_clean["dow"]  = pd.to_datetime(att_clean["Date"]).dt.day_name()
att_clean["hour"] = att_clean["Hour"]

# Synthetic check-ins for FRS129/FRS177 (classes that don't badge in)
classes_to_add = [
    {"name": "frs129", "count": 15, "hour": 13},
    {"name": "frs177", "count": 12, "hour": 10},
]
all_dates  = pd.to_datetime(att_clean["Date"]).unique()
class_days = [d for d in all_dates if pd.to_datetime(d).dayofweek in [1, 3]]

synthetic_rows = []
for day in class_days:
    for cls in classes_to_add:
        for _ in range(cls["count"]):
            synthetic_rows.append({
                "Date": day, "Hour": cls["hour"],
                "NetID": f"Adjustment_{cls['name']}",
                "Is_Student": True, "Project Type": "Class",
            })

att_clean = pd.concat([att_clean, pd.DataFrame(synthetic_rows)], ignore_index=True)
att_clean["dow"]  = pd.to_datetime(att_clean["Date"]).dt.day_name()
att_clean["hour"] = att_clean["Hour"]

# ── 3. TABS ───────────────────────────────────────────────────────────────────
tab_att, tab_event, tab_mr, tab_summary = st.tabs([
    "Attendance",
    "Trainings, Events & Club Usage",
    "Machine Usage",
    "Summary",
])

# ── ATTENDANCE TAB ────────────────────────────────────────────────────────────
with tab_att:
    st.header("Attendance Overview")

    daily = att_clean.groupby(att_clean["Date"].dt.date).size().reset_index(name="Count")
    daily["Cumulative"] = daily["Count"].cumsum()
    total_served = int(daily["Cumulative"].max())

    top_c1, top_c2 = st.columns(2)

    with top_c1:
        fig1, ax1 = plt.subplots(figsize=(9, 5))
        ax1.plot(daily["Date"], daily["Count"], color=CST["red"], linewidth=2)
        ax1.fill_between(daily["Date"], daily["Count"], color=CST["red"], alpha=0.08)
        ax1.set_title("Daily Check-ins")
        ax1.set_xlabel("")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig1, use_container_width=True)
        plt.close(fig1)

    with top_c2:
        fig5, ax5 = plt.subplots(figsize=(9, 5))
        ax5.fill_between(daily["Date"], daily["Cumulative"], color=CST["navy"], alpha=0.12)
        ax5.plot(daily["Date"], daily["Cumulative"], color=CST["navy"], linewidth=2)
        ax5.set_title("Cumulative Check-ins")
        ax5.set_xlabel("")
        ax5.text(0.03, 0.93,
                 f"Total served: {total_served:,}",
                 transform=ax5.transAxes,
                 fontsize=11, fontweight="bold", color=CST["near_black"],
                 verticalalignment="top",
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                           edgecolor=CST["light_gray"], linewidth=0.8))
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig5, use_container_width=True)
        plt.close(fig5)

    mid_c1, mid_c2 = st.columns(2)
    order_dow = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    with mid_c1:
        by_dow = att_clean.groupby("dow").size().reindex(order_dow).reset_index(name="Count")
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        ax2.bar(by_dow["dow"], by_dow["Count"], color=cst_colors(len(by_dow)))
        ax2.set_title("Check-ins by Day of Week")
        ax2.set_xlabel("")
        plt.xticks(rotation=40, ha="right")
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)
        plt.close(fig2)

    with mid_c2:
        by_hr = att_clean.groupby("Hour").size().reset_index(name="Count")
        fig3, ax3 = plt.subplots(figsize=(7, 4))
        ax3.bar(by_hr["Hour"], by_hr["Count"], color=cst_colors(len(by_hr)))
        ax3.set_title("Check-ins by Hour")
        ax3.set_xlabel("Hour (24h)")
        plt.tight_layout()
        st.pyplot(fig3, use_container_width=True)
        plt.close(fig3)

    st.subheader("Density Heatmap")
    heat = att_clean.groupby(["dow", "Hour"]).size().unstack(fill_value=0).reindex(order_dow)
    annot_text = heat.astype(str)
    for day in ["Tuesday", "Thursday"]:
        if day in annot_text.index:
            for hr in [10, 13]:
                if hr in annot_text.columns:
                    annot_text.loc[day, hr] = annot_text.loc[day, hr] + "*"

    fig4, ax4 = plt.subplots(figsize=(14, 5))
    sns.heatmap(heat, annot=annot_text, fmt="", cmap=CST_CMAP, ax=ax4,
                cbar=False, linewidths=0.3, linecolor=CST["light_gray"],
                annot_kws={"size": 8, "color": "white"})
    ax4.set_title("Check-ins by Day × Hour  (* = scheduled class)")
    ax4.set_xlabel("Hour (24h)")
    ax4.set_ylabel("")
    plt.tight_layout()
    st.pyplot(fig4, clear_figure=True, use_container_width=True)
    plt.close(fig4)

# ── TRAININGS & EVENTS TAB ────────────────────────────────────────────────────
with tab_event:
    st.header("Trainings, Events & Club Usage")

    tr = trainings.dropna(subset=["Date"]).copy()
    tr["show_up_rate"] = np.where(tr["Registered"] > 0, tr["Attended"] / tr["Registered"], np.nan)
    ev = events.dropna(subset=["Date"]).copy()
    ev["show_up_rate"] = np.where(ev["Registered"] > 0, ev["Attended"] / ev["Registered"], np.nan)

    r1c1, r1c2 = st.columns(2)

    with r1c1:
        show_up = tr.groupby("Event")["show_up_rate"].mean().sort_values()
        fig_tr, ax_tr = plt.subplots(figsize=(9, max(4, len(show_up) * 0.45)))
        colors_tr = [CST["red"] if v >= 1 else CST["navy"] for v in show_up.values]
        ax_tr.barh(show_up.index, show_up.values, color=colors_tr)
        ax_tr.axvline(x=1, linestyle="--", color=CST["slate"], alpha=0.7, linewidth=1)
        ax_tr.set_title("Training Show-up Rates")
        ax_tr.set_xlabel("Rate")
        plt.tight_layout()
        st.pyplot(fig_tr, use_container_width=True)
        plt.close(fig_tr)

    with r1c2:
        fig_ev, ax_ev = plt.subplots(figsize=(9, max(4, len(ev) * 0.45)))
        if not ev.empty:
            show_up_ev = ev.groupby("Event")["show_up_rate"].mean().sort_values()
            colors_ev = [CST["red"] if v >= 1 else CST["navy"] for v in show_up_ev.values]
            ax_ev.barh(show_up_ev.index, show_up_ev.values, color=colors_ev)
        ax_ev.axvline(x=1, linestyle="--", color=CST["slate"], alpha=0.7, linewidth=1)
        ax_ev.set_title("Event Show-up Rates")
        ax_ev.set_xlabel("Rate")
        plt.tight_layout()
        st.pyplot(fig_ev, use_container_width=True)
        plt.close(fig_ev)

    r2c1, r2c2 = st.columns(2)

    with r2c1:
        tr["Type"] = "Training"
        ev["Type"] = "Event"
        combined = pd.concat([tr[["Date", "Attended", "Type"]], ev[["Date", "Attended", "Type"]]])
        combined["Month"] = combined["Date"].dt.to_period("M").apply(lambda x: x.to_timestamp())
        by_type = combined.groupby(["Month", "Type"]).size().reset_index(name="Sessions")
        fig_comp, ax_comp = plt.subplots(figsize=(8, 4))
        sns.barplot(data=by_type, x="Month", y="Sessions", hue="Type", ax=ax_comp,
                    palette=[CST["navy"], CST["red"]])
        plt.xticks(rotation=45, ha="right")
        ax_comp.set_title("Trainings & Events per Month")
        ax_comp.set_xlabel("")
        plt.tight_layout()
        st.pyplot(fig_comp, use_container_width=True)
        plt.close(fig_comp)

    with r2c2:
        att_clean["is_weekend"] = pd.to_datetime(att_clean["Date"]).dt.dayofweek.isin([5, 6])
        club_by_date = att_clean[att_clean["is_weekend"]].groupby("Date").size().reset_index(name="Check-ins")
        fig_club, ax_club = plt.subplots(figsize=(8, 4))
        if not club_by_date.empty:
            ax_club.bar(club_by_date["Date"].astype(str), club_by_date["Check-ins"],
                        color=CST["purple"])
            plt.xticks(rotation=90, fontsize=7)
        ax_club.set_title("Weekend Club Usage")
        ax_club.set_xlabel("")
        plt.tight_layout()
        st.pyplot(fig_club, use_container_width=True)
        plt.close(fig_club)

# ── MACHINE USAGE TAB ─────────────────────────────────────────────────────────
with tab_mr:
    st.header("Machine Usage")
    mr = machine_res.dropna(subset=["Date"]).copy()

    if not mr.empty:
        m1c1, m1c2 = st.columns(2)

        with m1c1:
            by_mach = mr.groupby("Machine").size().sort_values()
            fig9, ax9 = plt.subplots(figsize=(8, max(3, len(by_mach) * 0.5)))
            ax9.barh(by_mach.index, by_mach.values, color=CST["navy"])
            ax9.set_title("Reservations by Machine")
            ax9.set_xlabel("Count")
            plt.tight_layout()
            st.pyplot(fig9, use_container_width=True)
            plt.close(fig9)

        with m1c2:
            pt_exp = mr["Project Type"].dropna().str.split(",").explode().str.strip()
            pt_counts = pt_exp.value_counts().reset_index(name="Reservations")
            fig10, ax10 = plt.subplots(figsize=(8, max(3, len(pt_counts) * 0.5)))
            ax10.bar(pt_counts["Project Type"], pt_counts["Reservations"],
                     color=CST["red"])
            ax10.set_title("Reservations by Project Type")
            plt.xticks(rotation=40, ha="right")
            plt.tight_layout()
            st.pyplot(fig10, use_container_width=True)
            plt.close(fig10)

        m2c1, m2c2 = st.columns(2)

        with m2c1:
            mr_daily = mr.groupby(mr["Date"].dt.date).size().cumsum()
            fig11, ax11 = plt.subplots(figsize=(8, 4))
            ax11.plot(mr_daily.index, mr_daily.values, color=CST["navy"], linewidth=2.5)
            ax11.fill_between(mr_daily.index, mr_daily.values, color=CST["navy"], alpha=0.1)
            ax11.set_title("Cumulative Machine Reservations")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig11, use_container_width=True)
            plt.close(fig11)

        with m2c2:
            mr["Month"] = mr["Date"].dt.to_period("M").apply(lambda x: x.to_timestamp())
            cum_mach = (
                mr.groupby(["Month", "Machine"]).size()
                .unstack(fill_value=0).cumsum()
                .stack().reset_index(name="Cumulative")
            )
            fig13, ax13 = plt.subplots(figsize=(8, 4))
            machines = cum_mach["Machine"].unique()
            pal = CST_PALETTE[:len(machines)]
            for mach, col in zip(machines, pal):
                sub = cum_mach[cum_mach["Machine"] == mach]
                ax13.plot(sub["Month"], sub["Cumulative"], label=mach, color=col, linewidth=2)
            ax13.legend()
            ax13.set_title("Cumulative Use by Machine Type")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig13, use_container_width=True)
            plt.close(fig13)

# ── SUMMARY TAB ───────────────────────────────────────────────────────────────
with tab_summary:
    st.header("Executive Summary")

    att_clean["Month"] = pd.to_datetime(att_clean["Date"]).dt.to_period("M")
    monthly_checkins = att_clean.groupby("Month").size()
    monthly_checkins.index = monthly_checkins.index.to_timestamp()

    id_col = "ID" if "ID" in att_clean.columns else "NetID"
    monthly_unique = att_clean.groupby("Month")[id_col].nunique()
    monthly_unique.index = monthly_unique.index.to_timestamp()

    monthly_events_att = combined.groupby(combined["Date"].dt.to_period("M"))["Attended"].sum()
    monthly_events_att.index = monthly_events_att.index.to_timestamp()

    mr["Month"] = mr["Date"].dt.to_period("M")
    monthly_mr = mr.groupby("Month").size()
    monthly_mr.index = pd.to_datetime(monthly_mr.index.to_timestamp())

    summary = pd.DataFrame({
        "Check-ins":              monthly_checkins,
        "Unique Users":           monthly_unique + 27,
        "Event+Training Attendance": monthly_events_att,
        "Machine Reservations":   monthly_mr,
    }).fillna(0).astype(int)

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Check-ins",    f"{summary['Check-ins'].sum():,}")
    k2.metric("Unique Users",        f"{summary['Unique Users'].max():,}")
    k3.metric("Event Attendance",    f"{summary['Event+Training Attendance'].sum():,}")
    k4.metric("Machine Reservations",f"{summary['Machine Reservations'].sum():,}")

    st.divider()
    st.subheader("Monthly Summary Table")
    st.dataframe(summary, use_container_width=True)

    summary_long = (
        summary.reset_index()
        .melt(id_vars="index", var_name="Metric", value_name="Count")
        .rename(columns={"index": "Month"})
    )

    fig12, ax12 = plt.subplots(figsize=(12, 5))
    metric_palette = {
        "Check-ins":                 CST["navy"],
        "Unique Users":              CST["red"],
        "Event+Training Attendance": CST["orange"],
        "Machine Reservations":      CST["purple"],
    }
    sns.barplot(data=summary_long, x="Month", y="Count", hue="Metric",
                palette=metric_palette, ax=ax12)
    ax12.set_title("Monthly Usage by Category")
    ax12.set_ylabel("Count")
    ax12.set_xlabel("")
    plt.xticks(rotation=45, ha="right")
    ax12.legend(loc="upper right", ncol=2)
    plt.tight_layout()
    st.pyplot(fig12, clear_figure=True, use_container_width=True)
    plt.close(fig12)

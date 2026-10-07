import shutil
import sys
import os

import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt

from pdf_report import create_pdf_report


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

BACKEND_DIR = os.path.join(BASE_DIR, "backend")
DATA_DIR = os.path.join(BASE_DIR, "data")

previous_billing_file = os.path.join(
    DATA_DIR,
    "previous_billing.csv"
)

os.makedirs(DATA_DIR, exist_ok=True)

sys.path.append(BACKEND_DIR)


# ============================================================
# CARD FUNCTIONS
# ============================================================

def metric_card(icon, title, value):

    return f"""
    <div class="metric-card">

        <div class="metric-title">
            <span class="metric-icon">{icon}</span>
            <span>{title}</span>
        </div>

        <div class="metric-value">
            {value}
        </div>

    </div>
    """


def empty_card(icon, title, value):

    return metric_card(icon, title, value)


# ============================================================
# RISK ANALYSIS
# ============================================================

def calculate_risk(row):

    cpu = float(row["cpu_usage"])
    cost = float(row["cost"])
    status = str(row["resource_status"]).lower()

    if status == "unattached":
        return "🔴 High Risk", "Unattached resource"

    if cpu < 10 and cost >= 150:
        return "🔴 High Risk", "Very low utilization + high cost"

    if cpu < 10:
        return "🟠 Medium Risk", "Low CPU utilization"

    if cpu < 25:
        return "🟡 Watch", "Below optimal utilization"

    return "🟢 Healthy", "Resource utilization looks reasonable"


# ============================================================
# BILLING ANALYSIS
# ============================================================

def analyze_file(file):

    if file is None:

        return (
            empty_card("💰", "Total Cost", "$0.00"),
            empty_card("🖥", "Resources", "0"),
            empty_card("⚠️", "Potential Waste", "0"),
            empty_card("🏆", "Top Service", "—"),
            empty_card("💡", "Potential Savings", "$0.00"),
            empty_card("⚡", "Efficiency Score", "0/100"),
            empty_card("📅", "Annual Run Rate", "—"),
            "### 📊 Billing Analysis\n\nUpload a CSV file and click **Analyze Billing**.",
            None,
            pd.DataFrame(),
            pd.DataFrame(),
            "### 💡 Optimization Recommendations\n\nUpload your billing CSV to receive recommendations.",
            "### 🧠 Executive FinOps Summary\n\nUpload your billing CSV to generate an executive summary."
        )

    try:

        # ----------------------------------------------------
        # SAVE CURRENT BILLING FILE
        # ----------------------------------------------------

        shutil.copy(
            file.name,
            previous_billing_file
        )

        df = pd.read_csv(file.name)

        # ----------------------------------------------------
        # VALIDATE CSV
        # ----------------------------------------------------

        required_columns = [
            "resource_id",
            "service",
            "resource_type",
            "cost",
            "cpu_usage",
            "resource_status"
        ]

        missing = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing:

            message = (
                "### ❌ Invalid Billing CSV\n\n"
                "The following required columns are missing:\n\n"
                + "\n".join(
                    f"- `{column}`"
                    for column in missing
                )
            )

            return (
                empty_card("💰", "Total Cost", "$0.00"),
                empty_card("🖥", "Resources", "0"),
                empty_card("⚠️", "Potential Waste", "0"),
                empty_card("🏆", "Top Service", "—"),
                empty_card("💡", "Potential Savings", "$0.00"),
                empty_card("⚡", "Efficiency Score", "0/100"),
                empty_card("📅", "Annual Run Rate", "—"),
                message,
                None,
                pd.DataFrame(),
                pd.DataFrame(),
                "### 💡 Optimization Recommendations\n\nPlease upload a valid billing CSV.",
                "### 🧠 Executive FinOps Summary\n\nPlease upload a valid billing CSV."
            )

        # ----------------------------------------------------
        # CLEAN DATA
        # ----------------------------------------------------

        df["cost"] = pd.to_numeric(
            df["cost"],
            errors="coerce"
        ).fillna(0)

        df["cpu_usage"] = pd.to_numeric(
            df["cpu_usage"],
            errors="coerce"
        ).fillna(0)

        # ----------------------------------------------------
        # BASIC CALCULATIONS
        # ----------------------------------------------------

        total_cost = float(
            df["cost"].sum()
        )

        resource_count = len(df)

        service_cost = (
            df.groupby("service")["cost"]
            .sum()
            .sort_values(ascending=False)
        )

        # ----------------------------------------------------
        # WASTE DETECTION
        # ----------------------------------------------------

        waste = df[
            (df["cpu_usage"] < 10)
            |
            (
                df["resource_status"]
                .astype(str)
                .str.lower()
                == "unattached"
            )
        ].copy()

        waste_count = len(waste)

        potential_savings = float(
            waste["cost"].sum()
        )

        top_service = (
            service_cost.index[0]
            if len(service_cost) > 0
            else "—"
        )

        savings_percentage = (
            (potential_savings / total_cost) * 100
            if total_cost > 0
            else 0
        )

        # ----------------------------------------------------
        # CLOUD EFFICIENCY SCORE
        # ----------------------------------------------------

        if resource_count > 0:

            waste_ratio = (
                waste_count / resource_count
            )

            efficiency_score = max(
                0,
                min(
                    100,
                    round(
                        100
                        - (waste_ratio * 60)
                        - (savings_percentage * 0.4)
                    )
                )
            )

        else:

            efficiency_score = 0

        # ----------------------------------------------------
        # EFFICIENCY STATUS
        # ----------------------------------------------------

        if efficiency_score >= 80:

            efficiency_status = "🟢 Excellent"

        elif efficiency_score >= 60:

            efficiency_status = "🟡 Good"

        else:

            efficiency_status = "🟠 Needs Optimization"

        # ----------------------------------------------------
        # ANNUAL RUN RATE
        # ----------------------------------------------------
        # Assumes uploaded billing represents one month.

        monthly_cost = total_cost

        annual_run_rate = (
            monthly_cost * 12
        )

        # ----------------------------------------------------
        # RISK ANALYSIS
        # ----------------------------------------------------

        risk_rows = []

        for _, row in df.iterrows():

            risk, reason = calculate_risk(row)

            risk_rows.append(
                {
                    "Resource": row["resource_id"],
                    "Service": row["service"],
                    "Cost": round(float(row["cost"]), 2),
                    "CPU Usage": f"{row['cpu_usage']:.1f}%",
                    "Status": row["resource_status"],
                    "Risk": risk,
                    "Reason": reason
                }
            )

        risk_df = pd.DataFrame(
            risk_rows
        )

        # ----------------------------------------------------
        # RISK COUNTS
        # ----------------------------------------------------

        high_risk = len(
            risk_df[
                risk_df["Risk"].str.contains(
                    "High Risk"
                )
            ]
        )

        medium_risk = len(
            risk_df[
                risk_df["Risk"].str.contains(
                    "Medium Risk"
                )
            ]
        )

        # ----------------------------------------------------
        # METRIC CARDS
        # ----------------------------------------------------

        total_card = metric_card(
            "💰",
            "Total Cost",
            f"${total_cost:,.2f}"
        )

        resources_card = metric_card(
            "🖥",
            "Resources",
            str(resource_count)
        )

        waste_card = metric_card(
            "⚠️",
            "Potential Waste",
            str(waste_count)
        )

        service_card = metric_card(
            "🏆",
            "Top Service",
            top_service
        )

        savings_card = metric_card(
            "💡",
            "Potential Savings",
            f"${potential_savings:,.2f}"
        )

        efficiency_card = metric_card(
            "⚡",
            "Efficiency Score",
            f"{efficiency_score}/100<br>"
            f"<small>{efficiency_status}</small>"
        )

        annual_card = metric_card(
            "📅",
            "Annual Run Rate",
            f"${annual_run_rate:,.2f}"
        )

        # ----------------------------------------------------
        # BILLING SUMMARY
        # ----------------------------------------------------

        summary = (
            "# 📊 Billing Analysis\n\n"
            "CloudWise analyzed your cloud billing data "
            "for cost concentration, utilization, "
            "potential waste and optimization opportunities.\n\n"
            "---\n\n"
            "## 💰 Cost Breakdown\n\n"
        )

        for service, cost in service_cost.items():

            percentage = (
                (cost / total_cost) * 100
                if total_cost > 0
                else 0
            )

            summary += (
                f"**{service}**  \n"
                f"${cost:,.2f} · {percentage:.1f}%\n\n"
            )

        # ----------------------------------------------------
        # WASTE INFORMATION
        # ----------------------------------------------------

        summary += "---\n\n"
        summary += "## ⚠️ Potentially Wasteful Resources\n\n"

        if waste_count == 0:

            summary += (
                "✅ No obvious potentially wasteful "
                "resources were detected."
            )

        else:

            summary += (
                f"CloudWise identified **{waste_count} resources** "
                "that may require attention.\n\n"
            )

            for _, row in waste.iterrows():

                summary += (
                    f"- **{row['resource_id']}** — "
                    f"${row['cost']:,.2f} — "
                    f"CPU {row['cpu_usage']}% — "
                    f"{row['resource_status']}\n"
                )

        # ----------------------------------------------------
        # CHART
        # ----------------------------------------------------

        fig, ax = plt.subplots(
            figsize=(9, 5)
        )

        service_cost.plot(
            kind="bar",
            ax=ax
        )

        ax.set_title(
            "Cloud Cost by Service",
            fontsize=15,
            fontweight="bold"
        )

        ax.set_xlabel(
            "Cloud Service"
        )

        ax.set_ylabel(
            "Cost ($)"
        )

        plt.xticks(
            rotation=25,
            ha="right"
        )

        plt.tight_layout()

        # ----------------------------------------------------
        # SMART RECOMMENDATIONS
        # ----------------------------------------------------

        recommendations = (
            "### 💡 Smart Optimization Recommendations\n\n"
        )

        if waste_count == 0:

            recommendations += (
                "### ✅ No obvious waste detected\n\n"
                "Your current resources do not show obvious "
                "low-utilization or unattached-resource patterns.\n\n"
            )

        else:

            recommendations += (
                f"⚠️ **{waste_count} resources may require attention.**\n\n"
                f"💰 Potentially affected cost: "
                f"**${potential_savings:,.2f}**\n\n"
                f"📉 Approximately **{savings_percentage:.1f}%** "
                f"of the current bill may be affected.\n\n"
                "---\n\n"
                "### Recommended Actions\n\n"
            )

            for _, row in waste.iterrows():

                resource = row["resource_id"]
                cost = float(row["cost"])
                cpu = float(row["cpu_usage"])
                status = str(row["resource_status"]).lower()

                if status == "unattached":

                    recommendations += (
                        f"🔴 **{resource}** — Review or remove "
                        f"the unattached resource. "
                        f"Current cost: **${cost:,.2f}**.\n\n"
                    )

                elif cpu < 10 and cost >= 150:

                    recommendations += (
                        f"🔴 **{resource}** — High-cost resource "
                        f"with only **{cpu:.1f}% CPU utilization**. "
                        f"Consider rightsizing or scheduling it. "
                        f"Current cost: **${cost:,.2f}**.\n\n"
                    )

                elif cpu < 10:

                    recommendations += (
                        f"🟠 **{resource}** — Very low CPU utilization "
                        f"({cpu:.1f}%). Review whether this resource "
                        f"is still required.\n\n"
                    )

            recommendations += (
                "---\n\n"
                "### General FinOps Actions\n\n"
                "🔹 Rightsize consistently underutilized resources.\n\n"
                "🔹 Review unattached storage and unused resources.\n\n"
                "🔹 Monitor high-cost services regularly.\n\n"
                "🔹 Configure cloud budgets and spending alerts.\n\n"
                "🔹 Review resource utilization before scaling.\n\n"
                "⚠️ *Potential savings are estimates and are not "
                "guaranteed savings.*"
            )

        # ----------------------------------------------------
        # EXECUTIVE SUMMARY
        # ----------------------------------------------------

        if efficiency_score >= 80:

            health_message = (
                "Cloud spending appears relatively efficient."
            )

        elif efficiency_score >= 60:

            health_message = (
                "Cloud spending is reasonably controlled, "
                "but some optimization opportunities exist."
            )

        else:

            health_message = (
                "Cloud spending shows meaningful optimization "
                "opportunities that should be reviewed."
            )

        executive_summary = (
            "### 🧠 Executive FinOps Summary\n\n"
            f"**Overall Status:** {efficiency_status}\n\n"
            f"**Efficiency Score:** "
            f"**{efficiency_score}/100**\n\n"
            f"{health_message}\n\n"
            "---\n\n"
            f"💰 **Current Billing:** "
            f"${total_cost:,.2f}\n\n"
            f"🖥 **Resources Analyzed:** "
            f"{resource_count}\n\n"
            f"⚠️ **Resources Requiring Attention:** "
            f"{waste_count}\n\n"
            f"🔴 **High-Risk Resources:** "
            f"{high_risk}\n\n"
            f"🟠 **Medium-Risk Resources:** "
            f"{medium_risk}\n\n"
            f"💡 **Potentially Affected Cost:** "
            f"${potential_savings:,.2f}\n\n"
            f"🏆 **Largest Cost Service:** "
            f"{top_service}\n\n"
            "---\n\n"
            "### 📅 Cost Projection\n\n"
            f"If this uploaded bill represents one month, "
            f"the estimated annual run rate would be "
            f"**${annual_run_rate:,.2f}**.\n\n"
            "⚠️ This is a simple run-rate projection, not a "
            "historical forecast. Actual future spending may differ."
        )

        # ----------------------------------------------------
        # RETURN
        # ----------------------------------------------------

        return (
            total_card,
            resources_card,
            waste_card,
            service_card,
            savings_card,
            efficiency_card,
            annual_card,
            summary,
            fig,
            waste,
            risk_df,
            recommendations,
            executive_summary
        )

    except Exception as e:

        error = (
            "### ❌ Analysis Error\n\n"
            f"`{str(e)}`"
        )

        return (
            empty_card("💰", "Total Cost", "$0.00"),
            empty_card("🖥", "Resources", "0"),
            empty_card("⚠️", "Potential Waste", "0"),
            empty_card("🏆", "Top Service", "—"),
            empty_card("💡", "Potential Savings", "$0.00"),
            empty_card("⚡", "Efficiency Score", "0/100"),
            empty_card("📅", "Annual Run Rate", "—"),
            error,
            None,
            pd.DataFrame(),
            pd.DataFrame(),
            "### 💡 Optimization Recommendations\n\n"
            "Please check your CSV file and try again.",
            "### 🧠 Executive FinOps Summary\n\n"
            "Analysis could not be completed."
        )


# ============================================================
# PDF REPORT
# ============================================================

def generate_finops_report(file):

    if file is None:
        return None

    try:

        df = pd.read_csv(file.name)

        required_columns = [
            "resource_id",
            "service",
            "resource_type",
            "cost",
            "cpu_usage",
            "resource_status",
        ]

        missing = [
            c for c in required_columns
            if c not in df.columns
        ]

        if missing:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(missing)
            )

        total_cost = float(
            df["cost"].sum()
        )

        resource_count = len(df)

        service_cost = (
            df.groupby("service")["cost"]
            .sum()
            .sort_values(ascending=False)
        )

        waste = df[
            (df["cpu_usage"] < 10)
            |
            (
                df["resource_status"]
                .astype(str)
                .str.lower()
                == "unattached"
            )
        ]

        waste_count = len(waste)

        potential_savings = float(
            waste["cost"].sum()
        )

        top_service = (
            service_cost.index[0]
            if len(service_cost) > 0
            else "—"
        )

        output_path = os.path.join(
            DATA_DIR,
            "CloudWise_FinOps_Report.pdf"
        )

        create_pdf_report(
            output_path=output_path,
            total_cost=total_cost,
            resource_count=resource_count,
            waste_count=waste_count,
            top_service=top_service,
            potential_savings=potential_savings,
            service_cost=service_cost,
            waste=waste,
        )

        return output_path

    except Exception as e:

        raise gr.Error(
            f"Could not generate PDF report: {str(e)}"
        )


# ============================================================
# CUSTOM CSS
# ============================================================

custom_css = """

body {

    margin: 0 !important;

    background:
        radial-gradient(
            circle at 8% 5%,
            rgba(124, 58, 237, 0.25),
            transparent 28%
        ),

        radial-gradient(
            circle at 92% 12%,
            rgba(76, 29, 149, 0.20),
            transparent 30%
        ),

        radial-gradient(
            circle at 50% 100%,
            rgba(91, 33, 182, 0.15),
            transparent 35%
        ),

        linear-gradient(
            135deg,
            #09080d 0%,
            #100c18 48%,
            #08070c 100%
        ) !important;

    color: #f5f3ff !important;
}


.gradio-container {

    max-width: 1180px !important;

    margin: auto !important;

    padding:
        25px
        30px
        100px
        30px !important;

    background: transparent !important;
}


#cloudwise-header {

    text-align: center;

    padding:
        40px
        25px
        35px;

    margin-bottom: 26px;

    border-radius: 25px;

    background:
        linear-gradient(
            145deg,
            rgba(31, 22, 45, 0.98),
            rgba(11, 9, 15, 0.98)
        );

    border:
        1px solid
        rgba(167, 139, 250, 0.55);

    box-shadow:
        0 22px 45px
        rgba(37, 8, 65, 0.82),

        0 8px 16px
        rgba(0, 0, 0, 0.90),

        inset 0 1px 0
        rgba(255, 255, 255, 0.05);
}


.cloud-icon {

    font-size: 48px;
    margin-bottom: 5px;
}


#cloudwise-header h1 {

    margin: 0 !important;

    font-size: 52px !important;

    font-weight: 900 !important;

    letter-spacing: -2px;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #ddd6fe,
            #a78bfa,
            #67e8f9
        );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;
}


#cloudwise-header p {

    margin:
        10px
        0
        0;

    color: #b7b1c4;

    font-size: 16px;
}


.cloudwise-badge {

    display: inline-block;

    margin-top: 18px;

    padding:
        8px
        17px;

    border-radius: 50px;

    color: #ddd6fe;

    background:
        rgba(124, 58, 237, 0.12);

    border:
        1px solid
        rgba(167, 139, 250, 0.38);

    box-shadow:
        0 7px 15px
        rgba(37, 8, 65, 0.55);

    font-size: 13px;
}


#billing-upload {

    padding: 24px !important;

    margin-bottom: 25px !important;

    border-radius: 20px !important;

    background:
        linear-gradient(
            145deg,
            rgba(31, 22, 45, 0.98),
            rgba(10, 8, 14, 0.98)
        ) !important;

    border:
        1px solid
        rgba(167, 139, 250, 0.58) !important;

    box-shadow:
        0 20px 42px
        rgba(37, 8, 65, 0.82),

        0 7px 14px
        rgba(0, 0, 0, 0.88),

        inset 0 1px 0
        rgba(255, 255, 255, 0.045) !important;
}


#billing-upload > div {

    background: transparent !important;

    border: none !important;

    box-shadow: none !important;
}


#billing-upload h2 {

    color: #ffffff !important;

    font-size: 22px !important;
}


#billing-upload .file {

    background:
        rgba(255, 255, 255, 0.045) !important;

    border:
        2px dashed
        rgba(196, 181, 253, 0.58) !important;

    border-radius:
        15px !important;

    box-shadow:
        0 10px 20px
        rgba(0, 0, 0, 0.60),

        inset 0 1px 0
        rgba(255, 255, 255, 0.035) !important;
}


#billing-upload .file > div,
#billing-upload .file .wrap,
#billing-upload .file .upload-container {

    background: transparent !important;

    border: none !important;

    box-shadow: none !important;
}


#billing-upload .file:hover {

    background:
        rgba(255, 255, 255, 0.07) !important;

    border-color:
        #c4b5fd !important;
}


#billing-upload .file p,
#billing-upload .file span {

    color: #f1f5f9 !important;
}


#billing-upload .file svg {

    color: #ddd6fe !important;
}


#analyze-button {

    width: 100% !important;

    min-height: 54px !important;

    margin-top: 16px !important;

    border-radius: 14px !important;

    border:
        1px solid
        rgba(221, 214, 254, 0.40) !important;

    background:
        linear-gradient(
            145deg,
            #8b5cf6,
            #5b21b6
        ) !important;

    color: white !important;

    font-size: 16px !important;

    font-weight: 800 !important;

    box-shadow:
        0 15px 30px
        rgba(37, 8, 65, 0.88),

        0 5px 10px
        rgba(0, 0, 0, 0.90);
}


#analyze-button:hover {

    transform:
        translateY(-2px);
}


.metric-row {

    gap: 16px !important;

    margin-bottom: 16px !important;
}


.metric-card {

    width: 100%;

    min-height: 128px;

    box-sizing: border-box;

    padding: 22px !important;

    border-radius: 18px;

    background:
        linear-gradient(
            145deg,
            rgba(31, 22, 45, 0.98),
            rgba(10, 9, 14, 0.98)
        );

    border:
        1px solid
        rgba(167, 139, 250, 0.48);

    box-shadow:
        0 15px 30px
        rgba(37, 8, 65, 0.78),

        0 5px 10px
        rgba(0, 0, 0, 0.88),

        inset 0 1px 0
        rgba(255, 255, 255, 0.045);

    transition:
        transform 0.2s ease,
        border-color 0.2s ease;
}


.metric-card:hover {

    transform:
        translateY(-4px);

    border-color:
        rgba(196, 181, 253, 0.82);
}


.metric-title {

    display: flex;

    align-items: center;

    gap: 8px;

    color: #c4b5fd;

    font-size: 14px;

    font-weight: 650;
}


.metric-icon {

    font-size: 18px;
}


.metric-value {

    margin-top: 17px;

    color: #ffffff;

    font-size: 24px;

    font-weight: 850;

    white-space: normal;

    overflow: hidden;

    text-overflow: ellipsis;
}


.metric-value small {

    display: block;

    margin-top: 5px;

    font-size: 12px;

    font-weight: 700;

    color: #c4b5fd;
}


#result-box {

    margin-top: 12px;

    padding: 25px;

    border-radius: 20px;

    background:
        linear-gradient(
            145deg,
            rgba(25, 19, 36, 0.96),
            rgba(9, 8, 12, 0.98)
        );

    border:
        1px solid
        rgba(167, 139, 250, 0.40);

    box-shadow:
        0 17px 35px
        rgba(37, 8, 65, 0.72),

        0 6px 12px
        rgba(0, 0, 0, 0.88);
}


#chart-box {

    margin-top: 20px !important;

    border-radius: 20px !important;

    overflow: hidden !important;

    background:
        linear-gradient(
            145deg,
            rgba(25, 19, 36, 0.96),
            rgba(9, 8, 12, 0.98)
        ) !important;

    border:
        1px solid
        rgba(167, 139, 250, 0.40) !important;

    box-shadow:
        0 18px 38px
        rgba(37, 8, 65, 0.78),

        0 6px 12px
        rgba(0, 0, 0, 0.90) !important;
}


#waste-box,
#risk-box {

    margin-top: 20px !important;

    border-radius: 20px !important;

    overflow: hidden !important;

    border:
        1px solid
        rgba(167, 139, 250, 0.40) !important;

    box-shadow:
        0 17px 35px
        rgba(37, 8, 65, 0.75),

        0 6px 12px
        rgba(0, 0, 0, 0.88) !important;
}


#recommendation-box,
#executive-box {

    margin-top: 20px;

    padding: 25px;

    border-radius: 20px;

    background:
        linear-gradient(
            145deg,
            rgba(31, 22, 45, 0.96),
            rgba(10, 9, 14, 0.98)
        );

    border:
        1px solid
        rgba(103, 232, 249, 0.28);

    box-shadow:
        0 18px 38px
        rgba(37, 8, 65, 0.78),

        0 6px 12px
        rgba(0, 0, 0, 0.90);
}


#report-button {

    width: 100% !important;

    min-height: 52px !important;

    margin-top: 12px !important;

    border-radius: 14px !important;

    border:
        1px solid
        rgba(196, 181, 253, 0.42) !important;

    background:
        linear-gradient(
            145deg,
            #24143d,
            #120c1d
        ) !important;

    color: #ddd6fe !important;

    font-size: 15px !important;

    font-weight: 750 !important;
}


#report-button:hover {

    transform:
        translateY(-2px);

    border-color:
        rgba(196, 181, 253, 0.78) !important;
}


#chat-button {

    position: fixed !important;

    right: 28px !important;

    bottom: 28px !important;

    z-index: 9999 !important;

    width: 66px !important;

    height: 66px !important;

    min-width: 66px !important;

    border-radius: 50% !important;

    display: flex !important;

    align-items: center !important;

    justify-content: center !important;

    background:
        linear-gradient(
            145deg,
            #8b5cf6,
            #5b21b6
        ) !important;

    border:
        1px solid
        rgba(221, 214, 254, 0.65) !important;

    color: white !important;

    text-decoration: none !important;

    font-size: 25px !important;

    box-shadow:
        0 16px 32px
        rgba(37, 8, 65, 0.92),

        0 6px 12px
        rgba(0, 0, 0, 0.92);
}


#chat-button:hover {

    transform:
        scale(1.1);
}


footer {

    display:
        none !important;
}


@media (max-width: 850px) {

    .gradio-container {

        padding:
            15px
            15px
            90px
            15px !important;
    }

    #cloudwise-header h1 {

        font-size:
            40px !important;
    }

    #cloudwise-header {

        padding:
            30px
            18px;
    }

    .metric-card {

        min-height:
            115px;
    }
}

"""


# ============================================================
# UI
# ============================================================

with gr.Blocks(
    title="CloudWise — AI FinOps Assistant",
    css=custom_css
) as app:

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    gr.HTML(
        """
        <div id="cloudwise-header">

            <div class="cloud-icon">
                ☁️
            </div>

            <h1>
                CloudWise
            </h1>

            <p>
                AI FinOps Assistant for Cloud Cost
                Intelligence & Optimization
            </p>

            <div class="cloudwise-badge">
                ✦ Smart Cloud Cost Intelligence
            </div>

        </div>
        """
    )


    # --------------------------------------------------------
    # UPLOAD
    # --------------------------------------------------------

    with gr.Group(
        elem_id="billing-upload"
    ):

        gr.Markdown(
            """
            ## 📁 Analyze Your Cloud Billing

            Upload your billing CSV to discover cost patterns,
            potential waste, resource health and optimization opportunities.
            """
        )

        file_input = gr.File(
            label="Billing CSV",
            file_types=[".csv"]
        )

        analyze_button = gr.Button(
            "🔍  Analyze Billing",
            variant="primary",
            elem_id="analyze-button"
        )

        report_button = gr.Button(
            "📥  Download FinOps Report",
            elem_id="report-button"
        )

        report_file = gr.File(
            label="Your CloudWise FinOps Report",
            interactive=False
        )


    # --------------------------------------------------------
    # METRIC ROW 1
    # --------------------------------------------------------

    with gr.Row(
        elem_id="metric-row-1",
        elem_classes="metric-row"
    ):

        total_cost_card = gr.HTML(
            metric_card(
                "💰",
                "Total Cost",
                "$0.00"
            )
        )

        resources_card = gr.HTML(
            metric_card(
                "🖥",
                "Resources",
                "0"
            )
        )

        waste_card = gr.HTML(
            metric_card(
                "⚠️",
                "Potential Waste",
                "0"
            )
        )


    # --------------------------------------------------------
    # METRIC ROW 2
    # --------------------------------------------------------

    with gr.Row(
        elem_id="metric-row-2",
        elem_classes="metric-row"
    ):

        top_service_card = gr.HTML(
            metric_card(
                "🏆",
                "Top Service",
                "—"
            )
        )

        savings_card = gr.HTML(
            metric_card(
                "💡",
                "Potential Savings",
                "$0.00"
            )
        )

        efficiency_card = gr.HTML(
            metric_card(
                "⚡",
                "Efficiency Score",
                "0/100"
            )
        )


    # --------------------------------------------------------
    # METRIC ROW 3
    # --------------------------------------------------------

    with gr.Row(
        elem_id="metric-row-3",
        elem_classes="metric-row"
    ):

        annual_card = gr.HTML(
            metric_card(
                "📅",
                "Annual Run Rate",
                "—"
            )
        )


    # --------------------------------------------------------
    # BILLING RESULT
    # --------------------------------------------------------

    result = gr.Markdown(
        """
        ### 📊 Billing Analysis

        Upload a CSV file and click **Analyze Billing**.
        """,
        elem_id="result-box"
    )


    # --------------------------------------------------------
    # CHART
    # --------------------------------------------------------

    chart = gr.Plot(
        label="📊 Cloud Cost Analysis",
        elem_id="chart-box"
    )


    # --------------------------------------------------------
    # WASTE TABLE
    # --------------------------------------------------------

    waste_table = gr.Dataframe(
        label="⚠️ Potentially Wasteful Resources",
        elem_id="waste-box"
    )


    # --------------------------------------------------------
    # RISK TABLE
    # --------------------------------------------------------

    risk_table = gr.Dataframe(
        label="🩺 Resource Health & Risk Analysis",
        elem_id="risk-box"
    )


    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    recommendations = gr.Markdown(
        """
        ### 💡 Smart Optimization Recommendations

        Upload your billing CSV to receive
        resource-specific recommendations.
        """,
        elem_id="recommendation-box"
    )


    # --------------------------------------------------------
    # EXECUTIVE SUMMARY
    # --------------------------------------------------------

    executive_summary = gr.Markdown(
        """
        ### 🧠 Executive FinOps Summary

        Upload your billing CSV to generate
        an executive cloud-cost summary.
        """,
        elem_id="executive-box"
    )


    # --------------------------------------------------------
    # ANALYZE ACTION
    # --------------------------------------------------------

    analyze_button.click(

        fn=analyze_file,

        inputs=file_input,

        outputs=[
            total_cost_card,
            resources_card,
            waste_card,
            top_service_card,
            savings_card,
            efficiency_card,
            annual_card,
            result,
            chart,
            waste_table,
            risk_table,
            recommendations,
            executive_summary
        ]

    )


    # --------------------------------------------------------
    # PDF REPORT
    # --------------------------------------------------------

    report_button.click(

        fn=generate_finops_report,

        inputs=file_input,

        outputs=report_file

    )


    # --------------------------------------------------------
    # AI CHAT
    # --------------------------------------------------------

    gr.HTML(
        """
        <a
            href="http://127.0.0.1:7861"
            id="chat-button"
            title="Open CloudWise AI Assistant"
        >
            🤖
        </a>
        """
    )


# ============================================================
# LAUNCH
# ============================================================

app.launch(
    server_port=7860,
    inbrowser=True
)
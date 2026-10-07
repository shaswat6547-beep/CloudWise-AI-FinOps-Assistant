
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
            "### 📊 Billing Analysis\n\nUpload a CSV file and click **Analyze Billing**.",
            None,
            pd.DataFrame(),
            "### 💡 Optimization Recommendations\n\nUpload your billing CSV to receive recommendations."
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
                message,
                None,
                pd.DataFrame(),
                "### 💡 Optimization Recommendations\n\nPlease upload a valid billing CSV."
            )

        # ----------------------------------------------------
        # CALCULATIONS
        # ----------------------------------------------------

        total_cost = float(df["cost"].sum())

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

        savings_percentage = (
            (potential_savings / total_cost) * 100
            if total_cost > 0
            else 0
        )

        # ----------------------------------------------------
        # CLOUD EFFICIENCY SCORE
        # ----------------------------------------------------

        if resource_count > 0:

            waste_ratio = waste_count / resource_count

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
        if efficiency_score >= 80:
            efficiency_status = "🟢 Excellent"
        elif efficiency_score >= 60:
            efficiency_status = "🟡 Good"
        else:
            efficiency_status = "🟠 Needs Optimization"

        efficiency_card = metric_card(
            "⚡",
            "Efficiency Score",
            f"{efficiency_score}/100<br><small>{efficiency_status}</small>"
        )

        # ----------------------------------------------------
        # BILLING SUMMARY
        # ----------------------------------------------------

        summary = (
            "# 📊 Billing Analysis\n\n"
            "Your cloud billing data has been analyzed successfully.\n\n"
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

        ax.set_xlabel("Cloud Service")

        ax.set_ylabel("Cost ($)")

        plt.xticks(
            rotation=25,
            ha="right"
        )

        plt.tight_layout()

        # ----------------------------------------------------
        # RECOMMENDATIONS
        # ----------------------------------------------------

        if waste_count == 0:

            recommendations = (
                "### 💡 Optimization Recommendations\n\n"
                "### ✅ No obvious waste detected\n\n"
                "Continue monitoring your cloud spending "
                "and configure budget alerts."
            )

        else:

            recommendations = (
                "### 💡 Optimization Recommendations\n\n"

                f"⚠️ **{waste_count} resources may require attention.**\n\n"

                f"💰 Potentially affected cost: "
                f"**${potential_savings:,.2f}**\n\n"

                f"📉 This represents approximately "
                f"**{savings_percentage:.1f}%** "
                "of the current bill.\n\n"

                "---\n\n"

                "### Recommended Actions\n\n"

                "🔹 **Rightsize low-utilization resources**  \n"
                "Review resources with very low CPU utilization.\n\n"

                "🔹 **Review unattached storage**  \n"
                "Remove storage that is no longer required.\n\n"

                "🔹 **Monitor expensive resources**  \n"
                "Regularly review your largest cost drivers.\n\n"

                "🔹 **Set cloud spending alerts**  \n"
                "Configure budgets to catch unexpected spending.\n\n"

                "---\n\n"

                "⚠️ *Potential savings are an estimate and are "
                "not guaranteed savings.*"
            )

        return (
    total_card,
    resources_card,
    waste_card,
    service_card,
    savings_card,
    efficiency_card,
    summary,
    fig,
    waste,
    recommendations
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
                
            error,
            None,
            pd.DataFrame(),
            "### 💡 Optimization Recommendations\n\n"
            "Please check your CSV file and try again."
        )



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

        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(missing))

        total_cost = float(df["cost"].sum())
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
        potential_savings = float(waste["cost"].sum())

        top_service = service_cost.index[0] if len(service_cost) > 0 else "—"

        output_path = os.path.join(DATA_DIR, "CloudWise_FinOps_Report.pdf")

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
        raise gr.Error(f"Could not generate PDF report: {str(e)}")



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

    return metric_card(
        icon,
        title,
        value
    )


# ============================================================
# CUSTOM CSS
# ============================================================

custom_css = """

/* ============================================================
   PAGE BACKGROUND
   ============================================================ */

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


/* ============================================================
   MAIN CONTAINER
   ============================================================ */

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


/* ============================================================
   CLOUDWISE HEADER
   ============================================================ */

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


/* ============================================================
   UPLOAD CARD
   ============================================================ */

#billing-upload {

    padding:
        24px !important;

    margin-bottom:
        25px !important;

    border-radius:
        20px !important;

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

    background:
        transparent !important;

    border:
        none !important;

    box-shadow:
        none !important;
}


#billing-upload h2 {

    color:
        #ffffff !important;

    font-size:
        22px !important;
}


/* ============================================================
   CSV DROP AREA
   ============================================================ */

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

    background:
        transparent !important;

    border:
        none !important;

    box-shadow:
        none !important;
}


#billing-upload .file:hover {

    background:
        rgba(255, 255, 255, 0.07) !important;

    border-color:
        #c4b5fd !important;

    box-shadow:

        0 12px 23px
        rgba(37, 8, 65, 0.72) !important;
}


#billing-upload .file p,
#billing-upload .file span {

    color:
        #f1f5f9 !important;
}


#billing-upload .file svg {

    color:
        #ddd6fe !important;
}


/* ============================================================
   ANALYZE BUTTON
   ============================================================ */

#analyze-button {

    width: 100% !important;

    min-height:
        54px !important;

    margin-top:
        16px !important;

    border-radius:
        14px !important;

    border:
        1px solid
        rgba(221, 214, 254, 0.40) !important;

    background:

        linear-gradient(
            145deg,
            #8b5cf6,
            #5b21b6
        ) !important;

    color:
        white !important;

    font-size:
        16px !important;

    font-weight:
        800 !important;

    box-shadow:

        0 15px 30px
        rgba(37, 8, 65, 0.88),

        0 5px 10px
        rgba(0, 0, 0, 0.90),

        inset 0 1px 0
        rgba(255, 255, 255, 0.10) !important;

    transition:
        0.18s ease !important;
}


#analyze-button:hover {

    transform:
        translateY(-2px);

    box-shadow:

        0 18px 35px
        rgba(37, 8, 65, 0.95),

        0 7px 13px
        rgba(0, 0, 0, 0.92) !important;
}


/* ============================================================
   METRIC ROW
   ============================================================ */

.metric-row {

    gap:
        16px !important;

    margin-bottom:
        16px !important;
}


/* ============================================================
   METRIC CARD
   ============================================================ */

.metric-card {

    width: 100%;

    height: 128px;

    box-sizing: border-box;

    padding:
        22px !important;

    border-radius:
        18px;

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
        border-color 0.2s ease,
        box-shadow 0.2s ease;
}


.metric-card:hover {

    transform:
        translateY(-4px);

    border-color:
        rgba(196, 181, 253, 0.82);

    box-shadow:

        0 20px 40px
        rgba(37, 8, 65, 0.88),

        0 7px 14px
        rgba(0, 0, 0, 0.92);
}


.metric-title {

    display: flex;

    align-items: center;

    gap: 8px;

    color:
        #c4b5fd;

    font-size:
        14px;

    font-weight:
        650;
}


.metric-icon {

    font-size:
        18px;
}


.metric-value {

    margin-top:
        17px;

    color:
        #ffffff;

    font-size:
        26px;

    font-weight:
        850;

    white-space:
        nowrap;

    overflow:
        hidden;

    text-overflow:
        ellipsis;
}


/* ============================================================
   BILLING RESULT
   ============================================================ */

#result-box {

    margin-top:
        12px;

    padding:
        25px;

    border-radius:
        20px;

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


/* ============================================================
   CHART
   ============================================================ */

#chart-box {

    margin-top:
        20px !important;

    border-radius:
        20px !important;

    overflow:
        hidden !important;

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


/* ============================================================
   WASTE TABLE
   ============================================================ */

#waste-box {

    margin-top:
        20px !important;

    border-radius:
        20px !important;

    overflow:
        hidden !important;

    border:
        1px solid
        rgba(167, 139, 250, 0.40) !important;

    box-shadow:

        0 17px 35px
        rgba(37, 8, 65, 0.75),

        0 6px 12px
        rgba(0, 0, 0, 0.88) !important;
}


/* ============================================================
   RECOMMENDATIONS
   ============================================================ */

#recommendation-box {

    margin-top:
        20px;

    padding:
        25px;

    border-radius:
        20px;

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


/* ============================================================
   FLOATING AI BUTTON
   ============================================================ */

#chat-button {

    position:
        fixed !important;

    right:
        28px !important;

    bottom:
        28px !important;

    z-index:
        9999 !important;

    width:
        66px !important;

    height:
        66px !important;

    min-width:
        66px !important;

    border-radius:
        50% !important;

    display:
        flex !important;

    align-items:
        center !important;

    justify-content:
        center !important;

    background:

        linear-gradient(
            145deg,
            #8b5cf6,
            #5b21b6
        ) !important;

    border:
        1px solid
        rgba(221, 214, 254, 0.65) !important;

    color:
        white !important;

    text-decoration:
        none !important;

    font-size:
        25px !important;

    box-shadow:

        0 16px 32px
        rgba(37, 8, 65, 0.92),

        0 6px 12px
        rgba(0, 0, 0, 0.92),

        inset 0 1px 0
        rgba(255, 255, 255, 0.12);

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}


#chat-button:hover {

    transform:
        scale(1.1);

    box-shadow:

        0 20px 40px
        rgba(37, 8, 65, 0.98),

        0 8px 16px
        rgba(0, 0, 0, 0.95);
}


/* ============================================================
   PDF REPORT BUTTON
   ============================================================ */

#report-button {
    width: 100% !important;
    min-height: 52px !important;
    margin-top: 12px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(196, 181, 253, 0.42) !important;
    background: linear-gradient(145deg, #24143d, #120c1d) !important;
    color: #ddd6fe !important;
    font-size: 15px !important;
    font-weight: 750 !important;
    box-shadow:
        0 12px 25px rgba(37, 8, 65, 0.78),
        0 4px 9px rgba(0, 0, 0, 0.88),
        inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
    transition: 0.18s ease !important;
}

#report-button:hover {
    transform: translateY(-2px);
    border-color: rgba(196, 181, 253, 0.78) !important;
    background: linear-gradient(145deg, #321b54, #171021) !important;
    box-shadow:
        0 16px 30px rgba(37, 8, 65, 0.90),
        0 6px 12px rgba(0, 0, 0, 0.92) !important;
}

/* ============================================================
   MOBILE
   ============================================================ */

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

        height:
            115px;
    }
}


/* ============================================================
   REMOVE GRADIO FOOTER
   ============================================================ */

footer {

    display:
        none !important;
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
    # BILLING UPLOAD
    # --------------------------------------------------------

    with gr.Group(
        elem_id="billing-upload"
    ):

        gr.Markdown(
            """
            ## 📁 Analyze Your Cloud Billing

            Upload your billing CSV to discover cost patterns,
            potential waste, and optimization opportunities.
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
    # METRIC CARDS
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
    # ANALYSIS RESULT
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
    # RECOMMENDATIONS
    # --------------------------------------------------------

    recommendations = gr.Markdown(
        """
        ### 💡 Optimization Recommendations

        Upload your billing CSV to receive
        intelligent recommendations.
        """,
        elem_id="recommendation-box"
    )


    # --------------------------------------------------------
    # ANALYZE BUTTON ACTION
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
    result,
    chart,
    waste_table,
    recommendations
]
    )


    # --------------------------------------------------------
    # PDF REPORT BUTTON ACTION
    # --------------------------------------------------------

    report_button.click(
        fn=generate_finops_report,
        inputs=file_input,
        outputs=report_file
    )


    # --------------------------------------------------------
    # FLOATING AI CHAT BUTTON
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

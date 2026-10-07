from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.units import inch


def create_pdf_report(
    output_path,
    total_cost,
    resource_count,
    waste_count,
    top_service,
    potential_savings,
    service_cost,
    waste,
):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CloudWiseTitle",
        parent=styles["Title"],
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#4B2E83"),
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "CloudWiseSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "CloudWiseHeading",
        parent=styles["Heading2"],
        fontSize=15,
        leading=20,
        textColor=colors.HexColor("#3B216B"),
        spaceBefore=12,
        spaceAfter=10,
    )

    normal_style = ParagraphStyle(
        "CloudWiseNormal",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#222222"),
    )

    story = []

    # Header
    story.append(Paragraph("☁ CloudWise", title_style))
    story.append(
        Paragraph(
            "AI FinOps Assistant — Cloud Cost & Optimization Report",
            subtitle_style,
        )
    )

    story.append(Spacer(1, 10))

    # Summary
    story.append(Paragraph("Executive Summary", heading_style))

    summary_data = [
        ["Metric", "Value"],
        ["Total Cloud Cost", f"${total_cost:,.2f}"],
        ["Resources Analyzed", str(resource_count)],
        ["Potentially Wasteful Resources", str(waste_count)],
        ["Top Service", str(top_service)],
        ["Potential Savings", f"${potential_savings:,.2f}"],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[3.5 * inch, 2.5 * inch],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#4B2E83"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CCCCCC"),
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F4F0FA"),
                    ],
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Service breakdown
    story.append(Paragraph("Cloud Cost Breakdown", heading_style))

    service_data = [["Service", "Cost", "Share"]]

    for service, cost in service_cost.items():
        percentage = (
            (float(cost) / total_cost) * 100
            if total_cost > 0
            else 0
        )

        service_data.append(
            [
                str(service),
                f"${float(cost):,.2f}",
                f"{percentage:.1f}%",
            ]
        )

    service_table = Table(
        service_data,
        colWidths=[3.0 * inch, 1.5 * inch, 1.5 * inch],
    )

    service_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#4B2E83"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CCCCCC"),
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F4F0FA"),
                    ],
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (-1, -1),
                    "RIGHT",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(service_table)
    story.append(Spacer(1, 20))

    # Waste section
    story.append(
        Paragraph(
            "Potentially Wasteful Resources",
            heading_style,
        )
    )

    if waste_count == 0:
        story.append(
            Paragraph(
                "No obvious potentially wasteful resources were detected.",
                normal_style,
            )
        )
    else:
        waste_data = [
            [
                "Resource",
                "Service",
                "Cost",
                "CPU",
                "Status",
            ]
        ]

        for _, row in waste.iterrows():
            waste_data.append(
                [
                    str(row["resource_id"]),
                    str(row["service"]),
                    f"${float(row['cost']):,.2f}",
                    f"{row['cpu_usage']}%",
                    str(row["resource_status"]),
                ]
            )

        waste_table = Table(
            waste_data,
            colWidths=[
                1.25 * inch,
                1.25 * inch,
                1.0 * inch,
                0.8 * inch,
                1.2 * inch,
            ],
        )

        waste_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#4B2E83"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#CCCCCC"),
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor("#F4F0FA"),
                        ],
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(waste_table)

    story.append(Spacer(1, 20))

    # Recommendations
    story.append(
        Paragraph(
            "Optimization Recommendations",
            heading_style,
        )
    )

    recommendations = [
        "Review resources with very low CPU utilization and consider rightsizing them.",
        "Review unattached storage resources and remove them if they are no longer required.",
        "Monitor high-cost resources regularly to identify unexpected spending.",
        "Configure cloud spending alerts and budgets to detect unusual cost increases.",
    ]

    for recommendation in recommendations:
        story.append(
            Paragraph(
                f"• {recommendation}",
                normal_style,
            )
        )
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Note: Potential savings are estimates based on the uploaded billing "
            "data and the CloudWise detection rules. They are not guaranteed savings.",
            normal_style,
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Generated by CloudWise — AI FinOps Assistant",
            subtitle_style,
        )
    )

    doc.build(story)
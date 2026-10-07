
import gradio as gr
import os
import sys

# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
DATA_DIR = os.path.join(BASE_DIR, "data")

sys.path.append(BACKEND_DIR)

from chat_engine import answer_question


PREVIOUS_BILLING_FILE = os.path.join(
    DATA_DIR,
    "previous_billing.csv"
)


# =========================================================
# DATA FUNCTIONS
# =========================================================

def use_previous_data():

    if os.path.exists(PREVIOUS_BILLING_FILE):

        return (
            PREVIOUS_BILLING_FILE,
            "✅ Previous billing data selected."
        )

    return (
        None,
        "⚠️ No previous billing data found."
    )


def use_new_data(file):

    if file is None:

        return (
            None,
            "⚠️ Please upload a billing CSV file."
        )

    return (
        file,
        "✅ New billing data selected."
    )


# =========================================================
# AI CHAT
# =========================================================

def ask_cloudwise(
    billing_path,
    question,
    history
):

    if history is None:
        history = []

    if not question or not question.strip():

        return history, ""

    if not billing_path:

        response = (
            "⚠️ Please select previous billing data "
            "or upload a new CSV file first."
        )

    else:

        response = answer_question(
            billing_path,
            question
        )

    history = history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": response}
    ]

    return history, ""


# =========================================================
# CUSTOM THEME
# =========================================================

custom_css = """

/* =========================================================
   PAGE BACKGROUND
   ========================================================= */

body {

    background:

        radial-gradient(
            circle at 8% 5%,
            rgba(124, 58, 237, 0.25),
            transparent 28%
        ),

        radial-gradient(
            circle at 94% 12%,
            rgba(76, 29, 149, 0.22),
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
            #100c18 45%,
            #08070c 100%
        ) !important;

    color: #f5f3ff !important;
}


/* =========================================================
   MAIN CONTAINER
   ========================================================= */

.gradio-container {

    max-width: 1180px !important;

    margin: auto !important;

    background: transparent !important;
}


/* =========================================================
   CLOUDWISE HEADER
   ========================================================= */

#cloudwise-header {

    text-align: center;

    padding: 28px 10px 25px;

    margin-bottom: 10px;
}


#cloudwise-header h1 {

    margin: 0;

    font-size: 43px;

    font-weight: 850;

    letter-spacing: -1.2px;

    background:

        linear-gradient(
            90deg,
            #ffffff 0%,
            #ddd6fe 35%,
            #a78bfa 65%,
            #67e8f9 100%
        );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;
}


#cloudwise-header p {

    margin-top: 9px;

    color: #aaa4b8;

    font-size: 14px;

    letter-spacing: 0.2px;
}


/* =========================================================
   PREVIOUS / NEW DATA
   ========================================================= */

#billing-area {

    border: 1px solid rgba(
        139,
        92,
        246,
        0.65
    ) !important;

    border-radius: 18px !important;

    background:

        linear-gradient(
            145deg,
            rgba(31, 22, 45, 0.96),
            rgba(10, 8, 15, 0.98)
        ) !important;

    padding: 20px !important;

    margin-bottom: 24px !important;

    box-shadow:

        0 20px 45px rgba(
            38,
            10,
            65,
            0.85
        ),

        0 8px 16px rgba(
            0,
            0,
            0,
            0.9
        ),

        inset 0 1px 0 rgba(
            255,
            255,
            255,
            0.06
        ) !important;
}


#billing-title {

    color: #ddd6fe !important;

    font-size: 18px !important;

    font-weight: 750 !important;

    margin-bottom: 12px !important;
}


/* =========================================================
   PREVIOUS DATA BUTTON
   ========================================================= */

#previous-button {

    background:

        linear-gradient(
            145deg,
            #251735,
            #100d16
        ) !important;

    color: #eee7ff !important;

    border: 1px solid rgba(
        167,
        139,
        250,
        0.75
    ) !important;

    border-radius: 13px !important;

    min-height: 58px !important;

    box-shadow:

        0 13px 25px rgba(
            37,
            8,
            65,
            0.85
        ),

        0 5px 10px rgba(
            0,
            0,
            0,
            0.9
        ),

        inset 0 1px 0 rgba(
            255,
            255,
            255,
            0.07
        ) !important;

    transition: 0.18s ease !important;
}


#previous-button:hover {

    transform: translateY(-2px);

    border-color: #c4b5fd !important;
}


/* =========================================================
   UPLOAD
   ========================================================= */

#upload-area {

    background:

        linear-gradient(
            145deg,
            #20172d,
            #0d0b12
        ) !important;

    border: 1px dashed rgba(
        167,
        139,
        250,
        0.75
    ) !important;

    border-radius: 13px !important;

    min-height: 58px !important;

    box-shadow:

        0 13px 25px rgba(
            37,
            8,
            65,
            0.85
        ),

        0 5px 10px rgba(
            0,
            0,
            0,
            0.9
        ),

        inset 0 1px 0 rgba(
            255,
            255,
            255,
            0.06
        ) !important;
}


#upload-area .file {

    border: none !important;

    background: transparent !important;

    box-shadow: none !important;
}


#status {

    color: #aaa4b8 !important;

    font-size: 12px !important;

    margin-top: 8px !important;
}


/* =========================================================
   QUICK QUESTIONS
   ========================================================= */

#quick-title {

    color: #ddd6fe !important;

    font-size: 17px !important;

    font-weight: 750 !important;

    margin-bottom: 11px !important;
}


.quick-btn {

    background:

        linear-gradient(
            145deg,
            #21182d,
            #0c0a10
        ) !important;

    color: #eeeaf5 !important;

    border: 1px solid rgba(
        139,
        92,
        246,
        0.60
    ) !important;

    border-radius: 13px !important;

    min-height: 48px !important;

    box-shadow:

        0 12px 24px rgba(
            37,
            8,
            65,
            0.78
        ),

        0 5px 9px rgba(
            0,
            0,
            0,
            0.88
        ),

        inset 0 1px 0 rgba(
            255,
            255,
            255,
            0.05
        ) !important;

    transition: 0.18s ease !important;
}


.quick-btn:hover {

    transform: translateY(-2px);

    border-color: #c4b5fd !important;

    box-shadow:

        0 15px 27px rgba(
            52,
            12,
            88,
            0.85
        ),

        0 6px 11px rgba(
            0,
            0,
            0,
            0.9
        ) !important;
}


/* =========================================================
   QUESTION AREA
   ========================================================= */

#question-row {

    margin-top: 20px !important;

    align-items: stretch !important;
}


#question-box textarea {

    background:

        linear-gradient(
            145deg,
            #1b1523,
            #0b090e
        ) !important;

    color: #ffffff !important;

    border: 1px solid rgba(
        167,
        139,
        250,
        0.70
    ) !important;

    border-radius: 14px !important;

    font-size: 15px !important;

    box-shadow:

        0 14px 28px rgba(
            37,
            8,
            65,
            0.82
        ),

        0 5px 10px rgba(
            0,
            0,
            0,
            0.9
        ),

        inset 0 1px 0 rgba(
            255,
            255,
            255,
            0.04
        ) !important;
}


#question-box textarea:focus {

    border-color: #c4b5fd !important;

    box-shadow:

        0 15px 30px rgba(
            37,
            8,
            65,
            0.9
        ),

        0 6px 12px rgba(
            0,
            0,
            0,
            0.92
        ),

        0 0 0 2px rgba(
            124,
            58,
            237,
            0.15
        ) !important;
}


/* =========================================================
   ASK AI
   ========================================================= */

#ask-button {

    background:

        linear-gradient(
            145deg,
            #8b5cf6,
            #5b21b6
        ) !important;

    color: #ffffff !important;

    font-weight: 800 !important;

    border: 1px solid rgba(
        221,
        214,
        254,
        0.65
    ) !important;

    border-radius: 14px !important;

    box-shadow:

        0 15px 30px rgba(
            37,
            8,
            65,
            0.92
        ),

        0 6px 12px rgba(
            0,
            0,
            0,
            0.92
        ),

        inset 0 1px 0 rgba(
            255,
            255,
            255,
            0.13
        ) !important;

    transition: 0.18s ease !important;
}


#ask-button:hover {

    transform: translateY(-2px);

    box-shadow:

        0 18px 34px rgba(
            37,
            8,
            65,
            0.95
        ),

        0 7px 14px rgba(
            0,
            0,
            0,
            0.95
        ) !important;
}


/* =========================================================
   CHAT / ANSWER
   ========================================================= */

#chat-section {

    margin-top: 24px !important;

    border: 1px solid rgba(
        139,
        92,
        246,
        0.72
    ) !important;

    border-radius: 20px !important;

    background:

        linear-gradient(
            145deg,
            rgba(30, 23, 40, 0.98),
            rgba(8, 7, 11, 0.99)
        ) !important;

    box-shadow:

        0 25px 50px rgba(
            37,
            8,
            65,
            0.92
        ),

        0 9px 18px rgba(
            0,
            0,
            0,
            0.92
        ),

        inset 0 1px 0 rgba(
            255,
            255,
            255,
            0.055
        ) !important;

    overflow: hidden !important;
}


/* Remove unwanted nested Gradio borders */

#chat-section > div {

    border: none !important;

    background: transparent !important;

    box-shadow: none !important;
}


#chat-history {

    border: none !important;

    background: transparent !important;

    box-shadow: none !important;
}


/* =========================================================
   DASHBOARD LINK
   ========================================================= */

#dashboard-link {

    text-align: center;

    margin-top: 25px;

    margin-bottom: 15px;
}


#dashboard-link a {

    display: inline-block;

    color: #c4b5fd;

    text-decoration: none;

    font-size: 14px;

    font-weight: 700;

    padding: 10px 18px;

    border: 1px solid rgba(
        139,
        92,
        246,
        0.35
    );

    border-radius: 10px;

    background: rgba(
        30,
        20,
        45,
        0.45
    );

    box-shadow:

        0 8px 18px rgba(
            37,
            8,
            65,
            0.65
        ),

        0 3px 7px rgba(
            0,
            0,
            0,
            0.7
        );

    transition: 0.18s ease;
}


#dashboard-link a:hover {

    color: #ffffff;

    border-color: #a78bfa;

    transform: translateY(-2px);

    box-shadow:

        0 12px 22px rgba(
            37,
            8,
            65,
            0.8
        ),

        0 4px 8px rgba(
            0,
            0,
            0,
            0.8
        );
}


/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 700px) {

    #cloudwise-header h1 {

        font-size: 32px;
    }

    #billing-area {

        padding: 15px !important;

        border-radius: 15px !important;
    }

    #chat-section {

        border-radius: 16px !important;
    }
}

"""


# =========================================================
# GRADIO APP
# =========================================================

with gr.Blocks(
    title="CloudWise AI",
    css=custom_css
) as app:

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    gr.HTML(
        """
        <div id="cloudwise-header">

            <h1>🤖 CloudWise AI</h1>

            <p>
                AI FinOps Assistant for Cloud Cost
                & Resource Optimization
            </p>

        </div>
        """
    )


    # -----------------------------------------------------
    # PREVIOUS / NEW DATA
    # -----------------------------------------------------

    with gr.Column(
        elem_id="billing-area"
    ):

        gr.Markdown(
            "📂 **Previous Data / New Data**",
            elem_id="billing-title"
        )

        with gr.Row():

            previous_button = gr.Button(
                "📊 Use Previous Data",
                elem_id="previous-button"
            )

            upload = gr.File(
                label="Upload New CSV",
                file_types=[".csv"],
                type="filepath",
                elem_id="upload-area"
            )

        status = gr.Markdown(
            "Choose previous billing data or upload a new CSV.",
            elem_id="status"
        )

        billing_path = gr.State(
            PREVIOUS_BILLING_FILE
            if os.path.exists(
                PREVIOUS_BILLING_FILE
            )
            else None
        )


    # -----------------------------------------------------
    # QUICK QUESTIONS
    # -----------------------------------------------------

    gr.Markdown(
        "💡 **Quick Questions**",
        elem_id="quick-title"
    )

    with gr.Row():

        total_button = gr.Button(
            "💰 Total Cost",
            elem_classes=["quick-btn"]
        )

        service_button = gr.Button(
            "🏆 Top Service",
            elem_classes=["quick-btn"]
        )

        waste_button = gr.Button(
            "⚠️ Find Waste",
            elem_classes=["quick-btn"]
        )

        summary_button = gr.Button(
            "📋 Summary",
            elem_classes=["quick-btn"]
        )


    # -----------------------------------------------------
    # RANDOM QUESTION
    # -----------------------------------------------------

    with gr.Row(
        elem_id="question-row"
    ):

        question = gr.Textbox(
            placeholder=(
                "Ask a random question "
                "about your cloud billing..."
            ),

            show_label=False,

            lines=2,

            scale=6,

            elem_id="question-box"
        )

        ask_button = gr.Button(
            "Ask AI",

            scale=1,

            elem_id="ask-button"
        )


    # -----------------------------------------------------
    # CHAT / ANSWER
    # -----------------------------------------------------

    with gr.Group(
        elem_id="chat-section"
    ):

      chatbot = gr.Chatbot(
    height=460,
    label="💬 Chat / Answer",
    elem_id="chat-history"
)  

    # -----------------------------------------------------
    # BACK TO MAIN DASHBOARD
    # -----------------------------------------------------

    gr.HTML(
        """
        <div id="dashboard-link">

            <a
                href="http://127.0.0.1:7860"
                
            >
                ← Back to CloudWise Dashboard
            </a>

        </div>
        """
    )


    # =====================================================
    # BUTTON EVENTS
    # =====================================================

    previous_button.click(

        fn=use_previous_data,

        inputs=[],

        outputs=[
            billing_path,
            status
        ]
    )


    upload.change(

        fn=use_new_data,

        inputs=upload,

        outputs=[
            billing_path,
            status
        ]
    )


    ask_button.click(

        fn=ask_cloudwise,

        inputs=[
            billing_path,
            question,
            chatbot
        ],

        outputs=[
            chatbot,
            question
        ]
    )


    question.submit(

        fn=ask_cloudwise,

        inputs=[
            billing_path,
            question,
            chatbot
        ],

        outputs=[
            chatbot,
            question
        ]
    )


    # -----------------------------------------------------
    # QUICK QUESTION: TOTAL COST
    # -----------------------------------------------------

    total_button.click(

        fn=ask_cloudwise,

        inputs=[
            billing_path,
            gr.State(
                "How much did I spend?"
            ),
            chatbot
        ],

        outputs=[
            chatbot,
            question
        ]
    )


    # -----------------------------------------------------
    # QUICK QUESTION: TOP SERVICE
    # -----------------------------------------------------

    service_button.click(

        fn=ask_cloudwise,

        inputs=[
            billing_path,
            gr.State(
                "Which service costs the most?"
            ),
            chatbot
        ],

        outputs=[
            chatbot,
            question
        ]
    )


    # -----------------------------------------------------
    # QUICK QUESTION: WASTE
    # -----------------------------------------------------

    waste_button.click(

        fn=ask_cloudwise,

        inputs=[
            billing_path,
            gr.State(
                "Find potentially wasteful resources."
            ),
            chatbot
        ],

        outputs=[
            chatbot,
            question
        ]
    )


    # -----------------------------------------------------
    # QUICK QUESTION: SUMMARY
    # -----------------------------------------------------

    summary_button.click(

        fn=ask_cloudwise,

        inputs=[
            billing_path,
            gr.State(
                "Give me a summary of my cloud billing."
            ),
            chatbot
        ],

        outputs=[
            chatbot,
            question
        ]
    )


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("                 CLOUDWISE AI")
    print("=" * 60)
    print()
    print("AI Chat:")
    print("http://127.0.0.1:7861")
    print()
    print("Main Dashboard:")
    print("http://127.0.0.1:7860")
    print()

    app.launch(
        server_port=7861,
        inbrowser=True
    )


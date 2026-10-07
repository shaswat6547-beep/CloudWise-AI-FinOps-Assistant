from chat_engine import answer_question

file_path = "sample_billing.csv"

questions = [
    "What is my total cloud cost?",
    "Which service costs the most?",
    "Which resources are wasting money?",
    "Which resource is the most expensive?"
]

print("\n===== CLOUDWISE AI CHAT TEST =====\n")

for question in questions:
    print("YOU:", question)
    print("CLOUDWISE:", answer_question(file_path, question))
    print()
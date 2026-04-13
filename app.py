# # # ================================
# # # 🚀 Fake Review Detection System
# # # ================================

# # print("🚀 App started...")

# # import pickle
# # import re
# # import gradio as gr
# # import google.generativeai as genai

# # # ================================
# # # 🔹 Load Model + Vectorizer
# # # ================================
# # with open('model.pkl', 'rb') as f:
# #     model = pickle.load(f)

# # with open('vectorizer.pkl', 'rb') as f:
# #     vectorizer = pickle.load(f)

# # print("✅ Model loaded")

# # # ================================
# # # 🔹 Gemini Setup
# # # ================================
# # genai.configure(api_key="AIzaSyCWpN3IBv3TLuN9i5TDg3eR9iwpiXWzFi4")  # 🔴 PUT YOUR KEY HERE

# # model_gemini = genai.GenerativeModel("gemini-flash-latest")

# # # ================================
# # # 🔹 Cache
# # # ================================
# # gemini_cache = {}

# # # ================================
# # # 🔹 Text Cleaning
# # # ================================
# # def clean_text(text):
# #     text = str(text).lower()
# #     text = re.sub(r'[^a-z\s]', '', text)
# #     text = re.sub(r'\s+', ' ', text)
# #     return text

# # # ================================
# # # 🔹 Gemini Function
# # # ================================
# # def analyze_with_gemini(review):
# #     print("🚨 Gemini API CALLED")

# #     if review in gemini_cache:
# #         print("✅ Using cache")
# #         return gemini_cache[review]

# #     try:
# #         prompt = f"""
# #         Analyze this review:

# #         "{review}"

# #         Respond EXACTLY like:
# #         Type: <AI/Human>
# #         Authenticity: <Fake/Genuine>
# #         Reason: <short reason>
# #         """

# #         response = model_gemini.generate_content(prompt)
# #         result = response.text.strip()

# #     except Exception as e:
# #         print("⚠️ Gemini failed → using fallback")

# #         result = """Type: Unknown
# # Authenticity: Fake
# # Reason: Fallback due to API issue"""

# #     gemini_cache[review] = result
# #     return result

# # # ================================
# # # 🔹 Main Logic
# # # ================================
# # def analyze_input(text):
# #     if not text.strip():
# #         return "⚠️ Please enter reviews"

# #     reviews = text.split("\n")

# #     processed = []
# #     max_fake_prob = -1
# #     suspicious_index = -1

# #     # 🔹 Step 1: ML (fast)
# #     for review in reviews:
# #         if review.strip() == "":
# #             continue

# #         cleaned = clean_text(review)
# #         vector = vectorizer.transform([cleaned])

# #         pred = model.predict(vector)[0]
# #         probs = model.predict_proba(vector)[0]

# #         fake_prob = probs[0]
# #         label = "Real" if pred == 1 else "Fake"

# #         processed.append((review, label, fake_prob))

# #         if fake_prob > max_fake_prob:
# #             max_fake_prob = fake_prob
# #             suspicious_index = len(processed) - 1

# #     if len(processed) == 0:
# #         return "⚠️ No valid reviews entered"

# #     print("🚨 Gemini will be called ONCE")

# #     # 🔹 Only ONE Gemini call
# #     gemini_output = analyze_with_gemini(processed[suspicious_index][0])

# #     results = []
# #     real_count = 0

# #     for i, (review, label, fake_prob) in enumerate(processed):

# #         if label == "Real":
# #             real_count += 1

# #         if i == suspicious_index:
# #             result = f"""
# # 🔥 Most Suspicious Review:
# # {review}

# # ML Label: {label}
# # Fake Probability: {fake_prob:.2f}

# # Gemini Analysis:
# # {gemini_output}
# # """
# #         else:
# #             result = f"""
# # Review: {review}
# # Label: {label}
# # Fake Probability: {fake_prob:.2f}
# # """

# #         results.append(result)

# #     total = len(processed)
# #     trust_score = (real_count / total) * 100

# #     return f"""
# # 📊 SUMMARY:
# # Total Reviews: {total}
# # Real Reviews: {real_count}
# # Trust Score: {trust_score:.2f}%

# # {'='*50}
# # """ + "\n".join(results)

# # # ================================
# # # 🔹 Gradio UI
# # # ================================
# # interface = gr.Interface(
# #     fn=analyze_input,
# #     inputs=gr.Textbox(
# #         lines=10,
# #         placeholder="Enter one review per line..."
# #     ),
# #     outputs="text",
# #     title="🧠 Fake Review Detection System",
# #     description="⚡ ML for bulk + 🤖 Gemini for deep analysis"
# # )

# # print("🚀 Launching Gradio...")

# # interface.launch(share=True, inbrowser=True)



# from flask import Flask, render_template, request
# import pickle
# import re
# import google.generativeai as genai

# app = Flask(__name__)

# # Load model
# with open('model.pkl', 'rb') as f:
#     model = pickle.load(f)

# with open('vectorizer.pkl', 'rb') as f:
#     vectorizer = pickle.load(f)

# # Gemini
# genai.configure(api_key="AIzaSyCWpN3IBv3TLuN9i5TDg3eR9iwpiXWzFi4")
# model_gemini = genai.GenerativeModel("gemini-flash-latest")

# gemini_cache = {}

# def clean_text(text):
#     text = str(text).lower()
#     text = re.sub(r'[^a-z\s]', '', text)
#     text = re.sub(r'\s+', ' ', text)
#     return text

# def analyze_with_gemini(review):
#     # Check cache
#     if review in gemini_cache:
#         return gemini_cache[review]

#     try:
#         prompt = f"""
# Analyze this review for authenticity.

# IMPORTANT:
# - Do NOT assume dates are invalid or fake.
# - Ignore whether the date is in the future.
# - Focus on writing style, detail, and realism.
# - Do NOT overthink or hallucinate reasons.

# Review:
# "{review}"

# Respond EXACTLY like:
# Type: <AI/Human>
# Authenticity: <Fake/Genuine>
# Reason: <short reason>
# """

#         response = model_gemini.generate_content(prompt)
#         result = response.text.strip()

#         # 🚫 Fix bad reasoning (extra safety)
#         if "future date" in result.lower():
#             result = """Type: Human
# Authenticity: Genuine
# Reason: Detailed and realistic review"""

#     except Exception as e:
#         print("Gemini error:", e)
#         result = """Type: Unknown
# Authenticity: Unknown
# Reason: API fallback"""

#     # Save to cache
#     gemini_cache[review] = result
#     return result

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     results = []
#     trust_score = None
    
#     if request.method == 'POST':
#         text = request.form['reviews']
#         reviews = text.split("\n")
        
#         processed = []
#         max_fake_prob = -1
#         suspicious_index = -1
        
#         for review in reviews:
#             if review.strip() == "":
#                 continue
            
#             cleaned = clean_text(review)
#             vector = vectorizer.transform([cleaned])
            
#             pred = model.predict(vector)[0]
#             probs = model.predict_proba(vector)[0]
            
#             fake_prob = probs[0]
#             label = "Real" if pred == 1 else "Fake"
            
#             processed.append((review, label, fake_prob))
            
#             if fake_prob > max_fake_prob:
#                 max_fake_prob = fake_prob
#                 suspicious_index = len(processed) - 1
        
#         if processed:
#             gemini_output = analyze_with_gemini(processed[suspicious_index][0])
            
#             real_count = sum(1 for r in processed if r[1] == "Real")
#             trust_score = round((real_count / len(processed)) * 100, 2)
            
#             for i, (review, label, prob) in enumerate(processed):
#                 results.append({
#                     "text": review,
#                     "label": label,
#                     "prob": round(prob, 2),
#                     "is_suspicious": i == suspicious_index,
#                     "gemini": gemini_output if i == suspicious_index else None
#                 })
    
#     return render_template('index.html', results=results, trust_score=trust_score)

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request
import pickle
import re
import google.generativeai as genai

app = Flask(__name__)

# Load model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# Gemini setup
genai.configure(api_key="AIzaSyCWpN3IBv3TLuN9i5TDg3eR9iwpiXWzFi4")
model_gemini = genai.GenerativeModel("gemini-flash-latest")

gemini_cache = {}

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def analyze_with_gemini(review):
    if review in gemini_cache:
        return gemini_cache[review]

    try:
        prompt = f"""
Analyze this review for authenticity.

IMPORTANT:
- Ignore date validity.
- Focus on writing style, realism, and detail.

Review:
"{review}"

Respond EXACTLY like:
Type: <AI/Human>
Authenticity: <Fake/Genuine>
Reason: <short reason>
"""
        response = model_gemini.generate_content(prompt)
        result = response.text.strip()

    except:
        result = "Type: Unknown | Authenticity: Unknown | Reason: API issue"

    gemini_cache[review] = result
    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    trust_score = None

    if request.method == 'POST':
        text = request.form['reviews']
        reviews = text.split("\n")

        processed = []
        max_fake_prob = -1
        suspicious_index = -1

        for review in reviews:
            if review.strip() == "":
                continue

            cleaned = clean_text(review)
            vector = vectorizer.transform([cleaned])

            pred = model.predict(vector)[0]
            probs = model.predict_proba(vector)[0]

            fake_prob = probs[0]
            label = "Real" if pred == 1 else "Fake"

            processed.append((review, label, fake_prob))

            if fake_prob > max_fake_prob:
                max_fake_prob = fake_prob
                suspicious_index = len(processed) - 1

        if processed:
            gemini_output = analyze_with_gemini(processed[suspicious_index][0])

            real_count = sum(1 for r in processed if r[1] == "Real")
            trust_score = round((real_count / len(processed)) * 100, 2)

            for i, (review, label, prob) in enumerate(processed):
                results.append({
                    "text": review,
                    "label": label,
                    "prob": round(prob, 2),
                    "is_suspicious": i == suspicious_index,
                    "gemini": gemini_output if i == suspicious_index else None
                })

    return render_template('index.html', results=results, trust_score=trust_score)

if __name__ == '__main__':
    app.run(debug=True)
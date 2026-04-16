from flask import Flask, render_template, request
import re
import os
import joblib
from google import genai  # ✅ updated SDK

app = Flask(__name__)

# ✅ Load ML model safely
model = joblib.load('model.joblib')
vectorizer = joblib.load('vectorizer.joblib')

# ✅ Gemini setup (new API)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        result = response.text.strip()

    except Exception as e:
        result = f"Type: Unknown | Authenticity: Unknown | Reason: {str(e)}"

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


# ✅ Only ONE run block (Render compatible)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
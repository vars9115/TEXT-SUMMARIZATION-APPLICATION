from flask import Flask, render_template, request
import nltk
import re
from collections import Counter

app = Flask(__name__)

# Download required NLTK data
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

STOP_WORDS = set(stopwords.words("english"))


def summarize_text(text, sentence_count=3):

    # Split text into sentences
    sentences = sent_tokenize(text)

    # If text is already short
    if len(sentences) <= sentence_count:
        return text

    # Tokenize words
    words = word_tokenize(text.lower())

    # Calculate word frequency
    word_frequency = Counter(
        word for word in words
        if word.isalnum() and word not in STOP_WORDS
    )

    if not word_frequency:
        return sentences[0]

    # Normalize frequency
    max_frequency = max(word_frequency.values())

    for word in word_frequency:
        word_frequency[word] /= max_frequency

    # Calculate sentence scores
    sentence_scores = {}

    for sentence in sentences:

        sentence_words = word_tokenize(sentence.lower())

        score = sum(
            word_frequency.get(word, 0)
            for word in sentence_words
        )

        sentence_scores[sentence] = score

    # Select top sentences
    best_sentences = sorted(
        sentence_scores,
        key=sentence_scores.get,
        reverse=True
    )[:sentence_count]

    # Keep original sentence order
    summary = [
        sentence for sentence in sentences
        if sentence in best_sentences
    ]

    return " ".join(summary)


@app.route("/", methods=["GET", "POST"])
def home():

    summary = ""
    original_text = ""

    if request.method == "POST":

        original_text = request.form.get("text", "")

        if original_text.strip():

            summary = summarize_text(
                original_text,
                sentence_count=3
            )

    return render_template(
        "index.html",
        summary=summary,
        original_text=original_text
    )


if __name__ == "__main__":
    app.run(debug=True)
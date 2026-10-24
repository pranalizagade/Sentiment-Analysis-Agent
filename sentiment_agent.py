import time
import json
import os
import re

import pandas as pd
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL")
DATA_FILE = os.getenv(
    "DATA_FILE",
    "Synthetic Data - Social Media Tweets.xlsx",
)

if not API_KEY or not MODEL:
    raise ValueError("Set GROQ_API_KEY and GROQ_MODEL in .env")

client = Groq(api_key=API_KEY)


def load_tweets():
    df = pd.read_excel(DATA_FILE)
    df.columns = [str(c).strip() for c in df.columns]

    required = {"Tweet_ID", "Tweet_Text"}
    if not required.issubset(df.columns):
        raise ValueError(
            f"Excel must contain columns: {sorted(required)}"
        )

    df = df.dropna(subset=["Tweet_ID", "Tweet_Text"]).copy()
    df["Tweet_ID"] = df["Tweet_ID"].astype(str).str.strip()
    df["Tweet_Text"] = df["Tweet_Text"].astype(str).str.strip()
    return df.drop_duplicates(subset=["Tweet_ID"])



def ask_llm(prompt):
    """Call the LLM and retry when the rate limit is reached."""
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a careful social media sentiment "
                            "analysis assistant. Consider context, "
                            "negation, sarcasm, and emojis. "
                            "Do not invent facts."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content.strip()

        except Exception as error:
            # Retry only API rate-limit errors.
            from groq import RateLimitError

            if not isinstance(error, RateLimitError):
                raise

            if attempt == 2:
                raise

            print("API rate limit reached. Waiting 60 seconds...")
            time.sleep(60)

    raise RuntimeError("LLM request failed after retries.")


def classify_tweets(tweets):
    prompt = f"""
Classify every supplied tweet as Positive, Negative, or Neutral.
Consider the overall meaning, negation, sarcasm and emojis.
Factual announcements without a clear opinion are Neutral.
Give a concise explanation supported by the tweet.
Return valid JSON only, without Markdown fences.

Format:
{{
  "results": [
    {{
      "tweet_id": "TWT-001",
      "sentiment": "Negative",
      "reason": "The author describes a disappointing experience."
    }}
  ]
}}

Tweets:
{json.dumps(tweets, ensure_ascii=False)}
"""
    raw = ask_llm(prompt)
    match = re.search(r"\{.*\}", raw, re.DOTALL)

    if not match:
        raise ValueError("LLM did not return valid JSON.")

    data = json.loads(match.group())
    valid_ids = {t["tweet_id"] for t in tweets}
    results = []

    for item in data.get("results", []):
        tweet_id = str(item.get("tweet_id", "")).strip()
        sentiment = str(item.get("sentiment", "")).title()

        if tweet_id not in valid_ids:
            continue
        if sentiment not in {"Positive", "Negative", "Neutral"}:
            continue

        results.append({
            "tweet_id": tweet_id,
            "sentiment": sentiment,
            "reason": str(item.get("reason", "")).strip(),
        })

    return results


class SentimentAgent:
    def __init__(self):
        self.df = load_tweets()
        self.history = []

    def analyze_id(self, tweet_id):
        rows = self.df[
            self.df["Tweet_ID"].str.upper() == tweet_id.upper()
        ]

        if rows.empty:
            return f"Tweet {tweet_id} was not found."

        tweet = {
            "tweet_id": rows.iloc[0]["Tweet_ID"],
            "text": rows.iloc[0]["Tweet_Text"],
        }
        result = classify_tweets([tweet])

        if not result:
            return "No valid sentiment result was returned."

        item = result[0]
        return (
            f"Tweet ID: {tweet['tweet_id']}\n"
            f"Tweet: {tweet['text']}\n"
            f"Sentiment: {item['sentiment']}\n"
            f"Reason: {item['reason']}"
        )

    def analyze_custom(self, text):
        result = classify_tweets([
            {"tweet_id": "CUSTOM-001", "text": text}
        ])

        if not result:
            return "No valid sentiment result was returned."

        item = result[0]
        return (
            f"Sentiment: {item['sentiment']}\n"
            f"Reason: {item['reason']}"
        )

    
    
    def overall_summary(self):
        tweets = [
            {
                "tweet_id": str(row["Tweet_ID"]),
                "text": str(row["Tweet_Text"]),
            }
            for row in self.df.to_dict(orient="records")
        ]

        # Cache results in memory to avoid repeating API calls.
        if not hasattr(self, "sentiment_cache"):
            self.sentiment_cache = {}

        pending = [
            tweet for tweet in tweets
            if tweet["tweet_id"] not in self.sentiment_cache
        ]

        # Small batches reduce the size of individual API requests.
        for start in range(0, len(pending), 5):
            batch = pending[start:start + 5]

            try:
                results = classify_tweets(batch)
            except Exception as error:
                return (
                    "Full-dataset analysis is incomplete. "
                    f"Classified {len(self.sentiment_cache)} of "
                    f"{len(tweets)} tweets so far. API error: {error}"
                )

            for item in results:
                self.sentiment_cache[item["tweet_id"]] = item

            # Do not claim a complete distribution if the model
            # omitted any tweet in a batch.
            returned_ids = {r["tweet_id"] for r in results}
            missing_ids = {
                t["tweet_id"] for t in batch
            } - returned_ids

            if missing_ids:
                return (
                    "Analysis incomplete. No full-dataset "
                    "percentages will be reported. Missing results: "
                    + ", ".join(sorted(missing_ids))
                )

        results = [
            self.sentiment_cache[tweet["tweet_id"]]
            for tweet in tweets
        ]

        counts = {
            label: sum(
                r["sentiment"] == label for r in results
            )
            for label in ("Positive", "Negative", "Neutral")
        }

        total = len(results)
        if total == 0:
            return "No tweets were classified successfully."

        lines = [
            f"Total tweets analyzed: {total}",
            "Overall sentiment distribution:",
        ]

        for label, count in counts.items():
            lines.append(
                f"{label}: {count} ({count / total * 100:.1f}%)"
            )

        return "\n".join(lines)



    def answer(self, question):
        question = question.strip()

        if question.lower().startswith("analyze:"):
            text = question[len("analyze:"):].strip()
            if not text:
                return "Please provide a tweet after 'analyze:'."
            return self.analyze_custom(text)

        ids = re.findall(r"\bTWT-\d{3}\b", question.upper())
        if ids:
            return "\n\n".join(
                self.analyze_id(tweet_id) for tweet_id in ids
            )

        summary_terms = (
            "overall sentiment",
            "sentiment distribution",
            "sentiment summary",
            "all tweets",
        )
        if any(term in question.lower() for term in summary_terms):
            return self.overall_summary()

        context = self.df.to_dict(orient="records")
        prompt = f"""
Answer the question using the supplied synthetic tweet dataset.
Do not invent tweet IDs, quotes, statistics or facts.
For exact overall percentages, use the sentiment summary operation.

Dataset:
{json.dumps(context, ensure_ascii=False)}

Previous conversation:
{json.dumps(self.history[-6:], ensure_ascii=False)}

Question: {question}

Give a concise answer and cite relevant tweet IDs where possible.
"""
        answer = ask_llm(prompt)
        self.history.extend([
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ])
        return answer

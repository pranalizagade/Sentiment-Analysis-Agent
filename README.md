# Sentiment Studio | AI-Powered Social Media Sentiment Analysis

<p align="center">
  <strong>Turn social media conversations into meaningful insights.</strong>
  <br/>
  An interactive AI assistant for tweet sentiment analysis, contextual interpretation, and sentiment exploration.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/LLM-Groq_API-orange?style=flat-square" alt="Groq API"/>
  <img src="https://img.shields.io/badge/Project-UC03-7057ff?style=flat-square" alt="UC03"/>
</p>

---

## Overview

Social media is full of opinions, reactions, feedback, and emotions. Extracting meaningful insights from these conversations requires understanding context—not just identifying positive or negative words.

**Sentiment Studio** is a Python-based AI application that uses a large language model (LLM) through the Groq API to analyze social media messages and explain their sentiment.

The project includes an interactive Streamlit dashboard where users can analyze individual tweets and explore available social media data.

## Features

| Feature | Description |
|---|---|
| 💬 Tweet Analysis | Submit a social media message for sentiment analysis. |
| 🧠 Contextual Understanding | Interpret the meaning and context behind a message. |
| 🔎 Explainable Results | View a natural-language explanation of the predicted sentiment. |
| 📊 Sentiment Visualization | Explore sentiment distributions and trends in the available dataset. |
| 🗂️ Dataset Explorer | Search and inspect available tweet data. |
| 📈 Overall Insights | Review sentiment summaries when supported by the available data and analysis results. |

## Application Preview

The Streamlit interface provides navigation for:

- **Overview** — explore the sentiment analysis application.
- **Analyze a tweet** — submit text and inspect the sentiment prediction.
- **Explore dataset** — search and explore the available tweet dataset.

> Add screenshots of your running dashboard here to give visitors a visual preview of the application.

<!-- Replace the placeholder below after adding a screenshot to your repository. -->
<!-- ![Sentiment Studio Dashboard](screenshots/dashboard.png) -->

## How It Works

```text
          Tweet / Social Media Text
                     |
                     v
             Input Processing
                     |
                     v
              Groq API + LLM
                     |
                     v
            Sentiment Interpretation
                     |
             +-------+-------+
             |               |
             v               v
       Sentiment Label   Explanation
             |               |
             +-------+-------+
                     |
                     v
             Results in Dashboard
```

## Technology Stack

- **Language:** Python
- **Frontend / Dashboard:** Streamlit
- **LLM Integration:** Groq API
- **Configuration:** Environment variables using `.env`
- **Data:** Excel-based social media tweet dataset, if supplied and used by the application

## Project Structure

```text
Sentiment-Analysis-Agent/
├── main.py
├── sentiment_agent.py
├── streamlit_app.py
├── requirements.txt
├── README.md
├── .gitignore
└── Synthetic Data - Social Media Tweets.xlsx  # If included
```

The `.env` file is created locally and should never be committed to GitHub.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/pranalizagade/Sentiment-Analysis-Agent.git
cd Sentiment-Analysis-Agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure your API key

Create a `.env` file in the project root and provide the credentials expected by your application.

For example:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_supported_model_name
```

Replace the placeholders with your own values. Use the exact variable names and model configuration expected by the source code. Never publish real credentials.

### 5. Launch the dashboard

```bash
python -m streamlit run streamlit_app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

### 6. Run the terminal assistant

If you want to use the original command-line interface, run:

```bash
python main.py
```

## Example

**Input message**

> "The new update looks amazing, but the application keeps crashing."

**Possible interpretation**

- Positive aspect: The user likes the update.
- Negative aspect: The user is frustrated by application crashes.
- Context: The message contains both praise and criticism.

The actual classification and explanation are generated by the configured model and may vary.

## Security and Data Privacy

- Keep API keys in your local `.env` file.
- Exclude `.env`, virtual environments, and Python cache files through `.gitignore`.
- Never commit credentials or private datasets.
- Publish the Excel dataset only if you have permission to share it and it is appropriate for a public repository.

## Future Enhancements

- Add interactive sentiment trend filters.
- Support batch tweet analysis and downloadable reports.
- Evaluate predictions against labeled test data.
- Add additional visualizations and model-performance metrics.
- Deploy the dashboard for public access.

## About the Developer

**Pranali Zagade**  
Artificial Intelligence & Data Science Engineering Student

Interested in AI/ML, generative AI, AI agents, and full-stack development.

- GitHub: [@pranalizagade](https://github.com/pranalizagade)
- Project Repository: [Sentiment-Analysis-Agent](https://github.com/pranalizagade/Sentiment-Analysis-Agent)

---

<p align="center">
  <i>Built as part of UC03 — Social Media Sentiment Analysis Agent.</i>
</p>

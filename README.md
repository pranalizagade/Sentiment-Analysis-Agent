
# UC03 – Social Media Sentiment Analysis Agent

## Overview
A Python-based AI assistant that analyzes social media tweets using a large language model through the Groq API.

## Features
- Analyze tweets by Tweet ID
- Classify sentiment as Positive, Negative, or Neutral
- Explain sentiment classifications
- Analyze custom tweet text
- Calculate overall sentiment distribution
- Handle contextual expressions and sarcasm

## Technologies
- Python
- Pandas
- Groq API
- python-dotenv
- OpenPyXL

## Setup
Install the required packages:

```bash
python -m pip install groq python-dotenv pandas openpyxl
```

Create a `.env` file containing your Groq API key and the model configuration expected by the application.

## Run
```bash
python main.py
```

Follow the terminal prompts to interact with the agent.


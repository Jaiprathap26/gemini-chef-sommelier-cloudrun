# 👨‍🍳 Gemini AI Culinary & Wine Sommelier Engine

[![Google Cloud Run](https://img.shields.io/badge/Google_Cloud_Run-Deployed-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Gemini 1.5 Flash](https://img.shields.io/badge/Model-Gemini_1.5_Flash-8E75C4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

An enterprise-grade generative AI assistant generating custom recipes and sommelier-level wine pairings based on multi-factor user constraints.

## Architecture
- **Model:** Google Gemini 2.5 Flash via Google GenAI SDK.
- **Frontend:** Streamlit interactive web interface with dynamic radio and selection controls.
- **Containerization:** Docker containerized and stored in Google Artifact Registry.
- **Deployment:** Serverless deployment on Google Cloud Run with autoscaling.

## Local & Cloud Run Execution
```bash
pip install -r requirements.txt
streamlit run app.py --server.port=8080


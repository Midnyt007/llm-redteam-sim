FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e .
ENV LLM_PROVIDER=openai
CMD ["python", "-m", "llm_redteam_sim.run", "--out", "out/docker"]

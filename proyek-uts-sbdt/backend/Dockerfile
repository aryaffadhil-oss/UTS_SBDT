# Stage 1: Builder & Model Training
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
COPY train_model.py .
RUN python train_model.py

# Stage 2: Runtime Image
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/model.joblib ./model.joblib
ENV PATH=/root/.local/bin:$PATH
COPY main.py .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
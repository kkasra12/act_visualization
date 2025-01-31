FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://quarto.org/download/latest/install.sh | bash

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["quarto", "render", "--output-dir", "docs"]

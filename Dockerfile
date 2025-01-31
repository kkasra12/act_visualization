FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y wget ca-certificates && rm -rf /var/lib/apt/lists/*

RUN wget -qO quarto.deb "https://quarto.org/download/latest/quarto-linux-amd64.deb" \
    && dpkg -i quarto.deb \
    && rm quarto.deb

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["quarto", "render", "--output-dir", "docs"]

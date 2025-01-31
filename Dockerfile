FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y wget ca-certificates libfontconfig && rm -rf /var/lib/apt/lists/*

RUN wget -qO quarto.deb "https://quarto.org/download/latest/quarto-linux-amd64.deb" && dpkg -i quarto.deb && rm quarto.deb
RUN quarto install tinytex

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader stopwords punkt wordnet

# CMD ["quarto", "render", "--output-dir", "docs_docker"]
# CMD quarto render --output-dir /tmp/docs_docker && cp -r /tmp/docs_docker/* docs_docker/
CMD ["sh", "-c", "quarto render --output-dir /tmp/docs_docker && cp -r /tmp/docs_docker/* docs_docker/"]

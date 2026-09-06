# Asgard Suite — immagine unica per tutti i moduli.
# Un solo image semplifica manutenzione e distribuzione: ogni servizio
# di docker-compose.yml usa la stessa immagine con command diversi.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dipendenze di tutti i moduli (layer cached finché i requirements non cambiano)
COPY Bifrost/requirements.txt /tmp/req-bifrost.txt
COPY Fenrir/requirements.txt /tmp/req-fenrir.txt
COPY Forseti/requirements.txt /tmp/req-forseti.txt
COPY Gjallarhorn/requirements.txt /tmp/req-gjallarhorn.txt
COPY Heimdall/requirements.txt /tmp/req-heimdall.txt
COPY Mjolnir/requirements.txt /tmp/req-mjolnir.txt
COPY Sleipnir/requirements.txt /tmp/req-sleipnir.txt
COPY Yggdrasil/requirements.txt /tmp/req-yggdrasil.txt
COPY Ragnarok/backend/requirements.txt /tmp/req-ragnarok.txt
COPY Ragnarok/backend/requirements-rag.txt /tmp/req-rag.txt
RUN pip install --no-cache-dir \
    -r /tmp/req-heimdall.txt -r /tmp/req-bifrost.txt -r /tmp/req-fenrir.txt \
    -r /tmp/req-mjolnir.txt -r /tmp/req-sleipnir.txt -r /tmp/req-yggdrasil.txt \
    -r /tmp/req-forseti.txt -r /tmp/req-gjallarhorn.txt \
    -r /tmp/req-ragnarok.txt -r /tmp/req-rag.txt

# Codice della suite
COPY . /app

# Utente non privilegiato. UID fisso (1000) per permessi consistenti
# nei bind-mount e volume Docker (utile per chi usa `user: "1000" in compose).
RUN useradd --create-home --uid 1000 asgard && chown -R 1000:1000 /app
USER 1000

# HTTP: Heimdall 8000, Ragnarök 8080, Gjallarhorn 8090, Forseti 8091, Bifrost 8092
EXPOSE 8000 8080 8090 8091 8092

# Default: orchestrator Ragnarök (i singoli servizi sovrascrivono il command)
WORKDIR /app/Ragnarok/backend
CMD ["python", "server.py"]

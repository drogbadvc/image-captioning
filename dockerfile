# Utiliser une image de base officielle Python
FROM python:3.8-slim

# Mettre à jour les packages et installer git et wget
RUN apt-get update \
    && apt-get install -y git wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers du projet dans le conteneur
COPY . /app

# Installer git
RUN apt-get update \
    && apt-get install -y git

# Installer les dépendances Python à partir de requirements.txt
# Assurez-vous que uvicorn est listé dans requirements.txt ou installez-le ici directement
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install uvicorn

# Télécharger le modèle pré-entraîné et le stocker dans le bon dossier
RUN mkdir -p api/pretrained \
    && wget -q -O api/pretrained/tag2text_swin_14m.pth https://huggingface.co/spaces/xinyu1205/recognize-anything/resolve/main/tag2text_swin_14m.pth

# Exposer le port sur lequel l'application va tourner
EXPOSE 8501 8000

# Utiliser un script pour démarrer à la fois Streamlit et Uvicorn
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Exécuter le script au démarrage du conteneur
CMD ["/app/start.sh"]

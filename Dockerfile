FROM python:3.12-slim

# Instalar dependencias del sistema y ODBC Driver para SQL Server
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    unixodbc-dev \
    tdsodbc \
    gnupg2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurar el repositorio de Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-tools.list

# Instalar el driver ODBC específico de SQL Server
RUN apt-get update && apt-get install -y --no-install-recommends \
    msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Comando de inicio corregido para la estructura app/main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

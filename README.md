# Portfolio Backend
This is the backend for my personal portfolio, built with FastAPI.
## ✨ Features
- **FastAPI**: Modern, fast (high-performance) web framework for building APIs.
- **SQLAlchemy & SQL Server**: For ORM and database interaction.
- **Pydantic**: For data validation and settings management.
- **JWT**: For secure authentication.
- **Docker & Docker Compose**: For containerization and easy setup.
- **uv**: For lightning-fast project and dependency management.
- **Layered Architecture**: For clean, scalable, and maintainable code.
## 🚀 Getting Started
### Environment Configuration (`.env` file)
Before running the project, you must configure your environment.
1.  **Create the `.env` file:**
    ```bash
    cp .env.example .env
    ```
2.  **Edit the `.env` file:**
    -   Set a strong `SECRET_KEY`.
    -   Choose your database setup by setting `USE_DOCKER_DB` to `True` or `False`.
    -   Fill in the database credentials (`DB_USER`, `DB_PASSWORD`, etc.) that correspond to your choice.
---
### Option 1: Running with Docker (Recommended)
This is the easiest way to get started, as it handles the database setup for you.
#### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
#### Steps
1.  **Configure your `.env` file:**
    -   Set `USE_DOCKER_DB=True`.
    -   Set a `DB_PASSWORD` for the local database.
    -   The other `DB_*` variables can usually be left as they are.
2.  **Build and Run with Docker Compose:**
    From the root of the project, run:
    ```bash
    docker-compose up --build
    ```
    This will build the FastAPI image, pull the SQL Server image, and start both services.
---
### Option 2: Running Locally with `uv`
Use this option if you prefer not to use Docker and want to connect to a remote database (like Azure SQL).
#### Prerequisites
- Python 3.11+
- `uv` installed (`pip install -U uv`)
- An ODBC Driver for SQL Server (e.g., [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server))
- Access to a SQL Server database (local or remote).
#### Steps
1.  **Configure your `.env` file:**
    -   Set `USE_DOCKER_DB=False`.
    -   Fill in the `DB_USER`, `DB_PASSWORD`, `DB_SERVER`, `DB_PORT`, and `DB_NAME` with the credentials for your remote database.
2.  **Create and activate a virtual environment:**
    ```bash
    uv venv --python 3.11
    source .venv/bin/activate  # On macOS/Linux
    # .venv\Scripts\activate  # On Windows
    ```
3.  **Install dependencies:**
    ```bash
    uv pip install -e .
    ```
4.  **Run the application:**
    For development with live reloading, run:
    ```bash
    uvicorn app.main:app --reload
    ```
## 🌐 Accessing the API
Once the server is running (with either method), the API will be available at `http://localhost:8000`.
You can access the interactive API documentation (Swagger UI) at:
**[http://localhost:8000/docs](http://localhost:8000/docs)**
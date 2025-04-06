
# Money Management Project

This project is a transaction management system that includes both an API and a Telegram bot. It uses Docker and Docker Compose for containerization, and PostgreSQL for data storage.

## Requirements

Before running the project, make sure you have the following tools installed:

- Docker
- Docker Compose

## Environment Setup

To ensure proper functionality, you need to fill in the environment files:

1. `.env` — the main environment file for the API.
2. `.env.bot` — the environment file for the Telegram bot.
3. `.env.backend` — the environment file for the backend service.

Each of these files needs to have the necessary parameters for database connection, API settings, and other key environment variables. To set up the example configuration, copy the environment files with the `.example` extension:

```bash
cp .env .env.example
cp .env.bot .env.bot.example
cp .env.backend .env.backend.example
```

After you fill in the correct values in these files, proceed to the next step.

## Running the Project

1. In the root directory of the project, run the command to build and start the containers:

```bash
docker compose up --build
```

This command will build the containers for the backend service and Telegram bot, and install all the dependencies from the `Dockerfile` and `docker-compose.yml`.

2. Once successfully started, your application will be available on the specified port, which is configured in the `docker-compose.yml`.

## Project Structure

```bash
.
├── alembic
│    ├── env.py
│    ├── script.py.mako
│    └── versions
│        └── d7932a85742e_create_transactions_table.py
├── alembic.ini
├── app
│    ├── api
│    │    ├── __init__.py
│    │    └── main.py
│    ├── bot
│    │    ├── bot_constants.py
│    │    ├── handlers
│    │    │    ├── add_transaction_handler.py
│    │    │    ├── delete_transaction_handler.py
│    │    │    ├── edit_transaction_handler.py
│    │    │    ├── get_report_handler.py
│    │    │    └── __init__.py
│    │    ├── init_bot.py
│    │    ├── init_logger.py
│    │    ├── __init__.py
│    │    ├── init_states.py
│    │    ├── money_bot.py
│    │    └── report_utils.py
│    ├── core
│    │    ├── db.py
│    │    └── __init__.py
│    ├── __init__.py
│    ├── models
│    │    ├── __init__.py
│    │    └── Transaction.py
│    ├── pydantic_validator.py
│    └── utils
│        └── currency.py
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.bot
├── pyproject.toml
├── README.md
├──requirements.txt
└── .env, .env.bot, .env.backend

```

## Notes

- Ensure that all environment variables in `.env`, `.env.bot`, and `.env.backend` are correctly filled in, otherwise the project may not start properly.
- If you encounter issues when starting the containers, check the logs with `docker-compose logs`.

## License

This project is licensed under the MIT License.

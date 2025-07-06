"""
BaseConfig is a configuration class that holds the essential settings and parameters
required by the application. This class provides a centralized way to manage configurations
related to debugging, testing, language models selection, Azure OpenAI client, database
connections, and prompt templates.
"""
import os
from sqlalchemy import create_engine
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector

from app.logger.logger import Logger


class BaseConfig(object):
    DEBUG = False
    TESTING = False

    SCHEDULE_WINDOW = os.environ.get("SCHEDULE_WINDOW", "*/15 * * * *")
    PRODUCT_FILE = os.environ.get("OPPORTUNITY_PRODUCT_DATA_FILE", r"C:\Users\04413P744\PycharmProjects\redhat-hackathon-2025\app\file_path\Opportunity Product Data.csv")

    # DB Config
    DATABASE_HOST = os.environ.get("PGVECTOR_HOST", "localhost")
    DATABASE_NAME = os.environ.get("PGVECTOR_DB", "opportunity_db")
    DATABASE_USER = os.environ.get("PGVECTOR_USER", "postgres")
    DATABASE_PASSWORD = os.environ.get("PGVECTOR_PASSWORD", "newpassword")
    DATABASE_PORT = os.environ.get("PGVECTOR_PORT", "5432")
    DATABASE_SCHEMA = os.environ.get("PGVECTOR_SCHEMA", "public")
    OPPORTUNITY_DETAILS_TABLE = "opportunity_details"
    OPPORTUNITY_PRODUCT_EMBEDDINGS_TABLE = "opportunity_product_embeddings"

    # Create the connection string with schema
    db_url = (f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}"
              f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}")
    SQLALCHEMY_DATABASE_URI = db_url

    # Connection string using PGVector utility
    CONNECTION_STRING = PGVector.connection_string_from_db_params(
        driver="psycopg2",
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
    )

    # # Azure OpenAI embeddings config
    # AZURE_API_BASE = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    # AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "")
    # AZURE_OPENAI_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "")
    # AZURE_OPENAI_API_KEY = os.environ.get("API_KEY", "")
    # AZURE_OPENAI_TYPE = os.environ.get("AZURE_OPENAI_TYPE", "azure")
    #
    # embedding_function = AzureOpenAIEmbeddings(
    #     azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
    #     openai_api_version=AZURE_OPENAI_API_VERSION,
    #     openai_api_key=AZURE_OPENAI_API_KEY,
    #     azure_endpoint=AZURE_API_BASE,
    #     openai_api_type=AZURE_OPENAI_TYPE,
    # )

    # Create the SQLAlchemy engine
    engine = create_engine(
        CONNECTION_STRING,
        connect_args={
            "keepalives": 1,
            "keepalives_idle": 10,
            "keepalives_interval": 5,
            "keepalives_count": 3,
            "connect_timeout": 60
        },
        pool_size=20,
        max_overflow=0,
        pool_timeout=60,
        pool_recycle=900,
        pool_pre_ping=True
    )


class DevConfig(BaseConfig):
    DEBUG = True


class ProdConfig(BaseConfig):
    DEBUG = False


config = {
    'dev': DevConfig,
    'prod': ProdConfig
}


# def get_embedding_model() -> AzureOpenAIEmbeddings:
#     return BaseConfig.embedding_function


# LOG related Global configuration
LOG_LEVEL = os.environ.get("LOGLEVEL", "DEBUG")
app_logger = Logger(name="opportunity-product-data", log_level=LOG_LEVEL).get_logger()

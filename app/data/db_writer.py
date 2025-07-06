import os
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from app.config.app_config import BaseConfig, app_logger #, get_embedding_model,
from app.models.model import OpportunityDetails, OpportunityProductEmbedding

# embedding_model = get_embedding_model()


def read_csv_with_fallback(file_path):
    encodings = ['utf-8', 'ISO-8859-1', 'cp1252']
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            print(f"File read successfully with encoding: {enc}")
            return df
        except UnicodeDecodeError:
            print(f"Failed with encoding: {enc}")
    raise ValueError("Unable to read the file with tested encodings.")


def clear_existing_data(session):
    """
    Clear existing data and reset auto-increment IDs
    """
    try:
        # Delete all records from both tables (cascade should handle embeddings)
        # embedding_count = session.query(OpportunityProductEmbedding).count()
        details_count = session.query(OpportunityDetails).count()

        # if details_count > 0 or embedding_count > 0:
        if details_count > 0:
            app_logger.info(f"Found existing data - Details: {details_count}")
            # app_logger.info(f"Found existing data - Details: {details_count}, Embeddings: {embedding_count}")

            # Delete all embeddings first (to avoid foreign key constraints)
            # session.query(OpportunityProductEmbedding).delete()
            # app_logger.info("Deleted all existing embeddings")

            # Delete all opportunity details
            session.query(OpportunityDetails).delete()
            app_logger.info("Deleted all existing opportunity details")

            # Reset auto-increment counters (PostgreSQL)
            try:
                session.execute(text("ALTER SEQUENCE opportunity_details_id_seq RESTART WITH 1"))
                # session.execute(text("ALTER SEQUENCE opportunity_product_embedding_id_seq RESTART WITH 1"))
                app_logger.info("Reset auto-increment sequences")
            except Exception as seq_e:
                app_logger.warning(f"Could not reset sequences (might be using different DB): {seq_e}")

            session.commit()
            app_logger.info("Successfully cleared existing data and reset IDs")
        else:
            app_logger.info("No existing data found - proceeding with fresh insert")

    except Exception as e:
        app_logger.error(f"Error clearing existing data: {e}")
        session.rollback()
        raise


def insert_opportunity_data():
    """
    Inserts opportunity details and embeddings into database.
    """
    try:
        Session = sessionmaker(bind=BaseConfig.engine)
        session = Session()

        # Clear existing data and reset IDs
        clear_existing_data(session)

        # Read Excel file
        df = read_csv_with_fallback(BaseConfig.PRODUCT_FILE)
        app_logger.info(f"Read {len(df)} rows from csv.")

        successful_inserts = 0
        failed_inserts = 0

        # Iterate through each row and insert data
        for idx, row in df.iterrows():
            try:
                # Read columns
                opportunity_ref = str(row['Opportunity Reference']) if pd.notnull(row['Opportunity Reference']) else None
                product_name = str(row['Opportunity Product Name']) if pd.notnull(row['Opportunity Product Name']) else None
                opportunity_name = str(row['Opportunity Name']) if pd.notnull(row['Opportunity Name']) else None
                product_family = str(row['Product Family']) if pd.notnull(row['Product Family']) else None
                sales_stage = str(row['Sales Stage']) if pd.notnull(row['Sales Stage']) else None
                opportunity_owner_country = str(row['Opportunity Owner Country']) if pd.notnull(row['Opportunity Owner Country']) else None
                origin_or_executing_country = str(row['Origin OR Executing Country']) if pd.notnull(row['Origin OR Executing Country']) else None
                executing_city_state = str(row['Executing City/State']) if pd.notnull(row['Executing City/State']) else None
                opportunity_type = str(row['Opportunity Type']) if pd.notnull(row['Opportunity Type']) else None
                product_quantity = float(row['Product Quantity']) if pd.notnull(row['Product Quantity']) else None
                annualized_gross_profit = float(row['Annualized Gross Profit']) if pd.notnull(row['Annualized Gross Profit']) else None
                total_product_gross_profit = float(row['Total Product Gross Profit']) if pd.notnull(row['Total Product Gross Profit']) else None
                total_opportunity_gross_profit_lost = float(row['Total Opportunity Gross Profit (Lost)']) if pd.notnull(row['Total Opportunity Gross Profit (Lost)']) else None
                total_opportunity_revenue = float(row['Total Opportunity Revenue']) if pd.notnull(row['Total Opportunity Revenue']) else None
                annualized_product_revenue = float(row['Annualized Product Revenue']) if pd.notnull(row['Annualized Product Revenue']) else None
                total_product_revenue = float(row['Total Product Revenue']) if pd.notnull(row['Total Product Revenue']) else None
                created_date = datetime.now(timezone.utc)

                # Insert into OpportunityDetails table
                details_record = OpportunityDetails(
                    opportunity_reference=opportunity_ref,
                    opportunity_name=opportunity_name,
                    product_family=product_family,
                    sales_stage=sales_stage,
                    opportunity_owner_country=opportunity_owner_country,
                    origin_or_executing_country=origin_or_executing_country,
                    executing_city_state=executing_city_state,
                    opportunity_type=opportunity_type,
                    product_quantity=product_quantity,
                    annualized_gross_profit=annualized_gross_profit,
                    total_product_gross_profit=total_product_gross_profit,
                    total_opportunity_gross_profit_lost=total_opportunity_gross_profit_lost,
                    total_opportunity_revenue=total_opportunity_revenue,
                    annualized_product_revenue=annualized_product_revenue,
                    total_product_revenue=total_product_revenue,
                    created_date=created_date
                )
                session.add(details_record)
                session.flush()
                successful_inserts += 1
                app_logger.info(f"Prepared row {idx + 1}: Reference {opportunity_ref}")

                # # Generate embedding
                # embedding = embedding_model.embed_query(product_name)
                #
                # # Insert into OpportunityProductEmbedding table
                # embedding_record = OpportunityProductEmbedding(
                #     details_id=details_record.id,
                #     opportunity_product_name=product_name,
                #     embedding=embedding,
                #     created_date = created_date
                # )
                # session.add(embedding_record)

                # app_logger.info(f"Inserted row {idx + 1}: Reference {opportunity_ref}")

            except Exception as row_e:
                failed_inserts += 1
                app_logger.error(f"Error preparing row {idx + 1}: {row_e}")

            session.commit()
            app_logger.info(f"Successfully inserted {successful_inserts} rows. Failed: {failed_inserts}")

    except SQLAlchemyError as db_e:
        app_logger.error(f"Database error: {db_e}")
        session.rollback()
    except Exception as e:
        app_logger.error(f"General error: {e}")
        session.rollback()
    finally:
        session.close()
        app_logger.info("Database session closed.")


if __name__ == "__main__":
    insert_opportunity_data()
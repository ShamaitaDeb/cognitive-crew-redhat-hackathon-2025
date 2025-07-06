from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, Float, DateTime
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship

Base = declarative_base()


class OpportunityDetails(Base):
    __tablename__ = 'opportunity_details'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    opportunity_reference = Column(String)
    opportunity_name = Column(String)
    product_family = Column(String)
    sales_stage = Column(String)
    opportunity_owner_country = Column(String)
    origin_or_executing_country = Column(String)
    executing_city_state = Column(String)
    opportunity_type = Column(String)
    product_quantity = Column(Float)
    annualized_gross_profit = Column(Float)
    total_product_gross_profit = Column(Float)
    total_opportunity_gross_profit_lost = Column(Float)
    total_opportunity_revenue = Column(Float)
    annualized_product_revenue = Column(Float)
    total_product_revenue = Column(Float)
    created_date = Column(DateTime, default=datetime.utcnow)

    embeddings = relationship("OpportunityProductEmbedding", back_populates="details", cascade="all, delete")


class OpportunityProductEmbedding(Base):
    __tablename__ = 'opportunity_product_embeddings'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    details_id = Column(Integer, ForeignKey('public.opportunity_details.id', ondelete="CASCADE"))
    opportunity_product_name = Column(String)
    embedding = Column(Vector(1536))
    created_date = Column(DateTime, default=datetime.utcnow)

    details = relationship("OpportunityDetails", back_populates="embeddings")
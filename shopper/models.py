from sqlalchemy import Column, Integer, String, Table, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .db import Base


trip_products = Table(
    "trip_products",
    Base.metadata,
    Column("trip_id", ForeignKey("trips.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True),
)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, index=True, nullable=False)

    trips = relationship("Trip", secondary=trip_products, back_populates="products")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", secondary=trip_products, back_populates="trips")

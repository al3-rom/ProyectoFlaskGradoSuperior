from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey, Numeric, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import db
from flask_login import UserMixin


# SQLAlchemy schemas

class Product(db.Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(5000), nullable=False)
    photo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    category: Mapped["Category"] = relationship(back_populates="products")
    seller: Mapped["User"] = relationship(back_populates="products")
    offers: Mapped[list["Offer"]] = relationship("Offer", back_populates="product", cascade="all, delete-orphan")

    blocked: Mapped["BlockedProduct"] = relationship(
        "BlockedProduct",
        uselist=False,
        back_populates="product",
        cascade="all, delete-orphan"
    )


class User(db.Model, UserMixin):
    
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=False) 
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=False)
    email_token: Mapped[str] = mapped_column(String(64),  unique=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=0, nullable=False)

    offers_made: Mapped[list["Offer"]] = relationship("Offer", back_populates="buyer", cascade="all, delete-orphan")
    role: Mapped["Role"] = relationship("Role", back_populates="users") 
    products: Mapped[list["Product"]] = relationship("Product", back_populates="seller")

    blocked_as_user: Mapped[list["blocked_users"]] = relationship("blocked_users", foreign_keys="blocked_users.user_id",back_populates="user", cascade="all, delete-orphan")
    blocked_as_moderator: Mapped[list["blocked_users"]] = relationship("blocked_users", foreign_keys="blocked_users.moderator_id",back_populates="moderator", cascade="all, delete-orphan")


class Role(db.Model):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="role")


class Category(db.Model):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")


# Blocked Products / Users

class blocked_users(db.Model):
    __tablename__ = "blocked_users"

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    moderator_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    created: Mapped[int] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    user: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[user_id],
        back_populates="blocked_as_user"
    )

    moderator: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[moderator_id],
        back_populates="blocked_as_moderator"
    )


class BlockedProduct(db.Model):
    __tablename__ = 'blocked_products'

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True, unique=True)
    moderator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    product: Mapped["Product"] = relationship("Product", back_populates="blocked")
    moderator: Mapped["User"] = relationship("User")


# Compra / Venda

class AcceptedOffer(db.Model):
    __tablename__ = 'accepted_offers'

    offer_id: Mapped[int] = mapped_column(ForeignKey("offers.id"), primary_key=True)
    instructions: Mapped[str] = mapped_column(String(255), nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    offer: Mapped["Offer"] = relationship("Offer", back_populates="accepted_offer")


class Offer(db.Model):
    __tablename__ = 'offers'
    __table_args__ = (
        UniqueConstraint("product_id", "buyer_id", name="uc_product_buyer"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    offer: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    product: Mapped["Product"] = relationship("Product", back_populates="offers")
    buyer: Mapped["User"] = relationship("User", back_populates="offers_made")
    accepted_offer: Mapped["AcceptedOffer"] = relationship(
        "AcceptedOffer",
        uselist=False,
        back_populates="offer",
        cascade="all, delete-orphan"
    )
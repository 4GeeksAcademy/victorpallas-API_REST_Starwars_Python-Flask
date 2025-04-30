import enum
from typing import List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class Favorites_Types(enum.Enum):
    planet = 1
    people = 2
    vehicle = 3
    film = 4


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(60), unique=False, nullable=False)
    firstname: Mapped[str] = mapped_column(
        String(60), unique=False, nullable=False)
    lastname: Mapped[str] = mapped_column(
        String(60), unique=False, nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    favorites: Mapped[list["Favorites"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
        }


class People(db.Model):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_from_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    favorites: Mapped[List["Favorites"]] = relationship(
        "Favorites", back_populates="people")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "favoritecount": len(self.favorites)

        }


class Planet(db.Model):
    __tablename__ = "planet"

    id: Mapped[int] = mapped_column(primary_key=True)
    #user_from_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    favorites: Mapped[List["Favorites"]] = relationship(
        "Favorites", back_populates="planet")

    def serialize(self):
        return {
            "id": self.id,
            #"username": self.username,
            "name": self.name,
            "favoritecount": len(self.favorites)

        }


class Favorites(db.Model):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[Favorites_Types] = mapped_column(Enum(Favorites_Types))

    planet_id: Mapped[int] = mapped_column(
        ForeignKey("planet.id"), nullable=True)
    people_id: Mapped[int] = mapped_column(
        ForeignKey("people.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)

    planet: Mapped["Planet"] = relationship(
        "Planet", back_populates="favorites")
    people: Mapped["People"] = relationship(
        "People", back_populates="favorites")
    user: Mapped[User] = relationship(back_populates="favorites")

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type.name,
            "user_id": self.user.id,
            "people_id": self.people.id,
            "planet_id": self.planet.id
        }

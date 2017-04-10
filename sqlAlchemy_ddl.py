import os
import sys
import logging

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    street_name = Column(String(250))
    street_number = Column(String(250))
    post_code = Column(String(250), nullable=False)
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship(Person)


logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

engine = create_engine('oracle+cx_oracle://hr:hr@den01zma:1522/xe', echo=False)

session = sessionmaker()
session.configure(bind=engine)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

s = session()

p1 = Person(id=1, name="Sarath 1")
p2 = Person(id=2, name="Sarath 2")

a1 = Address(id=1, street_name="Usman Saheb Pet", street_number="S H Pet", post_code="524002", person_id=1)
a2 = Address(id=2, street_name="Vittal Rao Nagar", street_number="Madhapur", post_code="500081", person_id=2)

s.add(p1)
s.add(p2)
s.add(a1)
s.add(a2)

s.commit()



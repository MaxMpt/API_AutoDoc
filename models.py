# from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship
#
# Base = declarative_base()
#
# class Car(Base):
#     __tablename__ = "cars"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)
#     is_active = Column(Boolean, default=True)
#     work_assignments = relationship("WorkAssignment", back_populates="car")
#
# class Color(Base):
#     __tablename__ = "colors"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)
#     is_active = Column(Boolean, default=True)
#     work_assignments = relationship("WorkAssignment", back_populates="color")
#
# class Person(Base):
#     __tablename__ = "persons"
#     id = Column(Integer, primary_key=True, index=True)
#     full_name = Column(String, index=True)
#     login = Column(String, unique=True, index=True)
#     password = Column(String)
#     age = Column(Integer)
#     role_id = Column(Integer, ForeignKey("roles.id"))
#     is_active = Column(Boolean, default=True)
#
#     role = relationship("Role", back_populates="persons")
#     work_assignments = relationship("WorkAssignment", back_populates="person")
#     work_assignment_works = relationship("WorkAssignmentWork", back_populates="executor")  # Новый релейшн
#
# class Role(Base):
#     __tablename__ = "roles"
#     id = Column(Integer, primary_key=True, index=True)
#     ident = Column(String, index=True)
#     name = Column(String, index=True)
#     is_active = Column(Boolean, default=True)
#     persons = relationship("Person", back_populates="role")
#
# class Work(Base):
#     __tablename__ = "works"
#     id = Column(Integer, primary_key=True, index=True)
#     ident = Column(String, index=True)
#     name = Column(String, index=True)
#     description = Column(String)
#     is_active = Column(Boolean, default=True)
#     work_assignment_works = relationship("WorkAssignmentWork", back_populates="work")
#
# class WorkAssignment(Base):
#     __tablename__ = "work_assignments"
#     id = Column(Integer, primary_key=True, index=True)
#     date = Column(DateTime)
#     vin = Column(String, nullable=True)
#     car_number = Column(String, nullable=True)
#     color_id = Column(Integer, ForeignKey("colors.id"))
#     person_id = Column(Integer, ForeignKey("persons.id"))
#     car_id = Column(Integer, ForeignKey("cars.id"))
#     is_active = Column(Boolean, default=True)
#     description = Column(String, nullable=True)
#
#     color = relationship("Color", back_populates="work_assignments")
#     person = relationship("Person", back_populates="work_assignments")
#     car = relationship("Car", back_populates="work_assignments")
#     work_assignment_works = relationship("WorkAssignmentWork", back_populates="work_assignment")
#
# class WorkAssignmentWork(Base):
#     __tablename__ = "work_assignment_works"
#     id = Column(Integer, primary_key=True, index=True)
#     work_assignment_id = Column(Integer, ForeignKey("work_assignments.id"))
#     work_id = Column(Integer, ForeignKey("works.id"))
#     executor_id = Column(Integer, ForeignKey("persons.id"))  # Новый внешний ключ на исполнителя
#     status = Column(Boolean, default=False)
#
#     work_assignment = relationship("WorkAssignment", back_populates="work_assignment_works")
#     work = relationship("Work", back_populates="work_assignment_works")
#     executor = relationship("Person", back_populates="work_assignment_works")  # Новый релейшн

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)  # Добавлена длина 255
    is_active = Column(Boolean, default=True)
    work_assignments = relationship("WorkAssignment", back_populates="car")

class Color(Base):
    __tablename__ = "colors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)  # Добавлена длина 255
    is_active = Column(Boolean, default=True)
    work_assignments = relationship("WorkAssignment", back_populates="color")

class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), index=True)  # Добавлена длина 255
    login = Column(String(255), unique=True, index=True)  # Добавлена длина 255
    password = Column(String(255))  # Добавлена длина 255
    age = Column(Integer)
    role_id = Column(Integer, ForeignKey("roles.id"))
    is_active = Column(Boolean, default=True)

    role = relationship("Role", back_populates="persons")
    work_assignments = relationship("WorkAssignment", back_populates="person")
    work_assignment_works = relationship("WorkAssignmentWork", back_populates="executor")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    ident = Column(String(255), index=True)  # Добавлена длина 255
    name = Column(String(255), index=True)  # Добавлена длина 255
    is_active = Column(Boolean, default=True)
    persons = relationship("Person", back_populates="role")

class Work(Base):
    __tablename__ = "works"
    id = Column(Integer, primary_key=True, index=True)
    ident = Column(String(255), index=True)  # Добавлена длина 255
    name = Column(String(255), index=True)  # Добавлена длина 255
    description = Column(String(2000))  # Добавлена длина 2000 для длинных описаний
    is_active = Column(Boolean, default=True)
    work_assignment_works = relationship("WorkAssignmentWork", back_populates="work")

class WorkAssignment(Base):
    __tablename__ = "work_assignments"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    vin = Column(String(255), nullable=True)  # Добавлена длина 255
    car_number = Column(String(255), nullable=True)  # Добавлена длина 255
    color_id = Column(Integer, ForeignKey("colors.id"))
    person_id = Column(Integer, ForeignKey("persons.id"))
    car_id = Column(Integer, ForeignKey("cars.id"))
    is_active = Column(Boolean, default=True)
    description = Column(String(2000), nullable=True)  # Добавлена длина 2000

    color = relationship("Color", back_populates="work_assignments")
    person = relationship("Person", back_populates="work_assignments")
    car = relationship("Car", back_populates="work_assignments")
    work_assignment_works = relationship("WorkAssignmentWork", back_populates="work_assignment")

class WorkAssignmentWork(Base):
    __tablename__ = "work_assignment_works"
    id = Column(Integer, primary_key=True, index=True)
    work_assignment_id = Column(Integer, ForeignKey("work_assignments.id"))
    work_id = Column(Integer, ForeignKey("works.id"))
    executor_id = Column(Integer, ForeignKey("persons.id"))
    status = Column(Boolean, default=False)

    work_assignment = relationship("WorkAssignment", back_populates="work_assignment_works")
    work = relationship("Work", back_populates="work_assignment_works")
    executor = relationship("Person", back_populates="work_assignment_works")
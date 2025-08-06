from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Role, Person, Work, WorkAssignment, WorkAssignmentWork, Car, Color
from datetime import datetime, date
import os
from main import engine  # Используем тот же engine, что и в main.py

SessionLocal = sessionmaker(autoflush=False, bind=engine)


def populate_data():
    # Проверяем, нужно ли заполнять данные
    db = SessionLocal()
    try:
        # Если уже есть данные - пропускаем заполнение
        if db.query(Car).count() > 0:
            print("Данные уже существуют, пропускаем заполнение.")
            return

        print("Начало заполнения данных...")

        # [Остальной код заполнения данных без изменений]
        cars = [
            Car(name="Toyota Corolla", is_active=True),
            Car(name="Honda Civic", is_active=True),
            Car(name="Ford Mustang", is_active=True),
            Car(name="BMW 3 Series", is_active=True),
            Car(name="Volkswagen Golf", is_active=True),
        ]
        db.add_all(cars)

        # Добавление цветов
        colors = [
            Color(name="Красный", is_active=True),
            Color(name="Синий", is_active=True),
            Color(name="Черный", is_active=True),
            Color(name="Белый", is_active=True),
            Color(name="Серебристый", is_active=True),
        ]
        db.add_all(colors)

        # Добавление ролей
        roles = [
            Role(ident="admin", name="Администратор", is_active=True),
            Role(ident="mechanic", name="Механик", is_active=True),
            Role(ident="inspector", name="Инспектор", is_active=True),
            Role(ident="manager", name="Менеджер", is_active=True),
            Role(ident="assistant", name="Ассистент", is_active=True),
        ]
        db.add_all(roles)

        db.flush()  # Чтобы получить ID для ролей

        # Добавление сотрудников
        persons = [
            Person(full_name="Иванов Иван Иванович", login="ivanov", password="pass123", is_active=True, age=30,
                   role_id=roles[1].id),
            Person(full_name="Петров Петр Петрович", login="petrov", password="pass456", is_active=True, age=35,
                   role_id=roles[1].id),
            Person(full_name="Сидоров Сергей Сергеевич", login="sidorov", password="pass789", is_active=True, age=40,
                   role_id=roles[2].id),
            Person(full_name="Козлова Анна Ивановна", login="kozlova", password="pass101", is_active=True, age=28,
                   role_id=roles[3].id),
            Person(full_name="Смирнов Алексей Викторович", login="smirnov", password="pass202", is_active=True, age=45,
                   role_id=roles[0].id),
        ]
        db.add_all(persons)

        # Добавление видов работ
        works = [
            Work(ident="oil_change", name="Замена масла", description="Замена моторного масла и фильтра",
                 is_active=True),
            Work(ident="tire_repair", name="Ремонт шин", description="Ремонт проколов и замена шин", is_active=True),
            Work(ident="brake_check", name="Проверка тормозов", description="Диагностика и ремонт тормозной системы",
                 is_active=True),
            Work(ident="engine_diag", name="Диагностика двигателя", description="Проверка и диагностика двигателя",
                 is_active=True),
            Work(ident="paint_job", name="Покраска кузова", description="Покраска кузова автомобиля", is_active=True),
        ]
        db.add_all(works)

        db.flush()  # Получим ID для cars, colors, persons, works

        # Добавление назначений работ
        work_assignments = [
            WorkAssignment(date=date.today(), color_id=colors[0].id, person_id=persons[0].id, car_id=cars[0].id,
                           is_active=True),
            WorkAssignment(date=date.today(), color_id=colors[1].id, person_id=persons[1].id, car_id=cars[1].id,
                           is_active=True),
        ]
        db.add_all(work_assignments)
        db.flush()

        # Добавление работ к назначению
        work_assignment_works = [
            WorkAssignmentWork(work_assignment_id=1, work_id=1, executor_id=1),
            WorkAssignmentWork(work_assignment_id=1, work_id=2, executor_id=2),
            WorkAssignmentWork(work_assignment_id=2, work_id=3, executor_id=1),
        ]
        db.add_all(work_assignment_works)

        # Сохраняем изменения
        db.commit()
        print("Данные успешно добавлены.")

    except Exception as e:
        db.rollback()
        print(f"Ошибка при заполнении данных: {e}")
        raise
    finally:
        db.close()




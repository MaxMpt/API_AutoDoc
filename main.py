import os
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import sessionmaker, selectinload, Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from starlette.responses import JSONResponse, Response
from fastapi.middleware.gzip import GZipMiddleware
import logging

from models import (
    Person as PersonModel,
    Role as RoleModel,
    Car as CarModel,
    Color as ColorModel,
    Work as WorkModel,
    WorkAssignment as WorkAssignmentModel,
    WorkAssignmentWork as WorkAssignmentWorkModel
)

# Configuration
PORT = int(os.environ.get("PORT", 8080))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "mysql+pymysql://root:CMCeBedBRBZzzAigbffERCHPFaibFUoo@switchyard.proxy.rlwy.net:55649/railway"
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create tables (for development)
def create_tables():
    from models import Base
    Base.metadata.create_all(bind=engine)


# FastAPI app
app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Startup event
@app.on_event("startup")
def startup():
    create_tables()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic Models
class PersonBase(BaseModel):
    full_name: str
    login: str
    password: str
    age: int
    role_id: int
    is_active: bool = True


class PersonCreate(PersonBase):
    pass


class Person(PersonBase):
    id: int

    class Config:
        from_attributes = True


class Role(BaseModel):
    id: int
    ident: str
    name: str
    is_active: bool = True

    class Config:
        from_attributes = True


class Car(BaseModel):
    id: int
    name: str
    is_active: bool = True

    class Config:
        from_attributes = True


class Color(BaseModel):
    id: int
    name: str
    is_active: bool = True

    class Config:
        from_attributes = True


class Work(BaseModel):
    id: int
    ident: str
    name: str
    description: str
    is_active: bool = True

    class Config:
        from_attributes = True


class WorkAssignmentBase(BaseModel):
    date: datetime
    vin: Optional[str] = None
    car_number: Optional[str] = None
    color_id: int
    person_id: int
    car_id: Optional[int] = None
    is_active: bool = True
    description: Optional[str] = None

class WorkAssignmentCreate(WorkAssignmentBase):
    works: List[dict] = []  # Явно указываем пустой список по умолчанию

class WorkAssignment(WorkAssignmentBase):
    id: int
    color: Color
    person: Person
    car: Optional[Car] = None
    work_assignment_works: List['WorkAssignmentWork'] = []

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WorkAssignmentWorkBase(BaseModel):
    work_id: int
    executor_id: int
    status: bool = False


class WorkAssignmentWorkCreate(WorkAssignmentWorkBase):
    pass


class WorkAssignmentWork(WorkAssignmentWorkBase):
    id: int
    work_assignment_id: int
    work: Work
    executor: Person

    class Config:
        from_attributes = True


WorkAssignment.model_rebuild()


# Endpoints
@app.get("/persons", response_model=List[Person])
def get_all_persons(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100
):
    result = db.execute(select(PersonModel).offset(skip).limit(limit))
    return result.scalars().all()

@app.get("/persons-status", response_model=List[Person])
def get_persons_status_work(db: Session = Depends(get_db)):
    query = db.execute(select(PersonModel).where(PersonModel.is_active == True)).scalars().all()
    return query


@app.post("/persons", response_model=Person, status_code=status.HTTP_201_CREATED)
def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    db_role = db.get(RoleModel, person.role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    db_person = PersonModel(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


@app.get("/cars", response_model=List[Car])
def get_all_cars(db: Session = Depends(get_db)):
    result = db.execute(select(CarModel))
    return result.scalars().all()


@app.post("/cars", response_model=Car, status_code=status.HTTP_201_CREATED)
def create_car(car: Car, db: Session = Depends(get_db)):
    db_car = CarModel(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


@app.get("/colors", response_model=List[Color])
def get_all_colors(db: Session = Depends(get_db)):
    result = db.execute(select(ColorModel))
    return result.scalars().all()


@app.post("/colors", response_model=Color, status_code=status.HTTP_201_CREATED)
def create_color(color: Color, db: Session = Depends(get_db)):
    db_color = ColorModel(**color.dict())
    db.add(db_color)
    db.commit()
    db.refresh(db_color)
    return db_color


@app.get("/works", response_model=List[Work])
def get_all_works(db: Session = Depends(get_db)):
    result = db.execute(select(WorkModel))
    return result.scalars().all()


@app.post("/works", response_model=Work, status_code=status.HTTP_201_CREATED)
def create_work(work: Work, db: Session = Depends(get_db)):
    db_work = WorkModel(**work.dict())
    db.add(db_work)
    db.commit()
    db.refresh(db_work)
    return db_work


class WorkAssignmentCreateResponse(BaseModel):
    id: int
    date: str
    vin: Optional[str] = None
    car_number: Optional[str] = None
    color_id: int
    person_id: int
    car_id: Optional[int] = None
    works: List[dict]
    success: bool

    class Config:
        from_attributes = True


@app.post("/work-assignments", response_model=WorkAssignmentCreateResponse)
def create_work_assignment(assignment: WorkAssignmentCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Creating new assignment with data: {assignment.dict()}")

        if isinstance(assignment.date, str):
            assignment.date = datetime.fromisoformat(assignment.date)

        db_assignment = WorkAssignmentModel(
            date=assignment.date,
            vin=assignment.vin,
            car_number=assignment.car_number,
            car_id=assignment.car_id,
            color_id=assignment.color_id,
            person_id=assignment.person_id,
            description=assignment.description,
            is_active=True
        )
        db.add(db_assignment)
        db.flush()

        works_list = []
        for work in assignment.works:
            db_work = WorkAssignmentWorkModel(
                work_assignment_id=db_assignment.id,
                work_id=work['work_id'],
                executor_id=work['executor_id'],
                status=False
            )
            db.add(db_work)
            works_list.append({
                'work_id': work['work_id'],
                'executor_id': work['executor_id'],
                'status': False
            })

        db.commit()

        response_data = {
            "id": db_assignment.id,
            "date": db_assignment.date.isoformat(),
            "vin": db_assignment.vin,
            "car_number": db_assignment.car_number,
            "color_id": db_assignment.color_id,
            "person_id": db_assignment.person_id,
            "car_id": db_assignment.car_id,
            "works": works_list,
            "success": True
        }

        logger.info(f"Assignment created successfully: {response_data}")
        return response_data

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating assignment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/work-assignments", response_model=List[WorkAssignment])
def get_all_work_assignments(
        year: Optional[int] = Query(None),
        month: Optional[int] = Query(None),
        day: Optional[int] = Query(None),
        db: Session = Depends(get_db)
):
    query = select(WorkAssignmentModel).options(
        selectinload(WorkAssignmentModel.color),
        selectinload(WorkAssignmentModel.person),
        selectinload(WorkAssignmentModel.car),
        selectinload(WorkAssignmentModel.work_assignment_works).selectinload(WorkAssignmentWorkModel.work),
        selectinload(WorkAssignmentModel.work_assignment_works).selectinload(WorkAssignmentWorkModel.executor)
    )

    if year and month and day:
        start = datetime(year, month, day)
        end = start + timedelta(days=1)
        query = query.where(WorkAssignmentModel.date >= start, WorkAssignmentModel.date < end)
    elif year and month:
        start = datetime(year, month, 1)
        end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        query = query.where(WorkAssignmentModel.date >= start, WorkAssignmentModel.date < end)

    result = db.execute(query)
    return result.scalars().all()


@app.get("/get-assignment/{assignment_id}", response_model=WorkAssignment)  # Новый URL
def get_work_assignment(assignment_id: int, db: Session = Depends(get_db)):
    query = select(WorkAssignmentModel).where(WorkAssignmentModel.id == assignment_id).options(
        selectinload(WorkAssignmentModel.color),
        selectinload(WorkAssignmentModel.person),
        selectinload(WorkAssignmentModel.car),
        selectinload(WorkAssignmentModel.work_assignment_works).selectinload(WorkAssignmentWorkModel.work),
        selectinload(WorkAssignmentModel.work_assignment_works).selectinload(WorkAssignmentWorkModel.executor)
    )
    result = db.execute(query)
    db_assignment = result.scalar_one_or_none()
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Work assignment not found")
    return db_assignment

#
# @app.put("/work-assignments/{assignment_id}")
# def update_work_assignment(
#     assignment_id: int,
#     assignment_data: WorkAssignmentCreate,
#     db: Session = Depends(get_db)
# ):
#     try:
#         # Начинаем транзакцию с контекстным менеджером
#         with db.begin():
#             # Получаем запись
#             db_assignment = db.query(WorkAssignmentModel)\
#                            .filter(WorkAssignmentModel.id == assignment_id)\
#                            .first()
#
#             if not db_assignment:
#                 raise HTTPException(status_code=404, detail="Work assignment not found")
#
#             # Обновляем основные поля
#             update_data = assignment_data.dict(exclude={'works'}, exclude_unset=True)
#             for field, value in update_data.items():
#                 setattr(db_assignment, field, value)
#
#             # Обрабатываем работы
#             if assignment_data.works:  # Проверяем список works напрямую
#                 # Удаляем все текущие работы
#                 db.query(WorkAssignmentWorkModel)\
#                   .filter(WorkAssignmentWorkModel.work_assignment_id == assignment_id)\
#                   .delete(synchronize_session=False)
#
#                 # Добавляем новые работы
#                 for work in assignment_data.works:
#                     new_work = WorkAssignmentWorkModel(
#                         work_assignment_id=assignment_id,
#                         work_id=work['work_id'],
#                         executor_id=work['executor_id'],
#                         status=work.get('status', False)
#                     )
#                     db.add(new_work)
#
#         return JSONResponse(
#             status_code=200,
#             content={"success": True, "message": "Work assignment updated successfully"}
#         )
#
#     except HTTPException:
#         db.rollback()
#         raise
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error updating assignment {assignment_id}: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail=f"Internal server error: {str(e)}"
#         )
@app.put("/work-assignments/{assignment_id}", response_model=WorkAssignmentCreateResponse)
def update_work_assignment(
        assignment_id: int,
        assignment: WorkAssignmentCreate,
        db: Session = Depends(get_db)
):
    try:
        logger.info(f"Updating assignment {assignment_id} with data: {assignment.dict()}")

        # Получаем существующее задание
        db_assignment = db.query(WorkAssignmentModel).filter(
            WorkAssignmentModel.id == assignment_id
        ).first()

        if not db_assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")

        # Обновляем основные данные
        if isinstance(assignment.date, str):
            assignment.date = datetime.fromisoformat(assignment.date)

        db_assignment.date = assignment.date
        db_assignment.vin = assignment.vin
        db_assignment.car_number = assignment.car_number
        db_assignment.car_id = assignment.car_id
        db_assignment.color_id = assignment.color_id
        db_assignment.person_id = assignment.person_id
        db_assignment.description = assignment.description

        # Удаляем все существующие работы для этого задания
        db.query(WorkAssignmentWorkModel).filter(
            WorkAssignmentWorkModel.work_assignment_id == assignment_id
        ).delete()

        # Добавляем обновленные работы с сохранением их статусов
        works_list = []
        for work in assignment.works:
            db_work = WorkAssignmentWorkModel(
                work_assignment_id=db_assignment.id,
                work_id=work['work_id'],
                executor_id=work['executor_id'],
                status=work.get('status', False)  # Сохраняем статус из входных данных
            )
            db.add(db_work)
            works_list.append({
                'work_id': work['work_id'],
                'executor_id': work['executor_id'],
                'status': work.get('status', False)
            })

        db.commit()

        response_data = {
            "id": db_assignment.id,
            "date": db_assignment.date.isoformat(),
            "vin": db_assignment.vin,
            "car_number": db_assignment.car_number,
            "color_id": db_assignment.color_id,
            "person_id": db_assignment.person_id,
            "car_id": db_assignment.car_id,
            "works": works_list,
            "success": True
        }

        logger.info(f"Assignment updated successfully: {response_data}")
        return response_data

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating assignment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))





@app.get("/work-assignment-works", response_model=List[WorkAssignmentWork])
def get_work_assignment_works(
        work_assignment_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    query = select(WorkAssignmentWorkModel).options(
        selectinload(WorkAssignmentWorkModel.work),
        selectinload(WorkAssignmentWorkModel.executor)
    )
    if work_assignment_id is not None:
        query = query.where(WorkAssignmentWorkModel.work_assignment_id == work_assignment_id)
    result = db.execute(query)
    return result.scalars().all()


@app.post("/work-assignment-works", response_model=WorkAssignmentWork, status_code=status.HTTP_201_CREATED)
def create_work_assignment_work(work: WorkAssignmentWorkCreate, db: Session = Depends(get_db)):
    db_assignment = db.get(WorkAssignmentModel, work.work_assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Work assignment not found")

    db_work = db.get(WorkModel, work.work_id)
    if not db_work:
        raise HTTPException(status_code=404, detail="Work not found")

    db_executor = db.get(PersonModel, work.executor_id)
    if not db_executor:
        raise HTTPException(status_code=404, detail="Executor not found")

    db_work_assignment_work = WorkAssignmentWorkModel(**work.dict())
    db.add(db_work_assignment_work)
    db.commit()
    db.refresh(db_work_assignment_work)
    return db_work_assignment_work


@app.post("/work-assignment-works/update-status/")
def update_work_status(data: dict, db: Session = Depends(get_db)):
    try:
        assignment_id = data["assignment_id"]
        updates = data["updates"]

        for update in updates:
            result = db.execute(
                select(WorkAssignmentWorkModel)
                .where(
                    WorkAssignmentWorkModel.work_assignment_id == assignment_id,
                    WorkAssignmentWorkModel.work_id == update["work_id"]
                )
            )
            waw = result.scalar_one_or_none()
            if waw:
                waw.status = update["status"]
                db.add(waw)

        db.commit()

        return {"success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/work-assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work_assignment(
        assignment_id: int,
        db: Session = Depends(get_db)
):
    try:
        # Сначала удаляем связанные работы
        db.execute(
            delete(WorkAssignmentWorkModel)
            .where(WorkAssignmentWorkModel.work_assignment_id == assignment_id)
        )

        # Затем удаляем саму карточку
        result = db.execute(
            delete(WorkAssignmentModel)
            .where(WorkAssignmentModel.id == assignment_id)
        )

        # Проверяем, была ли удалена хотя бы одна запись
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Work assignment not found")

        db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting work assignment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)

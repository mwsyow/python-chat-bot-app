# import datetime as dt
# from typing import List
# from uuid import UUID, uuid4
# from sqlalchemy.orm import (
#     DeclarativeBase, Mapped, mapped_column, relationship, Session
# )
# from sqlalchemy import (
#     create_engine, select
# )
# from .models import (
#     Base, PersonalInformation, User, Client
# )
# import os

# import tempfile

# from flask import Flask




import tempfile
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# Sample table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Use a temporary directory
with tempfile.TemporaryDirectory() as temp_dir:
    db_path = os.path.join(temp_dir, "test_database.sqlite")
    print(f"Using temp DB at: {db_path}")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Create the database engine
    engine = create_engine(f"sqlite:///{db_path}")

    # Create tables
    Base.metadata.create_all(engine)  # ✅ FIXED

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Insert sample data
    session.add(User(name="Alice"))
    session.commit()

    # Query data
    users = session.query(User).all()
    print([user.name for user in users])  # Output: ['Alice']





# if __name__ == '__main__':
#     f, p = tempfile.mkstemp()
#     eng = create_engine(f'sqlite:///{p}/db.sqlite')
#     Base.metadata.create_all(eng)
#     print(f, p)
#     os.close(f)
#     os.unlink(p)
    # uid2 = uuid4()
    # uid = uuid4()
  
    # engine = create_engine("sqlite://", echo=True)
    # Base.metadata.create_all(engine)
    
    # pi1 = PersonalInformation()
    # pi2 = PersonalInformation()
    # u1 = User(
    #     id=uid, username='mws', password='mws', personal_info=pi1
    # )
    # u2 = User(
    #     id=uid2, username='yow', password='yow', personal_info=pi2
    # )
    # s1 = Session(engine)
    # s2 = Session(engine)
    
    # s1.add_all([u1, u2])
    # s1.commit()
    # print(s1.scalars(select(User).filter_by(username='mws', password='mws')).one())
    # with Session(engine) as session:
    #     pi1 = PersonalInformation()
    #     pi2 = PersonalInformation()
    #     u1 = User(
    #         id=uid, username='mws', password='mws', personal_info=pi1
    #     )
    #     u2 = User(
    #         id=uid2, username='yow', password='yow', personal_info=pi2
    #     )
    #     session.add(u1)
    #     session.flush()
    #     session.commit()
    #     stmt = select(User).where(User.username == 'mws')
    #     mws = session.scalars(stmt).one()
    #     session.delete(mws)
    #     session.flush()
    #     session.rollback()
    #     print(session.execute(select(User)).all())
        # session.add(u2)
        # session.commit()
        # stmt = select(PersonalInformation)
        # res = session.execute(stmt).first()

        # print('res:', res)
        # print('res1:', session.get(PersonalInformation, 2) == res[0])
        
        # stmt = select(PersonalInformation).where(PersonalInformation.id.__eq__(1))
        
        # stmt = select(('id: '+ User.username).label('user_id'))
        # res = session.execute(stmt).all()
        # [print(r.user_id) for r in res]
    # new_session = Session(engine)
    # u = new_session.get(User, uid2)
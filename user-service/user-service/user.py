import datetime as dt
from uuid import UUID, uuid4
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, Session
)
from sqlalchemy import (
    String, DateTime, Uuid, Integer, ForeignKey, create_engine, select
)


class Base(DeclarativeBase):
    type_annotation_map = {
        str: String,
        dt.datetime: DateTime(timezone=True),
        UUID: Uuid,
        int: Integer
    }

class User(Base):
    __tablename__ = "user_account"
    
    id: Mapped[UUID] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]
    created_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.now())
    personal_info: Mapped['PersonalInformation'] = relationship(
        back_populates= 'user', cascade='all, delete-orphan'
    )
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, username= {self.username})"
    
class PersonalInformation(Base):
    __tablename__ = "personal_information"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('user_account.id'))
    user: Mapped['User'] = relationship(
        back_populates= 'personal_info'
    )
    
    def __repr__(self) -> str:
        return f"PersonalInformation(id={self.id}, name={self.name}, first_name={self.first_name})"

if __name__ == '__main__':
    uid2 = uuid4()
    uid = uuid4()
  
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        pi1 = PersonalInformation()
        pi2 = PersonalInformation()
        u1 = User(
            id=uid, username='mws', password='mws', personal_info=pi1
        )
        u2 = User(
            id=uid2, username='yow', password='yow', personal_info=pi2
        )
        session.add_all([u1, u2])
        
        stmt = select(User).where(User.username.__eq__('mws'))
        mws = session.scalars(stmt).one()
        mws.username = 'mws_updated'
        session.delete(mws)
        # stmt = select(PersonalInformation).where(PersonalInformation.id.__eq__(1))
        
        session.commit()
        
    
    
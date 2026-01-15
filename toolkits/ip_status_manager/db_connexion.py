from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker




engine = create_engine("sqlite:///sqlite.db", echo=True)
session = sessionmaker(bind=engine)
session = session()
Base = declarative_base()


class Connexion_Status(Base):
    __tablename__ = 'connexion_status'
    id = Column(Integer, primary_key=True)
    status = Column(String)
    origin = Column(String, default='protonvpn')
    city = Column(String, default='france')

    @classmethod
    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'origin': self.origin,
            'city': self.city
        }

def status_exists():
    status = session.query(Connexion_Status).first()
    return True if status else False

def create_status(status:dict={'status': 'disconnected', 'origin': 'protonvpn', 'city': 'france'}) -> None:
    status = Connexion_Status(status)
    session.add(status)
    session.commit()
    print("Status created:", status.status)

def create_status_if_not_exists():
    if not status_exists():
        create_status()
    else:
        print("Status already exists.")

def get_status():
    status = session.query(Connexion_Status).first()
    return status.to_dict if status else None

def set_status(new_status):
    status = session.query(Connexion_Status).first()
    if status:
        status.status = new_status.status
        status.origin = new_status.origin
        status.city = new_status.city
        session.commit()
        print("Status updated to:", status.status)
    else:
        print("No status found to update.")

def delete_status():
    status = session.query(Connexion_Status).first()
    if status:
        session.delete(status)
        session.commit()
        print("Status deleted.")
    else:
        print("No status found to delete.")


Base.metadata.create_all(engine)


# if __name__ == "__main__":
#     if not status_exists():
#         create_status()
#     else:
#         print("Status already exists.")
    
#     current_status = get_status()
#     if current_status:
#         print("Current status:", current_status.status)
    
#     set_status("connected")
    
#     current_status = get_status()
#     if current_status:
#         print("Updated status:", current_status.status)
    
#     delete_status()
# servidor/database/models.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from servidor.servidor_config import DATABASE_URL

Base = declarative_base()

class NReinasScore(Base):
    __tablename__ = 'n_reinas_scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    n_value = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False)
    attempts = Column(Integer, nullable=False)
    # player_id = Column(Integer, ForeignKey('players.id')) # Si tuvieras jugadores

    def __repr__(self):
        return f"<NReinasScore(n={self.n_value}, success={self.success}, attempts={self.attempts})>"

class KnightsTourScore(Base):
    __tablename__ = 'knights_tour_scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_position = Column(String, nullable=False) # e.g., "A1" o "(0,0)"
    moves_made = Column(Integer, nullable=False)
    completed = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<KnightsTourScore(start={self.start_position}, moves={self.moves_made}, completed={self.completed})>"

class TorresHanoiScore(Base):
    __tablename__ = 'torres_hanoi_scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    num_disks = Column(Integer, nullable=False)
    moves_made = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False) # Podría ser siempre true si solo guardas al completar

    def __repr__(self):
        return f"<TorresHanoiScore(disks={self.num_disks}, moves={self.moves_made}, success={self.success})>"

# --- Engine y Session Setup ---
# Podrías mover esto a db_manager.py si prefieres
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
   
    print("Creando tablas en la base de datos...")
    create_tables()
    print("Tablas creadas.")
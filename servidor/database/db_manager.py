# servidor/database/db_manager.py
from sqlalchemy.orm import Session
from servidor.database.models import SessionLocal, NReinasScore, KnightsTourScore, TorresHanoiScore

class DatabaseManager:
    def __init__(self):
        self.db: Session = SessionLocal()

    def close(self):
        self.db.close()

    def add_n_reinas_score(self, n_value: int, success: bool, attempts: int):
        score = NReinasScore(n_value=n_value, success=success, attempts=attempts)
        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)
        return score

    def add_knights_tour_score(self, start_position: str, moves_made: int, completed: bool):
        score = KnightsTourScore(start_position=start_position, moves_made=moves_made, completed=completed)
        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)
        return score

    def add_torres_hanoi_score(self, num_disks: int, moves_made: int, success: bool):
        score = TorresHanoiScore(num_disks=num_disks, moves_made=moves_made, success=success)
        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)
        return score

    # Podrías añadir métodos para obtener puntuaciones si fuera necesario
    # def get_n_reinas_scores(self):
    #     return self.db.query(NReinasScore).all()
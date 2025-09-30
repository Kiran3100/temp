class BaseRepository:
    def __init__(self, db):
        self.db = db

class HostelRepository(BaseRepository):
    def create(self, payload):
        obj = Hostel(**payload)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get(self, id):
        return self.db.query(Hostel).filter(Hostel.id == id).first()

    def list(self, limit=50, offset=0):
        return self.db.query(Hostel).offset(offset).limit(limit).all()

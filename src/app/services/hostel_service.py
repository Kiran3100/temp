from app.db.repositories import HostelRepository

class HostelService:
    def __init__(self, db):
        self.repo = HostelRepository(db)

    def create_hostel(self, data):
        return self.repo.create(data)

    def get_hostel(self, id):
        return self.repo.get(id)

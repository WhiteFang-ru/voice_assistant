from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class patients_needs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    need = db.Column(db.String, nullable=False)
    received_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return'<Запрос {} {} {}>'.format(self.need, self.received_at, self.status)




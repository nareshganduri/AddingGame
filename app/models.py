from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    results = db.relationship('Result', backref='user', lazy=True)

    def __repr__(self):
        return '<User #{} "{}">'.format(self.id, self.username)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_mode = db.Column(db.String(40), nullable=False)
    total_time = db.Column(db.Integer, nullable=False)
    final_score = db.Column(db.Float, nullable=False)

    def get_time_string(self):
        minutes = '{}'.format(self.total_time // 60)
        seconds = '{}'.format(self.total_time % 60)
        if len(seconds) == 1:
            seconds = '0' + seconds
        return '{}:{}'.format(minutes, seconds)
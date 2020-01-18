from userManagement.models import Users
from sqlalchemy.exc import IntegrityError


def db_load_example_data(app, db):

    users_list = [
        Users("admin1", "robert", "secret1", "2020-01-15T22:14:03Z", True),
        Users("admin2", "matic", "secret2", "2020-01-15T22:15:13Z", True),
        Users("user", "test user", "user", "2020-01-15T23:01:03Z", False),
    ]

    try:
        with app.app_context():
            for usr in users_list:
                if not Users.query.filter_by(username=usr.username).first():
                    db.session.add(usr)
            db.session.commit()
    except IntegrityError as e:
        app.logger.info("Integrity error: {}".format(e.args[0]))

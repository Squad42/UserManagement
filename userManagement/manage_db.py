from userManagement.models import db


def get_all(model):
    data = model.query.all()
    return data


def add_instance(model, **kwargs):
    instance = model(**kwargs)
    db.session.add(instance)
    commit_changes()


def delete_instance(model, username):
    model.query.filter_by(username=username).delete()
    commit_changes()


def edit_instance(model, username, **kwargs):
    instance = model.query.filter_by(username=username).all()[0]
    for attr, new_value in kwargs.items():
        setattr(instance, attr, new_value)
    commit_changes()


def commit_changes():
    db.session.commit()

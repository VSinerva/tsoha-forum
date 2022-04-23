from db import db
from users import check_csrf
from flask import session
import topics

def get_all(id):
    if session.get("is_admin"):
        sql = "SELECT id, user_id, subject, visible FROM threads WHERE topic_id=:id ORDER BY visible DESC , subject;"
    else:
        sql = "SELECT id, user_id, subject, visible FROM threads WHERE topic_id=:id and (visible=true OR user_id=:user_id) ORDER BY visible DESC, subject;"
    return db.session.execute(sql, {"id":id, "user_id":session.get("user_id")}).fetchall()

def get_thread(id : int):
    sql = "SELECT topic_id, user_id, subject, visible FROM threads WHERE id=:id;"
    result = db.session.execute(sql, {"id":id}).fetchone()
    return result

def exists(id):
    sql = "SELECT id FROM threads WHERE id=:id;"
    result = db.session.execute(sql, {"id":id}).fetchone()
    if result:
        return True
    return False

def visible(id):
    sql = "SELECT visible FROM threads WHERE id=:id;"
    result = db.session.execute(sql, {"id":id}).fetchone()
    if result:
        return result[0]
    return result

def create_thread(topic_id, subject):
    check_csrf()
    if not (topics.visible(topic_id) or session.get("is_admin")):
        return

    if session.get("user_id") and len(subject) > 0 and len(subject) <= 100:
        try:
            sql = "INSERT INTO threads(topic_id, user_id, subject) VALUES (:topic_id, :user_id, :subject) Returning threads.id;"
            new_id = db.session.execute(sql, {"topic_id":topic_id, "user_id":session.get("user_id"), "subject":subject}).fetchone()
            db.session.commit()
            if new_id:
                return new_id[0]
            return
        except:
            pass

def delete_thread(id : int):
    check_csrf()
    thread = get_thread(id)
    if session.get("is_admin") or session.get("user_id") == thread.user_id:
        sql = "UPDATE threads SET visible =false WHERE id=:id;"
        db.session.execute(sql, {"id":id})
        db.session.commit()

def restore_thread(id : int):
    check_csrf()
    thread = get_thread(id)
    if session.get("is_admin") or session.get("user_id") == thread.user_id:
        sql = "UPDATE threads SET visible =true WHERE id=:id;"
        db.session.execute(sql, {"id":id})
        db.session.commit()
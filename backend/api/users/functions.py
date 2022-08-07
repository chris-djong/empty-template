from .models import User

def get_no_reply_user():
    return User.objects.get(username="<addNoReplyUserHere>")


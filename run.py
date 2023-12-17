from flask import Flask, jsonify, request, g
from flask_restful import Api
import json
from auth.checksign import is_valid_sign
from resources.user import UserInit, SetTimeOffset, GetProfile
from resources.diary import NewDiary, RemoveDiary, GetBooks, GetBooksByJoin, GetDiary, EditDiary
from resources.posts import NewPost, RemovePost, GetBooksPosts, GetPostsByBookIds, AddAttachment, GetPost, EditTextPost, GetPostsByBookIdsInDay
from resources.moodes import GetMoodes, SetMood
from resources.settings import SetExtras, SetPublicParameters, SetNotifications
from resources.members import GetMembers, LeaveBook, KickMember
from resources.invites import CreateInvite, GetInvite, DeleteInvite, JoinByInvite
from resources.upload import UploadPhoto

from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": r"*"}})
api = Api(app)

@app.errorhandler(500)
def error_500(e):
    return dict(error=True, code=400, message='[BAD REQUEST] Произошла ошибка'), 400

@app.errorhandler(404)
def error_404(e):
    return dict(error=True, code=400, message='[BAD REQUEST] Этого метода не существует'), 400

@app.before_request
def before_request():
    try:
        r = request.data
        fd_sign = request.form.get('sign')
        if fd_sign == None:
            r = json.loads(r)
            sign_value = is_valid_sign(r['sign'])
        else:
            sign_value = is_valid_sign(fd_sign)
        if not sign_value[0]:
            return jsonify(dict(
                error=True,
                code=403,
                message='Неверная подпись'
            ))

        g.userid = int(sign_value[1])
    except:
        return jsonify(dict(
            error=True,
            code=403,
            message='Неверная подпись'
        ))


api.add_resource(UserInit, '/init')
api.add_resource(GetProfile, '/get_profile')
api.add_resource(SetTimeOffset, '/set_time_offset')

api.add_resource(GetBooks, '/get_books')
api.add_resource(GetBooksByJoin, '/get_books_join')
api.add_resource(NewDiary, '/new_book')
api.add_resource(EditDiary, '/edit_book')
api.add_resource(RemoveDiary, '/remove_book')
api.add_resource(GetDiary, '/get_book')

api.add_resource(NewPost, '/new_post')
api.add_resource(GetPost, '/get_post')
api.add_resource(AddAttachment, '/add_attachments')
api.add_resource(RemovePost, '/remove_post')
api.add_resource(EditTextPost, '/edit_text_post')
api.add_resource(GetBooksPosts, '/get_books_posts')
api.add_resource(GetPostsByBookIds, '/get_posts_by_bookids')
api.add_resource(GetPostsByBookIdsInDay, '/get_posts_by_bookids_in_day')

api.add_resource(SetExtras, '/set_extraQ')
api.add_resource(SetPublicParameters, '/set_privacy')
api.add_resource(SetNotifications, '/set_notifications')

api.add_resource(GetMoodes, '/get_moodes')
api.add_resource(SetMood, '/set_mood')

api.add_resource(GetMembers, '/get_members')
api.add_resource(KickMember, '/kick_member')

api.add_resource(GetInvite, '/get_invite')
api.add_resource(CreateInvite, '/create_invite')
api.add_resource(DeleteInvite, '/delete_invite')
api.add_resource(JoinByInvite, '/join')

api.add_resource(UploadPhoto, '/upload')

if __name__ == '__main__':
    context = ('local.crt', 'local.key')
    app.run(debug=True, port=10888, ssl_context='adhoc')

from flask_restful import Resource
from flask import g, request, send_file
from helpers.vk import VK_Community
from db.models import User
from helpers.upload_checker import markUpload, canUploadPhoto


vk_api_community = VK_Community()
def upload_photo_to_vk(photo):
    server = vk_api_community.getUploadServer()
    uploaded = vk_api_community.uploadToServer(server, photo)
    res = vk_api_community.savePhoto(**uploaded)
    sizes = res[0]['sizes']
    return max(sizes, key=lambda s: s['width']*s['height'])['url']

class UploadPhoto(Resource):
    def post(self):
        userid = g.get('userid')

        if "photo" not in request.files:
            return {"error":True, "message": "Неверный файл", "code":400}, 400

        photo = request.files["photo"]

        if photo.filename == "":
            return {"error":True, "message": "Неверный файл", "code":400}, 400

        if not (photo.filename.endswith(".jpg") or photo.filename.endswith(".jpeg") or photo.filename.endswith(
                ".png") or photo.filename.endswith(".heic")):
            return {"error":True, "message": "Неверный формат файла", "code":400}, 400

        if (request.content_length/(1024*1024)) > 3:
            return {"error": True, "message": "Максимальный размер фотографии 3 мб", "code": 400}, 400

        user = User.get(User.vk_id == userid)
        if not canUploadPhoto(user):
            return dict(
                error=True,
                code=429,
                message='Вы загрузили слишком много фотографий за последнее время'
            ), 429

        url_image = upload_photo_to_vk(photo)
        markUpload(user, url_image)
        return dict(
            error=False,
            code=200,
            image=url_image
        )
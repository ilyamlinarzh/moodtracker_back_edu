from auth.base import app_access_token, app_id, community_access_token
import vk_api
import requests


class VK:
    def __init__(self):
        self.api = vk_api.VkApi(token=app_access_token, api_version='5.154', app_id=app_id)

    def get_user(self, userid):
        api = self.api
        user = api.method('users.get', dict(
            user_ids=userid,
            fields='photo_200',
            lang='ru'
        ))

        return user[0]


class VK_Community:
    def __init__(self):
        self.api = vk_api.VkApi(token=community_access_token, api_version='5.154')

    def getUploadServer(self):
        api = self.api
        server = api.method('photos.getMessagesUploadServer')

        return server['upload_url']

    def uploadToServer(self, server, photo):
        files = {'photo': (photo.filename, photo.stream, photo.content_type)}
        upload_req = requests.post(server, files=files)
        return upload_req.json()

    def savePhoto(self, photo, server, hash):
        api = self.api
        save_req = api.method('photos.saveMessagesPhoto', dict(
            photo=photo,
            server=server,
            hash=hash
        ))

        return save_req
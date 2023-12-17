from db.models import UploadedImages
from helpers.time import getCurrentTimestamp

limits = {
    '5minutes': 20,
    'hour': 50,
    'day': 50,
    'week': 100,
    'month': 300
}


def markUpload(user, url):
    timestamp = getCurrentTimestamp()
    img = UploadedImages(
        user=user,
        timestamp=timestamp,
        url=url
    )

    img.save()
    return timestamp


def canUploadPhoto(user):
    timenow = getCurrentTimestamp()

    in5minutes = UploadedImages.select().where(
        (UploadedImages.timestamp > (timenow - (5 * 60))) &
        (UploadedImages.user == user)
    ).count()
    inhour = UploadedImages.select().where(
        (UploadedImages.timestamp > (timenow - (60 * 60))) &
        (UploadedImages.user == user)
    ).count()
    inday = UploadedImages.select().where(
        (UploadedImages.timestamp > (timenow - (24 * 60 * 60))) &
        (UploadedImages.user == user)
    ).count()
    inweek = UploadedImages.select().where(
        (UploadedImages.timestamp > (timenow - (7 * 24 * 60 * 60))) &
        (UploadedImages.user == user)
    ).count()
    inmonth = UploadedImages.select().where(
        (UploadedImages.timestamp > (timenow - (30 * 24 * 60 * 60))) &
        (UploadedImages.user == user)
    ).count()

    if inmonth >= limits['month']:
        return False

    if inweek >= limits['week']:
        return False

    if inday >= limits['day']:
        return False

    if inhour >= limits['hour']:
        return False

    if in5minutes >= limits['5minutes']:
        return False

    return True

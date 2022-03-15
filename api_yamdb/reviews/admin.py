import reviews.models as models
from django.contrib import admin

LIST_MODELS = [
    models.User,
    models.Category,
    models.Genre,
    models.Title,
    models.Review,
    models.Comment
]

admin.site.register(LIST_MODELS)

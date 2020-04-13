from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.views.decorators.cache import cache_page

from .views import ImagesListView, UploadView, image

urlpatterns = [
	path('', ImagesListView.as_view(), name='images_list'),
	path('upload/', UploadView.as_view(), name='upload'),
	path('<slug:slug>/', cache_page(None)(image), name='image'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

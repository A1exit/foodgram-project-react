from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ListSubscriptions, Subscribe

router = SimpleRouter()

router.register('users/subscriptions', ListSubscriptions,
                basename='subscriptions')

urlpatterns = [
    path('', include(router.urls)),
    url('', include('djoser.urls')),
    url(r'^auth/', include('djoser.urls.authtoken')),
    path('users/<int:id>/subscribe/', Subscribe.as_view()),
]

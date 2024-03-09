from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register('hours', views.ShiftHoursViewSet, basename='hours')
router.register('members', views.MemberViewSet, basename='hours')
router.register('', views.AttendanceViewSet, basename='attendance')

urlpatterns = router.urls

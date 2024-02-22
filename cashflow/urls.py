from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('openings', views.OpeningViewSet, basename='openings')
router.register('transactions', views.TransactionViewSet,
                basename='transactions')
router.register('transaction-details',
                views.TransactionDetailViewSet, basename='transaction-details')
router.register('runners',
                views.RunnerViewSet, basename='runners')

urlpatterns = router.urls

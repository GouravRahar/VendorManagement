from rest_framework.routers import DefaultRouter

from .views import VendorProfileViewset, PurchaseOrderViewset

router = DefaultRouter()
router.register(r'vendors', VendorProfileViewset, basename='vendor')
router.register(r'purchase_order', viewset=PurchaseOrderViewset,basename='purchase_order')
urlpatterns = router.urls

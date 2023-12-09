from rest_framework_nested import routers
from . import views
from django.urls import path,include

router = routers.DefaultRouter()
router.register('categories',views.CategoryViewSet)
# router.register('sub_categories',views.SubCategoryViewSet)
# router.register('topics',views.TopicViewSet)
router.register('courses',views.CourseViewSet,basename="courses")
router.register('discounts',views.DiscountViewSet)
router.register('sliders',views.SliderViewSet)
router.register('students',views.StudentViewSet)
router.register('enrollment',views.EnrollmentViewSet)
urlpatterns = [
    path('',include(router.urls)),
]
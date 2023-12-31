from rest_framework_nested import routers
from . import views
from django.urls import path,include,re_path
from django.views.generic import TemplateView

router = routers.DefaultRouter()
router.register('categories',views.CategoryViewSet)
# router.register('sub_categories',views.SubCategoryViewSet)
# router.register('topics',views.TopicViewSet)
router.register('courses',views.CourseViewSet,basename="courses")
router.register('discounts',views.DiscountViewSet)
router.register('sliders',views.SliderViewSet)
router.register('students',views.StudentViewSet)
router.register('enrollment',views.EnrollmentViewSet)
router.register('complete_subsections',views.CompleteSubSectionViewSet)
router.register('reviews',views.ReviewViewSet)
router.register('ratings',views.RatingViewSet)
router.register('splashs',views.SplashViewSet)
urlpatterns = [
    path('',include(router.urls)),
    path('ratings_summary/<int:course_id>/',views.rating_list),
    re_path(r'^password_reset_confirm/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z_\-]+)/$',
           TemplateView.as_view(template_name="learning/reset_password.html"), name='password_reset_confirm'),
]
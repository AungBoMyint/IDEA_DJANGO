from rest_framework_nested import routers
from . import views
from django.urls import path,include,re_path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import EmailTokenObtainPairView

router = routers.DefaultRouter()
router.register('categories',views.CategoryViewSet)
# router.register('sub_categories',views.SubCategoryViewSet)
# router.register('topics',views.TopicViewSet)
router.register('courses',views.CourseViewSet,basename="courses")
router.register('discounts',views.DiscountViewSet)
router.register('discount_items',views.DiscountItemsViewSet)
router.register('sliders',views.SliderViewSet)
router.register('youtube_links',views.YoutubeLinkViewSet)
router.register('facebook_links',views.FacebookLinkViewSet)
router.register('messenger_links',views.MessengerLinkViewSet)
router.register('courselinks',views.CourseLinkViewSet)
router.register('blog_links',views.BlogLinkViewSet)
router.register('students',views.StudentViewSet,basename="students")
router.register('enrollment',views.EnrollmentViewSet,basename="enrollment")
router.register('complete_subsections',views.CompleteSubSectionViewSet)
router.register('reviews',views.ReviewViewSet,basename="reviews")
router.register('ratings',views.RatingViewSet,basename="ratings")
router.register('splashs',views.SplashViewSet)
router.register('sections',views.SectionViewSet)
router.register('subsections',views.SubSectionViewSet)
router.register('videos',views.VideoViewSet)
router.register('blogs',views.BlogViewSet)
router.register('pdfs',views.PdfViewSet)
router.register('admin_enrollments',views.AdminEnrollStudentViewSet,basename="admin_enrollments")
router.register('admin_students', views.AdminStudentViewSet,basename="admin_students")
router.register('admin_ratings',views.AdminRatingViewSet,basename="admin_ratings")
router.register('admin_reviews',views.AdminReviewViewSet,basename="admin_reviews")
urlpatterns = [
    path('',include(router.urls)),
    path("token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('ratings_summary/<int:course_id>/',views.rating_list),
    re_path(r'^password_reset_confirm/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z_\-]+)/$',
           TemplateView.as_view(template_name="learning/reset_password.html"), name='password_reset_confirm'),
]
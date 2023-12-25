from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Subquery
from django.db.models import Count,Avg,Sum
from rest_framework import status
from django.db import transaction
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.shortcuts import get_list_or_404
from rest_framework.viewsets import ReadOnlyModelViewSet,GenericViewSet,ModelViewSet
from rest_framework.mixins import RetrieveModelMixin,ListModelMixin,UpdateModelMixin,CreateModelMixin
from rest_framework.filters import SearchFilter
from . import filters
from .permissions import IsCurrentUserOrReadOnly
from rest_framework.permissions import AllowAny,IsAuthenticated
from . import models
from . import serializers
from rest_framework.parsers import JSONParser 
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view,permission_classes
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .signals import enrollment as enrollment_signal
# Create your views here.
class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = models.Category.objects.annotate(
        courses_count = Count('courses')
    ).all()
    serializer_class = serializers.CategorySerializer
    filter_backends = [DjangoFilterBackend]

    """ @method_decorator(cache_page(5 * 60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)  """
    

# class SubCategoryViewSet(ReadOnlyModelViewSet):
#     queryset = models.SubCategory.objects.annotate(
#         topics_count = Count("topics")
#     ).all()
#     serializer_class = serializers.SubCategorySerializer
#     @method_decorator(cache_page(5 * 60))
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)

# class TopicViewSet(ReadOnlyModelViewSet):
#     queryset = models.Topic.objects.annotate(
#         courses_count = Count('courses')
#     ).all()
#     serializer_class = serializers.TopicSerializer
#     @method_decorator(cache_page(5 * 60))
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)

class CourseViewSet(RetrieveModelMixin,ListModelMixin,GenericViewSet):
    
    serializer_class = serializers.CourseSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter]
    filterset_class = filters.CourseFilter
    search_fields = ["title"]
    
    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.DetailCourseSerializer
        else:
            return serializers.CourseSerializer
    
    #---------------------For Caching-----------
    """ @method_decorator(cache_page(5 * 60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs) """
    #--------------------------
    def get_serializer_context(self):
        return {'user_id':self.request.user.id}
    def get_queryset(self):
        user_id = self.request.user.id  # Assuming user is authenticated
        # Subquery to get IDs of courses where the user is enrolled
        enrolled_courses = models.EnrollStudents.objects.filter(student__user_id=user_id).values('course_id').distinct()
        if self.action == "list":
            return models.Course.objects \
            .annotate(
            ratings_avg = Avg('ratings__rating',distinct=True),
            reviews_count = Count('reviews',distinct=True)
            ) \
        .prefetch_related('ratings') \
        .prefetch_related('reviews') \
        .exclude(id__in=Subquery(enrolled_courses))
        else:
            return models.Course.objects \
            .annotate(
            enroll_students_count=Count('enroll_students',distinct=True),
            ratings_avg = Avg('ratings__rating',distinct=True),
            reviews_count = Count('reviews',distinct=True),
            total_subsections = Count('sections__subsections',distinct=True),
            videos_count = Count("sections__subsections__video",distinct=True),
            pdfs_count = Count("sections__subsections__pdf",distinct=True),
            blogs_count = Count("sections__subsections__blog",distinct=True),
            video_durations = Sum("sections__subsections__video__duration"),
            pdf_durations = Sum("sections__subsections__pdf__duration"),
            blog_durations = Sum("sections__subsections__blog__duration"),
            ) \
        .prefetch_related('ratings') \
        .prefetch_related('reviews') \
        .select_related('discount_item__discount') \
        .prefetch_related('enroll_students__student__user') \
        .prefetch_related('category') \
        .prefetch_related('sections__subsections__video') \
        .prefetch_related('sections__subsections__blog') \
        .prefetch_related('sections__subsections__pdf') \
        .prefetch_related('sections__subsections__complete_subsections') \
        .exclude(id__in=Subquery(enrolled_courses))
    
        

class DiscountViewSet(ReadOnlyModelViewSet):
    queryset = models.Discount.objects \
    .annotate(
        enroll_students_count = Count('discount_items__course__enroll_students')
    ) \
    .prefetch_related(
        "discount_items__course__sections"
        ).all()
    serializer_class = serializers.DiscountSerializer
    """ @method_decorator(cache_page(5 * 60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs) """

class SubSectionViewSet(ReadOnlyModelViewSet):
    queryset = models.SubSection.objects.prefetch_related("video") \
    .prefetch_related("blog") \
    .prefetch_related("pdf") \
    .all()
    serializer_class = serializers.SubSectionSerializer
    """ @method_decorator(cache_page(5 * 60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs) """

class SliderViewSet(ReadOnlyModelViewSet):
    queryset = models.Slider.objects.prefetch_related(
        "messengerlink",
        "courselink",
        "facebooklink",
        "youtube",
        "blogs"
    ).all()
    serializer_class = serializers.SliderSerializer
    """ @method_decorator(cache_page(5 * 60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs) """

class StudentViewSet(ListModelMixin,CreateModelMixin,RetrieveModelMixin,GenericViewSet):
    queryset = models.Student.objects.select_related('user').all()
    serializer_class = serializers.StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'user_id':self.request.user.id}
    
    @action(detail=False,methods=['GET'],permission_classes=[IsAuthenticated])
    def enrolled_courses(self,request):

        enrolled_courses = models.Course.objects \
         \
            .annotate(
            enroll_students_count=Count('enroll_students',distinct=True),
            ratings_avg = Avg('ratings__rating',distinct=True),
            reviews_count = Count('reviews',distinct=True),
            total_subsections = Count('sections__subsections',distinct=True),
            videos_count = Count("sections__subsections__video",distinct=True),
            pdfs_count = Count("sections__subsections__pdf",distinct=True),
            blogs_count = Count("sections__subsections__blog",distinct=True),
            video_durations = Sum("sections__subsections__video__duration"),
            pdf_durations = Sum("sections__subsections__pdf__duration"),
            blog_durations = Sum("sections__subsections__blog__duration"),
            ) \
        .prefetch_related('ratings') \
        .prefetch_related('reviews') \
        .select_related('discount_item__discount') \
        .prefetch_related('enroll_students') \
        .prefetch_related('enroll_students__student__user') \
        .prefetch_related('category') \
        .prefetch_related('sections__subsections__video') \
        .prefetch_related('sections__subsections__blog') \
        .prefetch_related('sections__subsections__pdf') \
        .prefetch_related('sections__subsections__complete_subsections') \
        .filter(enroll_students__student__user_id=request.user.id,enroll_students__subscribed=True)
        #.filter(id__in=Subquery(models.EnrollStudents.objects.filter(student__user=request.user).values('course_id').distinct()))
        context = self.get_serializer_context()
        serialized_courses = serializers.EnrollCourseSerializer(enrolled_courses, many=True,context=context).data

        return Response(serialized_courses)

    @action(detail=False,methods=['GET','PUT'],permission_classes=[IsAuthenticated])
    def me(self,request):
        if request.method == 'GET':
            student =get_object_or_404(models.Student,user_id=request.user.id)
            serializer = serializers.StudentSerializer(student)
            return Response(serializer.data)
        elif request.method == 'PUT':
            student = models.Student.objects.get(user_id=request.user.id)
            serializer = serializers.StudentSerializer(student,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        

class EnrollmentViewSet(CreateModelMixin,UpdateModelMixin,GenericViewSet,RetrieveModelMixin):
    queryset = models.Enrollment.objects.prefetch_related('enroll_students').all()
    serializer_class = serializers.EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    """ @method_decorator(cache_page(5 * 60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs) """

    def create(self, request, *args, **kwargs):
        #check enroll_students is empty or not
        enroll_students = request.data.get("enroll_students",[])
        if len(enroll_students) < 1:
            return Response({"enroll_students":"Enroll Students shouldn't be empty"},status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            for course_id in enroll_students:
                student_queryset = models.EnrollStudents.objects.filter(course_id=course_id,student_id = request.user.student.id)
                exist = student_queryset.exists()
                if exist:
                    #mean update
                    subscribed_count = student_queryset.first().subscribed_count + 1
                    student_queryset.update(
                                            subscribed = True,
                                            expiration_date = timezone.now() + timedelta(minutes=2),
                                            subscribed_count = subscribed_count
                                        )
                else:
                    #crate
                    enrollment = models.Enrollment.objects.create()
                    models.EnrollStudents.objects.create(
                                    enrollment_id = enrollment.id,
                                    course_id = course_id,
                                    student_id = request.user.student.id,
                                    subscribed = True,
                                    expiration_date = timezone.now() + timedelta(minutes=2)
                                )
            return Response(data="Success",status=status.HTTP_200_OK)
            """ serializer = serializers.EnrollmentSerializer(enrollment)
            courses = models.Course.objects.filter(id__in=enroll_students).values("title")
            enrollment_signal.send_robust(self.__class__,data={
                "email": request.user.email,
                "student": request.user.username,
                "courses":courses,

            })
            
            return Response(serializer.data) """

class CompleteSubSectionViewSet(CreateModelMixin,GenericViewSet):
    queryset = models.CompleteSubSection.objects.all()
    serializer_class = serializers.CompleteSubSectionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'user_id':self.request.user.id}
    
    def create(self, request, *args, **kwargs):
        subsection_id = request.data.get("subsection")
        student_id = request.user.student.id
        complete_query = models.CompleteSubSection.objects.filter(
            subsection_id = subsection_id,
            student_id = student_id,
        )
        if complete_query.exists():
            return Response("Already completed,so can't did twice",status=status.HTTP_400_BAD_REQUEST)
        else:
            models.CompleteSubSection.objects.create(
            subsection_id = subsection_id,
            student_id = student_id,
            )
            return Response("ok",status=status.HTTP_201_CREATED)

@api_view(["GET"])
def rating_list(request:Request,course_id):
    if request.method == "GET":
        if(course_id):
            #if course id is passed
            #find all rating in this course_id
            rating_one_count = models.Rating.objects.filter(course_id=course_id,rating__lt=1.9).count()
            rating_two_count = models.Rating.objects.filter(course_id=course_id,rating__lt=2.9,rating__gt=1.9).count()
            rating_three_count = models.Rating.objects.filter(course_id=course_id,rating__lt=3.9,rating__gt=2.9).count()
            rating_four_count = models.Rating.objects.filter(course_id=course_id,rating__lt=4.9,rating__gt=3.9).count()
            rating_five_count = models.Rating.objects.filter(course_id=course_id,rating__gt=4.9).count()
            total_ratings = models.Rating.objects.filter(course_id=course_id).count()
            return Response(data={
                "rating_one":rating_one_count,
                "rating_two":rating_two_count,
                "rating_three":rating_three_count,
                "rating_four":rating_four_count,
                "rating_five":rating_five_count,
                "total_ratings":total_ratings,
            },status=status.HTTP_200_OK)

class ReviewViewSet(ModelViewSet ):
    #permission_classes = [IsAuthenticated]
    queryset = models.Review.objects.prefetch_related("student__user").prefetch_related("course").all()
    serializer_class = serializers.ReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["course_id"]

    def create(self, request, *args, **kwargs):
        course_id = request.data.get("course")
        student_id = request.user.student.id
        review_query = models.Review.objects.filter(course_id=course_id,student_id=student_id)
        if review_query.exists():
            return Response("You can't review twice!",status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def get_serializer_context(self):
        if(self.request.user.id):
            return {'student_id':self.request.user.student.id}
        else:
            return {'student_id':0}

class RatingViewSet(ModelViewSet ):
    #permission_classes = [IsAuthenticated]
    queryset = models.Rating.objects.prefetch_related("student__user").all()
    serializer_class = serializers.RatingSerializer

    def create(self, request, *args, **kwargs):
        course_id = request.data.get("course")
        student_id = request.user.student.id
        rating_query = models.Rating.objects.filter(course_id=course_id,student_id=student_id)
        if rating_query.exists():
            return Response("You can't rating twice!",status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def get_serializer_context(self):
        if(self.request.user.id):
            return {'student_id':self.request.user.student.id}
        else:
            return {'student_id':0}
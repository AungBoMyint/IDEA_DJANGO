from django.shortcuts import render
from django.db.models import Count,Avg
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
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view,permission_classes
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .signals import enrollment as enrollment_signal
# Create your views here.
class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    filter_backends = [DjangoFilterBackend]

    @method_decorator(cache_page(5 * 60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    

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

    
    #---------------------For Caching-----------
    @method_decorator(cache_page(5 * 60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    #--------------------------
    def get_serializer_context(self):
        return {'user_id':self.request.user.id}
    def get_queryset(self):
        return models.Course.objects \
    .annotate(
        enroll_students_count=Count('enroll_students',distinct=True),
        ratings_avg = Avg('ratings__rating',distinct=True),
        reviews_count = Count('reviews',distinct=True),
        total_subsections = Count('sections__subsections',distinct=True),
        videos_count = Count("sections__subsections__video",distinct=True),
        pdfs_count = Count("sections__subsections__pdf",distinct=True),
        blogs_count = Count("sections__subsections__blog",distinct=True)
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
    .all()
    
        

class DiscountViewSet(ReadOnlyModelViewSet):
    queryset = models.Discount.objects \
    .annotate(
        enroll_students_count = Count('discount_items__course__enroll_students')
    ) \
    .prefetch_related(
        "discount_items__course__sections"
        ).all()
    serializer_class = serializers.DiscountSerializer
    @method_decorator(cache_page(5 * 60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class SubSectionViewSet(ReadOnlyModelViewSet):
    queryset = models.SubSection.objects.prefetch_related("video") \
    .prefetch_related("blog") \
    .prefetch_related("pdf") \
    .all()
    serializer_class = serializers.SubSectionSerializer
    @method_decorator(cache_page(5 * 60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class SliderViewSet(ReadOnlyModelViewSet):
    queryset = models.Slider.objects.prefetch_related(
        "messengerlink",
        "courselink",
        "facebooklink",
        "youtube",
        "blogs"
    ).all()
    serializer_class = serializers.SliderSerializer
    @method_decorator(cache_page(5 * 60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class StudentViewSet(ListModelMixin,CreateModelMixin,RetrieveModelMixin,GenericViewSet):
    queryset = models.Student.objects.select_related('user').all()
    serializer_class = serializers.StudentSerializer
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(5 * 60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        return {'user_id':self.request.user.id}
    
    @action(detail=False,methods=['GET'],permission_classes=[IsAuthenticated])
    def enrolled_courses(self,request):
        enrollment = get_list_or_404(models.EnrollStudents.objects.filter(student__user__id=request.user.id) \
        .prefetch_related('course'))

        
        serializer = serializers.EnrollCourseSerializer(enrollment,many=True)
        return Response(serializer.data)

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
        

class EnrollmentViewSet(CreateModelMixin,GenericViewSet,RetrieveModelMixin):
    queryset = models.Enrollment.objects.prefetch_related('enroll_students').all()
    serializer_class = serializers.EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(5 * 60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        #check enroll_students is empty or not
        enroll_students = request.data.get("enroll_students",[])
        if len(enroll_students) < 1:
            return Response({"enroll_students":"Enroll Students shouldn't be empty"},status=status.HTTP_400_BAD_REQUEST)
        #if there has enroll_students already with course_id & user_id
        #then we remove this course_id
        for course_id in enroll_students:
            ifExist = models.EnrollStudents.objects.filter(course_id=course_id,student_id = request.user.student.id).first()
            if ifExist:
                course = models.Course.objects.get(pk=course_id)
                return Response(data=f'You have already enrolled this {course.title}',status=status.HTTP_400_BAD_REQUEST)
        #if not empty
        with transaction.atomic():
            #first we save Enrollment
            enrollment = models.Enrollment.objects.create()
            #second we loop and save enroll_students
            
            for course_id in enroll_students:
                models.EnrollStudents.objects.create(
                                    enrollment_id = enrollment.id,
                                    course_id = course_id,
                                    student_id = request.user.student.id
                                )
                
            #then return enrollment
        serializer = serializers.EnrollmentSerializer(enrollment)
        courses = models.Course.objects.filter(id__in=enroll_students).values("title")
        enrollment_signal.send_robust(self.__class__,data={
            "email": request.user.email,
            "student": request.user.username,
            "courses":courses,

        })
        return Response(serializer.data)
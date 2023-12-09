from django_filters.rest_framework import FilterSet
from .models import Course
import django_filters
from . import models

class CourseFilter(FilterSet):
    enroll_students_gt = django_filters.NumberFilter(field_name='enroll_students_count',method="students_gt",label="EnrollStudents Greater Than")
    enroll_students_lt = django_filters.NumberFilter(field_name='enroll_students_count',method="students_lt",label="EnrollStudents Less Than")
    ratings_gt = django_filters.NumberFilter(field_name="ratings_avg",lookup_expr='gt',label='Rating Greater Than')
    ratings_lt = django_filters.NumberFilter(field_name='ratings_avg',lookup_expr='lt',label="Rating Less Than")
    reviews_gt = django_filters.NumberFilter(field_name="reviews_count",lookup_expr='gt',label='Reviews Greater than')
    reviews_lt = django_filters.NumberFilter(field_name='reviews_count',lookup_expr='lt',label='Reviews Less than')
    #category = django_filters.CharFilter(field_name='category_id',method='filter_category',lookup_expr='exact',label="Filter with category")
    
    # def filter_category(self,queryset,name,value):
    #     if value is None:
    #         return queryset
    #     else:
    #         subcategory_id = models.SubCategory.objects.filter(category_id=value)
    #         topic_id = models.Topic.objects.filter(subcategory_id__in=subcategory_id)
    #         return queryset.filter(topic_id__in=topic_id)
    def students_gt(self,queryset,name,value):
            lookup = '__'.join([name, 'gt'])
            return queryset.filter(**{lookup: value})
    def students_lt(self,queryset,name,value):
            lookup = '__'.join([name, 'lt'])
            return queryset.filter(**{lookup: value})


    class Meta:
        model = Course
        fields = {
            'category_id': ['exact'],
            'price': ['lt','gt'],
        }
        filterset_fields = {
            'enroll_students_gt':['gt'],
            'enroll_students_lt':['lt'],
            'ratings_gt':['gt'],
            'ratings_lt':['lt'],
            'reviews_gt':['gt'],
            'reviews_lt':['lt'],
            'category':['exact']
        }
    
    

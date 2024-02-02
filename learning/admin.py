from collections.abc import Callable, Mapping, Sequence
from typing import Any
from django import forms
from django.utils.html import mark_safe
from tempfile import NamedTemporaryFile
from .forms import BlogLinkForm
from django.core.files.storage import default_storage
import pprint
import re
from django.db import models as base_models
from django.db.models.fields.related import ForeignKey
from .core import format_duration,format_duration_minutes,get_pdf_reading_time
from moviepy.editor import VideoFileClip
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from django.urls import reverse
from django.utils.html import format_html,format_html_join,urlencode
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from . import models
import nested_admin
from django import forms
from django.db.models import Count,Prefetch,Avg
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.admin import TabularInline,StackedInline
from django.forms.models import BaseInlineFormSet, ModelChoiceField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

admin.site.register(models.CustomUser)
# Register your models here.
@admin.register(models.Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['course','student','rating']

#Blog Link
@admin.register(models.BlogLink)
class BlogLinkAdmin(admin.ModelAdmin):
    list_display = ['id','slider']

#Course Link 
class CourseLinkAdmin(nested_admin.NestedStackedInline):
    list_display = ['id',"slider"]
    model = models.CourseLink

#Youtube Link
class YoutubeLinkAdmin(nested_admin.NestedStackedInline):
    list_display = ['id',"slider"]
    model = models.YoutubeLink
#Facebook Link
class FacebokLinkAdmin(nested_admin.NestedStackedInline):
    list_display = ['id',"slider"]
    model = models.FacebookLink
#Messenger Link
class MessengerLinkAdmin(nested_admin.NestedStackedInline):
    list_display = ['id',"slider"]
    model = models.MessengerLink

#Slider 
@admin.register(models.Slider)
class SliderAdmin(nested_admin.NestedModelAdmin):
    list_display = ['title','image']
    inlines = [CourseLinkAdmin,YoutubeLinkAdmin,FacebokLinkAdmin,MessengerLinkAdmin]
    

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title','image_']
   
    search_fields = ['title']
    list_per_page = 10
    list_display_links = ['title']

    @admin.display()
    def image_(self,category:models.Category):
        return mark_safe(f'<img src = "https://learn-ease.sgp1.digitaloceanspaces.com/api-media/media/public/{category.image.name}" width = "80" height = "80" style="object-fit: contain;"/>')
    
    # @admin.display()
    # def subcategories(self,category:models.Category):
    #     url = (reverse('admin:learning_subcategory_changelist')
    #            + '?' + urlencode({'category_id': category.id}))
    #     return format_html('<a href="{}">{}</a>',url,category.subcategories_count)

    # def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
    #     return super().get_queryset(request).annotate(
    #         subcategories_count = Count('subcategories')
    #     )

# @admin.register(models.SubCategory)
# class SubCategoryAdmin(admin.ModelAdmin):
#     list_display = ["title","category"]
#     list_editable = ["title"]
#     list_per_page = 10
#     list_display_links = None
#     autocomplete_fields = ["category"]
#     search_fields = ["title"]

# @admin.register(models.Topic)
# class TopicAdminPanel(admin.ModelAdmin):
#     list_display = ["title","subcategory"]
#     list_editable = ["title","subcategory"]
#     list_display_links = None
#     list_per_page = 10
#     search_fields = ["title"]

#     def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
#         return super().get_queryset(request).prefetch_related('subcategory')

@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["avatar_","name","points","membership","enrolled_courses"]
    fields = ["avatar",'preview',"user","points","membership"]
    readonly_fields = ['preview']

    @admin.display()
    def avatar_(self,student:models.Student):
        return mark_safe(f'<img src = "https://learn-ease.sgp1.digitaloceanspaces.com/api-media/media/public/{student.avatar.name}" width = "50" height = "50" style="object-fit: cover;border-radius: 50%"/>')
    @admin.display()
    def name(self,student:models.Student):
        return f'{student.user.first_name} {student.user.last_name}'
    @admin.display()
    def enrolled_courses(self,student:models.Student):
        return student.enroll_count
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request) \
         .annotate(enroll_count=Count('enroll_students')) \
         .select_related('user')
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'avatar':
            kwargs['widget'] = admin.widgets.AdminFileWidget(attrs={
                'class': 'image-preview',  # Add a class for targeting with JavaScript
            })
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    

admin.site.register(models.Review)

@admin.register(models.Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["enroll_at","total_income"]

    @admin.display()
    def total_income(self,enroll:models.Enrollment):
        total = '{:,}'.format(sum(en_stu.course.price for en_stu in enroll.enroll_students.all()))
        return  f'{total} Ks'

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request) \
        .prefetch_related('enroll_students__course','enroll_students__student__user')

@admin.register(models.EnrollStudents)
class EnrollStudentsAdmin(admin.ModelAdmin):
    list_display = ["user_name","course_title"]
    @admin.display()
    def user_name(self,enroll:models.EnrollStudents):
        return enroll.student.user.username
    @admin.display()
    def course_title(self,enroll:models.EnrollStudents):
        return enroll.course.title
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).select_related("student__user",'course')
    def get_form(self, request: Any, obj: Any | None = ..., change: bool = ..., **kwargs: Any) -> Any:
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['student'].queryset = form.base_fields['student'].queryset.select_related('user')
        return form
    
class DiscountItemForm(forms.ModelForm):
    class Meta:
        model = models.DiscountItem
        fields = '__all__'
    course = forms.ModelChoiceField(
        queryset=models.Course.objects.exclude(id__in=models.DiscountItem.objects.values_list('course_id', flat=True))
    )



@admin.register(models.DiscountItem)
class DiscountItemAdmin(admin.ModelAdmin):
    list_display = ["course","discount"]
    autocomplete_fields = ["course"]
    form = DiscountItemForm

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).select_related("course") \
        .prefetch_related("discount")
   

@admin.register(models.Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ["title","discount_items"]
    list_display_links = ["title"]
    @admin.display()
    def discount_items(self,discount:models.Discount):
        url = (reverse('admin:learning_discountitem_changelist') +
               '?' + urlencode({'discount_id': discount.id}))
        return format_html(
            '<a href={}>{}</a>',url,discount.discount_items_count
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request) \
                .prefetch_related(Prefetch('discount_items', queryset=models.DiscountItem.objects.select_related('course'))) \
                .annotate(discount_items_count=Count('discount_items')) \

    
    
    



@admin.register(models.Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ["title","duration_"]

    @admin.display()
    def duration_(self,blog:models.Blog):
        return format_duration(blog.duration)

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        # Save the blog post first
        super().save_model(request, obj, form, change)

        # Calculate reading time and save it
        words = obj.content.split()
        word_count = len(words)
        average_wpm = 60  # Average words per minute for reading
        reading_time = word_count / average_wpm
        obj.duration = round(reading_time*60)
        obj.save()

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request) \
        .select_related('subsection')
    def get_form(self, request: Any, obj: Any | None = ..., change: bool = ..., **kwargs: Any) -> Any:
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['subsection'].queryset = form.base_fields['subsection'].queryset.prefetch_related('section__course')
        return form

@admin.register(models.Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ["video_url","duration_","subsection"]
    formfield_overrides = {
        base_models.FileField:{'widget': forms.FileInput(attrs={'accept': 'video/*'})}
    }
    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        # Save the video file first
        super().save_model(request, obj, form, change)

        # Calculate duration and save it
        try:
            video_path = obj.video_url.name
            video_file = default_storage.open(video_path)
            with NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(video_file.read())

            # Use the temporary file path for VideoFileClip
            clip = VideoFileClip(temp_file.name)
            duration = clip.duration
            obj.duration = f'{round(duration)}s' if duration else '0s'  # Handle empty duration
            obj.save()

            # Delete the temporary file after processing
            temp_file.close()
        except Exception as e:
            print(f"Error: {e}")
    @admin.display()
    def duration_(self, video):
        try:
            time_int = int(video.duration.replace('s', '')) if video.duration else 0  # Handle empty duration
            return format_duration(time_int)
        except ValueError:
            return 'Invalid Duration'
        
    @admin.display()
    def subsection(self,video:models.Video):
        return video.subsection
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request) \
        .select_related('subsection')
    def get_form(self, request: Any, obj: Any | None = ..., change: bool = ..., **kwargs: Any) -> Any:
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['subsection'].queryset = form.base_fields['subsection'].queryset.prefetch_related('section__course')
        return form
    
@admin.register(models.Pdf)
class PdfAdmin(admin.ModelAdmin):
    list_display = ["pdf_url","duration_"]
    formfield_overrides = {
        base_models.FileField:{'widget': forms.FileInput(attrs={'accept': 'application/pdf'})}
    }
    @admin.display()
    def duration_(self,pdf:models.Pdf):
        return format_duration(pdf.duration)

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        super().save_model(request, obj, form, change)
        pdf_path = obj.pdf_url.name
        pdf_file = default_storage.open(pdf_path)
        with NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(pdf_file.read())
        obj.duration = get_pdf_reading_time(temp_file.name)
        obj.save()
        temp_file.close()

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request) \
        .select_related('subsection')
    def get_form(self, request: Any, obj: Any | None = ..., change: bool = ..., **kwargs: Any) -> Any:
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['subsection'].queryset = form.base_fields['subsection'].queryset.prefetch_related('section__course')
        return form



class VideoInline(nested_admin.NestedStackedInline):
    model = models.Video
    extra = 0
    def save_model(self, request, obj, form, change):
        print("Calling save model")
        obj.save()
class BlogInline(nested_admin.NestedStackedInline):
    model = models.Blog
    extra = 0
class PdfInline(nested_admin.NestedStackedInline):
    model = models.Pdf
    extra = 0

@admin.register(models.SubSection)
class SubSectionAdmin(nested_admin.NestedModelAdmin):
    search_fields = ["title"]
    list_display = ["title","section","course"]
    inlines = [VideoInline,BlogInline,PdfInline]
    autocomplete_fields = ["section"]

    """ def videos(self,subSection:models.SubSection):
        vid = models.Video.objects.filter(subsection_id=subSection.id)
        return format_html_join(
            ",",
            "<a href={}>{}</a>",
            ((reverse('admin:learning_video_changelist'),v.video_url) for v in vid)
        )
    def pdf(self,subSection:models.SubSection):
        pdf = models.Pdf.objects.filter(subsection_id=subSection.id)
        return format_html_join(
            ",",
            "<a href={}>{}</a>",
            ((reverse('admin:learning_pdf_changelist'),v.pdf_url) for v in pdf)
        )
    def blogs(self,subSection:models.SubSection):
        blog = models.Blog.objects.filter(subsection_id=subSection.id)
        if(blog):
            return blog.first().title
        return "" """
   
    @admin.display()
    def course(self,subsection:models.SubSection):
        return subsection.section.course
    def save_model(self, request, obj:models.SubSection, form, change):
        subsection = obj.save()
    
    
    
######
class SubSectionInline(nested_admin.NestedStackedInline):
    model = models.SubSection
    extra = 0
    inlines = [VideoInline,BlogInline,PdfInline]

########
class SectionInline(nested_admin.NestedStackedInline):
    model = models.Section
    extra = 0
    inlines = [SubSectionInline]
#####Section-------------#####
@admin.register(models.Section)
class SectionAdmin(nested_admin.NestedModelAdmin):
    list_display = ["title_course","course"]
    search_fields = ["title_course"]
    list_editable = ["course"]
    autocomplete_fields = ["course"]
    list_per_page = 10
    list_display_links = ["title_course"]
    inlines = [SubSectionInline]

    @admin.display()
    def title_course(self,section:models.Section):
        return section.title + " | " + section.course.title

#--------------------------#
@admin.register(models.Course)
class CourseAdmin(nested_admin.NestedModelAdmin):
    list_display = ["title","price","featured","reviews_count","ratings_avg","enroll_students","category","discount_price"]
    search_fields = ['title']
    autocomplete_fields = ['category']
    list_display_links = ['title']
    list_per_page = 10
    #inlines = [SectionInline]

    @admin.display()
    def discount_price(self,course:models.Course):
        original_amount = course.price
        discount_amount = (course.discount_item.discount.discount_percentage/100) * original_amount
        return  original_amount - discount_amount

    @admin.display(ordering="reviews_count")
    def reviews_count(self,course:models.Course):
        url = (reverse('admin:learning_review_changelist')
               + '?' + urlencode({'course_id': course.id}))
        return format_html("<a href='{}'>{}</a>",url,course.reviews_count)
    @admin.display()
    def ratings_avg(self,course:models.Course):
        return course.ratings_avg

    @admin.display()
    def enroll_students(self,course:models.Course):
        url = (reverse('admin:learning_enrollstudents_changelist')
               + '?' + urlencode({'course_id': course.id}))
        return format_html("<a href='{}'>{}</a>",url,course.enroll_students_count)
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request) \
        .select_related('category') \
        .prefetch_related('ratings') \
        .prefetch_related('sections__subsections__video') \
        .prefetch_related('sections__subsections__blog') \
        .prefetch_related('sections__subsections__pdf') \
        .select_related('discount_item__discount').annotate(
            enroll_students_count = Count('enroll_students',distinct=True),
            reviews_count = Count('reviews',distinct=True),
            ratings_avg= Avg('ratings__rating',distinct=True)
        )

# class FacebookLinkInline(nested_admin.NestedStackedInline):
#     model = models.FacebookLink
#     extra = 0
# class MessengerLinkInline(nested_admin.NestedStackedInline):
#     model = models.MessengerLink
#     extra = 0
# class YoutubeLinkInline(nested_admin.NestedStackedInline):
#     model = models.YoutubeLink
#     extra = 0
# class CourseLinkInline(nested_admin.NestedStackedInline):
#     model = models.CourseLink
#     extra = 0

# @admin.register(models.BlogLink)
# class BlogLinkAdmin(admin.ModelAdmin):
#     form = BlogLinkForm

# @admin.register(models.Slider)
# class SliderAdmin(nested_admin.NestedModelAdmin):
    # list_display = ["image","messengerlink","facebooklink","youtube_link","courselink"]
    
    # inlines = [FacebookLinkInline,MessengerLinkInline,YoutubeLinkInline,CourseLinkInline]
    
    # @admin.display()
    # def youtube_link(self,slider:models.Slider):
    #     return format_html('<a href={}>{}</a>',slider.youtube.link,slider.youtube.link)
    
    # def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
    #     return super().get_queryset(request).prefetch_related("messengerlink","facebooklink","youtube","courselink")
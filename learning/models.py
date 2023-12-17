from django.db import models
from django.utils.html import mark_safe
from django.conf.global_settings import AUTH_USER_MODEL
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from ckeditor.fields import RichTextField
from test_learning.storage_backends import PublicMediaStorage
# Create your models here.
class Category(models.Model):
    image = models.ImageField(upload_to='images/',null=True,storage=PublicMediaStorage())
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title
    
    def img_preview(self): #new
        return mark_safe(f'<img src = "{self.image}" width = "300"/>')

# class SubCategory(models.Model):
#     image = models.ImageField(upload_to='images/',null=True)
#     title = models.CharField(max_length=255)
#     category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="subcategories")

#     def __str__(self) -> str:
#         return self.title

# class Topic(models.Model):
#     image = models.ImageField(upload_to='images/',null=True)
#     title = models.CharField(max_length=255)
#     subcategory = models.ForeignKey(SubCategory,on_delete=models.CASCADE,related_name="topics")

#     def __str__(self) -> str:
#         return self.title

class Student(models.Model):
    BROWN = 'B'
    SLIVER = 'S'
    GOLD = 'G'
    MEMBERSHIP_CHOICES = [
        (BROWN,"Brown"),
        (SLIVER,"Sliver"),
        (GOLD,"Gold")
    ]
    avatar = models.ImageField(upload_to='images/',null=True)
    membership = models.CharField(choices=MEMBERSHIP_CHOICES,default=BROWN,max_length=1)
    points = models.PositiveIntegerField(null=True)
    user = models.OneToOneField(AUTH_USER_MODEL,on_delete=models.CASCADE)
    def preview(self):
            return mark_safe('<img src="https://learn-ease.sgp1.digitaloceanspaces.com/api-media/media/public/%s" width="200" height="200" style="object-fit:contain"/>' % (self.avatar.name))
    def __str__(self) -> str:
        return self.user.first_name + " " + self.user.last_name


class Course(models.Model):
    image = models.ImageField(upload_to='images/',null=True)
    video = models.FileField(upload_to='videos/',null=True)
    title = models.CharField(max_length=255)
    desc = models.TextField(null=True)
    price = models.IntegerField()
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name="courses")
    featured = models.BooleanField(default=False)
    def __str__(self) -> str:
        return self.title

class Review(models.Model):
    review = models.TextField()
    course = models.ForeignKey(Course,on_delete=models.PROTECT,related_name="reviews")
    student = models.ForeignKey(Student,on_delete=models.PROTECT,related_name="reviews")
    date = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.review
    
class Rating(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name="ratings")
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name="ratings")
    rating = models.FloatField()
    def __str__(self) -> str:
        return f'{self.rating}'

class Enrollment(models.Model):
    enroll_at = models.DateTimeField(auto_now_add=True)
    def __str__(self) -> str:
        return self.enroll_at.strftime("%A, %B %d, %Y")


class EnrollStudents(models.Model):
    enrollment = models.ForeignKey(Enrollment,on_delete=models.PROTECT,related_name="enroll_students")
    student = models.ForeignKey(Student,on_delete=models.PROTECT,related_name="enroll_students")
    course = models.ForeignKey(Course,on_delete=models.SET_NULL,null=True,related_name="enroll_students")
    def __str__(self) -> str:
        return self.student.user.first_name + " " + self.student.user.last_name



class Discount(models.Model):
    title = models.CharField(max_length=255)
    discount_percentage = models.IntegerField()
    image = models.ImageField(upload_to='images/',null=True)
    def __str__(self) -> str:
        return self.title

class DiscountItem(models.Model):
    course = models.OneToOneField(Course,on_delete=models.SET_NULL,null=True,related_name="discount_item")
    discount = models.ForeignKey(Discount,on_delete=models.CASCADE,related_name="discount_items")
    def __str__(self) -> str:
        return self.course.title

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    student = models.ForeignKey(Student,on_delete=models.CASCADE)

class Order(models.Model):
    placed_at = models.DateField(auto_now=True)

class OrderItem(models.Model):
    course = models.ForeignKey(Course,on_delete=models.PROTECT)
    student = models.ForeignKey(Student,on_delete=models.PROTECT)
    order = models.ForeignKey(Order,on_delete=models.PROTECT,related_name="items")

#---------------------------------------Section Related Models---------------------------------------------
class Section(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name="sections")

    def __str__(self) -> str:
        return self.title + " | " + self.course.title

class SubSection(models.Model):
    title = models.CharField(max_length=255)
    section = models.ForeignKey(Section,on_delete=models.CASCADE,related_name="subsections")
   
    def __str__(self) -> str:
        return self.title + " | " + self.section.course.title
    
class Blog(models.Model):
    image = models.ImageField(upload_to='images/',null=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    subsection = models.OneToOneField(SubSection,on_delete=models.CASCADE,related_name="blog",null=True)
    duration = models.PositiveIntegerField(blank=True,null=True)

    def __str__(self) -> str:
        return self.title
from django.core.exceptions import ValidationError
from django.db import models

def validate_file_extension(value):
    allowed_extensions = 'mp4'  # Add the allowed extensions here
    ext = str(value).lower().split('.')[-1]
    print(ext)
    if allowed_extensions != ext:
        raise ValidationError('File type not supported. Please upload a valid video file.')

class Video(models.Model):
    video_url = models.FileField(upload_to='videos/', null=True)
    duration = models.CharField(max_length=20, blank=True)  # Duration will be stored as a string
    subsection = models.OneToOneField(SubSection,on_delete=models.CASCADE,related_name="video",null=True)


class Pdf(models.Model):
    pdf_url = models.FileField(upload_to='pdfs/', null=True)
    duration = models.PositiveIntegerField(null=True,blank=True)
    subsection = models.OneToOneField(SubSection,on_delete=models.CASCADE,related_name="pdf",null=True)

    def __str__(self) -> str:
        return self.pdf_url.name
#-----------######------######----End------######---------######--------------------------------------------------------------

#---------------------------------Slider Related Model--------------------------------------------------------------------
class Slider(models.Model):
    image = models.ImageField(upload_to="images/")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self) -> str:
        return f'{self.created_at}'
    

class MessengerLink(models.Model):
    link = models.URLField()
    slider = models.OneToOneField(Slider,on_delete=models.CASCADE)
    def __str__(self) -> str:
        return self.link
    
class FacebookLink(models.Model):
    link = models.URLField()
    slider = models.OneToOneField(Slider,on_delete=models.CASCADE)
    def __str__(self) -> str:
        return self.link
    
class YoutubeLink(models.Model):
    link = models.URLField()
    slider = models.OneToOneField(Slider,on_delete=models.CASCADE,related_name="youtube")
    def __str__(self) -> str:
        return self.link
    
class CourseLink(models.Model):
    course = models.ManyToManyField(Course,related_name="courses")
    slider = models.OneToOneField(Slider,on_delete=models.CASCADE)
    def __str__(self) -> str:
        return self.slider.image.url
    
class BlogLink(models.Model):
    body = RichTextField()
    image = models.ImageField(upload_to='images/')
    slider = models.ForeignKey(Slider,on_delete=models.CASCADE,related_name="blogs")

#--------------------------------------------End---------------------------------------------------------------------------
#----------------For User's Progress------
class CompleteSubSection(models.Model):
    subsection = models.ForeignKey(SubSection,on_delete=models.CASCADE,related_name="complete_subsections")
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name="complete_subsections")
from . import models
from rest_framework import serializers
import pprint
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer,UserCreateSerializer as BaseUserCreateSerializer

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ["id","username","email","password","first_name","last_name"]

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id","username","email","first_name","last_name"]
class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = get_user_model()
        fields = ["id","username","email","password","first_name","last_name"]

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Student
        fields = '__all__'
    user = SimpleUserSerializer(read_only=True)

    def create(self, validated_data):
        user_id = self.context.get('user_id')
        instance = models.Student.objects.create(user_id=user_id,**validated_data)
        return instance

    



# class TopicSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Topic
#         fields = ["id","title","image",'subcategory',"courses_count"]
#     courses_count = serializers.IntegerField(read_only=True)

# class SubCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.SubCategory
#         fields = ["id","title","image","category","topics_count"]
#     topics_count = serializers.IntegerField(read_only=True)



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ["id","title","image","subcategories_count","subcategories_topics_count"]
    subcategories_count = serializers.IntegerField(read_only=True)
    subcategories_topics_count = serializers.IntegerField(read_only=True)
class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Blog
        fields = '__all__'
class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Video
        fields = '__all__'
class PdfSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pdf
        fields = '__all__'

class SubSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubSection
        fields = ["id","title","video","blog","pdf"]
    video = VideoSerializer()
    blog = BlogSerializer()
    pdf = PdfSerializer()
    

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Section
        fields = ["id","title","subsections"]
    subsections = SubSectionSerializer(many=True)
class EnrollStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnrollStudents
        fields = ["student"]
    student = StudentSerializer()

class SimpleCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ["id","title","desc","price",]
class EnrollCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnrollStudents
        fields = ['course']
    course = SimpleCourseSerializer()
class SimpleEnrollCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnrollStudents
        fields = ['course']
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Enrollment
        fields = ["id","enroll_at","enroll_students"]
    id = serializers.IntegerField(read_only=True)
    enroll_students = SimpleEnrollCourseSerializer(many=True)

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ["id","title","image","desc","price","discount_price","enroll_students_count","ratings_avg","reviews_count","is_enrolled","total_subsections","progress","category","videos","pdfs","blogs","enroll_students","sections"]
    enroll_students = EnrollStudentSerializer(many=True)
    sections = SectionSerializer(many=True)
    enroll_students_count = serializers.IntegerField()
    category = serializers.CharField()
    reviews_count = serializers.IntegerField()
    ratings_avg = serializers.DecimalField(max_digits=2,decimal_places=1)
    total_subsections = serializers.IntegerField()
    progress= serializers.IntegerField()
    videos = serializers.SerializerMethodField(
        method_name="get_videos",
    )
    pdfs = serializers.SerializerMethodField(
        method_name="get_pdfs",
    )
    blogs = serializers.SerializerMethodField(
        method_name="get_blogs",
    )

    progress = serializers.SerializerMethodField(
        method_name="get_progress",
    )

    discount_price = serializers.SerializerMethodField(
        method_name='get_discount_price'
    )
    is_enrolled = serializers.SerializerMethodField(
        method_name='check_is_enrolled'
    )

    def get_videos(self,course:models.Course):
        return course.videos_count
    def get_pdfs(self,course:models.Course):
        return course.pdfs_count
    def get_blogs(self,course:models.Blog):
        return course.blogs_count

    def get_progress(self,course:models.Course):
        total_sections = course.total_subsections
        complete_sections = 0
        try:
            complete_sections = models.CompleteSubSection.objects.filter(
            section__section__course= course.id,
            student_id = models.Student.objects.get(user_id = self.context["user_id"]).id
            ).count()
        except:
            print("Exception getting progress")
        if(total_sections <= 0):
            return 0
        return (complete_sections/total_sections) * 100

    def get_discount_price(self,course:models.Course):
        original_amount = course.price
        discount_amount = 0
        try:
            discount_amount = (course.discount_item.discount.discount_percentage/100) * original_amount
            return  original_amount - discount_amount
        except:
            return 0
    def check_is_enrolled(self,course:models.Course):
        #enroll_students = models.EnrollStudents.objects.prefetch_related('student__user').filter(course_id = course.id)
        try:
            user_list = [enrollment.student.user.id for enrollment in course.enroll_students.all()]
            return self.context.get('user_id') in user_list
        except:
            return False


class DiscountItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DiscountItem
        fields = ["id","course","discount"]
    course = SimpleCourseSerializer()

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Discount
        fields = ["id","title","discount_percentage","discount_items"]
    discount_items = DiscountItemSerializer(many=True)

class MessengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MessengerLink
        fields = '__all__'
class FacebookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FacebookLink
        fields = '__all__'
class YoutubeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.YoutubeLink
        fields = '__all__'
class CourseLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseLink
        fields = ['course']
    course = SimpleCourseSerializer(many=True)
class BlogLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BlogLink
        fields = '__all__'

class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Slider
        fields = ["id","image","created_at","messengerlink","facebooklink","youtube","courselink","blogs"]
    messengerlink = MessengerSerializer()
    facebooklink = FacebookSerializer()
    youtube = YoutubeSerializer()
    courselink = CourseLinkSerializer()
    blogs = BlogLinkSerializer(many=True)


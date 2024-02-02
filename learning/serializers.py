from . import models
from rest_framework import serializers
import pprint
from django.utils import timezone
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer,UserCreateSerializer as BaseUserCreateSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class EmailTokenObtainSerializer(TokenObtainSerializer):
    username_field = User.EMAIL_FIELD

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = self.user_authentication(email=email, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')

                refresh = self.get_token(user)  # Generate refresh token
                data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                return data
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

    def user_authentication(self, email, password):
        user = get_user_model().objects.filter(email=email).first()

        if user and user.check_password(password):
            return user

        return None

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
        fields = ["id","title","image","courses_count"]
    courses_count = serializers.IntegerField(read_only=True)
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
   
    
class DetailCourseSubSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubSection
        fields = ["id","title","video","blog","pdf","completed"]
    video = VideoSerializer()
    blog = BlogSerializer()
    pdf = PdfSerializer()
    completed = serializers.SerializerMethodField(method_name="get_completed")

    def get_completed(self,subsec:models.SubSection):
        student_query = models.Student.objects.filter(user_id = self.context["user_id"])
        if student_query.exists():
            completed_subsection = models.CompleteSubSection.objects.filter(student_id = student_query.first().id,
                                                                     subsection_id = subsec.id,)
            if completed_subsection.exists():
                return True
            else:
                return False
        else:
            return False
    
class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Section
        fields = ["id","title","subsections"]
    subsections = SubSectionSerializer(many=True)
class DetailCourseSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Section
        fields = ["id","title","subsections"]
    subsections = DetailCourseSubSectionSerializer(many=True)
class EnrollStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnrollStudents
        fields = ["student"]
    student = StudentSerializer()

class AdminEnrollStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnrollStudents
        fields = '__all__'

class SimpleCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ["id","title","image"]
    

class AdminGetEnrollStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnrollStudents
        fields = ['student','course','subscribed_count',
                  'subscribed','expiration_date']
    student = StudentSerializer()
    course = SimpleCourseSerializer()


class EnrollCourseSerializer(serializers.ModelSerializer):
        class Meta:
            model = models.Course
            #we have deleted "is_enrolled",
            fields = ["id","title","image","video","desc","price","discount_price","enroll_students_count",
                    "ratings_avg","reviews_count","total_subsections",
                    "subscribe_info",
                    "progress","category","videos","pdfs","blogs",
                    #"video_durations","pdf_durations","blog_durations",
                    "total_durations","enroll_students","sections"]
        enroll_students = EnrollStudentSerializer(many=True)
        sections = DetailCourseSectionSerializer(many=True)
        enroll_students_count = serializers.IntegerField()
        category = serializers.CharField()
        reviews_count = serializers.IntegerField()
        total_durations = serializers.SerializerMethodField(
            method_name="get_total_durations",
        )
        ratings_avg = serializers.SerializerMethodField(
            method_name="get_ratings",
        )
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
        subscribe_info = serializers.SerializerMethodField(method_name="get_subscription_info")
       
        def get_subscription_info(self, course):
            subscribed_course = course.enroll_students.filter(course_id=course.id)
            subscription_info = {
                'expiration_date': None,
                'day_left': None,
                'minute_left': None,
                'is_expired': None
            }
            
            if subscribed_course.exists():
                expiration_date = subscribed_course.first().expiration_date
                subscription_info['expiration_date'] = expiration_date
                
                # Calculate time left
                current_date = timezone.now()
                time_left = expiration_date - current_date
                subscription_info['day_left'] = time_left.days if time_left.days >= 0 else 0
                minutes = time_left.total_seconds() // 60
                subscription_info['minute_left'] = minutes if minutes >= 0 else 0
                #TODO:To change time_left.days to minutes
                subscription_info['is_expired'] = minutes < 0

            return subscription_info
        

        def get_total_durations(self,course:models.Course):
            return (course.video_durations or 0) + \
                    (course.pdf_durations or 0) + \
                    (course.blog_durations or 0)
        
        def get_ratings(self,course:models.Course):
            if(course.ratings_avg):
                return course.ratings_avg
            else:
                return 0.0
            
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
                subsection__section__course= course.id,
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
class OriginalCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = '__all__'
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        #"is_enrolled","progress", we deleted this.
        fields = ["id","title","image",
                  "ratings_avg","reviews_count","total_subsections","enroll_students_count"]
    reviews_count = serializers.IntegerField()
    enroll_students_count = serializers.IntegerField()
    ratings_avg = serializers.SerializerMethodField(
        method_name="get_ratings",
    )

    total_subsections = serializers.IntegerField()
    
    def get_ratings(self,course:models.Course):
        if(course.ratings_avg):
            return course.ratings_avg
        else:
            return 0.0
        
    

class DetailCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        #we have deleted "is_enrolled","progress",
        fields = ["id","title","image","video","desc","price","discount_price","enroll_students_count",
                  "ratings_avg","reviews_count","total_subsections",
                  "category","videos","pdfs","blogs",
                  #"video_durations","pdf_durations","blog_durations",
                  "total_durations","enroll_students","sections"]
    enroll_students = EnrollStudentSerializer(many=True)
    sections = DetailCourseSectionSerializer(many=True)
    enroll_students_count = serializers.IntegerField()
    category = serializers.CharField()
    # video_durations = serializers.FloatField()
    # pdf_durations = serializers.IntegerField()
    # blog_durations = serializers.IntegerField()
    reviews_count = serializers.IntegerField()
    total_durations = serializers.SerializerMethodField(
        method_name="get_total_durations",
    )
    ratings_avg = serializers.SerializerMethodField(
        method_name="get_ratings",
    )
    total_subsections = serializers.IntegerField()
    #progress= serializers.IntegerField()
    videos = serializers.SerializerMethodField(
        method_name="get_videos",
    )
    pdfs = serializers.SerializerMethodField(
        method_name="get_pdfs",
    )
    blogs = serializers.SerializerMethodField(
        method_name="get_blogs",
    )

    """ progress = serializers.SerializerMethodField(
        method_name="get_progress",
    ) """

    discount_price = serializers.SerializerMethodField(
        method_name='get_discount_price'
    )
    """ is_enrolled = serializers.SerializerMethodField(
        method_name='check_is_enrolled'
    ) """

    def get_total_durations(self,course:models.Course):
        return (course.video_durations or 0) + \
                (course.pdf_durations or 0) + \
                (course.blog_durations or 0)
    
    def get_ratings(self,course:models.Course):
        if(course.ratings_avg):
            return course.ratings_avg
        else:
            return 0.0
        
    def get_videos(self,course:models.Course):
        return course.videos_count
    def get_pdfs(self,course:models.Course):
        return course.pdfs_count
    def get_blogs(self,course:models.Blog):
        return course.blogs_count

    """ def get_progress(self,course:models.Course):
        total_sections = course.total_subsections
        complete_sections = 0
        try:
            complete_sections = models.CompleteSubSection.objects.filter(
            subsection__section__course= course.id,
            student_id = models.Student.objects.get(user_id = self.context["user_id"]).id
            ).count()
        except:
            print("Exception getting progress")
        if(total_sections <= 0):
            return 0
        return (complete_sections/total_sections) * 100 """

    def get_discount_price(self,course:models.Course):
        original_amount = course.price
        discount_amount = 0
        try:
            discount_amount = (course.discount_item.discount.discount_percentage/100) * original_amount
            return  original_amount - discount_amount
        except:
            return 0
    """ def check_is_enrolled(self,course:models.Course):
        #enroll_students = models.EnrollStudents.objects.prefetch_related('student__user').filter(course_id = course.id)
        try:
            user_list = [enrollment.student.user.id for enrollment in course.enroll_students.all()]
            return self.context.get('user_id') in user_list
        except:
            return False """


class DiscountItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DiscountItem
        fields = ["id","course","discount"]
    course = SimpleCourseSerializer()

class OriginalDiscountItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DiscountItem
        fields = ["id","course","discount"]

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Discount
        fields = ["id","title","image","discount_percentage","discount_items"]
    discount_items = DiscountItemSerializer(many=True,read_only=True)

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
class OriginalCourseLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseLink
        fields = "__all__"
class BlogLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BlogLink
        fields = '__all__'

class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Slider
        fields = ["id","title","image","created_at","messengerlink","facebooklink","youtube","courselink","blogs"]
    messengerlink = MessengerSerializer()
    facebooklink = FacebookSerializer()
    youtube = YoutubeSerializer()
    courselink = CourseLinkSerializer()
    blogs = BlogLinkSerializer(many=True)

class OriginalSliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Slider
        fields = "__all__"

class CompleteSubSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CompleteSubSection
        fields = ["subsection","student"]
    student = serializers.ReadOnlyField()

class AdminRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rating
        fields = '__all__'
class AdminGetRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rating
        fields = ['course','student','rating']
    course = serializers.SerializerMethodField(method_name='get_course_title')
    student = serializers.SerializerMethodField(method_name='get_student_name')
    def get_course_title(self,rating:models.Rating):
        return rating.course.title
    def get_student_name(self,rating:models.Rating):
        return rating.student.user.first_name + " " + rating.student.user.last_name
class AdminGetReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ['review','course','student','date']
    course = serializers.SerializerMethodField(method_name='get_course_title')
    student = serializers.SerializerMethodField(method_name='get_student_name')
    def get_course_title(self,review:models.Review):
        return review.course.title
    def get_student_name(self,review:models.Review):
        return review.student.user.first_name + " " + review.student.user.last_name
class AdminReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = '__all__'
        
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ["review","course","student","rating","date"]
    student = StudentSerializer(read_only=True)
    rating = serializers.SerializerMethodField(method_name="get_rating",read_only=True)
    def get_rating(self,review:models.Review):
        ratings = models.Rating.objects.filter(course_id=review.course,student_id=review.student.id)
        if(ratings.exists()):
            return ratings.first().rating
        else:
            return 0
    
    def create(self, validated_data):
        student_id = self.context.get('student_id')
        instance = models.Review.objects.create(student_id=student_id,**validated_data)
        return instance
    

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rating
        fields = ["rating","course","student"]
    student = StudentSerializer(read_only=True)
   
    def create(self, validated_data):
        student_id = self.context.get('student_id')
        instance = models.Rating.objects.create(student_id=student_id,**validated_data)
        return instance
class SplashSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Splash
        fields = "__all__"

class UploadSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Section
        fields = '__all__'
class UploadSubSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubSection
        fields = '__all__'
class UploadVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Video
        fields = '__all__'
class UploadPdfSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pdf
        fields = '__all__'
class UploadBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Blog
        fields = '__all__'

class AdminGetStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Student
        fields = ["avatar","membership","points","user","enrolled_courses"]
    user = SimpleUserSerializer(read_only=True)
    enrolled_courses = serializers.SerializerMethodField(method_name="get_enrolled_courses")
    def get_enrolled_courses(self,student:models.Student):
        distinct_courses = models.EnrollStudents.objects.filter(student__id=student.id).values('course').distinct()
        # Count the distinct courses
        unique_course_count = distinct_courses.count()
        return unique_course_count
class AdminUploadStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Student
        fields = '__all__'
    
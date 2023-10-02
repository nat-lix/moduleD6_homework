from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse

class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)

    def update_rating(self):
        postRate = self.post_set.aggregate(Sum('postRating')).get('postRating__sum')
        commentRate = self.authorUser.comment_set.aggregate(Sum('commentRating')).get('commentRating__sum')
        postCommentRate = Comment.objects.filter(commentPost__postAuthor=self).aggregate(Sum('commentRating')).get('commentRating__sum')
        
        if postRate == None:
            postRate = 0
        if commentRate == None:
            commentRate = 0
        if postCommentRate == None:
            postCommentRate = 0

        self.ratingAuthor = postRate*3 + commentRate + postCommentRate

        self.save(update_fields=['ratingAuthor'])

      

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    subscribers = models.ManyToManyField(User, through='CategorySubscriber')

    def __str__(self):
        return self.name

class CategorySubscriber(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

class Post(models.Model):
    postAuthor = models.ForeignKey(Author, on_delete=models.CASCADE)
    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'), 
    )
    categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    dateCreation = models.DateTimeField(auto_now_add=True)
    postCategory = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=128)
    text = models.TextField()
    postRating = models.SmallIntegerField(default=0)

    def like(self):
        self.postRating += 1
        self.save()

    def dislike(self):
        self.postRating += -1
        self.save()

    def preview(self):
        return self.text[0:123] + '...'
    
    def get_absolute_url(self):
        return f'/posts/{self.id}'
    
   
class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    commentRating = models.SmallIntegerField(default=0)

    def like(self):
        self.commentRating += 1
        self.save()

    def dislike(self):
        self.commentRating += -1
        self.save()

    def __str__(self):
        return self.commentUser.username



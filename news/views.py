from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.views import View
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse
from .models import Post, Category, Author
from .filters import PostFilter
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta

class PostList(ListView):
    model = Post
    template_name = 'news/posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 10

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
       context['choices'] = Post.CATEGORY_CHOICES
       context['form'] = PostForm()
       return context
    
    def post(self, request, *args, **kwargs):
       form = self.form_class(request.POST) # создаём новую форму, забиваем в неё данные из POST-запроса
       if form.is_valid(): # если пользователь ввёл всё правильно и нигде не накосячил, то сохраняем новый товар
           form.save()
       return super().get(request, *args, **kwargs)
    
    

class PostDetail(DetailView):
    model = Post
    template_name = 'news/post.html'
    context_object_name = 'post'
    queryset = Post.objects.all()

class Posts(View):
    def get(self, request):

        posts = Post.objects.order_by('-dateCreation')
        p = Paginator(posts, 1)
        posts = p.get_page(request.GET.get('page', 1))

        data = {
        'posts': posts,
        }

        return render(request, 'news/posts.html', data)

class SearchView(ListView):
    model = Post
    template_name = 'news/search.html'
    context_object_name = 'search'
    
    queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context
        
class PostCreate(CreateView, PermissionRequiredMixin):
    template_name = 'news/create_post.html'
    form_class = PostForm
    context_object_name = 'posts'
    permission_required = ('news.add_post', )

    def test_func(self):
        author = Author.objects.get(authorUser_id=self.request.user.id)
        yesterday = timezone.now() - timedelta(days=1)
        post_day = Post.objects.filter(author=author, dateCreation__gt=yesterday).count()
    
        print(post_day)
        if post_day > 3:
            raise PermissionDenied("Вы можете разместить не более 3 постов в день")

        else:
            return redirect('/posts')

class PostUpdateView(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    template_name = 'news/create_post.html'
    form_class = PostForm
    permission_required = ('news.change_post')

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

class PostDeleteView(DeleteView):
   template_name = 'news/delete_post.html'
   queryset = Post.objects.all()
   success_url = reverse_lazy('news:posts')

class CategoryDetail(DetailView):
    model = Category
    template_name = 'news/categories.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(id=self.kwargs['pk'])
        context['subscribers'] = category.subscribers.all()
        return context
    
def subscribe(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.add(request.user.id)
    return HttpResponseRedirect(reverse('news:categories', args=[pk]))

def unsubscribe(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.remove(request.user.id)
    return HttpResponseRedirect(reverse('news:categories', args=[pk]))

    
    


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post
from django.contrib.auth.models import User     
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView,DetailView,CreateView,UpdateView, DeleteView     

from rest_framework import status
from rest_framework import permissions
from .models import Post
from .serializers import PostSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.

posts = [
    {
        'author':"Author 1",
        'title':'Blog Post 1',
        'content': 'First Post Content',
        'date_posted': 'Jan 05 2023'
    },
     {
        'author':"Author 2",
        'title':'Blog Post 2',
        'content': 'Second Post Content',
        'date_posted': 'Jan 06 2023'
    },
]

def home(request):
    # context = {
    #     'posts':posts
    # }
    context = {
        'posts':Post.objects.all()
    }
    return render(request, 'blog/home.html',context)

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 20

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 20
    
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        return Post.objects.filter(author=user).order_by('-date_posted')
    

class PostDetailView(DetailView):
    model = Post

class PostCreateView(LoginRequiredMixin,CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)       

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True

        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()

        if self.request.user == post.author:
            return True

        return False



def about(request):
    return render(request, 'blog/about.html',{'title': 'About'})

class BlogListApiView(APIView):
    # add permission to check if user is authenticated

    permission_classes = [permissions.IsAuthenticated]

    # 1. List All
    def get(self, request, *args, **kwars):
        '''
        List all the blog items for give requested user
        '''

       # post = Post.objects.filter(author = request.user.id)
        post = Post.objects.all()
        serializer = PostSerializer(post, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)

    # 2. Create
    def post(self,request, *args, **kwargs):
        '''
        Create the post with given post data
        '''

        data = {
              'title':request.data('title'),
              'content':request.data('content'),
            
        }

        serializer = PostSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class PostDetailApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        '''
        Helper method to get the object with given post_id and user_id
        '''

        try:
            return Post.objects.get(id=id)
        except Post.DoesNotExist:
            return None

     # 3. Retrieve 
    def get(self,request, id, *args, **kwargs):
        '''
        Retrieve the Post with given Post_id
        '''

        post_instance = self.get_object(id)
        if not post_instance:
            return Response(
                {"res":"Object not found"},
                status = status.HTTP_400_BAD_REQUEST
            )

        serializer = PostSerializer(post_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)



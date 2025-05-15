from django.urls import path
from . import views

app_name = 'app_quote'

urlpatterns = [
    path('', views.main, name='main'),
    path('error/<str:message>', views.error, name='error-page'),

    path('tag/', views.tag, name='tag'),
    path('tag/<str:tag_name>', views.search_by_tag, name='quotes-by-tag'),

    path('quote/', views.quote, name='quote'),
    path('quote/<int:quote_id>/', views.quote_detail, name='quote-detail'),
    path('quote/edit/<int:quote_id>/', views.quote, name='quote-edit'),
    path('quote/delete/<int:quote_id>/', views.quote_delete, name='quote-delete'),

    path('author/', views.author, name='author'),
    path('author/<int:author_id>/', views.author_detail, name='author-detail'),
    path('author/edit/<int:author_id>/', views.author, name='author-edit'),
    path('author/delete/<int:author_id>/', views.author_delete, name='author-delete'),

    path('scrapdata/', views.scrap_data, name='scrap-data'),
]

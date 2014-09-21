from django.conf.urls import patterns, url

from advisor import views
#Career, Search, Home, Category, Category_Index, Institution_Career, Qualification, Institution_Index, Institution

# applies to the character immediately before (that's why you need to use brackets if more than one character)
# + -> 1 or many
# * -> 0 or many
# ? -> 0 or 1
urlpatterns = patterns('',
  url(r'^search/?$', views.search, name='search'),

  url(r'^career/(?P<career_name>\w+(\s+\w+)*)/liked/?$', views.unlike_career, name='unlike_career'),
  url(r'^career/(?P<career_name>\w+(\s+\w+)*)/like/?$', views.like_career, name='like_career'),
  url(r'^career/(?P<career_name>\w+(\s+\w+)*)/(?P<inst_name>\w[\w\s\(\)]*)/?$', views.institution_career, name='institution_career'),
  
  url(r'^career/(?P<career_name>\w+(\s+\w+)*)/?$', views.career, name='career'),
  url(r'^career/?$', views.career_index, name='career_index'),

  url(r'^institution/(?P<inst_name>\w[\w\s\(\)]*)/(?P<qualification_name>\w[\w\s\(\)]*)/liked/?$', views.unlike_qualification, name='unlike_qualification'),
  url(r'^institution/(?P<inst_name>\w[\w\s\(\)]*)/(?P<qualification_name>\w[\w\s\(\)]*)/like/?$', views.like_qualification, name='like_qualification'),

  url(r'^institution/(?P<inst_name>\w[\w\s\(\)]*)/(?P<qualification_name>\w[\w\s\(\)]*)/?$', views.qualification, name='qualification'),
  url(r'^institution/(?P<institution_name>\w[\w\s\(\)]*)/?$', views.institution, name='institution'),
  url(r'^institution/?$', views.institution_index, name='institution_index'),
  url(r'^category/(?P<category_name>\w+(\s+\w+)*)/?$', views.category, name='category'),
  url(r'^category/?$', views.category_index, name='category_index'),
  url(r'^qualification/?$', views.qualification_index, name='qualification_index'),
  

  url(r'^recommend/?$', views.recommend_careers_and_qualifications, name ='recommend_careers_and_qualifications'),

  url(r'^accounts/login/?$', views.login, name ='login'),
  url(r'^accounts/auth/?$', views.auth_view, name ='auth_view'),
  url(r'^accounts/logout/?$', views.logout, name ='logout'),
  url(r'^accounts/loggedin/?$', views.loggedin, name = 'loggedin'),
  url(r'^accounts/register/?$', views.register_user, name = 'register_user'),

  url(r'^', views.home, name='home'),
)
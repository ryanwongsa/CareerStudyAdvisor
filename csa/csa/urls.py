from django.conf.urls import patterns, include, url

from csa import views

from django.contrib import admin
admin.autodiscover()

# Proposed templates
# homepage is search page with category options
# domain.com/career/[career_name] -> career page
# domain.com/category/[category_name] -> list of careers belonging to that category
# domain.com/career/[career_name]/[university_name] -> list of degrees offered at the university that lead to that career
# domain.com/career/[career_name]/[university_name]/[degree_name] -> degree page
# domain.com/?=[search] -> results of search

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'csa.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # !!! csa.views.home ...how this work?
    url(r'^accounts/login/?$', views.login, name ='login'),
    url(r'^accounts/auth/?$', views.auth_view, name ='auth_view'),
    url(r'^accounts/logout/?$', views.logout, name ='logout'),
    url(r'^accounts/loggedin/?$', views.loggedin, name = 'loggedin'),
    url(r'^accounts/invalid/?$', views.invalid_login, name ='invalid_login'),
                       
    url(r'^accounts/register/?$', views.register_user, name = 'register_user'),
    url(r'^accounts/register_success/?$', views.register_success, name = 'register_success'),
                       

                       
    url(r'^admin/?', include(admin.site.urls)),
    url(r'^', include('advisor.urls')),
    #url(r'^career/', include('advisor.urls')),
                       
    

    
)

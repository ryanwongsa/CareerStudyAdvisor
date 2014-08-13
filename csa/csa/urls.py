from django.conf.urls import patterns, include, url

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

    url(r'^admin/?', include(admin.site.urls)),
    url(r'^', include('advisor.urls')),
    #url(r'^career/', include('advisor.urls')),
    
)

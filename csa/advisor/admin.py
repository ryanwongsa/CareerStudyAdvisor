#################################################################################
# Capstone Project - Career Study Advisor 
# By: Kevin Elliott (ellkev004), Ryan Wong (wngrya001) and Zena Kelz (klzzen001)
# 21/07/2014 - 22/09/2014
# This document is to make alterations to admin fields and to integrate the models
# into the admin site
#################################################################################

from django.contrib import admin
from advisor.models import Career, Institution, Category, Qualification,WebsiteLink, Subject, UserProfile
from django.db import models

'''
  All classes below the CommonInfo class inherit from the CommonInfo class
''' 
class CommonInfo(admin.ModelAdmin):
	search_fields=['name']
	ordering=['name']
'''
  class Media:
    from django.conf import settings
''' 

'''
  Adds a list filter to admin
''' 
class WebsiteLinkAdmin(CommonInfo):
	list_filter = ['link_to']

'''
  Adds a list filter to admin and the available to selected field in admin
'''		
class CareerAdmin(CommonInfo):
	list_filter = ['categories']
	filter_horizontal = ['categories','qualifications','companies','subjects']

'''
  Adds the available to selected field in admin
'''			
class InstitutionAdmin(CommonInfo):
	filter_horizontal = ['websites','handbooks','contact_details_websites','faculty_websites']

class CatagoryAdmin(CommonInfo):
	verbose_name_plural = "Catagories"

'''
  Adds a list filter to admin and the available to selected field in admin
'''	
class QualificationAdmin(CommonInfo):
	list_filter = ['institution']
	filter_horizontal = ['qualifications_websites','subjects']

class SubjectAdmin(CommonInfo):
	verbose_name_plural = "Subjects"

'''
  Adds a available to selected field in admin
'''	
class UserProfileAdmin(CommonInfo):
    list_filter = ['likes']
    list_filter = ['interests']
    list_filter = ['subjects']
    filter_horizontal = ['likes','interests','subjects']

'''
  Integration of models into the admin site
'''	
admin.site.register(Career,CareerAdmin)
admin.site.register(Institution,InstitutionAdmin)
admin.site.register(Category,CatagoryAdmin)
admin.site.register(Qualification,QualificationAdmin)
admin.site.register(WebsiteLink,WebsiteLinkAdmin)
admin.site.register(Subject,SubjectAdmin)
admin.site.register(UserProfile,UserProfileAdmin)
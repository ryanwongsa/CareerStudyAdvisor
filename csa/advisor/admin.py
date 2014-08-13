from django.contrib import admin
from advisor.models import Career, Institution, Category, Qualification,WebsiteLink
from django.db import models

#All classes below the CommonInfo class inherit from the CommonInfo class
class CommonInfo(admin.ModelAdmin):
	search_fields=['name']
	ordering=['name']

class WebsiteLinkAdmin(CommonInfo):
	list_filter = ['link_to']
		
class CareerAdmin(CommonInfo):
	list_filter = ['categories']
	filter_horizontal = ['categories','qualifications','companies']
		
class InstitutionAdmin(CommonInfo):
	filter_horizontal = ['websites','handbooks','contact_details_websites','faculty_websites']
	
class CatagoryAdmin(CommonInfo):
	verbose_name_plural = "Catagories"

class QualificationAdmin(CommonInfo):
	list_filter = ['institution']
	filter_horizontal = ['qualifications_websites']

admin.site.register(Career,CareerAdmin)
admin.site.register(Institution,InstitutionAdmin)
admin.site.register(Category,CatagoryAdmin)
admin.site.register(Qualification,QualificationAdmin)
admin.site.register(WebsiteLink,WebsiteLinkAdmin)
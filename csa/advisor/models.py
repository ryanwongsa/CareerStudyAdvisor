#################################################################################
# Capstone Project - Career Study Advisor 
# By: Kevin Elliott (ellkev004), Ryan Wong (wngrya001) and Zena Kelz (klzzen001)
# 21/07/2014 - 22/09/2014
#################################################################################

from django.db import models

################################################################################
# The catagory model stores the catagories which careers are assigned to. 
################################################################################

class Category (models.Model):
  name = models.CharField(primary_key=True,max_length=50)

  class Meta:
    verbose_name = "Category"
    verbose_name_plural = "Categories"

  def __unicode__(self):
    return self.name

################################################################################
# The WebsiteLink model is used to store all the links to external websites. 
################################################################################

class WebsiteLink (models.Model):
  name = models.CharField(primary_key=True,max_length=150)
  site_url = models.TextField()
  COMPLINK = 'Company'
  QUALINK = 'Qualification'
  INSTLINK = 'Institution'
  HANDLINK = 'Handbook'
  FACLINK = 'Faculty Website'
  CONLINK = 'Contact'
  LINK_TO_CHOICES = (
        (COMPLINK, 'Company'),
        (QUALINK, 'Qualification'),
        (INSTLINK, 'Institution'),
        (HANDLINK, 'Handbook'),
        (FACLINK, 'Faculty Website'),
        (CONLINK,'Contact')
    )
  link_to = models.CharField(max_length=15,
                                      choices=LINK_TO_CHOICES,
                                      default=INSTLINK)
  class Meta:
    verbose_name = "WebsiteLink"
    verbose_name_plural = "WebsiteLinks"

  def __unicode__(self):
    return self.name

################################################################################
# The Institution model is used to store information about educational 
# institutions  
################################################################################

class Institution (models.Model):
  name = models.CharField(primary_key=True,max_length=50)
  description = models.TextField()
  websites = models.ManyToManyField(WebsiteLink,blank=True, limit_choices_to={'link_to': 'Institution'}, related_name='institutions_website')
  handbooks = models.ManyToManyField(WebsiteLink,blank=True, limit_choices_to={'link_to': 'Handbook'},related_name='institutions_handbooks')
  faculty_websites = models.ManyToManyField(WebsiteLink,blank=True, limit_choices_to={'link_to': 'Faculty Website'},related_name='institutions_faculties')
  contact_details_websites = models.ManyToManyField(WebsiteLink,blank=True, limit_choices_to={'link_to': 'Contact'},related_name='institutions_contact_info')
  # qualifications

  class Meta:
    verbose_name = "Institution"
    verbose_name_plural = "Institutions"

  def __unicode__(self):
    return self.name
    
################################################################################
# The Subject model is used to store information about all subjects used within
# the website
################################################################################

class Subject (models.Model):
    name = models.CharField(primary_key=True,max_length=50)
    
    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
    
    def __unicode__(self):
        return self.name


################################################################################
# The Qualification model is used to store information about the qualifications 
# used within the website
################################################################################

class Qualification (models.Model):
  institution = models.ForeignKey(Institution)
  name = models.CharField(max_length=50)
  short_description = models.TextField()
  long_description = models.TextField()
  #courses = models.TextField(blank=True)
  subjects = models.ManyToManyField(Subject)
  qualifications_websites = models.ManyToManyField(WebsiteLink,blank=True, limit_choices_to={'link_to': 'Qualification'})

  class Meta:
    verbose_name = "Qualification"
    verbose_name_plural = "Qualifications"

  def __unicode__(self):
    return u'{} from {}'.format(self.name,self.institution)


################################################################################
# The Career model is used to store information about the careers 
# used within the website
################################################################################

class Career (models.Model):
  name = models.CharField(primary_key=True,max_length=50)
  short_description = models.TextField()
  description = models.TextField() 
  categories = models.ManyToManyField(Category)
  subjects = models.ManyToManyField(Subject)
  qualifications = models.ManyToManyField(Qualification)
  companies = models.ManyToManyField(WebsiteLink,blank=True, limit_choices_to={'link_to': 'Company'})

  class Meta:
    verbose_name = "Career"
    verbose_name_plural = "Careers"

  def __unicode__(self):
    return self.name


################################################################################
# The UserProfile model is used to store user profile information used within
# the website
################################################################################

class UserProfile (models.Model):
    name = models.CharField(primary_key=True,max_length=50)  # username
    likes = models.ManyToManyField(Career,blank=True) # careers
    likes_qualifications = models.ManyToManyField(Qualification,blank=True)
    interests = models.ManyToManyField(Category,blank=True)
    subjects = models.ManyToManyField(Subject,blank=True)
    
    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"
    
    def __unicode__(self):
        return self.name


################################################################################


from django.db import models

############################################

class Category (models.Model):
  name = models.CharField(max_length=50)

  class Meta:
    verbose_name = "Category"
    verbose_name_plural = "Categories"

  def __unicode__(self):
    return self.name

############################################

class WebsiteLink (models.Model):
  name = models.CharField(max_length=150)
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

############################################

class Institution (models.Model):
  name = models.CharField(max_length=50)
  description = models.TextField()
  websites = models.ManyToManyField(WebsiteLink, limit_choices_to={'link_to': 'Institution'}, related_name='institutions_website')
  handbooks = models.ManyToManyField(WebsiteLink, limit_choices_to={'link_to': 'Handbook'},related_name='institutions_handbooks')
  faculty_websites = models.ManyToManyField(WebsiteLink, limit_choices_to={'link_to': 'Faculty Website'},related_name='institutions_faculties')
  contact_details_websites = models.ManyToManyField(WebsiteLink, limit_choices_to={'link_to': 'Contact'},related_name='institutions_contact_info')
  # qualifications

  class Meta:
    verbose_name = "Institution"
    verbose_name_plural = "Institutions"

  def __unicode__(self):
    return self.name
    
############################################

class Subject (models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
    
    def __unicode__(self):
        return self.name


############################################

class Qualification (models.Model):
  institution = models.ForeignKey(Institution)
  name = models.CharField(max_length=50)
  short_description = models.TextField()
  long_description = models.TextField()
  courses = models.TextField()
  subjects = models.ManyToManyField(Subject)
  qualifications_websites = models.ManyToManyField(WebsiteLink, limit_choices_to={'link_to': 'Qualification'})

  class Meta:
    verbose_name = "Qualification"
    verbose_name_plural = "Qualifications"

  def __unicode__(self):
    return u'{} from {}'.format(self.name,self.institution)


############################################

class Career (models.Model):
  name = models.CharField(max_length=50)
  description = models.TextField() # [id1,id2,...]
  categories = models.ManyToManyField(Category)
  subjects = models.ManyToManyField(Subject)
  qualifications = models.ManyToManyField(Qualification)
  companies = models.ManyToManyField(WebsiteLink, limit_choices_to={'link_to': 'Company'})

  class Meta:
    verbose_name = "Career"
    verbose_name_plural = "Careers"

  def __unicode__(self):
    return self.name

############################################

class Subject (models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
    
    def __unicode__(self):
        return self.name

############################################

class UserProfile (models.Model):
    name = models.CharField(primary_key=True,max_length=50)  # actually is a username
    likes = models.ManyToManyField(Career)
    interests = models.ManyToManyField(Category)
    subjects = models.ManyToManyField(Subject)
    
    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"
    
    def __unicode__(self):
        return self.name


############################################


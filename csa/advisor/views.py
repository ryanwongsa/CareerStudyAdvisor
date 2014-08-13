from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic.base import View

from advisor.models import Career, Qualification, Institution, Category

class Career_Index(View):
  def get(self, request):
    list_of_careers = []
    for career in Career.objects.all():
      list_of_careers.append(career)
    
    careers = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
      letter_list = filter(lambda x: x.name.upper().startswith(letter), list_of_careers)
      if len(letter_list) > 0:
        letter_list.sort(key=lambda x: x.name)
        careers.append(letter_list)

    context = {"careers": careers}
    return render(request, "advisor/career_index.html", context)


def career(request, career_name):
  list_of_qualifications = []
  list_of_categories = []
  list_of_institutions = []
  list_of_companies = []
  
  c = Career.objects.get(name__iexact=career_name) #.get()  not  .filter()

  for qualification in c.qualifications.all(): #need .all() otherwise not iterable
    list_of_qualifications.append(qualification)
  for qualification in list_of_qualifications:
    if qualification.institution.name not in list_of_institutions:
      list_of_institutions.append(qualification.institution.name)
  for category in c.categories.all():
    list_of_categories.append(category)  
  for company in c.companies.all(): #need .all() otherwise not iterable
    list_of_companies.append(company)

### added
# for category in c.categories.all():
#list_of_similar_careers.append(category)
  list_of_similar_careers = []
  list_of_careers = []
  for career in Career.objects.all():
    if career.name != c.name:
      list_of_careers.append(career)
# list_of_careers is all of the careers
# list_of_categories is only for the categories for this career
# list_of_temp_categories is the categories that the other careers have


  for career in list_of_careers:
    list_of_temp_categories=[]
    for category in career.categories.all():
      list_of_temp_categories.append(category)
    
    for temp_career_category in list_of_temp_categories:
      if temp_career_category in list_of_categories:
        if career not in list_of_similar_careers:
          list_of_similar_careers.append(career)
##

  #these are the names of the variables in the template
  context = {"career": c, "institutions": list_of_institutions, "categories": list_of_categories, "companies": list_of_companies,"similarCareers": list_of_similar_careers}
  return render (request, "advisor/career.html", context)

class Search(View):
  def get(self, request):
    # request.GET is a dictionary where the query variable is the value in a key-value pair (i.e. it is the actual search text)
    query = request.GET["query"]
    list_of_careers = Career.objects.filter(name__icontains=query).all()
    list_of_institutions = Institution.objects.filter(name__icontains=query).all()
    list_of_qualifications = Qualification.objects.filter(name__icontains=query).all()
    list_of_categories = Category.objects.filter(name__icontains=query).all()
    #return HttpResponse(list_of_careers)
    
    list_of_careers_filtered = self.filter_list(list_of_careers)
    list_of_instituions_filtered = self.filter_list(list_of_institutions)
    list_of_qualifications_filtered = self.filter_list(list_of_qualifications)
    list_of_categories_filtered = self.filter_list(list_of_categories)

    context = {"careers": list_of_careers_filtered, "institutions": list_of_instituions_filtered, "qualifications": list_of_qualifications_filtered, "categories": list_of_categories_filtered, "search_term": query}
    return render (request, "advisor/search.html", context)

  def filter_list(self, temp_list):
    filtered_list = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
      letter_list = filter(lambda x: x.name.upper().startswith(letter), temp_list)
      if len(letter_list) > 0:
        letter_list.sort(key=lambda x: x.name)
        filtered_list.append(letter_list)
    return filtered_list

def qualification_index(request):
  list_of_qualifications = []
  for qualifications in Qualification.objects.all():
    list_of_qualifications.append(qualifications)
  qualifications = []
  for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    letter_list = filter(lambda x: x.name.upper().startswith(letter), list_of_qualifications)
    if len(letter_list) > 0:
      letter_list.sort(key=lambda x: x.name)
      qualifications.append(letter_list)
    
  context = {"qualifications": qualifications}
  return render (request, "advisor/qualification_index.html", context)

def home(request):
  categories = Category.objects.all()
  list_of_suggested_careers=[]
  for career in Career.objects.all():
          list_of_suggested_careers.append(career)
  context = {"categories": categories, "list_of_suggested_careers": list_of_suggested_careers }
  return render (request, "advisor/home.html", context)

def category(request, category_name):
  list_of_careers = []
  for career in Career.objects.all():
    if career.categories.filter(name__iexact=category_name).count() > 0:
      list_of_careers.append(career)

  careers = []
  for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        letter_list = filter(lambda x: x.name.upper().startswith(letter), list_of_careers)
        if len(letter_list) > 0:
            letter_list.sort()
            careers.append(letter_list)
  context = {"careers": careers, "category": category_name}
  return render (request, "advisor/category.html", context)

def category_index(request):
    list_of_categories = []
    for category in Category.objects.all():
        list_of_categories.append(category)
    categories = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        letter_list = filter(lambda x: x.name.upper().startswith(letter), list_of_categories)
        if len(letter_list) > 0:
            letter_list.sort(key=lambda x: x.name)
            categories.append(letter_list)
    
    context = {"categories": categories}
    return render (request, "advisor/category_index.html", context)

def institution_career(request, career_name, inst_name):
  
  list_of_qualifications = []
  list_of_qualifications_at_inst = []
  
  c = Career.objects.get(name__iexact=career_name) 

  for qualification in c.qualifications.all(): 
    list_of_qualifications.append(qualification)
  for qualification in list_of_qualifications:
    if qualification.institution.name == inst_name:
      list_of_qualifications_at_inst.append(qualification)
  

  context = {"institution": inst_name, "career": career_name, "qualifications": list_of_qualifications_at_inst}
  return render (request, "advisor/institution_career.html", context)

def qualification(request, qualification_name, inst_name):
  #return HttpResponse(inst_name + " " + qualification_name)
  list_of_qualifications_with_name = Qualification.objects.filter(name__iexact=qualification_name).all()
  #return HttpResponse(list_of_qualification_with_name)
  for qual in list_of_qualifications_with_name:
    if qual.institution.name == inst_name:
      q = qual # should only be one qualification that meets this criteria


  careers = Career.objects.all()
  list_of_careers_from_qualification = []
  list_of_websites = []

  for career in careers:
    if q in career.qualifications.all():
      list_of_careers_from_qualification.append(career)
    #for qualification in career.qualifications.all():
     # if qualification.name == q.name and qualification.institution == q.institution:
      #  list_of_careers_from_qualification.append(career)

  for web in q.qualifications_websites.all():
      list_of_websites.append(web)


  context = {"qualification": q, "careers": list_of_careers_from_qualification, "websites": list_of_websites}
  #return HttpResponse(len(list_of_careers_from_qualification))
  return render (request, "advisor/qualification.html", context)

def institution_index(request):
    list_of_institutions = []
    for institution in Institution.objects.all():
        list_of_institutions.append(institution)
    
    institution = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        letter_list = filter(lambda x: x.name.upper().startswith(letter), list_of_institutions)
        if len(letter_list) > 0:
            letter_list.sort(key=lambda x: x.name)
            institution.append(letter_list)
    
    context = {"institution": institution}
    return render(request, "advisor/institution_index.html", context)

#exact institution
def institution(request, institution_name):
    
    i = Institution.objects.get(name__iexact=institution_name) #.get()  not  .filter()
    
    
    list_of_qualifications=[]
    list_of_handbooks= []
    list_of_websites= []
    list_of_faculties = []
    list_of_contacts = []    
    
    for qualification in Qualification.objects.all():
        #   return HttpResponse(qualification.institution.name == institution_name)
        if qualification.institution.name == institution_name:
            list_of_qualifications.append(qualification.name)

    for handbook in i.handbooks.all():
      list_of_handbooks.append(handbook)

    for contact in i.contact_details_websites.all():
      list_of_contacts.append(contact)

    for faculty in i.faculty_websites.all():
      list_of_faculties.append(faculty)

    for web in i.websites.all():
      list_of_websites.append(web)

    
    #these are the names of the variables in the template
    context = {"institution": i, "qualifications": list_of_qualifications,"handbooks": list_of_handbooks,"websites": list_of_websites,"contactWebsites": list_of_contacts,"facultyWebsites": list_of_faculties}
    return render (request, "advisor/institution.html", context)



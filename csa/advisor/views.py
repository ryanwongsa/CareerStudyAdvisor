from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.views.generic.base import View
from django.contrib import auth
from forms import UserProfileForm
from forms import MyRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

from advisor.models import Career, Qualification, Institution, Category, Subject, UserProfile

def like_career (request, career_name):
  user = UserProfile.objects.get(name=request.user.username)
  career = Career.objects.get(name__iexact=career_name)

  if career not in user.likes.all():
    user.likes.add(career)

  return redirect ("advisor.views.career", career_name=career.name)

def unlike_career (request, career_name):
  user = UserProfile.objects.get(name=request.user.username)
  career = Career.objects.get(name__iexact=career_name)

  if career in user.likes.all():
    user.likes.remove(career)

  return redirect ("advisor.views.career", career_name=career.name)


def get_recommended_careers (user):
  '''
  All careers are stored in a 2D list of the form [[Career, score] ...], with score initially set to 0 for each career.
  This list contains the final list of scores for each career which will be used to recommend careers to the user.
  '''
  career_score_all = []
  for career in Career.objects.all():
    career_score_all.append([career, 0])


  '''
  All careers that the user has liked will have their scores increased by 4.
  '''
  careers_liked = user.likes.all()

  careers_liked_names = []
  for career in careers_liked:
    careers_liked_names.append(career.name)

  for pair in career_score_all:
    if pair[0].name in careers_liked_names:
      pair[1] = pair[1] + 4


  '''
  All careers that share qualifications with the careers the user has liked will have their scores increased by 2 for each shared qualification. 
  '''
  qualifications_for_liked_careers = [] 
  for career in careers_liked:
    for qualification in career.qualifications.all():
      qualifications_for_liked_careers.append(qualification.name)

  # all qualifications for all careers liked by the user
  qualifications_names_for_liked_careers_no_duplicates = list(set(qualifications_for_liked_careers))

  for pair in career_score_all:
    # skip the career if it is liked by the user. If this is not done, all liked careers will defaultly get 6 score for being liked instead of 4
    if pair[0].name in careers_liked_names:
      continue
    
    qualifications_names = []
    for qualification in pair[0].qualifications.all():
      qualifications_names.append(qualification.name)
    
    # all qualifications for current career
    qualifications_names_no_duplicates = list(set(qualifications_names))
    
    # for all qualifications for the current career, if the qualification is one that links to a career liked by the user -> add 2 to current career score
    for qualification_name in qualifications_names_no_duplicates:
      if qualification_name in qualifications_names_for_liked_careers_no_duplicates:
        pair[1] = pair[1] + 2


  '''
  All careers that share linked subjects with the the user will have their scores increased by 2 for each shared subject.
  '''
  subjects_selected = user.subjects.all()
  
  subjects_selected_names = []
  for subject in subjects_selected:
    subjects_selected_names.append(subject.name)
  
  for pair in career_score_all:
    for subject in pair[0].subjects.all():
      if subject.name in subjects_selected_names:
        pair[1] = pair[1] + 2


  '''
  All careers that share categories with the user's selected interests will have their scores increased by 3 for each interest.
  '''
  interests_selected = user.interests.all(); #in the context of a user's profile: categories are presented to the user as interests
  
  interests_selected_names = []
  for interest in interests_selected:
    interests_selected_names.append(interest.name)

  for pair in career_score_all:
    for category in pair[0].categories.all():
      if category.name in interests_selected_names:
        pair[1] = pair[1] + 3


  

  '''
  #return HttpResponse (user.subjects.all())
  careers_matching_subject_with_duplicates = []
  for subject in user.subjects.all():
    for career in Career.objects.all():
      if (subject in career.subjects.all()):
        careers_matching_subject_with_duplicates.append(career.name);

  #return HttpResponse (careers_matching_subject_with_duplicates)

  careers_matching_subject = list(set(careers_matching_subject_with_duplicates))
  context = {"full_name": user.name, "career_names": careers_matching_subject}
  '''

  #return render(request, "advisor/display_user_info.html", {"career_score_all": career_score_all, "user": user})
  
  career_score_all = sorted(career_score_all, key=lambda x:x[1], reverse=True) # sorts the 2D list on the second element of each list-element 

  return career_score_all

def recommend_careers (request):
  user = UserProfile(name=request.user.username)
  #return HttpResponse("hello")

  careers_recommended_all = get_recommended_careers(user)

  #return HttpResponse(careers_recommended_all)

  careers_recommended_top = careers_recommended_all[0:min(5,len(careers_recommended_all))]

  context = {"career_score_all": careers_recommended_all, "career_score_top": careers_recommended_top, "user":user}
  #return HttpResponse(careers_recommended_all)
  return render (request, "advisor/display_user_info.html", context)

def login(request):
  
    if request.user.is_authenticated():
        user_name = UserProfile(name=request.user.username)
        #form = UserProfileForm(initial={'interest': '', 'likes': ''})
        if request.POST:
            form = UserProfileForm(request.POST, instance=user_name)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/')
        else:
            form = UserProfileForm(instance=user_name)
    
        args = {}
        args.update(csrf(request))
    
        args['form'] = UserProfileForm()
        print args
        context = {"full_name": request.user.username, "args" :args}
        return HttpResponseRedirect("", context) #was /accounts/loggedin
    else:
        c={}
        
        c.update(csrf(request))
        
        context = {"c": c}
        return render(request, "login.html", context)
    

def auth_view(request):
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    user = auth.authenticate(username= username,password = password)
    
    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/')# was /accounts/loggedin
    else:
        context = {"invalid": True}
        return render(request, 'login.html', context)
#return HttpResponseRedirect('/accounts/login')# was /accounts/invalid!!!!


@login_required     # to access this page the user needs to be loggedin
def loggedin(request):
    user_name = UserProfile(name=request.user.username)
    #
    if request.POST:
        form = UserProfileForm(request.POST, instance=user_name)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = UserProfileForm(instance=user_name)
    
    args = {}
    args.update(csrf(request))

    list_of_categories = []
    list_of_subjects = []
    list_of_likes = []

    '''
    for user in UserProfile.objects.all():
        username = request.user.username
        userFromP = user
        #return HttpResponse(username == userFromP.pk);  #add pk if from models
        if username == userFromP.pk:
            return HttpResponse(UserProfile.objects.interests.all());
            for interests in UserProfile.objects.interests():
                return HttpResponse(username == userFromP.pk);
            #for user in UserProfile.objects.all():
        # if request.user.username == name
        #     for interests in
            #       list_of_categories.append(category)
    '''
    try: #if the user has updated their profile
        up = UserProfile.objects.get(name__iexact=request.user.username) #.get()  not  .filter()
    #return HttpResponse(up)

        for category in up.interests.all(): #need .all() otherwise not iterable
            list_of_categories.append(category)

        for subject in up.subjects.all(): #need .all() otherwise not iterable
            list_of_subjects.append(subject)

        for like in up.likes.all(): #need .all() otherwise not iterable
            list_of_likes.append(like)

        args['form'] = UserProfileForm(initial={"name":"ac","interests": list_of_categories,"subjects": list_of_subjects,"likes": list_of_likes}) # do not need likes here
    #Category.objects.all().values_list('id',flat=True)
        print args
        context = {"full_name": request.user.username, "args" :args,"likes":list_of_likes}
        return render(request, "loggedin.html", context)
    except:
        args['form'] = UserProfileForm() 
        print args
        context = {"full_name": request.user.username, "args" :args,"likes":list_of_likes}
        return render(request, "loggedin.html", context)
        pass

def invalid_login(request):
    return render(request, "invalid_login.html")


def logout(request):
    auth.logout(request)
    return render(request, "logout.html")

def register_user(request):
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            #autologin after register here
            new_user = form.save()
            new_user = authenticate(username=request.POST['username'],
                                        password=request.POST['password1'])
            auth.login(request, new_user)
            userprofile = UserProfile(name=request.POST['username'])
            userprofile.save()
            return HttpResponseRedirect('/accounts/loggedin')
        else:
            args = {}
            args.update(csrf(request))
    
            args['form'] = MyRegistrationForm()
            context={"invalid": True,"args":args}
            return render(request, 'register.html', context)

    args = {}
    args.update(csrf(request))
    
    args['form'] = MyRegistrationForm()
    context={"invalid": False,"args":args}
   
    return render(request, "register.html", context)

def register_success(request):
    return render(request, "register_success.html")


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

  user = UserProfile.objects.get(name=request.user.username)
  c = Career.objects.get(name__iexact=career_name)

  '''
    Uses a POST request to update the database (with the user's like or unlike) without going to another URL
  '''
  if request.method == "POST":
    if request.POST['action'] == "like":
      if c not in user.likes.all():
        user.likes.add(c)
      return HttpResponse("success") #actual text doesn't matter as the ajax call is not requesting information
    elif request.POST['action'] == "unlike":
      if c in user.likes.all():
        user.likes.remove(c)
      return HttpResponse("success")
    else:
      raise Http404

  
  user_liked_careers_names = []
  for career in user.likes.all():
    user_liked_careers_names.append(career.name)

  list_of_qualifications = []
  list_of_categories = []
  list_of_institutions = []
  list_of_companies = []
  
  career_liked = False
  if c.name in user_liked_careers_names:
    career_liked = True

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
  context = {"career": c, "institutions": list_of_institutions, "categories": list_of_categories, "companies": list_of_companies,"similarCareers": list_of_similar_careers, "career_liked": career_liked}
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
  user = UserProfile(name=request.user.username)

  categories = Category.objects.all()
  list_of_careers=[]
  list_of_suggested_careers=[]
  for career in Career.objects.all():
    list_of_careers.append(career)
    
  for suggested_careers in list_of_careers:
    list_of_suggested_careers.append(suggested_careers)
  
  '''
  for suggested_careers in list_of_careers:
    list_of_suggested_careers.append(suggested_careers)
  '''
  careers_recommended_all = get_recommended_careers(user)

  #return HttpResponse(careers_recommended_all)

  careers_recommended_top = careers_recommended_all[0:min(5,len(careers_recommended_all))]

  context = {"categories": categories, "list_of_suggested_careers": careers_recommended_top}
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
  list_of_subjects = []

  for career in careers:
    if q in career.qualifications.all():
      list_of_careers_from_qualification.append(career)
    #for qualification in career.qualifications.all():
     # if qualification.name == q.name and qualification.institution == q.institution:
      #  list_of_careers_from_qualification.append(career)

  for web in q.qualifications_websites.all():
      list_of_websites.append(web)

  '''
  All subjects belonging to a particular qualification will be added to a list_of_subjects list.
  This list subjects is then passed to qualification.html and used to display the subjects for 
  a particular qualification on the qualifcations page.
  '''    
  for sub in q.subjects.all():
      list_of_subjects.append(sub)

  '''
   The code below produces two lists to compare the subjects that a user has taken to a list of
   subjects required to obtain the qualification. The system then displays a list of subject
   requirements that have been met and a list of subjects that the user hasn't taken
   (and that are required).
  '''
  list_of_user_subjects = []
  user = UserProfile(name=request.user.username)

  for sub in user.subjects.all():
      list_of_user_subjects.append(sub.name)

  matched_user_subjects = []
  extra_subjects_needed = []
  
  for sub in list_of_subjects:
    matched = False
    for usersub in list_of_user_subjects:
      if sub.name == usersub:
        matched = True
        matched_user_subjects.append(sub)
        
    if matched == False:
       extra_subjects_needed.append(sub)

  context = {"qualification": q, "careers": list_of_careers_from_qualification, "websites": list_of_websites, "subjects": list_of_subjects,"matched_subjects": matched_user_subjects, "extra_subjects_needed": extra_subjects_needed}
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




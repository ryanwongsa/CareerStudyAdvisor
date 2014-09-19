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

def like_qualification (request, qualification_name, inst_name):
  list_of_qualifications_with_name = Qualification.objects.filter(name__iexact=qualification_name).all()
  for qual in list_of_qualifications_with_name:
    if qual.institution.name == inst_name:
      q = qual # should only be one qualification that meets this criteria

  user = UserProfile.objects.get(name=request.user.username)

  if q not in user.likes_qualifications.all():
    user.likes_qualifications.add(qualifcation)

  return redirect ("advisor.views.qualification", qualification_name=q.name, inst_name=q.institution)

def unlike_qualification (request, qualification_name, inst_name):
  list_of_qualifications_with_name = Qualification.objects.filter(name__iexact=qualification_name).all()
  for qual in list_of_qualifications_with_name:
    if qual.institution.name == inst_name:
      q = qual # should only be one qualification that meets this criteria

  user = UserProfile.objects.get(name=request.user.username)

  if q in user.likes_qualifications.all():
    user.likes_qualifications.remove(qualification)

  return redirect ("advisor.views.qualification", qualification_name=q.name, inst_name=q.institution)

def get_recommended_qualifications (user):
  qual_score_all = []
  for qual in Qualification.objects.all():
    qual_score_all.append([qual.id, ""]) # qualifications referenced by their id as neither their name or their institution are unique

  ''' Qualification liked -> +2
  '''
  qual_liked = user.likes_qualifications.all()

  qual_liked_ids = []
  for qual in qual_liked:
    qual_liked_ids.append(qual.id)

  for pair in qual_score_all:
    if pair[0] in qual_liked_ids:
      pair[1] = pair[1] + "+2[liked qual]"


  ''' for each shared subject between the qualification and the current user's profile -> +1
  '''
  subjects_selected = user.subjects.all() #subjects selected by user (for their profile)  

  subjects_selected_names = []
  for subject in subjects_selected:
    subjects_selected_names.append(subject.name)

  for pair in qual_score_all:
    qual = Qualification.objects.get(id=pair[0])
    qual_subjects = qual.subjects.all()
    qual_subjects_names = []
    for subject in qual_subjects:
      qual_subjects_names.append(subject.name)
    for subject_name in qual_subjects_names:
      if subject_name in subjects_selected_names:
        pair[1] = pair[1] + "+1[share subject]"


  ''' if another user shares 5 subjects with the current user, then each qualification that the other user likes will get +1
  '''
  users_all = UserProfile.objects.all()
  
  users_subjects_qual_likes = [] # [[user1_subjects, user1_qual_likes], [user2_subjects, user2_qual_likes], ...] for all users who share 5 or more subjects with current user
  for u in users_all:
    if u.name == user.name:
      continue
    users_subjects_qual_likes.append([u.subjects.all(),u.likes_qualifications.all()])

  users_subjects_qual_likes_names_ids = []
  for pair in users_subjects_qual_likes:
    subject_names = []
    qual_liked_ids = []
    for subject in pair[0]:
      subject_names.append(subject.name)
    for qual in pair[1]:
      qual_liked_ids.append(qual.id)
    users_subjects_qual_likes_names_ids.append([subject_names, qual_liked_ids])

  qual_id_score = {}
  for pair in users_subjects_qual_likes_names_ids:
    subjects_matched = filter (lambda subject_name: subject_name in subjects_selected_names, pair[0])
    if len(subjects_matched) >= 5:   # only care about liked qualifications if the other user shares >=5 subjects with current user
      for qual_id in pair[1]:
        if (qual_id_score.has_key(qual_id)):
          qual_id_score[qual_id] = qual_id_score[qual_id] + 1 # add one score if qual already in dictionary
        else:
          qual_id_score[qual_id] = 1 # create entry in dictionary for qualification if doesn't already exist

  for pair in qual_score_all:
    if qual_id_score.has_key(pair[0]):
      if qual_id_score[pair[0]] > 4:
        pair[1] = pair[1] + "+4[other users]"
      else:
        pair[1] = pair[1] + "+" + str(qual_id_score[pair[0]]) + "[other users:"+ Qualification.objects.get(id=pair[0]).name+"]"


  qual_score_all = sorted(qual_score_all, key=lambda x:x[1], reverse=True) # sorts the 2D list on the second element of each list-element 

  return qual_score_all


def get_recommended_careers (user):
  '''
    All careers are stored in a 2D list of the form [[Career, score] ...], with score initially set to 0 for each career.
    This list contains the final list of scores for each career which will be used to recommend careers to the user.
  '''
  career_score_all = []
  for career in Career.objects.all():
    career_score_all.append([career, ""])


  '''
    All careers that the user has liked will have their scores increased by 4.
  '''
  careers_liked = user.likes.all()

  careers_liked_names = []
  for career in careers_liked:
    careers_liked_names.append(career.name)

  for pair in career_score_all:
    if pair[0].name in careers_liked_names:
      pair[1] = pair[1] + "4[user like]+"


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
        pair[1] = pair[1] + "2[qual]+"


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
        pair[1] = pair[1] + "2[shared subject]+"


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
        pair[1] = pair[1] + "3[shared category]+"


  '''
    All careers which are liked by users who share 4 or more interests with the current user will have their scores:
      1. increased by 2 if the career is in any of the overlapping interests (categories)
      2. increased by 1 (for all other careers that have been liked)
    A career can get a maximum of 2 additional score during this process
  '''
  
  users_all = UserProfile.objects.all()
  
  users_interests_likes = [] # [[user1_interests, user1_likes], [user2_interests, user2_likes], ...] for all users who share 4 or more interests with current user
  for u in users_all:
    if u.name == user.name:
      continue
    users_interests_likes.append([u.interests.all(),u.likes.all()])

  users_interests_likes_names = []
  for pair in users_interests_likes:
    interests_names = []
    likes_names = []
    for interest in pair[0]:
      interests_names.append(interest.name)
    for career in pair[1]:
      likes_names.append(career.name)
    users_interests_likes_names.append([interests_names, likes_names])


  #return users_interests_likes_names

  careers_other_users_score = [] # [[career1_name, score_to_be_added], [...], ...]
  #careers_matched [] # [career1_name, ... ]

  # for each interests-liked_careers pair for other users
  for pair in users_interests_likes_names: # pair: [[interest1_name, interest2_name, ...],[career1_name, career2_name,...]]
    interests_matched = []
    
    # determines all overlapping interests between the current user and another user
    for interest in pair[0]:
      if interest in interests_selected_names:
        interests_matched.append(interest)

    # if 4 or more interests overlap then the careers that the other user likes get either 1 or 2 score based on their categories
    if len(interests_matched) >= 4:
      for career_name in pair[1]:
        career = Career.objects.get(name__iexact = career_name)
        category_match = False
        for category in career.categories.all():
          if category.name in interests_matched: 
            category_match = True
            break

        ''' 
          a greater weighting is given to  careers which have categories from the overlapping interests but 
          we still care about the other careers as the two users in question share interests so maybe the
          other careers are worth looking at by the current user
        ''' 
        if category_match:
          careers_other_users_score.append(career_name)
          careers_other_users_score.append(career_name)
        else:
          careers_other_users_score.append(career_name)

  careers_to_get_score = list(set(careers_other_users_score)) # no duplicates
  #return careers_other_users_score
  for career in careers_to_get_score:
    count_amount = careers_other_users_score.count(career)
    if count_amount >= 2:
      for pair in career_score_all:
        if pair[0].name == career:
          pair[1] = pair[1] + "2[other user:"+career+"]+"
    else:
      for pair in career_score_all:
        if pair[0].name == career:
          pair[1] = pair[1] + "1[other user:"+career+"]+"




  career_score_all = sorted(career_score_all, key=lambda x:x[1], reverse=True) # sorts the 2D list on the second element of each list-element 

  return career_score_all

def recommend_careers (request):
  user = UserProfile(name=request.user.username)
  #return HttpResponse("hello")

  careers_recommended_all = get_recommended_careers(user)

  qual_recommended_all = get_recommended_qualifications(user)

  #return HttpResponse (qual_recommended_all)

  #qual_score_all_objects = []
  for pair in qual_recommended_all:
    pair[0]=Qualification.objects.get(id=pair[0])

  #return HttpResponse(qual_score_all_objects)

  careers_recommended_top = careers_recommended_all[0:min(5,len(careers_recommended_all))]
  qual_recommended_top = qual_recommended_all[0:min(5,len(qual_recommended_all))]

  #return HttpResponse(qual_recommended_top)

  context = {"career_score_all": careers_recommended_all, "career_score_top": careers_recommended_top, "qual_score_all": qual_recommended_all, "qual_score_top": qual_recommended_top, "user":user}
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
    list_of_likes_qualifications = []
    

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
    

        for category in up.interests.all():
            list_of_categories.append(category)

        for subject in up.subjects.all(): 
            list_of_subjects.append(subject)

        for like in up.likes.all(): 
            list_of_likes.append(like)

        #return HttpResponse(len(up.likes_qualifications.all()))
        for qlike in up.likes_qualifications.all():
          list_of_likes_qualifications.append(qlike)

        args['form'] = UserProfileForm(initial={"name":"ac","interests": list_of_categories,"subjects": list_of_subjects,"likes": list_of_likes,"likes_qual": list_of_likes_qualifications}) 
    #Category.objects.all().values_list('id',flat=True)
        print args
        context = {"full_name": request.user.username, "args" :args,"likes":list_of_likes,"likes_qual": list_of_likes_qualifications}
        return render(request, "loggedin.html", context)
    except:
        args['form'] = UserProfileForm() 
        print args
        context = {"full_name": request.user.username, "args" :args,"likes":list_of_likes,"likes_qual": list_of_likes_qualifications}
        return render(request, "loggedin.html", context)
        pass

def invalid_login(request):
    return render(request, "invalid_login.html")


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

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
  c = Career.objects.get(name__iexact=career_name)
  if request.user.is_superuser:#Removes like feature
        
        list_of_qualifications = []
        list_of_categories = []
        list_of_institutions = []
        list_of_companies = []
        
        
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
  elif request.user.is_authenticated(): #includes like feature

      user = UserProfile.objects.get(name=request.user.username)

      '''
        Uses a POST request to update the database (with the user's like or unlike) without going to another URL
      '''
      if request.method == "POST":
        if request.POST['action'] == "like":
          if c not in user.likes.all():
            user.likes.add(c)
          return HttpResponse("success") #actual text doesn't matter as the ajax call is not requesting information
        elif request.POST['action'] == "liked":
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
  else:
      list_of_qualifications = []
      list_of_categories = []
      list_of_institutions = []
      list_of_companies = []
      
      
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
  user = UserProfile(name=request.user.username)

  categories = Category.objects.all()
  list_of_careers=[]
  list_of_suggested_careers=[]
  for career in Career.objects.all():
    list_of_careers.append(career)
    
  for suggested_careers in list_of_careers:
    list_of_suggested_careers.append(suggested_careers)
  
  
  #for suggested_careers in list_of_careers:
  #  list_of_suggested_careers.append(suggested_careers)
  
  careers_recommended_all = get_recommended_careers(user)

  #return HttpResponse(careers_recommended_all)

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
  list_of_qualifications_with_name = Qualification.objects.filter(name__iexact=qualification_name).all()
  for qual in list_of_qualifications_with_name:
    if qual.institution.name == inst_name:
      q = qual # should only be one qualification that meets this criteria

  if request.user.is_superuser:
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
    
    
    context = {"qualification": q, "careers": list_of_careers_from_qualification, "websites": list_of_websites, "subjects": list_of_subjects}
    return render (request, "advisor/qualification.html", context)

  elif request.user.is_authenticated(): #includes like feature

    user = UserProfile.objects.get(name=request.user.username)

    '''
      Uses a POST request to update the database (with the user's like or unlike) without going to another URL
    '''
    if request.method == "POST":
      if request.POST['action'] == "like":
        if q not in user.likes_qualifications.all():
          user.likes_qualifications.add(q)
        return HttpResponse("success") #actual text doesn't matter as the ajax call is not requesting information
      elif request.POST['action'] == "liked":
        if q in user.likes_qualifications.all():
          user.likes_qualifications.remove(q)
        return HttpResponse("success")
      else:
        raise Http404




    user_liked_qual_names = []
    for qual in user.likes_qualifications.all():
      user_liked_qual_names.append(qual.name)

    qual_liked = False
    if q.name in user_liked_qual_names:
      qual_liked = True


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

    context = {"qualification": q, "careers": list_of_careers_from_qualification, "websites": list_of_websites, "subjects": list_of_subjects,"matched_subjects": matched_user_subjects, "extra_subjects_needed": extra_subjects_needed, "qual_liked": qual_liked}
    return render (request, "advisor/qualification.html", context)

  else:
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
   

    context = {"qualification": q, "careers": list_of_careers_from_qualification, "websites": list_of_websites, "subjects": list_of_subjects}
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

    logo= "/static/"+institution_name.replace(" ", "").lower()+".gif"
    #these are the names of the variables in the template
    context = {"logo": logo,"institution": i, "qualifications": list_of_qualifications,"handbooks": list_of_handbooks,"websites": list_of_websites,"contactWebsites": list_of_contacts,"facultyWebsites": list_of_faculties}
    return render (request, "advisor/institution.html", context)




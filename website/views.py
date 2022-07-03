from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from firebase_admin import firestore
from website import query_firestore
from datetime import datetime
import ast


import requests

import firesql

from django import template


# from . import query_firestore
NAME = ""

def index(request):
    """Page d'accueil du site, remet la variable globale à zéro, déconnecte l'utilisateur"""
    request.session['HR_account']="" #retire le nom de l'utilisateur car il n'est pas connecté
    return render(request, 'index.html')


def log(request):
    return render(request, 'log.html')

def log_error(request):
    return render(request, 'log_error.html')


def log_form(request):
    """lance la page d'inscription, récupère les infos et les ajoute dans la base de données"""
    #print("Inside View")
    if request.method == "POST":
        # print("Inside post")
        name_hr = request.POST.get("name_hr", None)
        email_hr = request.POST.get("email_hr", None)
        mdp_hr = request.POST.get("mdp_hr", None)
        company_hr = request.POST.get("company_hr", None)
        # print(email_hr)
        # print(os.getcwd())

        query_firestore.create_hr(name_hr, email_hr, mdp_hr, company_hr)

    return render(request, 'log.html')


def login_form(request):
    """vérifie que les infos correspondent à un utilisateur connu et lance la page home
        stocke les informations essentielles dans une variable globale
        nom du RH et jobs attaché à ce RH"""

    #print("Inside View")
    if request.method == "POST":
        email_hr = request.POST["email_hr"]
        mdp_hr = request.POST["mdp_hr"]

        db = firestore.client()

        hr = db.collection('hrs').where("email", '==', f'{email_hr}').where("mdp", '==', f'{mdp_hr}')
        try:
            for hr in hr.stream():
                name_hr =hr.to_dict()["name"]
                request.session['HR_account']=hr.to_dict()
                #print(hr.to_dict())
            jobs = query_firestore.read_jobs(name_hr)
            nb_missions =query_firestore.get_nb_missions_affectees(jobs)
            messages = query_firestore.read_messages(name_hr)[:2]  # récupère les 2 derniers messages envoyés
            list_messages=[]

            for x in range(len(messages)):
                list_messages.append({"candidat":messages[x]["candidat"],"message":messages[x]["message"][:100]+"..."})
                print(list_messages[x])
            print(list_messages)

            resumes = query_firestore.read_resumes(name_hr)[:2]
            list_resumes = []

            for x in range(len(resumes)):
                list_resumes.append({"name":resumes[x]["name"],"date":resumes[x]["date"],"titre":query_firestore.get_job_title(name_hr, resumes[x]["url_resume"])})

            context = {
                'email_hr': f'{email_hr}',
                'mdp_hr': f'{mdp_hr}',
                'name_hr': f'{name_hr}',
                'jobs':jobs,
                'nb_missions' : nb_missions,
                'messages':list_messages,
                'resumes' : list_resumes
            }
            request.session['HR_account']['name'] = name_hr
            request.session['JOBS'] = jobs
            request.session['HR_account']['company'] = query_firestore.read_company(name_hr)
            return render(request, 'home.html', context)

        except:

            print("invalid password or email")
            context ={
                "message":"invalid password or email"
            }
            return render(request,"log_error.html", context)

def pages_contact(request):
    name_hr = request.session['HR_account']['name']
    context={
        "name_hr":name_hr
    }
    return render(request, 'pages-contact.html',context)


def home(request):
    """essentiellement le tableau de bord de l'utilisateur avec un rappel des missions"""
    #print("Inside Home")

    name_hr = request.session['HR_account']['name']
    jobs =request.session['JOBS']
    #print(name_hr)
    # col_hrs = db.collection('hrs').where("name", '==', f'{name_hr}')
    # hrs = col_hrs.stream()
    #print(name_hr)
    nb_missions =query_firestore.get_nb_missions_affectees(jobs)
    messages = query_firestore.read_messages(name_hr)[:2]  # récupère les 2 derniers messages envoyés
    list_messages = []
    for x in range(len(messages)):
        list_messages.append({"candidat": messages[x]["candidat"], "message": messages[x]["message"][:100]+"..."})
    print(list_messages)

    resumes = query_firestore.read_resumes(name_hr)[:2]
    list_resumes = []

    for x in range(len(resumes)):
        list_resumes.append({"name": resumes[x]["name"], "date": resumes[x]["date"],
                             "titre": query_firestore.get_job_title(name_hr, resumes[x]["url_resume"])})

    #print(messages)
    if request.method == "GET":
        titre = request.GET.get("titre")
        lieu = request.GET.get("lieu")
        url_desc = request.GET.get("url_desc")
        #print(titre,lieu)
        fiche = query_firestore.read_file(url_desc)
        #print(fiche)

    context = {
        'name_hr': request.session['HR_account']["name"],
        'jobs':jobs,
        'nb_missions' : nb_missions,
        'fiche':fiche,
        'messages':list_messages,
        'resumes' : list_resumes
    }
#    collections = hr.document('$hr_id').collection('job_description')
#    for collection in collections:
#        for doc in collection.stream():
#            print(f'{doc.id} => {doc.to_dict()}')

    # doc_hr = db.collection('hrs').document()
    # id = doc_hr.id
    return render(request, 'home.html', context)



def user_profile(request):
    """affiche les informations du RH"""
    name_hr = request.session['HR_account']["name"]
    email_hr = request.session['HR_account']["email"]
    company_hr = request.session['HR_account']["company"]
    new_name=name_hr

    if request.method == "POST":
        new_name=request.POST.get("fullName")
        name_company=request.POST.get("company")
        new_email=request.POST.get("email")
        query_firestore.set_hr(name_hr,new_name,new_email,name_company)
    #if request.method == "GET":
     #   password = request.GET.get("password")
      #  newPassword = request.GET.get("newPassword")
       # renewPassword = request.GET.get("renewPassword")
        #print(password)
        #result = query_firestore.set_mdp_hr(name_hr,password,newPassword,renewPassword)
   # print(request.GET.keys(),result)
    request.session['HR_account'] = query_firestore.read_hr(new_name).to_dict()
    name_hr = request.session['HR_account']["name"]
    context = {
        'email_hr': email_hr,
        'name_hr': name_hr,
        'company_hr' : company_hr
    }

    return render(request, 'user_profile.html', context)


def call_OCR_NLP(file):

    URL_OCR = "https://snipehr-ocr.herokuapp.com/ocr"
    URL_NLP = "https://snipehr-ocr.herokuapp.com/parse"
    body = {"file" : file}
    ocr_response =requests.post(URL_OCR,files=body).text
    d = {'text': ocr_response}
    nlp_response = requests.post(URL_NLP, data=d).text
    return nlp_response


def translate_call(fiche):
    URL ="https://snipehr-translate.herokuapp.com/translate"
    body = {
        "text" : fiche,
        "lang": "fr"
    }
    return requests.post(URL, data=body).text

def message_call(url, message):
    """ fait un call vers l'API qui envoie un message directement dans le linkedin du candidat"""
    api_URL = "https://snipehr.ew.r.appspot.com/message"
    body = {
        "url": "'" + url + "'",
        "message" : '"""' + message + '"""'
    }
    #print(requests.post(URL,data=body).text)
    print(url)
    return requests.post(api_URL,data=body).text


def classement_candidats(post,lieu, top_n, skills):
    """ """
    URL = "https://snipehr.ew.r.appspot.com/search"
    body = {
        "query": "'" + (post + " " + lieu).lower() + "'",
        "profile_number" : top_n,
        "skills":"'" + skills + "'"
    }
    #print(body["query"])
    return requests.post(URL,data=body).text


def candidats(request):
    name_hr = request.session['HR_account']['name']
    candidats =[{"name":"Khalida OUAMAR","email":"no need","phone":"no need","location":"Paris","title":"DevOps Senior","link":"https://www.linkedin.com/in/khalida-ouamar/"},{"name":"Amandine THIVET","email":"no need","phone":"no need","location":"Paris","title":"Data Engineer","link":"https://www.linkedin.com/in/amandine-thivet/"}]
    top_n = 3
    company = request.session['HR_account']['company']
    candidat_name =""
    message =""
    url_desc=""
    job_index = ""
    lien =""
    link=""
    print(request.method)
    if request.method == "POST":
        titre = request.POST.get("titre")
        lieu = request.POST.get("lieu")
        skills = request.POST.get("skills")
        url_desc = request.POST.get("url_desc")
        job_index=url_desc.split("/")[-1] if url_desc != None else ""
        print(request.POST.keys())
        if "message" in request.POST.keys():
            link = request.POST.get("url")
            candidat_name = request.POST.get("candidat_name")
            message = request.POST.get("message")
            response = message_call(link,message)
            if "Message sent" in response:
                query_firestore.create_message(name_hr, message, candidat_name,titre)  # Ajoute le message dans la base de données
        else:
            candidats += ast.literal_eval(classement_candidats(titre, lieu, top_n, skills))
            request.session["CANDIDATS"]=candidats
    if request.method == "GET":
        titre = request.GET.get("titre")
        lieu = request.GET.get("lieu")
        url_desc = request.GET.get("url_desc")
        link = request.GET.get("url")
        job_index=url_desc.split("/")[-1]
        skills = request.POST.get("skills")
        candidat_name = request.GET.get("candidat_name")
        lien="https://snipehr-website.herokuapp.com/my_candidate/"+name_hr+"/"+job_index
        #print(ast.literal_eval(candidats)[0]['title'])

    context = {
        'name_hr': name_hr,
        'candidats':request.session["CANDIDATS"],
        'n': top_n +2,
        "company_hr": company,
        'titre':titre,
        'lieu':lieu,
        'candidat_name':candidat_name,
        'candidat_link':link,
        'url_desc' : job_index,
        'lien':lien
    }
    return render(request, 'candidats.html',context)

def messagerie(request):
    name_hr = request.session['HR_account']['name']
    liste_message=query_firestore.read_messages(name_hr)
    context={
        'name_hr':name_hr,
        'messages':liste_message
    }
    return render(request, 'messagerie.html',context)

def historic(request):
    name_hr = request.session['HR_account']['name']
    liste_historic=[]
    if request.method == "POST":
        url_desc = request.POST.get("url_desc")
        if "commentaire" in request.POST.keys():
            commentaire = request.POST.get("commentaire")
            query_firestore.add_historic(name_hr, commentaire, url_desc) #Ajoute le commentaire dans notre base de donnée
        titre = request.POST.get("titre")
        liste_historic = query_firestore.liste_historic(name_hr,url_desc)
        #print(liste_historic[0]['date'])

    context = {
        "name_hr" : name_hr,
        "titre":titre,
        "liste_historic":liste_historic,
        "url_desc":url_desc
    }
    return render(request, 'historic.html',context)

def my_posts(request):
    """Page affichant l'enssemble des fiches de postes attaché à notre utilisateur
        depuis cette page on pourra également afficher les meilleurs candidats selon chaque fiche de poste
         La connecion avec le modèle qui récupère les profil n'a pas encore été effectué"""
    name_hr = request.session['HR_account']['name']
    fiche =""
    print(request.method)
    if request.method == "POST":
        titre = request.POST.get("titre")
        date = request.POST.get("date")
        lieu = request.POST.get("lieu")
        url_desc = request.POST.get("url_desc")
        url_historic = request.POST.get("url_historic")
        job_to_set = {"titre":titre,"date":date,"url_desc":url_desc,"url_historic":url_historic,"lieu":lieu}
        query_firestore.set_status(name_hr, job_to_set)
        request.session['JOBS'] = query_firestore.read_jobs(name_hr)

    if request.method == "GET":
        titre = request.GET.get("titre")
        lieu = request.GET.get("lieu")
        url_desc = request.GET.get("url_desc")
        print(titre,lieu)
        fiche = query_firestore.read_file(url_desc)
        print(fiche)

    #print(request.get_full_path())
    jobs = request.session['JOBS']

    context = {
        'name_hr': name_hr,
        'jobs':jobs,
        'fiche':fiche,
        'titre':titre,
        'lieu':lieu,
        'url_desc':url_desc

    }
    return render(request, 'my_posts.html',context)



def post_generator(request):
    """"Page qui récupère les informations rentré par le RH pour générer une mission"""
    name_hr =request.session['HR_account']['name']
    context = {
        'name_hr': name_hr
    }
    return render(request, 'post_generator.html',context)

def job_description(titre, skills, preferences):
    """Fonction qui fait la requête vers le modèle de génération de fiche de poste"""
    URL = "https://job-description-api.herokuapp.com/generate" #modèle de génération de fiche de poste déployé sur Heroku
    competence_mix = ""
    preference_mix = ""
    spot = '"'  # nécéssaire pour la structuration de la requête
    titre = spot + titre + spot
    skills = spot + skills + spot
    preferences = spot + preferences + spot


    body = {
        "title": titre,
        "skills": skills,
        "preferences": preferences
    }
    fiche = requests.post(URL, data=body).text
    return fiche



def post_generated(request):
    """page qui affiche la fiche de poste générée"""
    keys = list(request.POST.keys())
    fiche =""
    titre = request.POST["titre"] if "titre" in keys else ""
    lieu = request.POST["lieu"] if "lieu" in keys else ""
    entreprise = request.POST["entreprise"] if "entreprise" in keys else ""
    competences = request.POST["competences"] if "competences" in keys else ""
    preferences = request.POST["preferences"] if "preferences" in keys else ""
    contexte = request.POST["contexte"] if "contexte" in keys else ""
    TT = True if "TT_yes" in keys else False #Télétravail
    date = request.POST["date"] if "date" in keys else datetime.today().strftime('%Y-%m-%d')
    motiv =True if "motiv_yes" in keys else False #Lettre de motivation
    if request.method == "POST":
        fiche += entreprise +"\n"
        fiche+=contexte + "\n"

        fiche+="available from " + date

        fiche+=", in " + lieu + "\n"
        fiche += job_description(titre,competences,preferences)
        fiche_translated = translate_call(fiche)

        fiche += "possibility of teleworking,\n" if TT else ""
        fiche += "cover letter required for this position.\n" if motiv else ""
    #print("fiche contient :",fiche)

    name_hr =request.session['HR_account']['name']
    translate = True  if "translate" in request.POST.keys() else False
    if request.method == "GET":
        titre = request.GET["titre"]
        lieu = request.GET["lieu"]
        date = request.GET["date"]
        fiche = translate_call(request.GET.get("fiche"))
        competences = request.GET["competences"]
        translate= request.GET["translate"]
        print(titre,lieu,date,competences)
        print(translate,fiche)

    #print(titre, date, lieu)
    context = {"fiche":fiche,
            "titre":titre,
            'name_hr': name_hr,
            "lieu":lieu,
            "date":date,
            "competences":competences,
            "translate":translate
        }
    return render(request, 'post_generated.html',context)


def post_valid(request):
    """Page de validation de fiche de poste
        Une fois la fiche de poste satisfaisante pour le RH, il peut la valider et elle s'ajoute à la base de données
        en tant que collection imbriquée"""
    titre = request.POST["titre"]
    date = request.POST["date"]
    fiche = request.POST["fiche"]
    lieu = request.POST["lieu"]
    competences = request.POST["competences"]
    query_firestore.create_job_desc(titre, lieu, date, competences, fiche, request.session['HR_account']['name'])
    name_hr = request.session['HR_account']['name']
    request.session['JOBS'] = query_firestore.read_jobs(name_hr)  # met à jour la liste des jobs
    context = {
        'name_hr': name_hr
    }
    return render(request, 'post_valid.html', context)


def call_OCR(file):
    URL = "https://snipehr-ocr.herokuapp.com/ocr"
    body = {
        "file" : file
    }
    result =requests.post(URL,files=body)
    return result.text


def upload_post(request):
    """Page pour upload des fichiers représentant les fiches de postes préfaite"""
    name_hr =request.session['HR_account']['name']
    uploaded_file=""
    #print(request.POST.keys())
    if request.method == 'POST' and request.FILES['myfile']:
        titre = request.POST.get("titre")
        lieu = request.POST.get("lieu")
        myfile = request.FILES['myfile']
        if "txt" in myfile.name:
            uploaded_file = str(myfile.read())
            #print(uploaded_file)
        if 'pdf' in myfile.name:
            uploaded_file = call_OCR(myfile)
            #Notre OCR récupère 2 fois le texte, en faisant ce qui suit on retire le surplus de texte
            lines = uploaded_file.split('\n')
            i = len(lines)
        
            for l in lines[::-1]:
                if (" " in l):
                    break
                i -= 1
            # print(lines[i-1])

            fiche = '\n'.join(lines[:i])
            #print(fiche)
        #print(myfile.name)
        date =datetime.today().strftime('%Y-%m-%d')
        competences=""
        query_firestore.create_job_desc(titre, lieu, date,competences, fiche, name_hr)
        request.session['JOBS'] = query_firestore.read_jobs(name_hr)  # met à jour la liste des jobs
    context = {
        'name_hr': name_hr,
        'uploaded_file_url': uploaded_file
    }
    return render(request, 'upload_post.html',context)



def faq(request):
    """Page FAQ """
    name_hr =request.session['HR_account']['name']
    context = {
        'name_hr': name_hr
    }
    return render(request, 'pages-faq.html',context)



def cv_details(request):
    """Page qui récupère les informations du CV envoyé par le candidat"""
    name_hr =request.session['HR_account']['name']
    resumes =query_firestore.read_resumes(name_hr)

    for resume in resumes:
        resume["titre"]=query_firestore.get_job_title(name_hr,resume["url_resume"])

    email = ""
    phone = ""
    skills = ""
    if request.method == "POST":
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        skills = ast.literal_eval(request.POST.get("skills"))
        print(skills)
    context={
        "name_hr":name_hr,
        "resumes":resumes,
        "email": email,
        "phone":phone,
        "skills": skills
    }
    return render(request, 'cv_details.html',context)

from django.urls import resolve

def my_candidate(request,name_hr,url_desc):
    """Page à envoyer au candidat pour qu'il upload son CV"""
    return render(request, 'my_candidate.html')

def upload_cv(request,name_hr,url_desc):
    uploaded_file=""
    #print(request.POST.keys())
    uploaded = False
    if request.method == 'POST' and request.FILES['myfile']:
        name = request.POST.get("name")
        date = request.POST.get("date")
        lieu = request.POST.get("lieu")
        myfile = request.FILES['myfile']
        #print(name,date, lieu)
        response = ast.literal_eval(call_OCR_NLP(myfile))
        query_firestore.add_CV(name_hr, url_desc, myfile, name, date, lieu, response)
        uploaded = True

    context = {
        'uploaded': uploaded
    }
    return render(request, 'upload_cv.html',context)

import firebase_admin
from firebase_admin import credentials, firestore
import os
from gcloud import storage
from pprint import pprint
from datetime import datetime
import ast

from django import template

INDEX = 1
INDEX_historic = 1
INDEX_cv = 1
# Setup the connexion to the project
cred = credentials.Certificate("./website/serviceAccountKey.json")
#cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'./website/serviceAccountKey.json'
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'serviceAccountKey.json'

storage_client = storage.Client()


def increment_index_historic():
    """Fonction qui incrémente la variable globale INDEX_historic
        nécessaire pour l'unicité de notre historique dans la base de donnée"""

    global INDEX_historic
    INDEX_historic += 1
    return INDEX_historic


def increment_index():
    """Fonction qui incrémente la variable globale INDEX
        nécessaire pour l'unicité de notre fiche de poste dans la base de donnée"""
    global INDEX
    INDEX += 1
    return INDEX

def increment_index_cv():
    """Fonction qui incrémente la variable globale INDEX_historic
        nécessaire pour l'unicité de notre historique dans la base de donnée"""

    global INDEX_cv
    INDEX_cv += 1
    return INDEX_cv

def add_CV(name_hr,url_desc,file,name,date,lieu, dict_infos):
    global INDEX_historic
    #date = datetime.today().strftime('%Y-%m-%d')
    #name_file = "gs://snipehr_historic/"

    #dict_infos={"email":"norayda.nsiemo@gmail.com","phone":"+33768373205","skills":["Python","R","DevOps","MongoDB","documentation","flux","Python","R","Java","Jenkins","Airflow","Docker","Google","MySQL","MongoDB","Firebase","Tableau","documentation","flux"]}
    index_job =url_desc.split("/")[-1].split('.')[0]
    name_file = name_hr + "_" + index_job + "_" + str(INDEX_cv)
    increment_index_cv()

    #my_bucket = storage_client.get_bucket("snipehr_cvs")
    #pprint(vars(my_bucket))
    #blob = my_bucket.blob(name_file)
    #blob.upload_from_filename(file)
    #blob.upload_from_filename(file)

    db = firestore.client()
    new_cv={
        'name': name,
        'lieu' :lieu,
        'email': dict_infos['email'],
        'phone': dict_infos['phone'],
        'date' : date,
        'status': False,
        'url_resume': "gs://snipehr_cvs/" + name_file,
        'skills':dict_infos['skills']
    }
    #print(name_hr)
    db.collection('hrs').document(read_hr(name_hr).id).collection('resumes').add(new_cv)


def read_file_as_file(uri,name,date,poste):
    """Fonction qui lit la fiche de poste stocker dans le cloud storage à partir de l'URI """
    destination = "resumes/"+name+"_"+poste+"_"+date+'.pdf'
    blob=""
    if(uri != None):
        bucket = storage_client.get_bucket(uri.split("/")[-2])
        blob = bucket.blob(uri.split("/")[-1])
        blob = blob.download_to_filename(destination)
        #blob = blob.decode('utf-8')
    return blob

def read_file(uri):
    """Fonction qui lit la fiche de poste stocker dans le cloud storage à partir de l'URI """
    blob=""
    if(uri != None):
        bucket = storage_client.get_bucket(uri.split("/")[-2])

        blob = bucket.blob(uri.split("/")[-1])
        blob = blob.download_as_string()
        blob = blob.decode('utf-8')
    return blob

def liste_historic(name_hr,url_desc):
    """Fonction qui retourne la liste des historic pour une fiche de poste donnée"""
    liste =[]
    index_job =url_desc.split("/")[-1].split('.')[0]
    name_file = name_hr + "_" + index_job
    my_bucket = storage_client.get_bucket("snipehr_historic")

    blobs_all = list(my_bucket.list_blobs(prefix=name_file)) #récupère les fiches dont le nom du RH =name_hr et le job concerné à l'index du job en paramètre
    print(blobs_all)
    for blob in blobs_all:
        blob = blob.download_as_string()
        blob = blob.decode('utf-8')
        liste.append(ast.literal_eval(blob))
    return liste


def add_historic(name_hr, commentaire, url_desc):
    """Fonction qui ajoute un historique à une fiche de poste donnée"""
    global INDEX_historic
    date = datetime.today().strftime('%Y-%m-%d')
    #name_file = "gs://snipehr_historic/"
    index_job =url_desc.split("/")[-1].split('.')[0] #exemple dans l'URI gs://snipehr_job_desc/1.txt ça récupèrera 1
    my_bucket = storage_client.get_bucket("snipehr_historic")
    #pprint(vars(my_bucket))
    print(index_job)
    name = name_hr + "_" + index_job + "_" + str(INDEX_historic)+".txt"
    increment_index_historic()
    #text_file = open(name, "w")
    #n = text_file.write(commentaire)
    #text_file.close()

    historic =str({"date":date,"commentaire":commentaire})
    blob = my_bucket.blob(name)
    blob.upload_from_string(historic)

    print(blob)

def get_nb_missions_affectees(liste_jobs):
    """Fonction qui renvoie le nombre exacte de missions affecté à partir de la liste des jobs lié au profil"""
    nb=0
    for job in liste_jobs:
        if(job["status"]):
            nb+=1
    return nb

def set_status(name_hr,job_to_set):
    """Fonction qui met à jour le status d'une mission"""
    job =get_job(name_hr,job_to_set)
    print(job)
    print(job.to_dict()["status"])
    hr=read_hr(name_hr)
    status = job.to_dict()["status"]
    db.collection('hrs').document(hr.id).collection('job_description').document(job.id).update({"status": not status})

def read_company(name_hr):
    """Fonction qui retourne le nom de la compagnie du RH connecté"""
    hr=read_hr(name_hr)
    return hr.to_dict()["company"]

def chiffrement_message(message,clef):
    return None

def dechiffrement_message(message,clef):
    return None

def create_message(name_hr,message,nom,post):
    """Fonction qui crée et chiffre le message dans la base de donnée"""
    db = firestore.client()
    date = datetime.today().strftime('%Y-%m-%d')
    new_message={
        'date': f'{date}',
        'message': f'{message}',
        'candidat':f'{nom}',
        'post':f'{post}'
    }
    db.collection('hrs').document(read_hr(name_hr).id).collection('messages').add(new_message)

    return None

def create_job_desc(titre,lieu, date, competences, fiche, name_hr):
    global INDEX
    """Fonction qui ajoute une fiche de poste dans la base de donée"""
    url_desc="gs://snipehr_job_desc/"
    url_historic="gs://snipehr_historic/"
    lieu =lieu
    my_bucket = storage_client.get_bucket("snipehr_job_desc")
    #pprint(vars(my_bucket))
    name = str(INDEX)+".txt"
    increment_index()
    #text_file = open(name, "w")
    #n = text_file.write(fiche)
    #text_file.close()
    blob = my_bucket.blob(name)
    blob.upload_from_string(fiche)

    url_desc+=name
    db = firestore.client()
    new_job_desc={
        'titre': f'{titre}',
        'lieu' :f'{lieu}',
        'date': f'{date}',
        'status': False,
        'url_desc': f'{url_desc}',
        'url_historic': f'{url_historic}',
        'skills':f'{competences}'
    }
    #print(name_hr)
    db.collection('hrs').document(read_hr(name_hr).id).collection('job_description').add(new_job_desc)

def create_hr(name_hr, email_hr, mdp_hr, company_hr):
    """Fonction qui ajoute un RH à notre base de donée """
    db = firestore.client()
    # A voir pour ajouter le doc avec un id auto généré
    new_hr = {
        'name': f'{name_hr}',
        'email': f'{email_hr}',
        'mdp': f'{mdp_hr}',
        'company': f'{company_hr}'
    }

    db.collection('hrs').add(new_hr)
    db.collection('hrs').document(read_hr(name_hr).id).collections('job_description')

def set_hr(past_name,name_hr, email_hr, company_hr):
    db = firestore.client()
    new_hr = {
        'name': f'{name_hr}',
        'email': f'{email_hr}',
        'company': f'{company_hr}'
    }
    hr=read_hr(past_name)
    db.collection('hrs').document(hr.id).update(new_hr)


def get_job(name_hr,job_to_set):
    """Fonction qui nous permet d'avoir l'ID d'une jfiche de description"""
    col_jobs = db.collection('hrs').document(read_hr(name_hr).id).collection('job_description')
    jobs = col_jobs.stream()
    dictfilt = lambda x, y: dict([(i, x[i]) for i in x if i in set(y)])

    for job in jobs:
        print(dictfilt(job.to_dict(),("url_desc","date")))
        print(dictfilt(job_to_set,("url_desc","date")))
        #print(dictfilt(job.to_dict(),("date","titre","url_desc","url_historic")))
        if dictfilt(job_to_set,("url_desc","date")) == dictfilt(job.to_dict(),("url_desc","date")):
            return job

def read_hr(name_hr):
    """fonction qui nous perme d'avoir l'ID du RH à partir du nom"""
    # Only get 1 document or hrs
    col_hrs = db.collection('hrs').where("name", '==', f'{name_hr}')
    hrs = col_hrs.stream()

    for hr in hrs:
        #print(f'{hr.id} => {hr.to_dict()}')
        return hr


def read_hrs():
    """Fonction qui nous permet d'avoir la liste des RHs"""
    # Get the hole hrs collection
    col_hrs = db.collection('hrs')
    hrs = col_hrs.stream()
    for hr in hrs:
        print(f'{hr.id} => {hr.to_dict()}')

def test(email_hr, mdp_hr):
    hr = db.collection('hrs').where("email", '==', f'{email_hr}').where("mdp", '==', f'{mdp_hr}').get()
    print(hr)
    for h in hr:
        print(f'{h.id} => {h.to_dict()}')

def read_jobs(name_hr):
    """Fonction qui retourne la liste des fiches de poste associé à un RH"""
    collections = db.collection('hrs').document(read_hr(name_hr).id).collection("job_description").stream()
    list_jobs = []
    for collection in collections:
        list_jobs.append(collection.to_dict())
    return list_jobs

def read_resumes(name_hr):
    """Fonction qui retourne la liste des fiches de poste associé à un RH"""
    collections = db.collection('hrs').document(read_hr(name_hr).id).collection("resumes").stream()
    list_resumes = []
    for collection in collections:
        list_resumes.append(collection.to_dict())
    return list_resumes

def read_messages(name_hr):
    """Fonction qui retourne la liste des fiches de poste associé à un RH"""
    messages = db.collection('hrs').document(read_hr(name_hr).id).collection('messages').stream()
    list_messages = []
    i=1
    message_dict ={}
    for message in messages:
        message_dict=message.to_dict()
        message_dict['index']=i
        i+=1
        list_messages.append(message_dict)
    return list_messages

def get_job_title(name_hr,url_resume):
    titre =""
    url_desc = "gs://snipehr_job_desc/" + url_resume.split("/")[-1].split("_")[-2] +'.txt'
    jobs = read_jobs(name_hr)
    for job in jobs:
        if (job["url_desc"]==url_desc):
            titre=job["titre"]
    return titre

if __name__ == '__main__':
    #create_hr('Khalida', 'test@gmail.fr', 'azerty', 'ESGI')
    #read_hr('Test')
    #test('test@test.fr', 'test')
    #jobs = read_job(read_hr("Test"))
    #print(jobs)

    #titre=""
    #date=""
    #status= True
    #url_desc=""
    #url_historic =""
    #create_job_desc(titre, date, status, url_desc, url_historic, read_hr("Khalida"))
    name_hr ="Test"
    #job_to_set = {'date': '2022-08-25', 'titre': 'Data Analyst', 'url_desc': '', 'url_historic': ''}
    #print(get_job(name_hr,{'titre': 'Data', 'date': '2022-11-10', 'url_desc': 'gs://snipehr_job_desc/1.txt', 'url_historic': 'gs://snipehr_job_desc/'}).to_dict()["status"])
    #set_status(name_hr, job_to_set)
    #print(get_job(name_hr,job_to_set).to_dict()["status"])

    #print(read_job(read_hr("Test"))["jobs"])
    #set_status("Test",{'status': False, 'date': '2022-08-25', 'titre': 'Data Analyst', 'url_desc': '', 'url_historic': ''})

    #read_file("gs://snipehr_job_desc/1.txt")
    commentaire ="Test des commentaires"
    url_desc = "gs://snipehr_job_desc/1.txt"
    #add_historic(name_hr, commentaire, url_desc)
    #add_historic(name_hr, commentaire, url_desc)
    #print(liste_historic(name_hr, url_desc))

    #print(get_nb_missions_affectees(read_jobs(name_hr)))
    #add_CV(name_hr,url_desc,"CVNorayda_NSIEMO.pdf","Norayda NSIEMO","2022-09-23","Paris", dict())

    #read_file_as_file("gs://snipehr_cvs/Test_1_1","Norayda NSIEMO","2022-09-23","Data Engineer")



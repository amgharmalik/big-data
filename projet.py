import xml.etree.cElementTree as et
import pandas as pd
import matplotlib.pyplot as plt
import requests
import numpy
import time

def getvalueofnode(node):
    """ return node text or None """
    return node.text if node is not None else None

job_list = list()
meteo_interval = list()
def setjoblist(job_list):
    stop = False
    stopcarac = ''
    while(stop == False):
        job_list.append(input("Quel type de langage souhaitez-vous exercer ? "))
        while(stopcarac != 'O' and stopcarac !='o' and stopcarac !='N' and stopcarac !='n'):
            stopcarac = input("Tapez O pour arreter, N pour continuer ")
        if(stopcarac == 'O' or stopcarac == 'o'):
            stop = True
        stopcarac = ''
def setmeteo(meteo_interval):
    min = input("Quelle est la temperature minimale que vous souhaitez avoir ? ")
    min = float(min)
    max = input("Quelle est la temperature maximale que vous souhaitez avoir ? ")
    max = float(max)
    
    meteo_interval.append(min)
    meteo_interval.append(max)
        
setjoblist(job_list)
setmeteo(meteo_interval)

#on ajoute les jobs de stackoverflow dans un fichier texte puis on initialise le dataframe des jobs
link_xml = requests.get("https://stackoverflow.com/jobs/feed")
with open('jobfeed.xml','wb') as f:
    f.write(link_xml.content)
job_xml = et.parse("jobfeed.xml").getroot()
job_dfcols = ['job','location']
job_df = pd.DataFrame(columns=job_dfcols)
    
#on initialise un dataframe qui stockera chaque ville
response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=London&mode=json&units=metric&APPID=bb9645da9e6688f53ba4d9224957fe73")
responsejson = response.json()
meteo_dict={'location':responsejson["name"],'Temp':responsejson["main"]["temp"]}   
meteo_df = pd.DataFrame([meteo_dict],columns= meteo_dict.keys())

#on ajoute chaque job trouvé dans le fichier XML dans le dataframe (job + localisation)
for node in job_xml[0].findall('item'):
    job = node.find('category')
    location = node.find('{http://stackoverflow.com/jobs/}location')
    job_df = job_df.append(
    pd.Series([getvalueofnode(job), getvalueofnode(location)], index=job_dfcols),
            ignore_index=True)

#on garde qu'une seule version de chaque ville puis on retire le pays rattaché à la ville grâce à un regex
uniquedf = job_df['location'].unique()
job_df['location'].replace(to_replace=", [A-Z,a-z]+$",value="", regex=True,inplace=True)

#on stock la météo de chaque ville dans le dataframe de meteo
for x in uniquedf:
    if(x!= None):
        virgule = x.find(',')
        town = x[0:virgule]
        parameters ={"APPID":"bb9645da9e6688f53ba4d9224957fe73","q":town,"mode":"json","units":"metric"}
        response = requests.get("http://api.openweathermap.org/data/2.5/weather", params=parameters)
        responsejson = response.json()
        if('name' in responsejson):
            meteo_dict={'location':responsejson["name"],'Temp':responsejson["main"]["temp"]}
            df = pd.DataFrame([meteo_dict],columns= meteo_dict.keys())
            print(town)
            meteo_df = meteo_df.append(df)
print("Recherche terminee.")            
dfmerge = pd.merge(meteo_df,job_df)

#affichage du resultat
locationdf = dfmerge[(dfmerge["job"].isin(job_list))&(dfmerge["Temp"]>=meteo_interval[0])&(dfmerge["Temp"]<=meteo_interval[1])]
print(locationdf)
uniquemeteodf = locationdf.drop_duplicates(subset=['location','Temp'])
uniquelocationdf1 = locationdf.drop_duplicates(subset=['location','Temp','job'])
print(uniquelocationdf1)
uniquelocationdf = locationdf['location'].unique()
print("Affichage des villes les plus interessantes pour vous, basees sur vos souhaits")
print(uniquelocationdf)
countjob = pd.value_counts(locationdf['job'].values, sort=True)
print("Voici le nombre de postes disponibles pour chaque langage")
print(countjob)
print("Voici le nombre de postes disponibles pour chaque ville")
numberofjobdf = locationdf.groupby('location')[['job']].count()
print(locationdf.groupby('location')[['job']].count())
graph = uniquemeteodf.plot.bar(x="location",rot=0, title='Meteo',figsize=(30,10), fontsize=12)
plt.show()
#locationdf.plot.bar(x="job",rot=0, title='Job', figsize=(15,10), fontsize=12)
time.sleep(300)

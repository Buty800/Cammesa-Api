import json
import requests
from datetime import datetime
import pandas as pd
import re

from file_classes import File

CLIENT_SECRET = "2b67241d-11e5-4ef9-90fb-ae8aae195c6b"

URL = {
    "LOGIN" : "https://keycloak.cammesa.com/auth/realms/Cammesa/protocol/openid-connect/token",
    "LOGOUT" : "https://keycloak.cammesa.com/auth/realms/Cammesa/protocol/openid-connect/logout",
    "DOC" : "https://api.cammesa.com/pub-svc/secure/findDocumentosByNemoRango",
    "ZIPFILE" : "https://api.cammesa.com/pub-svc/secure/findAllAttachmentZipByNemoId",
    "FILE":  "https://api.cammesa.com/pub-svc/secure/findAttachmentByNemoId",
    "LAST_DOC" : "https://api.cammesa.com/pub-svc/secure/obtieneFechaUltimoDocumento" 
}

def tipo(s): return re.sub(r'\d.*', '', s)
def fecha(s) : return re.sub("[^0-9]", "",s)

class Cammesa:
    def __init__(self, username:str, psw:str):
        self.username = username
        self.psw = psw

        self.logged = False
        self.acces_token = None
        self.refresh_token = None

    def login(self):
        """
        Logea a la api de Cammesa con el usuario y contraseña pasados en la creación del objeto
        """
        if not self.logged:
            login_data = {"username":self.username, "password":self.psw, "client_secret":CLIENT_SECRET, "grant_type":"password", "client_id":"cds"}
            login_request = requests.post(url = URL["LOGIN"], data=login_data)
            
            if login_request.status_code == 200:
                login_response = login_request.json()
                self.acces_token = login_response["access_token"]
                self.refresh_token = login_response["refresh_token"]
                self.logged = True
        
            return login_request.status_code
        else:
            return 409
        
    def logout(self):
        """
        Logout de la api de Cammesa con el usuario y contraseña pasados en la creación del objeto
        """
        if self.logged:
            logout_data = {"client_secret":CLIENT_SECRET, "client_id":"cds", "refresh_token":self.refresh_token}
            logout_request = requests.post(url = URL["LOGOUT"], data=logout_data)

            if logout_request.ok:
                self.logged = False
                self.acces_token = None
                self.refresh_token = None
            
            return logout_request.status_code
        else:
            return 409
    
    def getdoc(self, date_from:datetime, date_to:datetime, nemo:str)->json:
        """
        Devuelve los documentos de un NEMO en unrango de fechas
        """
        header = {"Authorization":"Bearer " + self.acces_token}

        doc_params = {"fechadesde":date_from.isoformat(), "fechahasta":date_to.isoformat(),"nemo":nemo}
        doc_request = requests.get(url=URL["DOC"], headers=header, params=doc_params, timeout=30)

        if doc_request.status_code != 200 : return doc_request.status_code

        return doc_request.json(), doc_request.status_code
        
    def getfile(self, docid:str, attchid:str, nemo:str, download:bool = False, path="./"):
        """
        Devuelve el archivo asociado a un NEMO, docId y attachmentId. \n
        Para descargar el archivo en el directorio actual download = True. \n
        Si download = False devuelve un objeto del tipo File.
        """
        header = {"Authorization":"Bearer " + self.acces_token}
        file_params = {"docId":docid, "attachmentId": attchid, "nemo":nemo}
        file_request = requests.get(url=URL["FILE"], headers=header, params=file_params, timeout=60)


        if file_request.status_code != 200 : return file_request.status_code

        response = File(file_request.content, attchid)

        if download: response.download(path)
    
        return response
    
    def lastdocdate(self, nemo:str):
        """
        Devuelve la fecha del último documento de un NEMO 
        """
        header = {"Authorization":"Bearer " + self.acces_token}
        date_params = {"nemo":nemo}
        date_request = requests.get(url=URL["LAST_DOC"], headers=header, params=date_params, timeout=60)
            
        if not date_request.ok: return date_request.status_code

        return date_request.json()
        
    def lastdocbyfile(self, date_from:datetime, date_to:datetime, nemo:str, df:bool=False)->dict|pd.DataFrame:
        """
        Devuelve una tabla con el id de la ultima actualización de cada archivo en un rango de fechas
        """
        docs, code = self.getdoc(date_from, date_to, nemo)
        if code != 200: return "ERROR", code

        docs = pd.DataFrame().from_records(docs )
        docs = docs[["id","adjuntos","version"]]

        docs["version"] = pd.to_datetime(docs["version"])
        docs = docs.explode("adjuntos")
        docs.rename(columns={"adjuntos":"adjunto"}, inplace=True)
        
        docs["adjunto"] = docs["adjunto"].apply(lambda x: x["id"])
        docs["tipo"] = docs["adjunto"].apply(tipo)
        docs["mes"] = pd.to_datetime(docs["adjunto"].apply(fecha),format="%y%m", utc=True)
        docs = docs.groupby(["adjunto"]).max()


        return docs if df else docs.to_dict("index")










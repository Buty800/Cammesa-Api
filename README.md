# Cammesa_Api
Modulo para facilitar la conexión con la api de Cammesa

[Documentación de la API](https://microfe.cammesa.com/static-content/CammesaWeb/download-manager-files/Api/Documentacion%20API%20Web.pdf)

Código de ejemplo: 
```python
        session = Cammesa("user", "psw")

        print(session.login())
        try: 
            docs = session.lastdocbyfile(datetime(2023,1,1),datetime(2023,1,30),"DTE_UNIF")
            file = session.getfile(docs["DTE2301.zip"]["id"], "DTE2301.zip", "DTE_UNIF")
        except BaseException as e: print(type(e), e)
        print(session.logout())

        print(file["DTE2301.MDB"]["PAFTT"])
```

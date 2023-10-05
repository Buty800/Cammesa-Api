from zipfile import ZipFile
from io import BytesIO
import magic
import re

class File:
    def __new__(cls, file:bytes, name:str="file", *args, **kwargs):
        
        mime = magic.Magic(mime=True)
        filetype = mime.from_buffer(file)

        class_mapping = {
            'application/zip': Zip,
            'text/plain': Txt,
            'application/x-msaccess': Mdb
        }

        file_class = class_mapping.get(filetype, File)
        instance = super().__new__(file_class)
        return instance

    def __init__(self, file:bytes, name:str="file", *args, **kwargs):
        self.__file_content = file
        self.name = re.sub(r'[\\/:*?"<>|]', '_',name).rsplit('.', 1)[0]
        self.__readed = False
    
    def download(self, path:str="./")->None:
        """
        Downloads the file in the current direcotry or in the path passed as a parameter. 
        """
        try:
            with open(path + self.name + self.filetype, "wb") as file:
                file.write(self.__file_content)
        except BaseException as err:
            print(type(err), err)

    def __str__(self): return self.type + ": " + self.name



class Zip(File):
    filetype = ".zip"
    def __init__(self, file:bytes, name:str="zip", read:bool=True, *args, **kwargs):
        super().__init__(file, name, *args, **kwargs)
        if read: self.read()
     
    def __iter__(self)->iter:
        if self._File__readed: return iter(self.zip.items())
        else: raise FileNotFoundError("The file was not readed. Use the read() method first")

    def __getitem__(self,filename:str)->File|None:
        if self._File__readed: return self.zip.get(filename, None)
        else: raise FileNotFoundError("The file was not readed. Use the read() method first")
    
    def read(self):
        self._File__readed = True
        with ZipFile(BytesIO(self._File__file_content), "r") as zip_ref: 
            self.names = zip_ref.namelist()
            self.zip = {filename: File(zip_ref.read(filename), filename) for filename in self.names}


class Txt(File):
    filetype = ".txt"
    def __init__(self, file:bytes, name:str="txt", read:bool=True, *args, **kwargs):
        super().__init__(file, name, *args, **kwargs)
        if read: self.read()

    def __getitem__(self,index:int)->str:
        if self._File__readed: return self.txt[index]
        else: raise FileNotFoundError("The file was not readed. Use the read() method first")

    def read(self):
        self._File__readed = True
        self.txt = BytesIO(self._File__file_content).readlines()
        self.txt = list(map(lambda x: str(x)[2:-1].strip() if type(x) == bytes else x, self.txt))

class Mdb(File):
    filetype = ".mdb"

    def __init__(self, file:bytes, name:str="access", read:bool=True, *args, **kwargs):
        super().__init__(file, name, *args, **kwargs)
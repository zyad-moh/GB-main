import os

class TemplateParser():

    def __init__(self, language:str = None , default_language = 'en'):
        self.default_language = default_language
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.language = None 
        self.set_lenguage(language)
    def set_lenguage (self, language:str = None , default_language = 'en'):
        if not language:
            self.language = self.default_language

        language_path = os.path.join(self.current_path , "locales" ,language)
        # here is the language_path originally not exist
        if os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language


    # group : rag , key : (doc,system,footer) , vars :$doc_num
    def get(self,group:str,key:str,vars1:dict={}): # here i want to change the language and key (system,doc,fotter) on run time 
        
        if not group or not key:
            return None
       
        # we need to ensure that rag is exist in thia language so if is not exsist i will change the language
        group_path = os.path.join(self.current_path , "locales" ,self.language,f"{group}.py")
        targeted_languge = self.language
      
      
        if not os.path.exists( group_path ):
            group_path = os.path.join(self.current_path , "locales" ,self.default_language,f"{group}.py")
            targeted_languge = self.default_language
      
      
        if not os.path.exists( group_path ):
            return None
      
      
        module = __import__(f"stores.llm.templates.locales.{targeted_languge}.{group}",fromlist=[group])
        
        if not module:
            return None

        key_attribute = getattr(module,key)# get all variables in that module or on var(key)
        return key_attribute.substitute(vars1) # vars1 while get doc 

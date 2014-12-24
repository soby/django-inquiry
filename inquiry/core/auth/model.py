from django.contrib.auth.backends import ModelBackend as djModelBackend

class ModelBackend(djModelBackend):
    """ 
        Stock django ModelBackend that checks is_active
    """
    def authenticate(self,*args,**kwargs):
        res = super(ModelBackend,self).authenticate(*args,**kwargs)
        if res:
            if not res.is_active:
                return None
        return res
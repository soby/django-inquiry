import copy

def dict_like(obj):
    items = getattr(obj,'items',None)
    return callable(items)

def remove_fields(fields,orig,onCopy=True):
    if onCopy:
        something = copy.deepcopy(orig)
    else:
        something = orig
    if dict_like(something):
        # dict-like object check
        for k,v in something.items():
            if k in fields:
                del something[k]
            elif dict_like(v) or isinstance(v,list) or isinstance(v,tuple):
                something[k] = remove_fields(fields,v)

    elif isinstance(something,list) or isinstance(something,tuple):
        for x in something:
            # side effects. This will edit in place, but it's on the copy
            remove_fields(fields,x,onCopy=False)
    
    # else it's a string. just return it
    return something

def DEFAULT_PREPROC(x): return x

def compare_dict_lists(a,b,preProcessFunc=DEFAULT_PREPROC):
    aclone = []
    aclone.extend(a)
    bclone = []
    bclone.extend(b)
    for itema in a:
        posta = preProcessFunc(itema)
        found = False
        for itemb in bclone:
            postb = preProcessFunc(itemb)
            if posta == postb:
                found = True
                break
        if found:
            bclone.remove(itemb)
            aclone.remove(itema)
    return aclone,bclone
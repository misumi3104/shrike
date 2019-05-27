import webapp2,json,os,urllib
from google.appengine.ext.webapp import template, blobstore_handlers, RequestHandler
from google.appengine.api import urlfetch, app_identity, mail, memcache,taskqueue

def httpfunc_appengine(method,url,header,data):
    try:
        r=urlfetch.fetch(url=url, payload=data, method={"POST":urlfetch.POST,"GET":urlfetch.GET}[method], headers=header)
        return (r.status_code, r.content)
    except urlfetch.DownloadError, e:
        return e
def wsgiapp(accesstable):
    return webapp2.WSGIApplication(accesstable)
def textres(content,**kwargs):
    headers={}
    if "type" in kwargs:
        headers['Content-Type'] = kwargs["type"]
    return webapp2.Response(content,headers=headers)
def tempres(temp,params,**kwargs):
    tmp = os.path.join(os.path.dirname(__file__), "../" + temp)
    return textres(template.render(tmp, params),**kwargs)
def jsonres(content,**kwargs):
    kw={}
    if kwargs.get("indent",0):
        kw["indent"]=kwargs["indent"]
    content=json.dumps(content, **kw)
    return webapp2.Response(content,content_type="application/json")
def passres(uri):
    return webapp2.redirect(uri)
def requestjson(request):
    return json.loads(request.body)
def requestargs(request):
    result={}
    result.update(request.GET)
    result.update(request.POST)
    return result
def urlformat(formatstring,request,params):
    kwargs={}
    if params:
        kwargs.update({"params":urllib.urlencode(params)})
    if request:
        kwargs.update({"host":request.host_url,"path": request.path,"query":request.query_string})
    return formatstring.format(**kwargs)

def addtask(path,params):
    taskqueue.add(queue_name="default",url=path,params=params)

class BlobHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        self.send_blob(photo_key)
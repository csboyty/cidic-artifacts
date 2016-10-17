import urllib2
import ssl
import json
import httplib, urllib
def httpGet(url):
    print url
    try:
        gcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        f = urllib2.urlopen(url, context = gcontext)
        s = f.read()
        return True, s
    except :
        try:
            f = urllib2.urlopen(url)
            s = f.read()
            return True, s
        except:
            return False, None

def httpPost(url, data):
        if isinstance(data, dict):
            data = json.dumps(data)
        headers = {'Content-Type':'application/json', 'Accept':'application/json'}
        request = urllib2.Request(url = url, data = data, headers = headers)
        try:
            response = urllib2.urlopen(request)
            resp = response.read()
            return json.loads(resp)
        except Exception, e:
            print e
            return {"resultCode":512, "errMsg":"SERVER_OR_NETWORK_ERR"}

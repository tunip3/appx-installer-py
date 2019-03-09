import sys
import datetime
import requests
import urllib3
import os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XboxOneDevmodeApi(object):
    PORT = 11443

    def __init__(self, ip_addr):
        self.ip_addr = ip_addr
        self.base_url = 'https://{0}:{1}'.format(self.ip_addr, self.PORT)
        self.session = requests.session()

        # Console has self-signed / unverified cert
        # SSL verification is disabled here
        self.session.verify = False

    @property
    def _csrf_header(self):
        return {'X-CSRF-Token': self.session.cookies.get('CSRF-Token')}

    def _get(self, endpoint, *args, **kwargs):
        return self.session.get(self.base_url + endpoint, *args, **kwargs)

    def _post(self, endpoint, *args, **kwargs):
        return self.session.post(self.base_url + endpoint, headers=self._csrf_header, *args, **kwargs)

    def set_credentials(self, user, pwd):
        self.session.auth = (user, pwd)

    def get_root(self):
        return self._get('/')
    
    def install(self, filename):
        appx=open(filename, 'rb')
        files = {'upload_file': appx}
        url="/api/app/packagemanager/package?package="+filename
        return self._post(url, files=files)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('ERROR: Please provide IP address')
        print('Usage: {0} <ip> <username> <password>'.format(sys.argv[0]))
        sys.exit(1)
    
    ip_address = sys.argv[1]
    api = XboxOneDevmodeApi(ip_address)

    if len(sys.argv) == 4:
        username = sys.argv[2]
        password = sys.argv[3]
        api.set_credentials(username, password)

    r = api.get_root()
    if r.status_code != 200:
        print('ERROR: Authentication failed, HTTP Status: {0}'.format(r.status_code))
        sys.exit(2)

    ext=[".appx", ".appxbundle", ".msix", "msixbundle"]    
    for file in os.listdir(os.curdir):
        if file.endswith(tuple(ext)):
            api.install(file)

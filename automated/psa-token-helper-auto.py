import urllib.parse
import traceback
import requests
import hashlib
import secrets
import base64
import sys
import json
import argparse
import contextlib
from PyQt5.QtCore import QByteArray, QUrl, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlScheme, QWebEngineUrlSchemeHandler
from PyQt5 import QtWidgets, QtCore


QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons


def timeout():
    print("timeout")
    app.exit(1)


brands = {
    "citroen": {
        "scheme":       "mymacsdk",
        "realm":        "citroen.com",
        "clientid":     "5364defc-80e6-447b-bec6-4af8d1542cae",
        "clientsecret": "iE0cD8bB0yJ0dS6rO3nN1hI2wU7uA5xR4gP7lD6vM0oH0nS8dN",
    },
    "ds": {
        "scheme":       "mymdssdk",
        "realm":        "driveds.com",
        "clientid":     "cbf74ee7-a303-4c3d-aba3-29f5994e2dfa",
        "clientsecret": "X6bE6yQ3tH1cG5oA6aW4fS6hK0cR0aK5yN2wE4hP8vL8oW5gU3",
    },
    "opel": {
        "scheme":       "mymopsdk",
        "realm":        "opel.com",
        "clientid":     "07364655-93cb-4194-8158-6b035ac2c24c",
        "clientsecret": "F2kK7lC5kF5qN7tM0wT8kE3cW1dP0wC5pI6vC0sQ5iP5cN8cJ8",
    },
    "peugeot": {
        "scheme":       "mymap",
        "realm":        "peugeot.com",
        "clientid":     "1eebc2d5-5df3-459b-a624-20abfcf82530",
        "clientsecret": "T5tP7iS0cO8sC0lA2iE2aR7gK6uE5rF3lJ8pC3nO1pR7tL8vU1",
    },

}


parser = argparse.ArgumentParser(description='Automated PSA Token Helper', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("-b", "--brand", type=str, choices=brands.keys(), required=True, help="Vehicle brand")
parser.add_argument("-u", "--username", type=str, required=True, help="Username")
parser.add_argument("-p", "--password", type=str, required=True, help="Password")
parser.add_argument("-c", "--countrycode", type=str, default="de", help="Countrycode")
parser.add_argument("-t", "--timeout", type=int, default="15", help="Timeout between each step")

code_verifier = ""


def generate_sha256_pkce(length):
    if not (43 <= length <= 128):
        raise ValueError("Invalid length: %d" % length)
    verifier = secrets.token_urlsafe(length)
    encoded = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode('ascii')).digest())
    challenge = encoded.decode('ascii')[:-1]
    return verifier, challenge


class DummyUrlSchemeHandler(QWebEngineUrlSchemeHandler):
    def __init__(self):
        super().__init__()

    def requestStarted(self, request):
        return


class CustomUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()

    def interceptRequest(self, info):
        url = info.requestUrl()
        for brand, data in brands.items():
            if url.scheme() != data["scheme"]:
                continue
            try:
                window.timer.stop()
                url_params = urllib.parse.parse_qs(url.query())
                code = url_params["code"]
                post_url = f"https://idpcvs.{data['realm']}/am/oauth2/access_token"
                post_data = {
                    "grant_type":    "authorization_code",
                    "code":          code,
                    "code_verifier": code_verifier,
                    "redirect_uri":  data["scheme"]+"://oauth2redirect/"+args.countrycode.lower(),
                }
                auth = f"{data['clientid']}:{data['clientsecret']}"
                post_headers = {
                    "Authorization": "Basic " + base64.b64encode(auth.encode()).decode()
                }
                res = requests.post(post_url, data=post_data, headers=post_headers)
                res.raise_for_status()
                tokens = res.json()
                print(json.dumps(tokens, indent=4))
                app.exit(0)
            except Exception:
                print(traceback.format_exc())
                app.exit(1)


class WebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        pass


step = 0


def loadFinished():
    global step
    url = window.browser.url().toString()
    if 'OPLoginPage.php' in url:
        if step < 1:
            step = 1
            window.timer.stop()
            window.timer.start(args.timeout*1000)
        script = """
function fillform()
{
  let form = document.getElementById("gigya-login-form");
  if(form)
  {
    form.elements["username"].value=%%user%%;
    form.elements["password"].value=%%pass%%;
    for (let i = 0; i < form.elements.length; i++) {
      if (form.elements[i].type === "submit") {
        form.elements[i].click();
      }
    }
  }
  else
    setTimeout(fillform, 500);
}
setTimeout(fillform, 500);
        """
        window.browser.page().runJavaScript(script.replace("%%user%%", json.dumps(args.username)).replace("%%pass%%", json.dumps(args.password)))
    if 'authorize-consentments' in url:
        if step < 2:
            step = 2
            window.timer.stop()
            window.timer.start(args.timeout*1000)
        window.browser.page().runJavaScript("""
function clickconsent()
{
  let button = document.getElementById("consentbutton");
  if(button)
    button.click();
  else
    setTimeout(clickconsent, 500);
}
setTimeout(clickconsent, 500);
        """)


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.timer = QTimer(self)
        self.timer.timeout.connect(timeout)
        self.timer.start(args.timeout*1000)

        self.setWindowTitle("PSA Token Helper")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.browser = QWebEngineView()
        page = WebEnginePage(self.browser)
        self.browser.setPage(page)
        self.layout.addWidget(self.browser)

        self.interceptor = CustomUrlRequestInterceptor()
        self.browser.page().profile().setUrlRequestInterceptor(self.interceptor)

        for brand, data in brands.items():
            self.browser.page().profile().installUrlSchemeHandler(QByteArray(data["scheme"].encode()), DummyUrlSchemeHandler())

        self.browser.loadFinished.connect(loadFinished)

        url = f"https://idpcvs.{brands[args.brand]['realm']}/am/oauth2/authorize?client_id={brands[args.brand]['clientid']}&redirect_uri={brands[args.brand]['scheme']}%3A%2F%2Foauth2redirect%2F{args.countrycode.lower()}&response_type=code&scope=openid%20profile&code_challenge_method=S256&code_challenge={code_verifier}"
        self.browser.load(QUrl(url))

    def show_tokens(self, access, refresh):
        custom_html = f"""
<h1>Received Tokens:</h1>
<pre>
    accessToken: {access}
    refreshToken: {refresh}
</pre>
        """
        self.browser.setHtml(custom_html)

    def show_error(self, error):
        custom_html = f"""
<h1>Receive Tokens failed!</h1>
<pre>
{error}
</pre>
        """
        self.browser.setHtml(custom_html)


if __name__ == "__main__":

    with contextlib.redirect_stderr(sys.stdout):
        args, unknownargs = parser.parse_known_args()

    for brand, data in brands.items():
        QWebEngineUrlScheme.registerScheme(
            QWebEngineUrlScheme(QByteArray(data["scheme"].encode())))

    app = QApplication(unknownargs)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec_())

import requests
import sys
from requests import ReadTimeout


class Sender:
    # This implementation based from Quriiri: https://quriiri.fi/tekniset-resurssit/
    # which has been slightly updated to pass linters
    USER_AGENT = "Quriiri-TX-Python/1.0.1 %s" % requests.utils.default_user_agent()

    url = None
    session = None

    def __init__(self, apikey, url):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": Sender.USER_AGENT,
                "Authorization": "apikey %s" % apikey,
                "Content-Type": "application/json",
            }
        )
        self.url = url

    def __del__(self):
        self.session.close()

    def _fill_messages(self, resp, destinations, status):
        messages = resp.setdefault("messages", {})
        for destination in destinations:
            messages.setdefault(
                destination, {"converted": destination, "status": status}
            )

    def send_sms(self, sender, destination, text, **optional):
        if isinstance(destination, str):
            destination = (destination,)

        data = {
            "sender": sender,
            "destination": destination,
            "text": text,
        }

        for param in (
            "sendertype",
            "batchid",
            "billingref",
            "drurl",
            "drtype",
            "validity",
        ):
            value = optional.get(param)
            if value:
                data[param] = value
        if optional.get("flash"):
            data["flash"] = True

        req = requests.Request("POST", self.url, json=data)
        req = self.session.prepare_request(req)
        req.headers.pop("Accept", None)
        req.headers.pop("Accept-Encoding", None)

        implicit_status = "UNKNOWN"
        try:
            resp = self.session.send(req)
        except (ValueError, ReadTimeout):
            ex = sys.exc_info()[1]
            if isinstance(ex, requests.exceptions.ReadTimeout):
                key = "warnings"
            else:
                key = "errors"
                implicit_status = "FAILED"
            resp = {key: [{"message": repr(ex)}]}
        else:
            implicit_status, resp = self._format_response(implicit_status, resp)
        self._fill_messages(resp, destination, implicit_status)

        for key in "errors", "warnings":
            resp.setdefault(key, [])

        return resp

    @staticmethod
    def _format_response(implicit_status, resp):
        try:
            resp = resp.json()
        except ValueError:
            if resp.status_code >= 400:
                key = "errors"
                message = "HTTP %s %s" % (resp.status_code, resp.reason)
                implicit_status = "FAILED"
            else:
                key = "warnings"
                message = repr(sys.exc_info()[1])
            resp = {key: [{"message": message}]}
        else:
            if "errors" in resp and resp["errors"]:
                implicit_status = "FAILED"
        return implicit_status, resp

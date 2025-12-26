import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401


DEFAULT_BASE_URL = "https://api.ultramsg.com"


class Client(BaseClient):
    def __init__(self, token: str, instance: str, base_url: str = DEFAULT_BASE_URL, **kwargs):
        self.token = token
        self.instance = instance
        super().__init__(base_url=base_url, **kwargs)

    def send_chat_message(self, to: str, body: str, priority: int = 1) -> dict:
        return self._http_request(
            method="POST",
            url_suffix=f"/{self.instance}/messages/chat",
            data={
                "token": self.token,
                "to": to,
                "body": body,
                "priority": priority,
            },
        )

    def get_instance_status(self) -> dict:
        return self._http_request(
            method="GET",
            url_suffix=f"/{self.instance}/instance/status",
            params={"token": self.token},
        )


def send_whatsapp(client: Client, to: str, text: str) -> CommandResults:
    res = client.send_chat_message(to=to, body=text, priority=1)
    readable_output = tableToMarkdown("UltraMSG - WhatsApp message sent", res)
    return CommandResults(readable_output=readable_output, raw_response=res)


def test_module(client: Client) -> str:
    try:
        res = client.get_instance_status()
        status = (
            res.get("status", {})
            .get("accountStatus", {})
            .get("substatus")
        )
        if status == "connected":
            return "ok"
        if status:
            return f"Instance Status is: '{status}'. Should be 'connected'. Please check your instance."
        return "Unable to determine instance status. Please check your instance and token."
    except Exception:
        # Keep a user-friendly error message for test-module.
        return "Please check your instance and token."


def main():
    params = demisto.params()
    token = params.get("token")
    instance = params.get("instance")
    insecure = bool(params.get("insecure", False))
    use_proxy = bool(params.get("proxy", False))

    client = Client(
        token=token,
        instance=instance,
        verify=not insecure,
        proxy=use_proxy,
    )
    try:
        if demisto.command() == "send-whatsapp":
            to = demisto.args().get("id")
            text = demisto.args().get("text")
            if not to or not text:
                raise DemistoException("Both 'id' (phone number or group id) and 'text' are required.")
            return_results(send_whatsapp(client, to=to, text=text))
        elif demisto.command() == "test-module":
            return_results(test_module(client))
    except Exception as err:
        return_error(str(err))


if __name__ in ["__builtin__", "builtins", "__main__"]:
    main()

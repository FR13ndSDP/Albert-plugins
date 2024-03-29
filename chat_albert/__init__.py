"""chat GPT in albert

Synopsis: chat message|[g/t]
g: gpt-3.5-turbo
t: text-davinci-003
"""
# import threading
# import queue
from pathlib import Path
from time import sleep
import os
import openai
from albert import *

md_iid = "2.0"
md_version = "1.0"
md_id = "chat_albert"
md_name = "ChatGPT"
md_description = "Chat with GPT"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/"
md_lib_dependencies = "openai"
md_maintainers = "@Fr13ndSDP"

openai.api_key =
openai.organization =

os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"
os.environ["all_proxy"] = "socks5://127.0.0.1:7891"

definition = [
    {
        "role": "system",
        "content": "you are my helpful assitant, answear my questions in detail.",
    }
]

msg = []


def chat_reply(message):
    try:
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=message, temperature=1.0, request_timeout=30
        )
        return chat.choices[0].message.content
    except:
        return "Time's up!"


def completion_reply(message):
    try:
        complete = openai.Completion.create(
            model="text-davinci-003",
            prompt=message,
            temperature=0,
            max_tokens=512,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            request_timeout=20,
        )
        return complete.choices[0].text
    except:
        return "Time's up!"


class Plugin(PluginInstance, TriggerQueryHandler):
    def __init__(self):
        TriggerQueryHandler.__init__(self,
                                     id=md_id,
                                     name=md_name,
                                     description=md_description,
                                     defaultTrigger='chat ')
        PluginInstance.__init__(self, extensions=[self])
        self.icon = [f"file:{Path(__file__).parent}/Bot.png"]

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()
        global msg
        history = []
        # keep last 5 conversations
        if len(msg) > 10:
            msg = msg[-10:]

        if stripped:
            # give enough time to type
            for number in range(50):
                sleep(0.01)
                if not query.isValid:
                    return

            # start conversation only if stripped has "|"
            if len(stripped) >= 3:
                if (stripped[-1] == "g") & (stripped[-2] == "|"):
                    # display bot definition
                    query.add(
                        StandardItem(
                            id=md_id,
                            text=definition[0]["content"],
                            iconUrls=self.icon,
                            subtext="GPT Definition",
                        )
                    )

                    msg.append(
                        {"role": "user", "content": stripped[:-2]},
                    )
                    reply = chat_reply(definition + msg)
                    if reply == "Time's up!":
                        msg.pop(-1)
                    else:
                        msg.append({"role": "assistant", "content": reply})

                    item = StandardItem()
                    item.iconUrls = self.icon
                    item.subtext = "GPT says, Click to copy"
                    item.text = reply
                    item.actions = [
                        Action(
                            "copy",
                            "Copy result to clipboard",
                            lambda t=item.text: setClipboardText(t),
                        )
                    ]
                    query.add(item)
                elif (stripped[-1] == "t") & (stripped[-2] == "|"):
                    reply = completion_reply(stripped[:-2])
                    item = StandardItem()
                    item.iconUrls = self.icon
                    item.subtext = "GPT says, Click to copy"
                    item.text = reply.replace("\n", "")
                    item.actions = [
                        Action(
                            "copy",
                            "Copy result to clipboard",
                            lambda t=item.text: setClipboardText(t),
                        )
                    ]
                    query.add(item)
            if msg:
                # display chat history
                for item in msg:
                    history.append(item["content"])

                query.add(
                    StandardItem(
                        id=md_id,
                        text="\n".join(history),
                        iconUrls=self.icon,
                        subtext="History",
                        actions=[
                            Action(
                                "copy",
                                "Copy result to clipboard",
                                lambda t=str(msg): setClipboardText(t),
                            )
                        ],
                    )
                )

        else:
            query.add(
                StandardItem(
                    id=md_id,
                    text=md_name,
                    iconUrls=self.icon,
                    subtext="Enter message to chat",
                )
            )

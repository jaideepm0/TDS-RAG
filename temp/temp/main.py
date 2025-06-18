import json
import os
from pprint import pprint


def get_topic_list(f: dict) -> None:
    topic_list = data["topic_list"]
    if not os.path.exists("./topic_list.json"):
        with open("./topic_list.json", "w") as file:
            json.dump(topic_list, file)
    else:
        print("===The topic_list.json already existts===")
    return topic_list


def topics(f: dict) -> None:
    topics = f.get('topics')
    if not os.path.exists('./topics_list_topics.json'):
        with open('./topics_list_topics.json', 'w') as file:
            json.dump(topics, file)
    else:
        print("===Topics from topics_list has been extracted===")
    return topics


with open("./temp.json", "r") as f:
    data = json.load(f)
    c = get_topic_list(data)
    c = topics(c)
    pprint(c[0].keys())

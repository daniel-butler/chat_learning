import time

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
import spacy

nlp = spacy.load('en_core_web_sm')


@shared_task
def analyze_text(room_group_name, text):
    channel_layer = get_channel_layer()
    doc = nlp(text)
    vals = [f"{token.text}: {token.pos_} {token.dep_}" for token in doc]
    for count_down in reversed(range(5)):
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'chat_message',
                'message': f"Results in {count_down + 1}"
            }
        )
        time.sleep(1)

    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'chat_message',
            'message': f"{text=} {' '.join(vals)}",
        }
    )

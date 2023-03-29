import random
from collections import defaultdict
import time

from flask_socketio import emit

from statemanagement import global_state


logger = None


def send_history(participant):
    for utterance_info in global_state.participants[participant]['dialog_history']:
        emit('utterance', utterance_info)


def handle_utterance(participant, utterance, bot, socketio):
    utterance_info = {
        'role': 'user',
        'content': utterance
    }
    participant_info = global_state.participants[participant]
    participant_info['dialog_history'].append(utterance_info)
    session_id = participant_info['session_id']
    emit('utterance', utterance_info, to=session_id)
    socketio.start_background_task(
        get_and_process_response_from_bot, bot, participant_info['dialog_history'], session_id, socketio)


def get_and_process_response_from_bot(bot, dialog_history, session_id, socketio):
    logger.debug('getting response from bot')
    utterance = bot.get_response(dialog_history)
    logger.info('response from bot: ' + utterance)
    utterance_info = {
        'role': 'assistant',
        'content': utterance
    }
    dialog_history.append(utterance_info)
    socketio.emit('utterance', utterance_info, to=session_id)

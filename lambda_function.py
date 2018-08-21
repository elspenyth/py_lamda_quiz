"""
An enhanced version of the Alexa python skill kit basics, updated to function as a quiz game dealing with questions about flags.
"""

from __future__ import print_function
import json
from random import randint

questions = json.loads(open('questions.json').read())
alexa_phrases = ["Next question. ","Let's try this one. ","How about another flag. ", "let's see if you know this one. "]

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "QuizAnswer":
        return answer_question(intent, session)
    elif intent_name == "GetScore":
        return get_score(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help(intent, session)
    elif intent_name == "AMAZON.RepeatIntent":
        return repeat_question(intent, session)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {"score": 0, "total_questions": 0}
    card_title = "Welcome"
    next_index = randint(0, len(questions)-1)
    print(next_index)
    session_attributes['nextAnswer'] = questions.keys()[next_index]
    speech_output = "Let's start the game. You can ask me to repeat a question or to tell you your score at any time. I would describe your first flag as being " + questions[session_attributes['nextAnswer']]
    reprompt_text =  questions[session_attributes['nextAnswer']]

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_help(intent, session):
    card_title = "Help"
    should_end_session = False
    speech_output = "The way this game works is that I read out a description of a flag, and you tell me your best guess wchich country it belongs to. If you need to hear a description again, just ask me to repeat it. I am also keeping track of the number of correct answers you have given this game. You can request this by asking for your score. "
    speech_output += "Your current flag is. " + questions[session['attributes']['nextAnswer']]
    reprompt_text =  questions[session['attributes']['nextAnswer']]

    return build_response(session['attributes'], build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_score(intent, session):
    """ Say the score for this session """
    card_title = "Score"
    should_end_session = False
    score = session['attributes'].get('score', 0)
    total_questions = session['attributes'].get('total_questions', 0)
    speech_output = "So far you have correctly identified %d out of %d flags. " %(score, total_questions)

    speech_output += "Your current flag is. " + questions[session['attributes']['nextAnswer']]
    reprompt_text =  questions[session['attributes']['nextAnswer']]

    return build_response(session['attributes'], build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def repeat_question(intent, session):
    """ Say the score for this session """
    card_title = "Repeat"
    should_end_session = False

    speech_output = "Your current flag is. " + questions[session['attributes']['nextAnswer']]
    reprompt_text =  questions[session['attributes']['nextAnswer']]

    return build_response(session['attributes'], build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def answer_question(intent, session):
    """ Person answers the question and it's tested here and a new question is asked
    """

    card_title = intent['name']
    session_attributes = {
        'score': session['attributes'].get('score', 0),
        'total_questions': session['attributes'].get('total_questions', 0)
    }

    should_end_session = False

    speech_output = ""

    # Check the response is valid
    if 'Country' in intent['slots']:
        session_attributes['total_questions'] += 1
        answer = intent['slots']['Country']['value']
        if answer.lower() == session['attributes'].get('nextAnswer', 'Not set').lower():
            session_attributes['score'] += 1
            speech_output += "Correct! "
        else:
            speech_output += "Sorry, it was " + session['attributes'].get('nextAnswer', 'Not set yet') + ". "

    # Ask next question
    next_index = randint(0, len(questions)-1)
    aindex = randint(0, len(alexa_phrases)-1)
    session_attributes['nextAnswer'] = questions.keys()[next_index]
    speech_output += alexa_phrases[aindex] + questions[session_attributes['nextAnswer']]
    reprompt_text =  questions[session_attributes['nextAnswer']]

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
}

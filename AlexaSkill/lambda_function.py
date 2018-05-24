#REMINDER: Uncomment SMS Lines (Ctrl + F Search sms_body)
#======== HEALTHBUDDY LAMBDA FUNCTION ========#
#Author: Ernest Yeo 
#For: Nanyang Polytechnic Final Year Project
#Admin Number: 162995S
#Pre-Requisites: DynamoDB, Alexa Skills Kit, Amazon S3
#Grades: 
    #Target/Goal: DISTINCTION/A
    #Interim: A
    #Final: Distinction
#Email Credentials:
    #Email: censored
    #Password: censored
#======== CODES ARE NOT TO BE REUSED, DISTRIBUTED OR PUBLISHED IN ANY FORM WITHOUT PERMISSION ========#

from __future__ import print_function
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import dateutil.parser
import datetime
import time
import os
import math
import random
from decimal import Decimal
import smtplib


CardTitlePrefix = "HealthBuddy"

#====NOTE=====
# FOR AUDIO RESPONSES MAKE SURE THAT IT IS 90 SEC MAX AND BITRATE IS 48KPS, I USED AUDACITY

#================ JSON to build Responses =================
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    """
    Build a speechlet JSON representation of the title, output text, 
    reprompt text & end of session
    """

    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': CardTitlePrefix + " - " + title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_special_speechlet_response(title, output, reprompt_text, should_end_session):
    """
    Build a speechlet JSON representation of the title, output text, 
    reprompt text & end of session
    """

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title': CardTitlePrefix + " - " + title,
            'content': title
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_special_speechlet_response_noCard(output, reprompt_text, should_end_session):
    """
    Build a speechlet JSON representation of the title, output text, 
    reprompt text & end of session
    """

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
    
def build_response(session_attributes, speechlet_response):
    """
    Build the full response JSON from the speechlet response
    """
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
    
def build_SimpleCard(title, body):
    card = {}
    card['type'] = 'Simple'
    card['title'] = title
    card['content'] = body
    return card

def build_PlainSpeech(body):
    speech = {}
    speech['type'] = 'PlainText'
    speech['text'] = body
    return speech
    
def conversation(title, body, session_attributes):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
    speechlet['shouldEndSession'] = False
    return build_response(session_attributes, speechlet) 

def statement(title, body):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
    speechlet['shouldEndSession'] = False
    return build_response({}, speechlet)
    
"""def updateddialog():
    message = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    return build_response({},message) """

"""def updateddialog2():
    message = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    return build_response({},message) """

def elicit_slot(title, output, slot):
   return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title': CardTitlePrefix + " - " + title,
            'content': output
        },
        "directives": [ {
            "type": "Dialog.ElicitSlot",
            "slotToElicit": slot
        } ],
        'shouldEndSession' : False
    }

def elicit_slot2(title, output, slot):
   return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': CardTitlePrefix + " - " + title,
            'content': output
        },
        "directives": [ {
            "type": "Dialog.ElicitSlot",
            "slotToElicit": slot
        } ],
        'shouldEndSession' : False
    }

def send_sms(phoneNumber ,msg):
    sms_client = boto3.client('sns')
    sms_recipent = "+65" +str(phoneNumber)
    sms_client.publish(
        PhoneNumber = sms_recipent,
        Message = msg,
        MessageAttributes = {
            'AWS.SNS.SMS.SenderID': {
                'DataType': 'String',
                'StringValue': 'HealthBuddy' 
            }
        }
        )
#================================================================= INTENT ROUTER =======================================================
def on_intent(event, context):
    """ Called when the user specifies an intent for this skill """

    intent_request = event['request']
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    userID = event['session']['user']['userId']
    loggedin = get_session(userID,event)
    deviceID = event['context']['System']['device']['deviceId']
    configured = device_configured(deviceID)
    
    if configured:
        if intent_name == "StartRounding":
            if loggedin != 0:
                patientID = get_roundID(userID)
                languageSettings = get_User_LanguageSettings(patientID)
                if languageSettings == "English":
                    lastRoundingID = get_lastRounding(patientID)
                    if lastRoundingID !=0:
                        datetimeNow = str(datetime.datetime.now().strftime('%H:%M %d-%m-%Y'))
                        currentTime = datetime.datetime.strptime(datetimeNow, '%H:%M %d-%m-%Y')
                        
                        datetimeThen = get_lastRounding_Time(lastRoundingID)
                        lastRoundingTime = datetime.datetime.strptime(datetimeThen, '%H:%M %d-%m-%Y')
                        
                        nextTime = str(lastRoundingTime.strftime('%H:%M'))
                        nextDate = str(lastRoundingTime.strftime('%d-%B-%Y'))
                        nowTime = str(currentTime.strftime('%H:%M'))
                        nowDate = str(currentTime.strftime('%d-%B-%Y'))
                        
                        if currentTime > lastRoundingTime:
                            return start_Rounding(event)
                        elif currentTime < lastRoundingTime:
                            title = "Rounding Already Complete"
                            body = "You have already completed your rounding session for the hour, your next rounding session is due at " + nextTime + " on " + nextDate + " the time now is " +nowTime + "."
                            return statement(title, body)
                    else:
                        return start_Rounding(event)
                elif languageSettings == "Mandarin":
                    lastRoundingID = get_lastRounding(patientID)
                    if lastRoundingID !=0:
                        datetimeNow = str(datetime.datetime.now().strftime('%H:%M %d-%m-%Y'))
                        currentTime = datetime.datetime.strptime(datetimeNow, '%H:%M %d-%m-%Y')
                        
                        datetimeThen = get_lastRounding_Time(lastRoundingID)
                        lastRoundingTime = datetime.datetime.strptime(datetimeThen, '%H:%M %d-%m-%Y')
                        
                        nextTime = str(lastRoundingTime.strftime('%H:%M'))
                        nextDate = str(lastRoundingTime.strftime('%d-%B-%Y'))
                        nowTime = str(currentTime.strftime('%H:%M'))
                        nowDate = str(currentTime.strftime('%d-%B-%Y'))
                        
                        if currentTime > lastRoundingTime:
                            return start_Rounding_Chinese(event)
                        elif currentTime < lastRoundingTime:
                            title = "Rounding Already Complete"
                            
                            nextHour = str(lastRoundingTime.strftime('%I'))
                            nowHour = str(currentTime.strftime('%I'))
                            
                            intnextHour = int(nextHour)
                            intNowHour = int(nowHour)
                            
                            if intnextHour < 10:
                                if intNowHour == 2:
                                    nextHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/2.mp3'/>"
                                else:
                                    nextHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/" + str(intnextHour) + ".mp3'/>"
                            
                            if intnextHour == 10 or intnextHour == 12 or intnextHour == 11:
                                secondNumber = intnextHour - 10
                                if secondNumber == 2:
                                    nextHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/10.mp3'/><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/2.mp3'/>"
                                else:
                                    nextHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/10.mp3'/><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/" + str(secondNumber) + ".mp3'/>"
                            
                            if intNowHour < 10:
                                if intNowHour == 2:
                                    nowHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/2.mp3'/>"
                                else:
                                    nowHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/" + str(intNowHour) + ".mp3'/>"
                            
                            if intNowHour == 10 or intNowHour == 12 or intNowHour == 11:
                                secondNumber = intnextHour - 10
                                if secondNumber == 2:
                                    nowHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/10.mp3'/><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/2.mp3'/>"
                                else:
                                    nowHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/10.mp3'/><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/" + str(secondNumber) + ".mp3'/>"
                            
                            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_RoundingAlreadyDone.mp3"
                            audioBuilder = "<audio src='" + audioFileURL + "'/>"
                            
                            speech_output = "<speak>" +nowHourSpeech +audioBuilder +nextHourSpeech +" tien </speak>"
                            return build_response({}, build_special_speechlet_response(title,speech_output,speech_output,False))
                    else:
                        return start_Rounding_Chinese(event)
            elif loggedin == 0:
                return notloggedin()
        elif intent_name == "ChineseStartRounding":
            if loggedin != 0:
                patientID = get_roundID(userID)
                languageSettings = get_User_LanguageSettings(patientID)
                if languageSettings == "English":
                    lastRoundingID = get_lastRounding(patientID)
                    if lastRoundingID !=0:
                        datetimeNow = str(datetime.datetime.now().strftime('%H:%M %d-%m-%Y'))
                        currentTime = datetime.datetime.strptime(datetimeNow, '%H:%M %d-%m-%Y')
                        
                        datetimeThen = get_lastRounding_Time(lastRoundingID)
                        lastRoundingTime = datetime.datetime.strptime(datetimeThen, '%H:%M %d-%m-%Y')
                        
                        nextTime = str(lastRoundingTime.strftime('%H:%M'))
                        nextDate = str(lastRoundingTime.strftime('%d-%B-%Y'))
                        nowTime = str(currentTime.strftime('%H:%M'))
                        nowDate = str(currentTime.strftime('%d-%B-%Y'))
                        
                        if currentTime > lastRoundingTime:
                            return start_Rounding(event)
                        elif currentTime < lastRoundingTime:
                            title = "Rounding Already Complete"
                            body = "You have already completed your rounding session for the hour, your next rounding session is due at " + nextTime + " on " + nextDate + " the time now is " +nowTime + "."
                            return statement(title, body)
                    else:
                        return start_Rounding(event)
                elif languageSettings == "Mandarin":
                    lastRoundingID = get_lastRounding(patientID)
                    if lastRoundingID !=0:
                    	datetimeNow = str(datetime.datetime.now().strftime('%H:%M %d-%m-%Y'))
                    	currentTime = datetime.datetime.strptime(datetimeNow, '%H:%M %d-%m-%Y')
                    	
                    	datetimeThen = get_lastRounding_Time(lastRoundingID)
                    	lastRoundingTime = datetime.datetime.strptime(datetimeThen, '%H:%M %d-%m-%Y')
                    	
                    	nextTime = str(lastRoundingTime.strftime('%H:%M'))
                    	nextDate = str(lastRoundingTime.strftime('%d-%B-%Y'))
                    	nowTime = str(currentTime.strftime('%H:%M'))
                    	nowDate = str(currentTime.strftime('%d-%B-%Y'))
                    	
                    	if currentTime > lastRoundingTime:
                    		return start_Rounding_Chinese(event)
                    	elif currentTime < lastRoundingTime:
                    		title = "Rounding Already Complete"
                    		
                    		nextHour = str(lastRoundingTime.strftime('%I'))
                    		nowHour = str(currentTime.strftime('%I'))
                    		
                    		intnextHour = int(nextHour)
                    		intNowHour = int(nowHour)
                    		
                    		if intnextHour < 10:
                    			if intNowHour == 2:
                    				nextHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/2.mp3'/>"
                    			else:
                    				nextHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/" + str(intnextHour) + ".mp3'/>"
                    		
                    		if intnextHour == 10 or intnextHour == 12 or intnextHour == 11:
                    			secondNumber = intnextHour - 10
                    			if secondNumber == 2:
                    				nextHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/10.mp3'/><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/2.mp3'/>"
                    			else:
                    				nextHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/10.mp3'/><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/" + str(secondNumber) + ".mp3'/>"
                    		
                    		if intNowHour < 10:
                    			if intNowHour == 2:
                    				nowHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/2.mp3'/>"
                    			else:
                    				nowHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/" + str(intNowHour) + ".mp3'/>"
                    		
                    		if intNowHour == 10 or intNowHour == 12 or intNowHour == 11:
                    			secondNumber = intnextHour - 10
                    			if secondNumber == 2:
                    				nowHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/10.mp3'/><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/2.mp3'/>"
                    			else:
                    				nowHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/10.mp3'/><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/" + str(secondNumber) + ".mp3'/>"
                    		
                    		audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_RoundingAlreadyDone.mp3"
                    		audioBuilder = "<audio src='" + audioFileURL + "'/>"
                    		
                    		speech_output = "<speak>" +nowHourSpeech +audioBuilder +nextHourSpeech +" tien </speak>"
                    		return build_response({}, build_special_speechlet_response(title,speech_output,speech_output,False))
                    else:
                        return start_Rounding_Chinese(event)
            elif loggedin == 0:
                return notloggedin()
        elif intent_name == "LastRoundingIntent":
            if loggedin != 0:
                return myLastRounding(event)
            elif loggedin== 0:
                return notloggedin()
        elif intent_name == "RoundingSummary":
            if loggedin != 0:
                return roundingSummary(event)
            elif loggedin == 0:
                return notloggedin()
        elif intent_name == "EmergencyIntent":
            if loggedin!= 0:
                return call_urgent(event)
            elif loggedin == 0:
                return notloggedin()
        elif intent_name == "DietIntent":
            if loggedin!= 0:
                return set_diet(event)
            elif loggedin == 0:
                return notloggedin()
        elif intent_name == "MedicalConditionInfo":
            return get_Condition(event)
        elif intent_name == "SignInIntent":
            if loggedin != 0:
                title = "Please Sign Out"
                body = "You are already signed in, please sign out first."
                return statement(title, body)
            elif loggedin == 0:
                return signIn(event)
        elif intent_name == "ChangeUserIntent":
            return change_user(event['session']['user']['userId'],event)
        elif intent_name == "AddPatientIntent":
            return register_user(event)
        elif intent_name == "DeviceSettingsIntent":
            return device_settings(event)
        elif intent_name == "UserSettingsIntent":
            if loggedin != 0:
                return user_settings(event)
            elif loggedin == 0:
                return notloggedin()
        elif intent_name == "ChangeSettings":
            if loggedin != 0:
                patientID = get_roundID(userID)
                languageSettings = get_User_LanguageSettings(patientID)
                if languageSettings == "English":
                    return change_settings(event)
                elif languageSettings == "Mandarin":
                    return update_user_settings_Chinese(event)
            elif loggedin == 0:
                return notloggedin()
            return change_settings(event)
        elif intent_name == "DeletePatientIntent":
            return delete_patient(event, userID)
        elif intent_name == "ChineseStartRounding":
            if loggedin != 0:
                patientID = get_roundID(userID)
                languageSettings = get_User_LanguageSettings(patientID)
                if languageSettings == "English":
                    lastRoundingID = get_lastRounding(patientID)
                    if lastRoundingID !=0:
                        datetimeNow = str(datetime.datetime.now().strftime('%H:%M %d-%m-%Y'))
                        currentTime = datetime.datetime.strptime(datetimeNow, '%H:%M %d-%m-%Y')
                        
                        datetimeThen = get_lastRounding_Time(lastRoundingID)
                        lastRoundingTime = datetime.datetime.strptime(datetimeThen, '%H:%M %d-%m-%Y')
                        
                        nextTime = str(lastRoundingTime.strftime('%H:%M'))
                        nextDate = str(lastRoundingTime.strftime('%d-%B-%Y'))
                        nowTime = str(currentTime.strftime('%H:%M'))
                        nowDate = str(currentTime.strftime('%d-%B-%Y'))
                        
                        if currentTime > lastRoundingTime:
                            return start_Rounding(event)
                        elif currentTime < lastRoundingTime:
                            title = "Rounding Already Complete"
                            body = "You have already completed your rounding session for the hour, your next rounding session is due at " + nextTime + " on " + nextDate + " the time now is " +nowTime + "."
                            return statement(title, body)
                    else:
                        return start_Rounding(event)
                elif languageSettings == "Mandarin":
                    lastRoundingID = get_lastRounding(patientID)
                    if lastRoundingID !=0:
                    	datetimeNow = str(datetime.datetime.now().strftime('%H:%M %d-%m-%Y'))
                    	currentTime = datetime.datetime.strptime(datetimeNow, '%H:%M %d-%m-%Y')
                    	
                    	datetimeThen = get_lastRounding_Time(lastRoundingID)
                    	lastRoundingTime = datetime.datetime.strptime(datetimeThen, '%H:%M %d-%m-%Y')
                    	
                    	nextTime = str(lastRoundingTime.strftime('%H:%M'))
                    	nextDate = str(lastRoundingTime.strftime('%d-%B-%Y'))
                    	nowTime = str(currentTime.strftime('%H:%M'))
                    	nowDate = str(currentTime.strftime('%d-%B-%Y'))
                    	
                    	if currentTime > lastRoundingTime:
                    		return start_Rounding_Chinese(event)
                    	elif currentTime < lastRoundingTime:
                    		title = "Rounding Already Complete"
                    		
                    		nextHour = str(lastRoundingTime.strftime('%I'))
                    		nowHour = str(currentTime.strftime('%I'))
                    		
                    		intnextHour = int(nextHour)
                    		intNowHour = int(nowHour)
                    		
                    		if intnextHour < 10:
                    			if intNowHour == 2:
                    				nextHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/2.mp3'/>"
                    			else:
                    				nextHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/" + str(intnextHour) + ".mp3'/>"
                    		
                    		if intnextHour == 10 or intnextHour == 12 or intnextHour == 11:
                    			secondNumber = intnextHour - 10
                    			if secondNumber == 2:
                    				nextHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/10.mp3'/><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/2.mp3'/>"
                    			else:
                    				nextHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/10.mp3'/><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/" + str(secondNumber) + ".mp3'/>"
                    		
                    		if intNowHour < 10:
                    			if intNowHour == 2:
                    				nowHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/2.mp3'/>"
                    			else:
                    				nowHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/" + str(intNowHour) + ".mp3'/>"
                    		
                    		if intNowHour == 10 or intNowHour == 12 or intNowHour == 11:
                    			secondNumber = intnextHour - 10
                    			if secondNumber == 2:
                    				nowHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/10.mp3'/><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/2.mp3'/>"
                    			else:
                    				nowHourSpeech = "<audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/10.mp3'/><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_Number/" + str(secondNumber) + ".mp3'/>"
                    		
                    		audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_RoundingAlreadyDone.mp3"
                    		audioBuilder = "<audio src='" + audioFileURL + "'/>"
                    		
                    		speech_output = "<speak>" +nowHourSpeech +audioBuilder +nextHourSpeech +" tien </speak>"
                    		return build_response({}, build_special_speechlet_response(title,speech_output,speech_output,False))
                else:
                    return start_Rounding_Chinese(event)
            elif loggedin == 0:
                return notloggedin()
        elif intent_name == "WhosInWard":
            return whos_in_ward(event)
        elif intent_name =="ReconfigureDevice":
            return reconfigure_device(event)
        elif intent_name == "ForgotAccount":
            return forgot_account(event)
        elif intent_name == "WhosInBed":
            return whos_in_Bed(event)
        elif intent_name == "WhereAmI":
            return where_am_I(event)
        elif intent_name == "FeedbackIntent":
            if loggedin != 0:
                return send_Feedback(event)
            elif loggedin == 0:
                return notloggedin()
        elif intent_name == "AMAZON.HelpIntent":
            return handle_help_request()
        elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
            return handle_session_end_request(event)
        elif intent_name == "TestIntent":
            return Numbers_Chinese_Test(event)
        else:
            #raise ValueError("Invalid intent")
            return valueError()
    #If the Device is not configured I will BLOCK all Functions        
    elif not configured:
        if intent_name == "DeviceSettingsIntent":
            return device_settings(event)
        elif intent_name == "AMAZON.HelpIntent":
            return not_configured_handle_help_request()
        elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
            return not_configured_handle_session_end_request_(event)
        else: 
            return notConfiguredMessage()
    
def notloggedin():
    title = "Please Sign In"
    body = "You are currently not signed in to any accounts, please sign in first."
    return statement(title, body)

def valueError():
    title = "Invalid Intent"
    body = "Sorry, I did not catch you. Please say Help for available commands"
    return statement(title, body)

def notConfiguredMessage():
    attributes = {}
    card_title = "Please Configure Your Device First"
    speech_output = "You are not allowed to perform that operation as your device has not been configured. " +\
                    "Please configure your device first by saying configure device."
    return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,False))
#============================================= FUNCTIONS ========================================================================================
#=============== BASICS ==================
"""Welcome Card and Speech (COMPLETED)"""
def get_welcome_response(event):
    userID = event['session']['user']['userId']
    patientID = get_roundID(userID)
    deviceID = event['context']['System']['device']['deviceId']
    configured = device_configured(deviceID)
    #If Configured
    if configured:
        if get_session(userID, event) == 1:
            userLanguageSettings = get_User_LanguageSettings(patientID)
            if PatientinRounding(patientID) == 0 :
                if userLanguageSettings == "English":
                    """ For the session to have some attributes"""
                    attributes = {}
                    card_title = "Welcome"
                    speech_output = "Welcome back to HealthBuddy, "+ str(get_inUse(userID,event)) +". Say Start Rounding to Start Your Rounding Session"
                    should_end_session = False
                    return build_response(attributes,build_speechlet_response(card_title, speech_output, "Say Start Rounding to Start Your Rounding Session", should_end_session))
                elif userLanguageSettings == "Mandarin": #(NOT DONE)
                    attributes = {}
                    card_title = "欢迎"
                    
                    audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_WelcomeRound.mp3"
                    audioBuilder = "<audio src = '" +audioFileURL +"'/>"
                    speech_output = "<speak>"+ audioBuilder +"</speak>"
                    should_end_session = False
                    return build_response(attributes,build_special_speechlet_response(card_title, speech_output, speech_output, should_end_session))
            elif PatientinRounding(patientID) != 0:
                attributes = PatientinRounding(patientID)
                card_title = "Welcome"
                speech_output = "Welcome back to HealthBuddy, "+ str(get_inUse(userID,event)) +". You have a rounding session in progress, say Start Rounding to Resume Your Rounding Session"
                should_end_session = False
                return build_response(attributes,build_speechlet_response(card_title, speech_output, "Say Start Rounding to Start Your Rounding Session", should_end_session))
        else:
            """ For the session to have some attributes"""
            attributes = {}
            card_title = "Welcome"
            should_end_session = False
            speech_output = "Welcome to HealthBuddy ! Say Create Account to start your first time setup or Sign in by saying Sign in."
            return build_response(attributes,build_speechlet_response(card_title, speech_output, "Please Start your first time setup or Sign in by saying Sign in", should_end_session))
    #If Not Configured
    elif not configured:
        attributes = {}
        card_title = "Welcome"
        speech_output = "Welcome to Health Buddy. I've noticed that this is your first time in HealthBuddy. To Begin using Health Buddy, Please First Configure this Device by saying configure device. "
        should_end_session = False
        return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,False))

"""Goodbye Card and Speech"""
#Configured
def handle_session_end_request(event):
    """If User quits halfways during rounding"""
    if event['session'].get('attributes'):
        if event['session']['attributes'].get('current_question_no'):
            if int(event['session']['attributes']['current_question_no']) != 2:
                attributes = event['session']['attributes']
                """Insert Attribute Map into Database For The Patient"""
                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                table = dynamodb.Table('Patients')
                userID = event['session']['user']['userId']
                roundingID = get_roundID(userID)
                response = table.update_item(
                    Key={
                        "RoundingID" : roundingID
                    },
                    UpdateExpression="SET UserSession =:q",
                    ExpressionAttributeValues={
                        ':q' : attributes
                    },
                    ReturnValues="UPDATED_NEW"
                    )
                """Return Response"""
                card_title = "Session Saved"
                speech_output = "Thank You for Using HealthBuddy. Have a nice day!"
                # Setting this to true ends the session and exits the skill.
                should_end_session = True
                return build_response({}, build_speechlet_response(
                    card_title, speech_output, None, should_end_session))
    else:    
        card_title = "Session Ended"
        speech_output = "Thank You for Using HealthBuddy. Have a nice day!"
        # Setting this to true ends the session and exits the skill.
        should_end_session = True
        return build_response({}, build_speechlet_response(
            card_title, speech_output, None, should_end_session))
#Not Configured
def not_configured_handle_session_end_request_(event):
    card_title = "Session Ended"
    speech_output = "Thank You for Using HealthBuddy. You can Configure Your Device anytime. Have a nice day!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    attributes = {}
    return build_response(attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

"""Help Function"""
#Not Configured
def not_configured_handle_help_request():
    card_title = "Help"
    speech_output = "You have not configured this device, to configure this device, say Configure device"
    should_end_session = False
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session)) 
#Configured
def handle_help_request():
    card_title = "Help"
    speech_output = "Here are the list of commands you can use. Start Rounding, View Account Settings, Change Account Settings, Change Device Settings, View Device Settings."
    should_end_session = False
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

#=============== METHODS =================
#================= WORKING=================
"""Check if Account Exists 
If an account exists with the User ID provided, the method returns 1"""
def get_session(userID,event):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    deviceID = event['context']['System']['device']['deviceId']
    response = table.scan(
    FilterExpression = Attr("DeviceID").eq(deviceID) & Attr("userID").eq(userID) & Attr("inUse").eq(1)
    )
    result = len(response["Items"])
    if result == 0:
        return 0
    else:
        return 1
        
"""Get Patient Name from roundingID"""
def get_username(roundingID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.get_item(
            Key={
                'RoundingID' : roundingID
            }
        )
    return response["Item"]["patientname"]

"""Get the name of the current account in use for the userID"""        
def get_inUse(userID,event):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    deviceID = event['context']['System']['device']['deviceId']
    response = table.scan(
        FilterExpression = Attr("userID").eq(userID) & Attr("inUse").eq(1) & Attr("DeviceID").eq(deviceID)
        )
    for current in response["Items"]:
        name  = current["patientname"]
        return name

"""Get RoundingID of CURRENT USER from User ID"""        
def get_roundID(userID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
        FilterExpression = Attr("userID").eq(userID) and Attr("inUse").eq(1)
        )
    for current in response["Items"]:
        RoundingID  = current["RoundingID"]
        return RoundingID
        
"""Get The RoundingID For The Last Patient Inserted (Patient Table)
This serves as the Auto-Increment PK for the Patient Table"""
def get_max_RoundingID():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('PatientIDs')
    response = table.scan(
         FilterExpression = Attr("PatientID").eq(0)
        )
    for id in response["Items"]:
        max = id["MaxID"]
        return int(max)
        
"""Get The RoundingID For The Last Rounding Done by patients (Roundings Table)
This serves as the Auto-Increment PK for the Patient Table"""
def get_max_roundingID2():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('PatientIDs')
    response = table.scan(
         FilterExpression = Attr("PatientID").eq(1)
        )
    for id in response["Items"]:
        max = id["MaxID"]
        return int(max)
        
"""After that you have to update the PK in the PatientID table"""
def update_max_RoundingID(newID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('PatientIDs')
    key = 0
    response = table.update_item(
        Key={
            "PatientID" : key
        },
        UpdateExpression="SET MaxID =:q",
        ExpressionAttributeValues={
            ':q' : newID
        },
        ReturnValues="UPDATED_NEW"
        )
    return response
    
"""After that you have to update the PK in the PatientID table"""
def update_max_RoundingID2(newID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('PatientIDs')
    key = 1
    response = table.update_item(
        Key={
            "PatientID" : key
        },
        UpdateExpression="SET MaxID =:q",
        ExpressionAttributeValues={
            ':q' : newID
        },
        ReturnValues="UPDATED_NEW"
        )
    return response    

"""Check if the user is in the state of rounding(Rounding Halfway) - Followed up in Welcome Message"""
def PatientinRounding(patientID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
         FilterExpression = Attr("RoundingID").eq(patientID)
        )
    for stuff in response["Items"]:
        if stuff["UserSession"] != 0 :
            return stuff["UserSession"]
        else:
            return 0

"""Set Restore Session to Default On Rounding Completion"""
def patientCompleteRounding(patientID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.update_item(
    Key={
        "RoundingID" : patientID
    },
    UpdateExpression="SET UserSession =:q",
    ExpressionAttributeValues={
        ':q' : 0
    },
    ReturnValues="UPDATED_NEW"
    )
    return response
    
"""Retrieves the Latest Rounding ID Completed by A Patient"""
def get_lastRounding(patientID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Roundings')
    response = table.scan(
        FilterExpression = Attr("PatientID").eq(patientID) and Attr("Latest").eq(1)
        )
    if len(response['Items']) > 0:
        for latest in response["Items"]:
            roundingID  = latest["RoundingID"]
            return roundingID
    else:
        return 0
        
"""Update to Set Lastest to False"""
def expire_Rounding(patientID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Roundings')
    roundingID = get_lastRounding(patientID)
    response = table.update_item(
        Key={
            "RoundingID" : roundingID
        },
        UpdateExpression="SET Latest =:q",
        ExpressionAttributeValues={
            ':q' : 0
        },
        ReturnValues="UPDATED_NEW"
        )
    return response
    
"""Get Last RoundingTime"""
def get_lastRounding_Time(roundingID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Roundings')
    response = table.scan(
        FilterExpression = Attr("RoundingID").eq(roundingID)
        )
    if len(response['Items']) > 0:
        for latest in response["Items"]:
            nextRounding  = latest["NextRounding"]
            return nextRounding
 
"""Answer Slot Validation"""
def validateAnswer(answer):
    try:
        val = int(answer)
        return True
    except ValueError:
        return False
        
"""Validate Phone Number if it exists"""
def validateNumber(phoneNumber):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
        FilterExpression = Attr("phoneNumber").eq(phoneNumber)
        )
    if len(response['Items']) > 0:
        return 1
    else:
        return 0

"""Get InUse Number"""
def get_inUse_Phone(userID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
        FilterExpression = Attr("userID").eq(userID) & Attr("inUse").eq(1)
        )
    for current in response["Items"]:
        phoneNumber  = current["phoneNumber"]
        return phoneNumber

"""Get Phone from RoundingID"""
def get_User_Phone(roundingID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
        FilterExpression = Attr("RoundingID").eq(roundingID)
        )
    #If Found Return the Phone
    if len(response["Items"]) == 1:
        for item in response["Items"]:
            phoneNumber = item["phoneNumber"]
            return phoneNumber
    elif len(response["Items"]) == 0:
        return 0
        
"""Get LanguageSettings from RoundingID"""
def get_User_LanguageSettings(roundingID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
        FilterExpression = Attr("RoundingID").eq(roundingID)
        )
    #If Found Return the Language
    if len(response["Items"]) == 1:
        for item in response["Items"]:
            LanguageSettings = item["LanguageSettings"]
            return LanguageSettings
    elif len(response["Items"]) == 0:
        return 0
        
""" It returns 0 if no account, return Rounding ID if found"""
def get_RoundingID_from_Phone(phoneNumber):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
        FilterExpression = Attr("phoneNumber").eq(phoneNumber)
        )
    #If Found Return the Rounding ID
    if len(response["Items"]) == 1:
        for rounding in response["Items"]:
            roundingID = rounding["RoundingID"]
            return roundingID
    elif len(response["Items"]) == 0:
        return 0

"""Get RoundingID from Name"""
"""Returns roundingID if Only 1 Account Exists, returns 0/-1 otherwise (-1 means more than 1 account), (0 means no account)"""
def get_RoundingID_from_Name(patientName):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
        FilterExpression = Attr("patientname").eq(patientName)
        )
    #If Found
    if len(response["Items"]) > 0:
        #If Duplicate
        if len(response["Items"]) > 1: 
            return -1
        elif len(response["Items"]) == 1:
            for rounding in response["Items"]:
                roundingID = rounding["RoundingID"]
                return roundingID 
    elif len(response["Items"]) == 0:
        return 0
    
    
#============================== INTENTS ============================================
#============================== USER ACCOUNT MANAGEMENT ============================
#===== Create Account (ENGLISH & CHINESE) =====
def register_user(event):
    audio_output = ""
    userID = event['session']['user']['userId']
    deviceID = event['context']['System']['device']['deviceId']
    dialog_state = event['request']['dialogState']
    if not event['request']['intent']['slots']['language'].get('value'):
        card_title = ""
        speech_output = "<speak>What is your preferred language? Chinese, or English? -- <audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignUp/ZH_SignUp1.mp3'/></speak>"
        reprompt_string = ""
        return build_response({},elicit_slot(card_title, speech_output, "language")) 
    elif event['request']['intent']['slots']['language'].get('value'):
        languageSettings = event['request']['intent']['slots']['language']['resolutions']['resolutionsPerAuthority']
        for items in languageSettings:
            if items.get('values'):
                for items in items['values']:
                    language = items['value']['name']
            else:
                language = event['request']['intent']['slots']['language']['value']
            
        if language == "English":
            #== ask for name
            if not event['request']['intent']['slots']['fullname'].get('value'):
                card_title = ""
                speech_output = "Please tell me your name."
                reprompt_string = ""
                return build_response({},elicit_slot2(card_title, speech_output, "fullname"))
            if event['request']['intent']['slots']['fullname'].get('value'):
                #==ask for phone
                if not event['request']['intent']['slots']['phoneNumber'].get('value'):
                    card_title = ""
                    speech_output = "What is your phone number?"
                    reprompt_string = ""
                    return build_response({},elicit_slot2(card_title, speech_output, "phoneNumber"))
                elif event['request']['intent']['slots']['phoneNumber'].get('value'):
                    slots = event['request']['intent']['slots']['fullname']['value']
                    phone = event['request']['intent']['slots']['phoneNumber']['value']
                    userID  = event['session']['user']['userId']
                    validation = validateNumber(phone)
                    if validation == 0:
                        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                        table = dynamodb.Table('Patients')
                        roundingID = get_max_RoundingID() + 1
                        response = table.put_item(
                                Item = {
                                    "RoundingID": roundingID,
                                    "userID": userID,
                                    "patientname": slots,
                                    "inUse": 0,
                                    "phoneNumber" : phone,
                                    "UserSession" : 0,
                                    "LanguageSettings": "English",
                                    "DeviceID": deviceID
                                }
                            )
                        response2 = update_max_RoundingID(roundingID) #Update it to give the new maxRoundingID
                        card_title = "Patient Added"
                        speech_output = "Completed"+ ", -- " +slots + " has been added to the Patient List. Say Sign in to Sign in Now"
                        reprompt_string = ""
                        return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_string , False))
                    elif validation == 1:
                        card_title = ""
                        speech_output = "<speak>There is already an account registered with that number, please say another number.</speak>"
                        return build_response({},elicit_slot(card_title, speech_output, "phoneNumber")) 
        elif language == "Mandarin":
            #If Full Name not Filled
            if not event['request']['intent']['slots']['fullname'].get('value'):
                card_title = ""
                speech_output = "<speak><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignUp/ZH_SignUp2.mp3'/></speak>"
                reprompt_string = ""
                return build_response({},elicit_slot(card_title, speech_output, "fullname"))   
            #Now get Phone Number
            elif event['request']['intent']['slots']['fullname'].get('value'):
                fullname = event['request']['intent']['slots']['fullname']['value']
                if not event['request']['intent']['slots']['ZH_phoneNumber'].get('value'):
                    attributes = {
                        'idx' : 0,
                        'value': "",
                        'speech': []
                    }
                    card_title = ""
                    speech_output = "<speak><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_GetPhoneNumber.mp3'/></speak>"
                    reprompt_string = ""
                    return build_response(attributes,elicit_slot(card_title, speech_output, "ZH_phoneNumber"))
                elif event['request']['intent']['slots']['ZH_phoneNumber'].get('value'):
                    previousNo = str(event['request']['intent']['slots']['ZH_phoneNumber']['value'])
                    NumberMatch = "ER_SUCCESS_NO_MATCH"
                    providedNumber = event['request']['intent']['slots']['ZH_phoneNumber']['resolutions']['resolutionsPerAuthority']
                    for items in providedNumber:
                        if items.get('values'):
                            for items in items['values']:
                                previousNo = str(items['value']['name'])
                    for items in providedNumber:    
                        if items.get('status'):
                            NumberMatch = items['status']['code']
                    idxValue = int(event['session']['attributes']['idx'])
                    spoken = list(event['session']['attributes']['speech'])
                    #If match will be ER_SUCCESS_MATCH . If no match then ER_SUCCESS_NO_MATCH
                    if NumberMatch == "ER_SUCCESS_MATCH" and previousNo != "10": 
                        if idxValue == 0:
                            idx =  idxValue + 1
                            spoken.extend([previousNo])
                            attributes = {
                                'idx': idx ,
                                'value': previousNo,
                                'speech': spoken
                            }
                            speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/" +previousNo +".mp3'/></speak>"
                            return build_response(attributes, elicit_slot("",speech_output,"ZH_phoneNumber"))
                        while idxValue > 0 and idxValue < 7:
                            idx = idxValue + 1
                            spoken.extend([previousNo])
                            phoneNumber = event['session']['attributes']['value']
                            newNumber = phoneNumber + previousNo
                            attributes = {
                                  'idx': idx,
                                  'value': newNumber,
                                  'speech': spoken
                                }
                            speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/" +previousNo +".mp3'/></speak>"
                            return build_response(attributes,elicit_slot("",speech_output,"ZH_phoneNumber"))
                        else:
                            index = 0
                            number = str(event['session']['attributes']['value'])
                            spoken.extend([previousNo])
                            chineseList = spoken
                            for items in chineseList:
                                if items == "0":
                                    audio_output += "<emphasis level='strong'>lin -- </emphasis> "
                                elif items == "1":
                                    audio_output += "<emphasis level='strong'>y'all -- </emphasis>"
                                elif items == "2":
                                    audio_output += "<emphasis level='strong'>aer -- </emphasis>"
                                elif items == "3":
                                    audio_output += "<emphasis level='strong'>sun -- </emphasis>"
                                elif items == "4":
                                    audio_output += "<emphasis level='strong'>shi -- </emphasis>"
                                elif items == "5":
                                    audio_output += "<emphasis level='strong'>wu -- </emphasis>"
                                elif items == "6":
                                    audio_output += "<emphasis level='strong'>leo -- </emphasis>"
                                elif items == "7":
                                    audio_output += "<emphasis level='strong'>qi -- </emphasis>"
                                elif items == "8":
                                    audio_output += "<emphasis level='strong'>bhar -- </emphasis>"
                                elif items == "9":
                                    audio_output += "<emphasis level='strong'>jail -- </emphasis>"
            
                                    
                            returnNumber = number + previousNo
                            
                            validation = validateNumber(returnNumber)
                            if validation == 0:
                                attributes = {
                                'idx': idxValue,
                                'value': returnNumber,
                                }
                                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                table = dynamodb.Table('Patients')
                                roundingID = get_max_RoundingID() + 1
                                response = table.put_item(
                                        Item = {
                                            "RoundingID": roundingID,
                                            "userID": userID,
                                            "patientname": fullname,
                                            "inUse": 0,
                                            "phoneNumber" : returnNumber,
                                            "UserSession" : 0,
                                            "LanguageSettings": "Mandarin",
                                            "DeviceID" : deviceID
                                        }
                                    )
                                response2 = update_max_RoundingID(roundingID) #Update it to give the new maxRoundingID
                                card_title = "帐户创建成功"
                                
                                NameaudioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignUp/ZH_Name.mp3"
                                NumberaudioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignUp/ZH_PhoneNumber.mp3"
                                ConfirmationAudioURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignUp/ZH_SignUp5.mp3"
                                
                                NameaudioBuilder = "<audio src = '" +NameaudioFileURL + "'/> "
                                NumberaudioBuilder = "<audio src = '" +NumberaudioFileURL + "'/> "
                                ConfirmationaudioBuilder = "<audio src = '" +ConfirmationAudioURL + "'/> "
                                
                                NameOutput = NameaudioBuilder +" " +fullname
                                NumberOutput = NumberaudioBuilder +" " +audio_output
                                
                                speech_output = "<speak>"
                                speech_output_end = "</speak>"
                                
                                returnSpeech = speech_output + NameOutput + NumberOutput + "." +ConfirmationaudioBuilder +" Sign In." +speech_output_end
                                
                                return build_response(attributes, build_special_speechlet_response(card_title, returnSpeech, returnSpeech , False))
                            elif validation == 1:
                                attributes = {
                                    'idx' : 0,
                                    'value': "",
                                    'speech': []
                                }
                                card_title = ""
                                speech_output = "<speak><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignUp/ZH_SignUp6.mp3'/></speak>"
                                return build_response(attributes,elicit_slot(card_title, speech_output, "ZH_phoneNumber"))
                    elif NumberMatch == "ER_SUCCESS_NO_MATCH" or previousNo == "10":
                        phoneNumber = event['session']['attributes']['value']
                        attributes = {
                            'idx': idxValue,
                            'value': phoneNumber,
                            'speech': spoken
                        }
                        if previousNo == "10":
                            card_title = "Number out of Range"
                            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/ZH_PhoneNoTens.mp3"
                            speech_output = "<speak><audio src = '" +audioFileURL +"' /></speak>"
                            return build_response(attributes, elicit_slot(card_title,speech_output,"ZH_phoneNumber"))
                        elif NumberMatch == "ER_SUCCESS_NO_MATCH":
                            card_title = "Invalid Number"
                            speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/ZH_TellNumber.mp3' /></speak>"
                            return build_response(attributes, elicit_slot(card_title,speech_output,"ZH_phoneNumber"))

        else:
            card_title = ""
            speech_output = "<speak>Sorry, "+ str(language) +" is not a supported language. Currently, the only supported languages are English and Chinese. " + "What is your preferred language?-- <audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignUp/ZH_SignUp1.mp3'/></speak>"
            reprompt_string = ""
            return build_response({},elicit_slot(card_title, speech_output, "language"))

#===== Sign Out (ENGLISH AND CHINESE)=====            
"""Switch Account/ Sign Out"""
def change_user(userID,event):
    if get_session(userID,event) > 0:
        #name = get_inUse(userID)
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('Patients')
        roundingID = get_roundID(userID)
        language = get_User_LanguageSettings(roundingID)
        response = table.update_item(
            Key={
                "RoundingID" : roundingID
            },
            UpdateExpression="SET inUse =:q",
            ExpressionAttributeValues={
                ':q' : 0
            },
            ReturnValues="UPDATED_NEW"
            )
        if language == "English":
            title =  "You have Signed Out from --"
            body = "Signed Out, Say Sign In to Sign in anytime."
            return build_response({}, build_speechlet_response(title, body, "" , True))
        elif language == "Mandarin":
            title = "You have Signed Out from --"
            body = "<speak><audio src ='https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignOut/ZH_SignOut.mp3'/></speak>"
            return build_response({}, build_special_speechlet_response(title, body, "" , True))
    else:
        title = "No Account Detected"
        body =  "There is no user detected on this device, Please say Create Account to Start First Time Setup, or Sign in by Saying Sign In"
        return statement(title, body)
        
#===== Sign In (English ONLY) =====
"""First To get user from the Slot Value (E.g Phone Number provided) (ENGLISH)"""
"""Sign In, Gets The name Provided, scans table for account, if found then get name and sign in"""
"""If name has duplicate then prompt for phone number"""
def signIn(event):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    attributes = {}
    dialog_state = event['request']['dialogState']
    if not event['request']['intent']['slots']['language'].get('value'):
        card_title = ""
        speech_output = "<speak>What is your preferred language? Chinese, or English? -- <audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignUp/ZH_SignUp1.mp3'/></speak>"
        reprompt_string = ""
        return build_response({},elicit_slot(card_title, speech_output, "language")) 
    elif event['request']['intent']['slots']['language'].get('value'):
        languageSettings = event['request']['intent']['slots']['language']['resolutions']['resolutionsPerAuthority']
        for items in languageSettings:
            if items.get('values'):
                for items in items['values']:
                    language = items['value']['name']
            else:
                language = event['request']['intent']['slots']['language']['value']
            
        if language == "English":
            if not event['request']['intent']['slots']['fullname'].get('value'):
                card_title = ""
                speech_output = "What is your name??"
                return build_response(attributes,elicit_slot2(card_title, speech_output, "fullname")) 
            elif event['request']['intent']['slots']['fullname'].get('value'):
                fullname = event['request']['intent']['slots']['fullname']['value']
                name = fullname
                roundingID = get_RoundingID_from_Name(fullname)
                #If No Account with that Name
                if roundingID == 0:
                    card_title = ""
                    speech_output = "Sorry, there is no account found with the name " +fullname +". Try again by telling me your name again, or create an account first by saying --Sign Up."
                    return build_response(attributes,elicit_slot2(card_title, speech_output, "fullname")) 
                #If Duplicate Account, Ask for Phone Number
                elif roundingID == -1:
                    if not event['request']['intent']['slots']['phoneNumber'].get('value'):
                        card_title = ""
                        speech_output = "There is more than one account registered with the name "+ fullname +". To continue with the Sign in process, Please Tell me your phone number"
                        return build_response(attributes,elicit_slot2(card_title, speech_output, "phoneNumber")) 
                    elif event['request']['intent']['slots']['phoneNumber'].get('value'):
                        phoneNumber = event['request']['intent']['slots']['phoneNumber']['value']
                        if validateNumber(phoneNumber) == 0:
                            card_title = ""
                            speech_output = "<speak>Sorry, there is no account found with the number <say-as interpret-as='digits'>" +phoneNumber +"</say-as>. Try again by telling me your phoneNumber again, or create an account first by saying --Sign Up.</speak>"
                            return build_response(attributes,elicit_slot(card_title, speech_output, "phoneNumber")) 
                        elif validateNumber(phoneNumber) == 1:
                            roundingID = get_RoundingID_from_Phone(phoneNumber)
                            name = get_username(roundingID)
                            
                            deviceID = event['context']['System']['device']['deviceId']
                            dbDeviceID = get_deviceID_from_RoundingID(roundingID)
                            
                            dbUserID = get_userID_from_RoundingID(roundingID)
                            userID = event['session']['user']['userId']
                            
                            if userID != dbUserID or deviceID !=dbDeviceID:
                                dbWard = get_ward_from_DeviceID(dbDeviceID)
                                currentWard = get_ward_from_DeviceID(deviceID)
                                
                                dbBed = get_bed_from_DeviceID(dbDeviceID)
                                currentBed = get_bed_from_DeviceID(deviceID)
                                
                                if not event['request']['intent']['slots']['choice'].get('value'):
                                    #ELICIT THE SLOT
                                    card_title = ""
                                    speech_output = "I've noticed that the device you used has changed. " +\
                                    "You were saved in Ward " +str(dbWard) +\
                                    " and Bed " +str(dbBed) +\
                                    ". Would you like to to transfer your patient details to this Bed?"
                                    return build_response(attributes,elicit_slot2(card_title, speech_output, "choice")) 
                                elif event['request']['intent']['slots']['choice'].get('value'):
                                    choice = event['request']['intent']['slots']['choice']['value']
                                    if choice.lower()=="yes":
                                        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                        table = dynamodb.Table('Patients')
                                        
                                        response = table.update_item(
                                        Key={
                                            "RoundingID" : roundingID
                                        },
                                        UpdateExpression="SET inUse =:q, userID = :d, DeviceID= :p",
                                        ExpressionAttributeValues={
                                            ':q' : 1,
                                            ':d' : userID,
                                            ':p' : deviceID
                                        },
                                        ReturnValues="UPDATED_NEW"
                                        )
                                        
                                        title =  "Welcome Back to HealthBuddy -- " +name
                                        speech_output = "Welcome Back to HealthBuddy " +name + "! " +\
                                        "I have transferred your details to Ward " +str(currentWard) +\
                                        " and Bed " +str(currentBed) +\
                                        ". To start your rounding session, please say Start Rounding."
                                        return build_response(attributes, build_speechlet_response(title, speech_output, "" , False))
                                    elif choice.lower() == "no":
                                        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                        table = dynamodb.Table('Patients')
                                        response = table.update_item(
                                        Key={
                                            "RoundingID" : roundingID
                                        },
                                        UpdateExpression="SET inUse =:q",
                                        ExpressionAttributeValues={
                                            ':q' : 1
                                        },
                                        ReturnValues="UPDATED_NEW"
                                        )
                                        title =  "Welcome Back to HealthBuddy -- " +name
                                        body = "-- Welcome Back to HealthBuddy " +name + "! To start your rounding session, please say Start Rounding."
                                        return build_response(attributes, build_speechlet_response(title, body, "" , False))
                                    else:
                                        card_title = ""
                                        speech_output = "Sorry, Please tell me Yes, or No. I've noticed that the device you used has changed. " +\
                                        "You were saved in Ward " +str(dbWard) +\
                                        " and Bed " +str(dbBed) +\
                                        ". Would you like to to transfer your patient details to this Bed?"
                                        return build_response(attributes,elicit_slot2(card_title, speech_output, "choice")) 
                            elif dbUserID == userID or deviceID == dbDeviceID:
                                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                table = dynamodb.Table('Patients')
                                response = table.update_item(
                                Key={
                                    "RoundingID" : roundingID
                                },
                                UpdateExpression="SET inUse =:q",
                                ExpressionAttributeValues={
                                    ':q' : 1
                                },
                                ReturnValues="UPDATED_NEW"
                                )
                                title =  "Welcome Back to HealthBuddy -- " +name + "."
                                body = "-- Welcome Back to HealthBuddy " +name + "!"
                                return build_response(attributes, build_speechlet_response(title, body, "" , False))
                #if Only One Account, Sign In
                elif roundingID != 0 or roundingID != -1:
                    deviceID = event['context']['System']['device']['deviceId']
                    dbDeviceID = get_deviceID_from_RoundingID(roundingID)
                    
                    dbUserID = get_userID_from_RoundingID(roundingID)
                    userID = event['session']['user']['userId']
                    
                    if userID != dbUserID or dbDeviceID != deviceID:
                        dbWard = get_ward_from_DeviceID(dbDeviceID)
                        currentWard = get_ward_from_DeviceID(deviceID)
                        
                        dbBed = get_bed_from_DeviceID(dbDeviceID)
                        currentBed = get_bed_from_DeviceID(deviceID)
                        
                        if not event['request']['intent']['slots']['choice'].get('value'):
                            #ELICIT THE SLOT
                            card_title = ""
                            speech_output = "I've noticed that the device you used has changed. " +\
                            "You were saved in Ward " +str(dbWard) +\
                            " and Bed " +str(dbBed) +\
                            ". Would you like to to transfer your patient details to this Bed?"
                            return build_response(attributes,elicit_slot2(card_title, speech_output, "choice")) 
                        elif event['request']['intent']['slots']['choice'].get('value'):
                            choice = event['request']['intent']['slots']['choice']['value']
                            if choice.lower()=="yes":
                                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                table = dynamodb.Table('Patients')
                                
                                response = table.update_item(
                                Key={
                                    "RoundingID" : roundingID
                                },
                                UpdateExpression="SET inUse =:q, userID = :d, DeviceID = :p",
                                ExpressionAttributeValues={
                                    ':q' : 1,
                                    ':d' : userID,
                                    ':p' : deviceID
                                },
                                ReturnValues="UPDATED_NEW"
                                )
                                
                                title =  "Welcome Back to HealthBuddy -- " +name
                                speech_output = "Welcome Back to HealthBuddy " +name + "! " +\
                                "I have transferred your details to Ward " +str(currentWard) +\
                                " and Bed " +str(currentBed) +\
                                ". To start your rounding session, please say Start Rounding."
                                return build_response(attributes, build_speechlet_response(title, speech_output, "" , False))
                            elif choice.lower() == "no":
                                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                table = dynamodb.Table('Patients')
                                response = table.update_item(
                                Key={
                                    "RoundingID" : roundingID
                                },
                                UpdateExpression="SET inUse =:q",
                                ExpressionAttributeValues={
                                    ':q' : 1
                                },
                                ReturnValues="UPDATED_NEW"
                                )
                                title =  "Welcome Back to HealthBuddy -- " +name
                                body = "-- Welcome Back to HealthBuddy " +name + "! To start your rounding session, please say Start Rounding."
                                return build_response(attributes, build_speechlet_response(title, body, "" , False))
                            else:
                                card_title = ""
                                speech_output = "Sorry, Please tell me Yes or No. I've noticed that the device you used has changed. " +\
                                "You were saved in Ward " +str(dbWard) +\
                                " and Bed " +str(dbBed) +\
                                ". Would you like to to transfer your patient details to this Bed?"
                                return build_response(attributes,elicit_slot2(card_title, speech_output, "choice")) 
                    elif dbUserID == userID or dbDeviceID == deviceID:
                        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                        table = dynamodb.Table('Patients')
                        response = table.update_item(
                        Key={
                            "RoundingID" : roundingID
                        },
                        UpdateExpression="SET inUse =:q",
                        ExpressionAttributeValues={
                            ':q' : 1
                        },
                        ReturnValues="UPDATED_NEW"
                        )
                        title =  "Welcome Back to HealthBuddy -- " +name + "."
                        body = "-- Welcome Back to HealthBuddy " +name + "!"
                        return build_response(attributes, build_speechlet_response(title, body, "" , False))
        elif language == "Mandarin":
            #If Full Name not Filled
            if not event['request']['intent']['slots']['fullname'].get('value'):
                card_title = ""
                speech_output = "<speak><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignUp/ZH_SignUp2.mp3'/></speak>"
                reprompt_string = ""
                return build_response({},elicit_slot(card_title, speech_output, "fullname"))   
            elif event['request']['intent']['slots']['fullname'].get('value'):
                fullname = event['request']['intent']['slots']['fullname']['value']
                roundingID = get_RoundingID_from_Name(fullname)
                #If No Account with that Name
                if roundingID == 0:
                    card_title = ""
                    audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/noAccountFound.mp3"
                    audioBuilder = "<audio src='" +audioBuilder + "'/>"
                    speech_output = "<speak>"+ audioBuilder +"</speak>"
                    return build_response(attributes,elicit_slot(card_title, speech_output, "fullname"))
                #Ask for Phone
                elif roundingID == -1:
                    if event['request']['intent']['slots']['ZH_phoneNumber'].get('value'):
                        providedNumber = event['request']['intent']['slots']['ZH_phoneNumber']['resolutions']['resolutionsPerAuthority']
                        previousNo = str(event['request']['intent']['slots']['ZH_phoneNumber']['value'])
                        NumberMatch = "ER_SUCCESS_NO_MATCH"
                        for items in providedNumber:
                            if items.get('values'):
                                for items in items['values']:
                                    previousNo = str(items['value']['name'])
                        for items in providedNumber:    
                            if items.get('status'):
                                NumberMatch = items['status']['code']
                        idxValue = int(event['session']['attributes']['idx'])
                        spoken = list(event['session']['attributes']['speech'])
                        #If match will be ER_SUCCESS_MATCH . If no match then ER_SUCCESS_NO_MATCH
                        if NumberMatch == "ER_SUCCESS_MATCH" and previousNo != "10": 
                            if idxValue == 0:
                                idx =  idxValue + 1
                                spoken.extend([previousNo])
                                attributes = {
                                    'idx': idx ,
                                    'value': previousNo,
                                    'speech': spoken
                                }
                                speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/" +previousNo +".mp3'/></speak>"
                                return build_response(attributes, elicit_slot("",speech_output,"ZH_phoneNumber"))
                            while idxValue > 0 and idxValue < 7:
                                idx = idxValue + 1
                                spoken.extend([previousNo])
                                phoneNumber = event['session']['attributes']['value']
                                newNumber = phoneNumber + previousNo
                                attributes = {
                                      'idx': idx,
                                      'value': newNumber,
                                      'speech': spoken
                                    }
                                speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/" +previousNo +".mp3'/></speak>"
                                return build_response(attributes,elicit_slot("",speech_output,"ZH_phoneNumber"))
                            else:
                                index = 0
                                number = str(event['session']['attributes']['value'])
                                spoken.extend([previousNo])
                                chineseList = spoken
                                for items in chineseList:
                                    if items == "0":
                                        audio_output += "<emphasis level='strong'>lin -- </emphasis> "
                                    elif items == "1":
                                        audio_output += "<emphasis level='strong'>y'all -- </emphasis>"
                                    elif items == "2":
                                        audio_output += "<emphasis level='strong'>aer -- </emphasis>"
                                    elif items == "3":
                                        audio_output += "<emphasis level='strong'>sun -- </emphasis>"
                                    elif items == "4":
                                        audio_output += "<emphasis level='strong'>shi -- </emphasis>"
                                    elif items == "5":
                                        audio_output += "<emphasis level='strong'>wu -- </emphasis>"
                                    elif items == "6":
                                        audio_output += "<emphasis level='strong'>leo -- </emphasis>"
                                    elif items == "7":
                                        audio_output += "<emphasis level='strong'>qi -- </emphasis>"
                                    elif items == "8":
                                        audio_output += "<emphasis level='strong'>bhar -- </emphasis>"
                                    elif items == "9":
                                        audio_output += "<emphasis level='strong'>jail -- </emphasis>"
                
                                        
                                returnNumber = number + previousNo
                                
                                attributes = {
                                    'idx': idxValue,
                                    'value': returnNumber,
                                }
                                if validateNumber(returnNumber) == 0:
                                    card_title = ""
                                    audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/noAccountFound"
                                    audioBuilder = "<audio src='" +audioFileURL +"'/>"
                                    speech_output = "<speak>" +audioBuilder +"</speak>"
                                    return build_response(attributes,elicit_slot(card_title, speech_output, "phoneNumber")) 
                                elif validateNumber(returnNumber) == 1:
                                    roundingID = get_RoundingID_from_Phone(phoneNumber)
                                    name = get_username(roundingID)
                                    
                                    deviceID = event['context']['System']['device']['deviceId']
                                    dbDeviceID = get_deviceID_from_RoundingID(roundingID)
                                    
                                    dbUserID = get_userID_from_RoundingID(roundingID)
                                    userID = event['session']['user']['userId']
                                    
                                    if userID != dbUserID:
                                        dbWard = get_ward_from_DeviceID(dbDeviceID)
                                        currentWard = get_ward_from_DeviceID(deviceID)
                                        
                                        dbBed = get_bed_from_DeviceID(dbDeviceID)
                                        currentBed = get_bed_from_DeviceID(deviceID)
                                        
                                        if not event['request']['intent']['slots']['choice'].get('value'):
                                            #ELICIT THE SLOT
                                            card_title = ""
                                            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_deviceChanged.mp3"
                                            audioBuilder = "<audio src='" +audioFileURL +"'/>"
                                            attributes = {
                                                'idx': idxValue,
                                                'value': returnNumber,
                                            }
                                            speech_output = "<speak>"+audioBuilder+"</speak>"
                                            return build_response(attributes,elicit_slot(card_title,speech_output,"choice"))
                                        elif event['request']['intent']['slots']['choice'].get('value'):
                                            for items in choiceList:
                                                if items.get('values'):
                                                    for items in items['values']:
                                                        choice = str(items['value']['name'])
                
                                            if choice.lower()=="yes":
                                                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                                table = dynamodb.Table('Patients')
                                                
                                                response = table.update_item(
                                                Key={
                                                    "RoundingID" : roundingID
                                                },
                                                UpdateExpression="SET inUse =:q, userID = :d, DeviceID= :p",
                                                ExpressionAttributeValues={
                                                    ':q' : 1,
                                                    ':d' : userID,
                                                    ':p' : deviceID
                                                },
                                                ReturnValues="UPDATED_NEW"
                                                )
                                                audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_WelcomeRound.mp3"
                                                audioBuilder = "<audio src='" +audioFileURL + "'/>"
                                                
                                                title =  "Welcome Back to HealthBuddy -- " +name + "."
                                                body = "<speak>"+audioBuilder+"</speak>"
                                                return build_response(attributes, build_special_speechlet_response(title, body, "" , False))
                                            elif choice.lower() == "no":
                                                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                                table = dynamodb.Table('Patients')
                                                response = table.update_item(
                                                Key={
                                                    "RoundingID" : roundingID
                                                },
                                                UpdateExpression="SET inUse =:q",
                                                ExpressionAttributeValues={
                                                    ':q' : 1
                                                },
                                                ReturnValues="UPDATED_NEW"
                                                )
                                                audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_WelcomeRound.mp3"
                                                audioBuilder = "<audio src='" +audioFileURL + "'/>"
                                                
                                                title =  "Welcome Back to HealthBuddy -- " +name + "."
                                                body = "<speak>"+audioBuilder+"</speak>"
                                                return build_response(attributes, build_special_speechlet_response(title, body, "" , False))
                                            else:
                                                card_title = ""
                                                audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_deviceChanged.mp3"
                                                audioBuilder = "<audio src='" +audioFileURL +"'/>"
                                                attributes = {
                                                    'idx': idxValue,
                                                    'value': returnNumber,
                                                }
                                                speech_output = "<speak>"+audioBuilder+"</speak>"
                                                return build_response(attributes,elicit_slot(card_title,speech_output,"choice"))
                                    #If Same device
                                    elif dbUserID == userId:
                                        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                        table = dynamodb.Table('Patients')
                                        response = table.update_item(
                                        Key={
                                            "RoundingID" : roundingID
                                        },
                                        UpdateExpression="SET inUse =:q",
                                        ExpressionAttributeValues={
                                            ':q' : 1
                                        },
                                        ReturnValues="UPDATED_NEW"
                                        )
                                        audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_WelcomeRound.mp3"
                                        audioBuilder = "<audio src='" +audioFileURL + "'/>"
                                        
                                        title =  "Welcome Back to HealthBuddy -- " +name + "."
                                        body = "<speak>"+audioBuilder+"</speak>"
                                        return build_response(attributes, build_special_speechlet_response(title, body, "" , False))
                        elif NumberMatch == "ER_SUCCESS_NO_MATCH" or previousNo == "10":
                            phoneNumber = event['session']['attributes']['value']
                            attributes = {
                                'idx': idxValue,
                                'value': phoneNumber,
                                'speech': spoken
                            }
                            if previousNo == "10":
                                audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/ZH_PhoneNoTens.mp3"
                                speech_output = "<speak><audio src = '" +audioFileURL +"' /></speak>"
                                return build_response(attributes, build_special_speechlet_response_noCard(speech_output,speech_output,False))
                            elif NumberMatch == "ER_SUCCESS_NO_MATCH":
                                speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/ZH_TellNumber.mp3' /></speak>"
                                return build_response(attributes, build_special_speechlet_response_noCard(speech_output,speech_output,False))
                    elif not event['request']['intent']['slots']['ZH_phoneNumber'].get('value'):
                        attributes = {
                            'idx' : 0,
                            'value': "",
                            'speech': []
                        }
                        speech = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_GetPhoneNumber.mp3'/></speak>"
                        return build_response(attributes,elicit_slot("",speech,"ZH_phoneNumber"))
                    else:
                        attributes = {}
                        card_title = "Error"
                        speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_Error.mp3'/></speak>"
                        return build_response(attributes,build_special_speechlet_response(card_title,speech_output,speech_output,False ))
                #If One Account.
                elif roundingID != 0 or roundingID != -1:
                    deviceID = event['context']['System']['device']['deviceId']
                    dbDeviceID = get_deviceID_from_RoundingID(roundingID)
                    name = event['request']['intent']['slots']['fullname']['value']
                    dbUserID = get_userID_from_RoundingID(roundingID)
                    userID = event['session']['user']['userId']
                    
                    #If Different Device
                    if userID != dbUserID:
                        dbWard = get_ward_from_DeviceID(dbDeviceID)
                        currentWard = get_ward_from_DeviceID(deviceID)
                        
                        dbBed = get_bed_from_DeviceID(dbDeviceID)
                        currentBed = get_bed_from_DeviceID(deviceID)
                        
                        if not event['request']['intent']['slots']['choice'].get('value'):
                            #ELICIT THE SLOT
                            card_title = ""
                            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_deviceChanged.mp3"
                            audioBuilder = "<audio src='" +audioFileURL +"'/>"
                            
                            speech_output = "<speak>"+audioBuilder+"</speak>"
                            return build_response(attributes,elicit_slot(card_title, speech_output, "choice")) 
                        elif event['request']['intent']['slots']['choice'].get('value'):
                            choiceList = event['request']['intent']['slots']['choice']['resolutions']['resolutionsPerAuthority']
                            for items in choiceList:
                                if items.get('values'):
                                    for items in items['values']:
                                        choice = str(items['value']['name'])

                            if choice.lower()=="yes":
                                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                table = dynamodb.Table('Patients')
                                
                                response = table.update_item(
                                Key={
                                    "RoundingID" : roundingID
                                },
                                UpdateExpression="SET inUse =:q, userID = :d, DeviceID = :p",
                                ExpressionAttributeValues={
                                    ':q' : 1,
                                    ':d' : userID,
                                    ':p' : deviceID
                                },
                                ReturnValues="UPDATED_NEW"
                                )
                                
                                title =  "Welcome Back to HealthBuddy -- " +name
                                audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_WelcomeRound.mp3"
                                audioBuilder = "<audio src='" +audioFileURL + "'/>"
                                
                                title =  "Welcome Back to HealthBuddy -- " +name + "."
                                body = "<speak>"+audioBuilder+"</speak>"
                                return build_response(attributes, build_special_speechlet_response(title, body, "" , False))
                            elif choice.lower() == "no":
                                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                table = dynamodb.Table('Patients')
                                response = table.update_item(
                                Key={
                                    "RoundingID" : roundingID
                                },
                                UpdateExpression="SET inUse =:q",
                                ExpressionAttributeValues={
                                    ':q' : 1
                                },
                                ReturnValues="UPDATED_NEW"
                                )
                                audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_WelcomeRound.mp3"
                                audioBuilder = "<audio src='" +audioFileURL + "'/>"
                                
                                title =  "Welcome Back to HealthBuddy -- " +name + "."
                                body = "<speak>"+audioBuilder+"</speak>"
                                return build_response(attributes, build_special_speechlet_response(title, body, "" , False))
                            else:
                                card_title = ""
                                audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_deviceChanged.mp3"
                                audioBuilder = "<audio src='" +audioFileURL +"'/>"
                                speech_output = "<speak>"+audioBuilder+"</speak>"
                                return build_response(attributes,elicit_slot(card_title, speech_output, "choice")) 
                    #If Same device, sign in
                    elif dbUserID == userID:
                        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                        table = dynamodb.Table('Patients')
                        response = table.update_item(
                        Key={
                            "RoundingID" : roundingID
                        },
                        UpdateExpression="SET inUse =:q",
                        ExpressionAttributeValues={
                            ':q' : 1
                        },
                        ReturnValues="UPDATED_NEW"
                        )
                        audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_WelcomeRound.mp3"
                        audioBuilder = "<audio src='" +audioFileURL + "'/>"
                        
                        title =  "Welcome Back to HealthBuddy -- " +name + "."
                        body = "<speak>"+audioBuilder+"</speak>"
                        return build_response(attributes, build_special_speechlet_response(title, body, "" , False))
        else:
            card_title = ""
            speech_output = "<speak>What is your preferred language? Chinese, or English? -- <audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignUp/ZH_SignUp1.mp3'/></speak>"
            reprompt_string = ""
            return build_response({},elicit_slot(card_title, speech_output, "language")) 
"""Get userID from RoundingID"""
def get_userID_from_RoundingID(roundingID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
        FilterExpression = Attr("RoundingID").eq(roundingID)
        )
    #If Found Return the userID
    if len(response["Items"]) == 1:
        for item in response["Items"]:
            userID = item["userID"]
            return userID
    elif len(response["Items"]) == 0:
        return 0

"""Get DeviceID from roundingID"""
def get_deviceID_from_RoundingID(roundingID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
        FilterExpression = Attr("RoundingID").eq(roundingID)
        )
    #If Found Return the deviceID
    if len(response["Items"]) == 1:
        for item in response["Items"]:
            deviceID = item["DeviceID"]
            return deviceID
    elif len(response["Items"]) == 0:
        return 0
    
#===== Start Rounding =====            
""" StartRounding (ENGLISH)"""    
def start_Rounding(event):
    userID = event['session']['user']['userId']
    #attributes = event['session']['attributes']
    name = get_inUse(userID,event)
    if event['session'].get('attributes'):
        if event['session']['attributes']['current_question_no'] == 1:
            event['request']['intent']['slots']['questionOne']['value'] = int(event['session']['attributes']['questionOne'])
    else:
        attributes = {
            "current_question_no": 0
        }
    #Both Not Answered
    if not event['request']['intent']['slots']['questionOne'].get('value') and not event['request']['intent']['slots']['questionTwo'].get('value'):
        card_title = "Rounding Started"
        speech_output = '<speak> I am now starting ' +name +"'s rounding session. " + \
                        "Starting Rounding Session.... How Many Glasses of Water have you drank today?</speak>"
        reprompt_string = ""
        attributes = {
            'current_question_no' : 0
        }
        return build_response(attributes,elicit_slot(card_title, speech_output, "questionOne"))
    #QuestionOne Answered and Question 2 Not Answered
    elif event['request']['intent']['slots']['questionOne'].get('value') and not event['request']['intent']['slots']['questionTwo'].get('value'):
        questionOneAnswer = event['request']['intent']['slots']['questionOne']['value']
        if validateAnswer(questionOneAnswer):
            attributes = {
                'current_question_no' : 1,
                'questionOne' : int(questionOneAnswer)
            }
            card_title = "Rounding Continued"
            speech_output = "<speak>Continuing Rounding... How Many Times have you gone to the Washroom today</speak>"
            reprompt_string= ""
            return build_response(attributes, elicit_slot(card_title, speech_output, "questionTwo"))
        else:
            """Clear the Value from the Slot"""
            questionOneAnswer = None
            attributes = {
                'current_question_no' : 0
            }
            card_title = "Invalid Answer"
            speech_output = "<speak>Sorry, I did not catch you, please say a number. How Many Glasses of Water have you drank today?</speak>"
            reprompt_string= ""
            return build_response(attributes, elicit_slot(card_title, speech_output, "questionOne"))
    #Both Answered
    elif event['request']['intent']['slots']['questionOne'].get('value') and event['request']['intent']['slots']['questionTwo'].get('value'):
        questionOneAnswer = event['request']['intent']['slots']['questionOne']['value']
        questionTwoAnswer = event['request']['intent']['slots']['questionTwo']['value']
        if validateAnswer(questionTwoAnswer):
            attributes = {
                'current_question_no' : 2,
                'questionOne' : int(questionOneAnswer),
                'questionTwo' : int(questionTwoAnswer),
                'completed': 1
            }
            datetimeNow = datetime.datetime.now()
            completedTime = str(datetimeNow.strftime('%H:%M %d-%m-%Y'))
            
            nextTime = datetime.datetime.now() + datetime.timedelta(hours=1)
            nextRounding = str(nextTime.strftime('%H:%M %d-%m-%Y')).format(nextTime)
            
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.Table('Roundings')
            
            glasses = event['request']['intent']['slots']['questionOne']['value']
            washroom = event['request']['intent']['slots']['questionTwo']['value']
            
            roundingID = get_max_roundingID2() + 1
            patientID = get_roundID(userID)
            #Now I have to Update the Previous Rounding to Expire It First.
            if get_lastRounding(patientID) != 0:
                response5 = expire_Rounding(patientID)
            
            response = table.put_item(
                    Item = {
                        "RoundingID": roundingID,
                        "PatientID": patientID,
                        "WaterGlasses": glasses,
                        "WashRoom": washroom,
                        "Completed": completedTime,
                        "NextRounding": nextRounding,
                        "Latest" : 1
                    }
                )
            response2 = update_max_RoundingID2(roundingID) #Update it to give the new maxRoundingID
            
            response3 = patientCompleteRounding(patientID)
            
            #==Send SMS==
            sms_body = "Hello, "+name +". Here is your last rounding: You drank " +str(glasses) + " glasses of water and you made a visit to the washroom " +str(washroom) +" times. Your Next Rounding Session will be at "  +str(nextTime.strftime('%H:%M')) +'. Thank You!'
            phoneNumber = get_User_Phone(patientID)
            response4 = send_sms(phoneNumber, sms_body)
            card_title = "Rounding Complete!"
            
            speech_output = '<speak> Rounding Completed. ' + \
                    'Thank You for using HealthBuddy, You have drank ' +str(glasses) + ' glasses of water and ' +\
                    'You have gone to the washroom ' +str(washroom) + ' times, your next rounding session will be at ' +str(nextTime.strftime('%H:%M')) +'. Good-bye!'+\
                    '</speak>'
            reprompt_string = ""
            return build_response(attributes, build_special_speechlet_response(card_title, speech_output, reprompt_string , True))
        else:
            """Clear the Value from the Slot"""
            questionTwoAnswer = None
            attributes = {
                'current_question_no' : 1,
                'questionOne' : int(questionOneAnswer)
            }
            card_title = "Invalid Answer"
            speech_output = "<speak>Sorry, I did not catch you, please say a number. How Many times have you gone to the washroom today?</speak>"
            reprompt_string= ""
            return build_response(attributes, elicit_slot(card_title, speech_output, "questionTwo"))

""" StartRounding (CHINESE) """            
def start_Rounding_Chinese(event):
    userID = event['session']['user']['userId']
    name = get_inUse(userID,event)
    if event['session'].get('attributes'):
        if event['session']['attributes'].get('current_question_no'):
            if event['session']['attributes']['current_question_no'] == 1:
                event['request']['intent']['slots']['da_yi']['value'] = int(event['session']['attributes']['questionOne'])
    else:
        attributes = {
            "current_question_no": 0
        }
    #Both Not Answered
    if not event['request']['intent']['slots']['da_yi'].get('value') and not event['request']['intent']['slots']['da_er'].get('value'):
        card_title = "Rounding Started"
        
        audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_RoundStart.mp3"
        audioBuilder = "<audio src = '" + audioFileURL + "'/>"
        
        audioFileURL2 = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_RoundStart2.mp3"
        audioBuilder2 = "<audio src = '" + audioFileURL2 + "'/>"
        
        audioFileURL3 = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_RoundQ1.mp3"
        audioBuilder3 = "<audio src = '" + audioFileURL3 + "'/>"
        
        speech_output = "<speak>" +audioBuilder +name +audioBuilder2 + audioBuilder3 +\
                        "</speak>"
        reprompt_string = ""
        attributes = {
            'current_question_no' : 0
        }
        return build_response(attributes,elicit_slot(card_title, speech_output, "da_yi"))
    #QuestionOne Answered
    elif event['request']['intent']['slots']['da_yi'].get('value') and not event['request']['intent']['slots']['da_er'].get('value'):
        questionOneAnswer = ""
        if event['request']['intent']['slots']['da_yi'].get('resolutions'):
            value = event['request']['intent']['slots']['da_yi']['resolutions']['resolutionsPerAuthority']
            for items in value:
                if items.get('values'):
                    for items in items['values']:
                        questionOneAnswer = int(items['value']['name'])
        else:
            questionOneAnswer = int(event['session']['attributes']['questionOne'])
            
        if validateAnswer(questionOneAnswer):
            attributes = {
                'current_question_no' : 1,
                'questionOne' : int(questionOneAnswer)
            }
            card_title = "Rounding Continued"
            
            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_RoundQ2.mp3"
            audioBuilder = "<audio src = '" + audioFileURL + "'/>"
            
            speech_output = "<speak>" + audioBuilder + "</speak>"
            reprompt_string= ""
            return build_response(attributes, elicit_slot(card_title, speech_output, "da_er"))
        else:
            attributes = {
                'current_question_no' : 0
            }
            card_title = "Invalid Answer"
            
            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_AnswerError.mp3"
            audioBuilder = "<audio src = '" + audioFileURL + "'/>"
            
            audioFileURL2 = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_RoundQ1.mp3"
            audioBuilder2 = "<audio src = '" + audioFileURL2 + "'/>"
            
            speech_output = "<speak>" +audioBuilder +audioBuilder2 +"</speak>"
            #speech_output = "<speak>Sorry, I did not catch you, please say a number. How Many Glasses of Water have you drank today?</speak>"
            reprompt_string= ""
            return build_response(attributes, elicit_slot(card_title, speech_output, "da_yi"))
    #Both Answered
    elif event['request']['intent']['slots']['da_yi'].get('value') and event['request']['intent']['slots']['da_er'].get('value'):
        questionOneAnswer = ""
        questionTwoAnswer = ""
        
        if event['session'].get('attributes'):
            if event['session']['attributes'].get('questionOne'):
                questionOneAnswer = event['session']['attributes']['questionOne']   
            else:
                questionOneList = event['request']['intent']['slots']['da_yi']['resolutions']['resolutionsPerAuthority']
                for items in questionOneList:
                    for items in items['values']:
                        questionOneAnswer = int(items['value']['name'])
        
           
        questionTwoList = event['request']['intent']['slots']['da_er']['resolutions']['resolutionsPerAuthority']
        for items2 in questionTwoList:
            if items2.get('values'):
                for items2 in items2['values']:
                    questionTwoAnswer = int(items2['value']['name'])
        if validateAnswer(questionTwoAnswer):
            attributes = {
                'current_question_no' : 2,
                'questionOne' : int(questionOneAnswer),
                'questionTwo' : int(questionTwoAnswer),
                'completed': 1
            }
            datetimeNow = datetime.datetime.now()
            completedTime = str(datetimeNow.strftime('%H:%M %d-%m-%Y'))
            
            nextTime = datetime.datetime.now() + datetime.timedelta(hours=1)
            nextRounding = str(nextTime.strftime('%H:%M %d-%m-%Y')).format(nextTime)
            
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.Table('Roundings')
            
            glasses = int(questionOneAnswer)
            washroom = int(questionTwoAnswer)
            
            roundingID = get_max_roundingID2() + 1
            patientID = get_roundID(userID)
            #Now I have to Update the Previous Rounding to Expire It First.
            if get_lastRounding(patientID) != 0:
                response5 = expire_Rounding(patientID)
            
            response = table.put_item(
                    Item = {
                        "RoundingID": roundingID,
                        "PatientID": patientID,
                        "WaterGlasses": glasses,
                        "WashRoom": washroom,
                        "Completed": completedTime,
                        "NextRounding": nextRounding,
                        "Latest" : 1
                    }
                )
            response2 = update_max_RoundingID2(roundingID) #Update it to give the new maxRoundingID
            
            response3 = patientCompleteRounding(patientID)
            
            #==Send SMS==
            phoneNumber = get_User_Phone(patientID)
            sms_body = "你好，"+name +"。在你上次测量中你喝了 " +str(glasses) + " 杯水和上了 " +str(washroom) +" 次厕所。你下一次的测量时间是"  +\
            str(nextTime.strftime('%H')) + " 点 " +\
            str(nextTime.strftime('%M'))+ " 分。 谢谢您使用健康好友！"
            response4 = send_sms(phoneNumber, sms_body)
            
            audio_output = ""
            if glasses == 0:
                audio_output = "<emphasis level='strong'>lin -- </emphasis> "
            elif glasses == 1:
                audio_output = "<emphasis level='strong'>yi -- </emphasis>"
            elif glasses == 2:
                audio_output = "<emphasis level='strong'>liang -- </emphasis>"
            elif glasses == 3:
                audio_output = "<emphasis level='strong'>sun -- </emphasis>"
            elif glasses == 4:
                audio_output = "<emphasis level='strong'>shi -- </emphasis>"
            elif glasses == 5:
                audio_output = "<emphasis level='strong'>wu -- </emphasis>"
            elif glasses == 6:
                audio_output = "<emphasis level='strong'>leo -- </emphasis>"
            elif glasses == 7:
                audio_output = "<emphasis level='strong'>qi -- </emphasis>"
            elif glasses == 8:
                audio_output = "<emphasis level='strong'>bhar -- </emphasis>"
            elif glasses == 9:
                audio_output = "<emphasis level='strong'>jail -- </emphasis>"
            
            audio_output2 = ""    
            if washroom == 0:
            	audio_output2 = "<emphasis level='strong'>lin -- </emphasis> "
            elif washroom == 1:
            	audio_output2 = "<emphasis level='strong'>yi -- </emphasis>"
            elif washroom == 2:
            	audio_output2 = "<emphasis level='strong'>liang -- </emphasis>"
            elif washroom == 3:
            	audio_output2 = "<emphasis level='strong'>sun -- </emphasis>"
            elif washroom == 4:
            	audio_output2 = "<emphasis level='strong'>shi -- </emphasis>"
            elif washroom == 5:
            	audio_output2 = "<emphasis level='strong'>wu -- </emphasis>"
            elif washroom == 6:
            	audio_output2 = "<emphasis level='strong'>leo -- </emphasis>"
            elif washroom == 7:
            	audio_output2 = "<emphasis level='strong'>qi -- </emphasis>"
            elif washroom == 8:
            	audio_output2 = "<emphasis level='strong'>bhar -- </emphasis>"
            elif washroom == 9:
            	audio_output2 = "<emphasis level='strong'>jail -- </emphasis>"
                                    
            card_title = "Rounding Complete!"
            
            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_RoundEnd1.mp3"
            audioBuilder = "<audio src ='" +audioFileURL + "'/>"
            
            audioFileURL2 = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_RoundEnd2.mp3"
            audioBuilder2 = "<audio src ='" +audioFileURL2 + "'/>"
            
            audioFileURL3 = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_RoundEnd3.mp3"
            audioBuilder3 = "<audio src ='" +audioFileURL3 + "'/>"
            
            audioFileURL4 = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_RoundEnd4.mp3"
            audioBuilder4 = "<audio src ='" +audioFileURL4 + "'/>"
            
            speech_output = "<speak>" + \
                    audioBuilder + audio_output +\
                    audioBuilder2 + audio_output2 +\
                    audioBuilder3 +\
                    audioBuilder4 +str(nextTime.strftime('%H')) + " tien " +\
                    str(nextTime.strftime('%M')) + " fern " +\
                    '</speak>'
            reprompt_string = ""
            return build_response(attributes, build_special_speechlet_response(card_title, speech_output, reprompt_string , True))
        elif not validateAnswer(questionTwoAnswer):
            attributes = {
                'current_question_no' : 1,
                'questionOne' : int(questionOneAnswer)
            }
            card_title = "Invalid Answer"
            
            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_AnswerError.mp3"
            audioBuilder = "<audio src = '" + audioFileURL + "'/>"
            
            audioFileURL2 = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Round/ZH_RoundQ2.mp3"
            audioBuilder2 = "<audio src = '" + audioFileURL2 + "'/>"
            
            speech_output = "<speak>" +audioBuilder +audioBuilder2 +"</speak>"
            
            #speech_output = "<speak>Sorry, I did not catch you, please say a number. How Many times have you gone to the washroom today?</speak>"
            reprompt_string= ""
            return build_response(attributes, elicit_slot(card_title, speech_output, "da_er"))
    else:
        return statement("","An Error Occured Please Try again.")


#===== SETTINGS =====
"""Settings Middleman/Router (ENGLISH)"""
def change_settings(event):
    deviceID = event['context']['System']['device']['deviceId']
    configured = device_configured(deviceID)
    if not event['request']['intent']['slots']['Type'].get('value'):
        if not event['request']['intent']['slots']['UserSettings'].get('value'):
            speech_output = "Which setting would you like to change? User or Device"
            return build_response({}, elicit_slot2("", speech_output , "Type"))
        elif event['request']['intent']['slots']['UserSettings'].get('value'):
            return update_user_settings(event)
    if event['request']['intent']['slots']['Type'].get('value'):
        settingType = event['request']['intent']['slots']['Type']['value']
        if settingType.lower() == "device":
            if not event['request']['intent']['slots']['DeviceSettingsTwo'].get('value'):
                speech_output = "Would you like to change the device settings, or reconfigure this device?"
                return build_response({}, elicit_slot2("", speech_output , "DeviceSettingsTwo"))
            if event['request']['intent']['slots']['DeviceSettingsTwo'].get('value'):
                SettingsField =  event['request']['intent']['slots']['DeviceSettingsTwo']['value']
                if SettingsField.lower()=="device settings" or SettingsField.lower() =="settings" or SettingsField.lower=="device" or SettingsField.lower()=="change" or SettingsField.lower() == "change device settings":
                    return update_device_settings(event)
                elif SettingsField.lower() =="reconfigure" or SettingsField.lower() == "re configure" or SettingsField.lower() == "reconfigure device" or SettingsField.lower()=="reconfigure this device" or SettingsField.lower()=="reconfiguration":
                    if configured:
                        return reconfigure_device(event)
                    elif not configured:
                        reconfiguration = 0
                        if event['session'].get('attributes'):
                            if event['session']['attributes'].get('reconfiguration'):
                                reconfiguration = 1
                        
                        if reconfiguration == 0:
                            return statement("Reconfiguration Failed - Please Configure Device First", "Unable to reconfigure device as this device has not been configured. Please open device settings to configure this device first.")
                        elif reconfiguration == 1:
                            return device_settings(event)
                else:
                    speech_output = "Sorry, I did not hear you. Would you like to change the device settings, or reconfigure the device?"
                    return build_response({}, elicit_slot2("", speech_output , "DeviceSettingsTwo"))
        elif settingType.lower() == "user" or settingType.lower() == "account":
            return update_user_settings(event)
        else:
            speech_output = "Sorry, I did not catch you. Which setting would you like to change? User or Device"
            return build_response({}, elicit_slot2("", speech_output , "Type"))

#===== User Settings ======
"""Get User Settings (ENGLISH) """
def user_settings(event):
    attributes={}
    userID = event['session']['user']['userId']
    hasAccount = get_session(userID,event)
    #-Got No Account Signed In
    if hasAccount == 0:
        card_title = "No User Signed In."
        speech_output = "Sorry, There is no user signed into this device. Please sign in first by saying Sign In"
        reprompt_text = "Please sign in first to access your user settings."
        return build_response(attributes, build_speechlet_response(card_title,speech_output,reprompt_text,False))
    #-Has Account
    elif hasAccount == 1:
        roundingID = get_roundID(userID)
        name = get_username(roundingID)
        phoneNumber = get_User_Phone(roundingID)
        languageSettings = get_User_LanguageSettings(roundingID)
        if phoneNumber == 0 and languageSettings ==0 and name ==0:
            card_title = "Error."
            speech_output = "Sorry, I am unable to retrieve your account details at this time."
            return build_response(attributes, build_speechlet_response(card_title,speech_output,speech_output,False))
        else:
            card_title = "Patient "+str(roundingID) +" Details"
            speech_output = "<speak> Here are your account details, Your name is -- " +name +\
                            ". Your phone number is -- <say-as interpret-as='digits'>" +phoneNumber +"</say-as>" +\
                            ", and your current language set is -- " +languageSettings +\
                            ". To make any changes, please say -- update user settings --</speak>"
            return build_response(attributes, build_special_speechlet_response(card_title,speech_output,speech_output,False))
    #-No account associated with the user ID-
    else:
        card_title = "No User Detected."
        speech_output = "Sorry, There is no user signed into this device. Please sign in first by saying Sign In"
        reprompt_text = "Please sign in first to access your user settings."
        return build_response(attributes, build_speechlet_response(card_title,speech_output,reprompt_text,False))

"""For Updating User Settings (ENGLISH)"""
def update_user_settings(event):
    if event['session'].get('attributes'):
        if not event['session']['attributes'].get('current_question_no'):
            attributes = event['session']['attributes']
    else:
        attributes = {}
    userID = event['session']['user']['userId']
    signedIn = get_session(userID,event)
    roundingID = get_roundID(userID)
    if signedIn == 1:
        if not event['request']['intent']['slots']['UserSettings'].get('value'):
            speech_output = "Which Setting would you like to update -- Name, Phone Number or Language?"
            return build_response(attributes, elicit_slot2("", speech_output , "UserSettings"))
        elif event['request']['intent']['slots']['UserSettings'].get('value'):
            userSettings = event['request']['intent']['slots']['UserSettings']['value']
            
            
            # -- Change Name --
            if userSettings.lower() == "name":
                if event['session'].get('attributes'):
                    if event['session']['attributes'].get('newName'):
                        if event['request']['intent']['slots']['choiceTwo'].get('value'):
                            clear = event['request']['intent']['slots']['choiceTwo']
                            clear.pop('value')
                            clear.pop('resolutions')
                            attributes = {
                                'NameLoop' : True
                            }
                            
                        if event['request']['intent']['slots']['choice'].get('value'):
                            clear2 = event['request']['intent']['slots']['choice']
                            clear2.pop('value')
                            clear2.pop('resolutions')
                            clear3 = event['session']['attributes']
                            clear3.pop('newName')

                #- Prompt User for new name -
                if not event['request']['intent']['slots']['newName'].get('value'):
                    speech_output = "What is your new name?"
                    return build_response(attributes, elicit_slot2("", speech_output , "newName"))
                elif event['request']['intent']['slots']['newName'].get('value'):
                    oldName = get_username(roundingID)
                    newName = event['request']['intent']['slots']['newName']['value']
                    if oldName != newName:
                    #- Ask User if he/she is sure that he want to change the name to newName.
                        if not event['request']['intent']['slots']['choice'].get('value'):
                            speech_output = "You are changing your name from --" +oldName +" to --" +newName +", are you sure?"
                            return build_response(attributes, elicit_slot2("", speech_output , "choice"))
                        elif event['request']['intent']['slots']['choice'].get('value'):
                            choice = event['request']['intent']['slots']['choice']['value']
                            if choice.lower() == "yes":
                                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                table = dynamodb.Table('Patients')
                                response = table.update_item(
                                    Key={
                                        "RoundingID" : roundingID
                                    },
                                    UpdateExpression="SET patientname =:q",
                                    ExpressionAttributeValues={
                                        ':q' : newName
                                    },
                                    ReturnValues="UPDATED_NEW"
                                    )
                                card_title = "Patient ID " +str(roundingID) +": Name Changed"
                                speech_output = "Completed. Your name has been changed from --" +oldName +" to --" +newName + "."
                                return build_response(attributes, build_speechlet_response(card_title,speech_output,speech_output, False))
                            elif choice.lower() == "no":
                                #ask User if they wanna give a new name. (Use ChoiceTwo)
                                if event['session'].get('attributes'):
                                    if event['session']['attributes'].get('NameLoop'):
                                        loop = 1
                                else:
                                    loop = 0
                                
                                if not event['request']['intent']['slots']['choiceTwo'].get('value'):
                                    speech_output = "Oops. I think that I might have heard your name incorrectly. Would you like to give me another name?"
                                    return build_response(attributes, elicit_slot2("", speech_output , "choiceTwo")) 
                                elif loop == 1:
                                    speech_output = "Oops. I think that I might have heard your name incorrectly. Would you like to give me another name?"
                                    attributes= {}
                                    return build_response(attributes, elicit_slot2("", speech_output , "choiceTwo")) 
                                elif event['request']['intent']['slots']['choiceTwo'].get('value'):
                                    choiceTwo = event['request']['intent']['slots']['choiceTwo']['value']
                                    #If Yes Ask user to Give new name
                                    if choiceTwo.lower() == "yes":
                                        #Do the Attributes
                                        attributes = {
                                            'newName' : True
                                        }
                                        speech_output = "Sorry I Misheard. Please tell me your new name."
                                        return build_response(attributes, elicit_slot2("", speech_output , "newName"))
                                    #no new name, so cancel change
                                    elif choiceTwo.lower() == "no":
                                        card_title=" Name Change Cancelled"
                                        speech_output = "Ok, The Account Name Change was cancelled. You can change or update your user settings anytime by opening user settings"
                                        reprompt_string = "Account Name Change was cancelled."
                                        return build_response(attributes,build_speechlet_response(card_title, speech_output, reprompt_string, False))
                                    else:
                                        speech_output = "Sorry, I did not catch you. Would you like to tell me another name?"
                                        return build_response(attributes, elicit_slot2("", speech_output , "choiceTwo")) 
                            else:
                                speech_output = "Sorry, I did not catch you. Please tell me Yes, or No. You are changing your name from --" +oldName +" to --" +newName +", are you sure?"
                                return build_response(attributes, elicit_slot2("", speech_output , "choice"))
                    else:
                        card_title = "Name already "+newName +", no Changes made."
                        speech_output = "Your name is already " +newName + ". No changes have been made."
                        return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output, False))
                
            #-- Change Language -- (Still Requires Validation)
            elif userSettings.lower() == "language settings" or userSettings.lower() == "language":
                if event['session'].get('attributes'):
                    if event['session']['attributes'].get('newLanguage'):
                        if event['request']['intent']['slots']['choiceTwo'].get('value'):
                            clear = event['request']['intent']['slots']['choiceTwo']
                            clear.pop('value')
                            clear.pop('resolutions')
                            attributes = {
                                'LanguageLoop' : True
                            }
                            
                        if event['request']['intent']['slots']['choice'].get('value'):
                            clear2 = event['request']['intent']['slots']['choice']
                            clear2.pop('value')
                            clear2.pop('resolutions')
                            clear3 = event['session']['attributes']
                            clear3.pop('newLanguage')

                #- Prompt User for new Language -
                if not event['request']['intent']['slots']['newLanguage'].get('value'):
                    speech_output = "Which Language would you like to change to?"
                    return build_response(attributes, elicit_slot2("", speech_output , "newLanguage"))
                elif event['request']['intent']['slots']['newLanguage'].get('value'):
                    oldLanguageSettings = get_User_LanguageSettings(roundingID)
    
                    languageSettings = event['request']['intent']['slots']['newLanguage']['resolutions']['resolutionsPerAuthority']
                    for items in languageSettings:
                        if items.get('values'):
                            for items in items['values']:
                                newLanguageSettings = items['value']['name']
                        else:
                            newLanguageSettings = event['request']['intent']['slots']['newLanguage']['value']
                    
                    if newLanguageSettings == "English" or newLanguageSettings == "Mandarin":
                        if oldLanguageSettings == "English":
                            #- Ask User if he/she is sure that he want to change the old language to new Language.
                            if not event['request']['intent']['slots']['choice'].get('value'):
                                speech_output = "You are changing your language from --" +oldLanguageSettings +" to --" +newLanguageSettings +", are you sure?"
                                return build_response(attributes, elicit_slot2("", speech_output , "choice"))
                            elif event['request']['intent']['slots']['choice'].get('value'):
                                choice = event['request']['intent']['slots']['choice']['value']
                                if choice.lower() == "yes":
                                    if newLanguageSettings != oldLanguageSettings:
                                        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                        table = dynamodb.Table('Patients')
                                        response = table.update_item(
                                            Key={
                                                "RoundingID" : roundingID
                                            },
                                            UpdateExpression="SET LanguageSettings =:q",
                                            ExpressionAttributeValues={
                                                ':q' : newLanguageSettings
                                            },
                                            ReturnValues="UPDATED_NEW"
                                            )
                                        if newLanguageSettings == "Mandarin":
                                            card_title = "Patient ID " +str(roundingID) +": LanguageSettings Changed"
                                            speech_output = "<speak><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_LanguageSettingEN_toZH.mp3'/></speak>"
                                            return build_response(attributes,build_special_speechlet_response(card_title,speech_output,speech_output,False))
                                        else:
                                            return build_response(attributes,build_speechlet_response("Error","An Error Occurred","",True))
                                    elif newLanguageSettings == oldLanguageSettings:
                                        if oldLanguageSettings == "English":
                                            card_title = "New Language Setting same as Previous Language Setting. No Changes were made."
                                            speech_output = "Your Language Setting is already configured as English."
                                            return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,False))
                                elif choice.lower() == "no":
                                    if event['session'].get('attributes'):
                                        if event['session']['attributes'].get('LanguageLoop'):
                                            loop = 1
                                    else:
                                        loop = 0
                                    #ask User if they wanna give a new Language. (Use ChoiceTwo)
                                    if not event['request']['intent']['slots']['choiceTwo'].get('value'):
                                        speech_output = "Oops. I think that I might misheard you. Would you like to tell me the language you would like to change to again?"
                                        return build_response(attributes, elicit_slot2("", speech_output , "choiceTwo")) 
                                    elif loop == 1:
                                        speech_output = "Oops. I think that I might misheard you. Would you like to tell me the language you would like to change to again?"
                                        attributes= {}
                                        return build_response(attributes, elicit_slot2("", speech_output , "choiceTwo"))
                                    elif event['request']['intent']['slots']['choiceTwo'].get('value'): 
                                        choiceTwo = event['request']['intent']['slots']['choiceTwo']['value']
                                        #If Yes Ask user to Give new Language
                                        if choiceTwo.lower() == "yes":
                                            #Do the Attributes
                                            attributes = {
                                                'newLanguage' : True
                                            }
                                            speech_output = "Sorry I Misheard. Please tell me your new Language."
                                            return build_response(attributes, elicit_slot2("", speech_output , "newLanguage"))
                                        #no new Language, so cancel change
                                        elif choiceTwo.lower() == "no":
                                            card_title="Language Change Cancelled"
                                            speech_output = "Ok, The Account Language Settings Change was cancelled. You can change or update your user settings anytime by opening user settings"
                                            reprompt_string = "Account Language Change was cancelled."
                                            return build_response(attributes,build_speechlet_response(card_title, speech_output, reprompt_string, False))
                                        else:
                                            speech_output = "Sorry, I did not catch you. Would you like to tell me the language you would like to change to again?"
                                            return build_response(attributes, elicit_slot2("", speech_output , "choiceTwo")) 
                                else:
                                    speech_output = "Sorry, I did not catch you. Please tell me Yes, or No. You are changing your language from --" +oldLanguageSettings +" to --" +newLanguageSettings +", are you sure?"
                                    return build_response(attributes, elicit_slot2("", speech_output , "choice"))
                    else:
                            speech_output = "Sorry, I did not catch you. Would you like to change your language to English or Chinese?"
                            return build_response(attributes, elicit_slot2("", speech_output , "newLanguage"))
                             
            #-- Change Phone -- (done)
            elif userSettings.lower() == "phone number" or userSettings.lower() == "phone" or userSettings.lower() == "number":
                if event['session'].get('attributes'):
                    if event['session']['attributes'].get('newNumber'):
                        if event['request']['intent']['slots']['choiceTwo'].get('value'):
                            clear = event['request']['intent']['slots']['choiceTwo']
                            clear.pop('value')
                            clear.pop('resolutions')
                            attributes = {
                                'PhoneLoop' : True
                            }
                            
                        if event['request']['intent']['slots']['choice'].get('value'):
                            clear2 = event['request']['intent']['slots']['choice']
                            clear2.pop('value')
                            clear2.pop('resolutions')
                            clear3 = event['session']['attributes']
                            clear3.pop('newNumber')
                    
                if not event['request']['intent']['slots']['newNumber'].get('value'):
                    speech_output = "What is your new phone number?"
                    return build_response(attributes, elicit_slot2("", speech_output , "newNumber"))
                elif event['request']['intent']['slots']['newNumber'].get('value'):
                    newNumber = event['request']['intent']['slots']['newNumber']['value']
                    oldNumber = get_User_Phone(roundingID)
                    if oldNumber != newNumber:
                        if validateNumber(newNumber) == 0:
                            #- Ask User if he/she is sure that he want to change the old number to new number.
                            if not event['request']['intent']['slots']['choice'].get('value'):
                                speech_output = "<speak>You are changing your phone number from --<say-as interpret-as='digits'>" +oldNumber +"</say-as> to --<say-as interpret-as='digits'>" +newNumber +"</say-as>, are you sure?</speak>"
                                return build_response(attributes, elicit_slot("", speech_output , "choice"))
                            elif event['request']['intent']['slots']['choice'].get('value'):
                                choice = event['request']['intent']['slots']['choice']['value']
                                if choice.lower() == "yes":
                                    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                    table = dynamodb.Table('Patients')
                                    response = table.update_item(
                                    Key={
                                        "RoundingID" : roundingID
                                    },
                                    UpdateExpression="SET phoneNumber =:q",
                                    ExpressionAttributeValues={
                                        ':q' : newNumber
                                    },
                                    ReturnValues="UPDATED_NEW"
                                    )
                                    card_title = "Patient ID " +str(roundingID) +": Number Changed"
                                    speech_output = "<speak> Completed. Your Number has been changed from <say-as interpret-as='digits'>" +oldNumber +"</say-as> to <say-as interpret-as='digits'>" +newNumber +"</say-as></speak>"
                                    return build_response(attributes,build_special_speechlet_response(card_title,speech_output,speech_output, False))
                                elif choice.lower() == "no":
                                    if event['session'].get('attributes'):
                                        if event['session']['attributes'].get('PhoneLoop'):
                                            loop = 1
                                    else:
                                        loop = 0
                                    #ask User if they wanna give a new Number. (Use ChoiceTwo)
                                    if not event['request']['intent']['slots']['choiceTwo'].get('value'):
                                        speech_output = "Oops. I think that I might misheard you. Would you like to tell me the number you would like to change to again?"
                                        return build_response(attributes, elicit_slot2("", speech_output , "choiceTwo")) 
                                    elif loop == 1:
                                        speech_output = "Oops. I think that I might misheard you. Would you like to tell me the language you would like to change to again?"
                                        attributes= {}
                                        return build_response(attributes, elicit_slot2("", speech_output , "choiceTwo"))
                                    elif event['request']['intent']['slots']['choiceTwo'].get('value'): 
                                        choiceTwo = event['request']['intent']['slots']['choiceTwo']['value']
                                        #If Yes Ask user to Give new Number
                                        if choiceTwo.lower() == "yes":
                                            #Do the Attributes
                                            attributes = {
                                                'newNumber' : True
                                            }
                                            speech_output = "Sorry I Misheard. Please tell me your new Phone Number."
                                            return build_response(attributes, elicit_slot2("", speech_output , "newNumber"))
                                        #no new Number, so cancel change
                                        elif choiceTwo.lower() == "no":
                                            card_title="Number Change Cancelled"
                                            speech_output = "Ok, The Phone Number Change was cancelled. You can change or update your user settings anytime by opening user settings"
                                            reprompt_string = "Account Phone Number Change was cancelled."
                                            return build_response(attributes,build_speechlet_response(card_title, speech_output, reprompt_string, False))
                                        else:
                                            speech_output = "Sorry, I did not catch you. Would you like to tell me the Phone Number you would like to change to again?"
                                            return build_response(attributes, elicit_slot2("", speech_output , "choiceTwo")) 
                                else:
                                    speech_output = "<speak>You are changing your phone number from --<say-as interpret-as='digits'>" +oldNumber +"</say-as> to --<say-as interpret-as='digits'>" +newNumber +"</say-as>, are you sure?</speak>"
                                    return build_response(attributes, elicit_slot("", speech_output , "choice"))
                        elif validateNumber(newNumber) == 1:
                            card_title = "No Changes Made. New Phone Number Provided Exists."
                            speech_output = "The Phone Number you provided Exists. No changes have been made."
                            return build_response(attributes, build_speechlet_response(card_title, speech_output, speech_output, False)) 
                    elif oldNumber == newNumber:
                        card_title = "No Changes Made. New Phone Number Provided is the Same."
                        speech_output = "The Phone Number you provided is the same. No changes have been made."
                        return build_response(attributes, build_speechlet_response(card_title, speech_output, speech_output, False)) 
            else:
                speech_output = "Sorry, I did not catch you. Which Setting would you like to update -- Name, Phone Number or Language?"
                return build_response(attributes, elicit_slot2("", speech_output , "UserSettings"))
            
    else:
        card_title = "No User Signed In."
        speech_output = "Sorry, There is no user signed into this device. Please sign in first by saying Sign In"
        reprompt_text = "Please sign in first to change your user settings."
        return build_response(attributes, build_speechlet_response(card_title,speech_output,reprompt_text,False))
        
#===== Device Settings (ENGLISH) =====
"""Checks if the device is already configured"""
def device_configured(deviceID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Devices')
    response = table.scan(
        FilterExpression = Attr("deviceID").eq(deviceID)
        )
    #If Found Return True otherwise return false
    if len(response["Items"]) > 0 :
        return True
    elif len(response["Items"]) == 0 :
        return False
        
"""If Configured returns settings list item"""
def get_device_settings(deviceID):
    exists = device_configured(deviceID)
    if exists:
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.Table('Devices')
            response = table.scan(
            FilterExpression = Attr("deviceID").eq(deviceID)
            )
            return response
    elif not exists:
        return False

"""Bed validation so that no Duplicate devices for a bed"""
def get_bed(bedNo, wardNo):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Devices')
    response = table.scan(
        FilterExpression = Attr("bedNo").eq(bedNo) & Attr('wardNo').eq(wardNo)
        )
    if len(response["Items"]) > 0:
        return False
    elif len(response["Items"]) == 0:
        return True
        
""" View Device Settings Intent"""
def device_settings(event):
    attributes = {}
    if event['session'].get('attributes'):
        if event['session']['attributes'].get('reconfiguration'):
            attributes = {
                'reconfiguration' : 1
            }
    card_title = "Complete"
    deviceID = event['context']['System']['device']['deviceId']
    configured = device_configured(deviceID)
    if not configured:
        if not event['request']['intent']['slots']['choice'].get('value'):
            speech_output = "This device has not been configured. Would you like to configure it now??"
            return build_response(attributes, elicit_slot2("", speech_output , "choice"))
        if event['request']['intent']['slots']['choice'].get('value'):
            choice = event['request']['intent']['slots']['choice']['value']
            if choice.lower() == "yes":
                if not event['request']['intent']['slots']['ward'].get('value'):
                    speech_output = "Please Tell me the ward number where this device is located."
                    return build_response(attributes, elicit_slot2("", speech_output , "ward"))
                    
                elif event['request']['intent']['slots']['ward'].get('value'):
                    if validateAnswer(event['request']['intent']['slots']['ward']['value']):
                        if not event['request']['intent']['slots']['bed'].get('value'):
                            speech_output = "This device is now configured in Ward " + str(event['request']['intent']['slots']['ward']['value']) + ". Now, tell me the Bed Number of this device."
                            return build_response(attributes, elicit_slot2("", speech_output , "bed"))
                        elif event['request']['intent']['slots']['bed'].get('value'):
                            if validateAnswer(event['request']['intent']['slots']['bed']['value']):
                                ward = event['request']['intent']['slots']['ward']['value']
                                bed = event['request']['intent']['slots']['bed']['value']
                                if get_bed(bed, ward):
                                    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                    table = dynamodb.Table('Devices')
                                    response = table.put_item(
                                            Item = {
                                                "deviceID": deviceID,
                                                "wardNo": ward,
                                                "bedNo": bed
                                            }
                                        )
                                    speech_output = "Setup complete! This device is now configured in ward " +str(ward) + ", bed number " +str(bed)
                                    return build_response(attributes, build_speechlet_response(card_title, speech_output, speech_output , True))
                                elif not get_bed(bed, ward):
                                    if not event['request']['intent']['slots']['choiceTwo'].get('value'):
                                        speech_output = "There is already an existing device configured to Bed -- "+ bed +" -- in Ward " +ward + ". -- Would you like to replace the existing device with this device? --"
                                        return build_response(attributes, elicit_slot2("", speech_output , "choiceTwo"))
                                    elif event['request']['intent']['slots']['choiceTwo'].get('value'):
                                        choice2 = event['request']['intent']['slots']['choiceTwo']['value']
                                        if choice2.lower() == "yes":
                                            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                            table = dynamodb.Table('Devices')
                                            
                                            response = table.scan(
                                            FilterExpression = Attr("bedNo").eq(bed) & Attr('wardNo').eq(ward)
                                            )
                                            for item in response["Items"]:
                                                oldDevice = item["deviceID"]
                                            
                                            response2 = table.delete_item(
                                                Key = {
                                                'deviceID' : oldDevice
                                                }
                                            )
                                            
                                            response3 = table.put_item(
                                                Item = {
                                                "deviceID": deviceID,
                                                "wardNo": ward,
                                                "bedNo": bed
                                                }
                                            )
                                            speech_output = "Setup complete! This device is now configured in ward " +str(ward) + ", bed number " +str(bed)
                                            return build_response(attributes, build_speechlet_response(card_title, speech_output, speech_output , True))
                                        elif choice2.lower() == "no":
                                            return build_response(attributes, build_speechlet_response(card_title, "Ok. Setup Cancelled, you can choose to setup this device anytime by opening device settings.", "Ok. Setup Cancelled, you can choose to setup this device anytime by opening device settings." , True))
                                        else:
                                            speech_output = "Sorry, I did not get you. Please tell me Yes, or No. -- Would you like to replace the existing device in ward " +ward +" with this device?"
                                            return build_response(attributes, elicit_slot2("", speech_output , "choiceTwo"))
                            else:
                                speech_output = "Sorry, Please say a number, tell me the bed number where this device is located."
                                return build_response(attributes, elicit_slot2("", speech_output , "bed"))
                    elif not validateAnswer(event['request']['intent']['slots']['ward']['value']):
                        speech_output = "Sorry, Please say a number, tell me the Ward number where this device is located."
                        return build_response(attributes, elicit_slot2("", speech_output , "ward"))
            elif choice.lower() == "no":
                return build_response(attributes, build_speechlet_response(card_title, "Ok. Setup Cancelled, you can choose to setup this device anytime by opening device settings.", "Ok. Setup Cancelled, you can choose to setup this device anytime by opening device settings." , True))
            else:
                speech_output = "Sorry, I did not get you. Please tell me Yes, or No. Would you like to configure this device now?"
                return build_response(attributes, elicit_slot2("", speech_output , "choice"))
    if configured:
        device = get_device_settings(deviceID)
        for item in device["Items"]:
            bedNo = item["bedNo"]
            wardNo = item["wardNo"]
            card_title = "Device Information"
            reprompt_string = "This device is in Ward " +wardNo + " , Bed " +bedNo +". To make changes, say -- update device settings -- or to reconfigure -- say -- reconfigure device"
            speech_output = "This Amazon Echo Device is located in -- Ward -- " +wardNo +" -- and -- Bed -- " +bedNo +".-- To reconfigure this device, -- please say -- reconfigure device. -- Or--, to edit the configuration,-- please say -- Update Device Settings "
        return build_response(attributes,build_speechlet_response(card_title, speech_output, reprompt_string , True))

"""For re-configuration"""
def reconfigure_device(event):
    deviceID = event['context']['System']['device']['deviceId']
    if not event['request']['intent']['slots']['choice'].get('value'):
        speech_output = "Are you sure you want to reconfigure this Device? This Action is Irreversable and your Current Settings will be removed."
        return build_response({}, elicit_slot2("", speech_output , "choice"))
    if event['request']['intent']['slots']['choice'].get('value'):
        choice = event['request']['intent']['slots']['choice']['value']
        if choice.lower() == "yes":
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.Table('Devices')
            response = table.delete_item(
                    Key = {
                        'deviceID' : deviceID
                    }
                )
            if not event['request']['intent']['slots']['choiceTwo'].get('value'):
                speech_output = "The configuration of this device has been reset. Say Configure device to configure it now"
                attributes = {
                    'reconfiguration' : 1
                }
                return build_response(attributes, elicit_slot2("", speech_output , "choiceTwo"))
            elif event['request']['intent']['slots']['choiceTwo'].get('value'):
                choiceTwo = event['request']['intent']['slots']['choiceTwo']['value']
                if choiceTwo.lower() == "yes":
                    speech_output = "You can configure your device anytime by opening device settings. Goodbye."
                    return build_response(attributes, build_speechlet_response(card_title, speech_output, "" , False))  
                elif choiceTwo.lower() == "no":
                    speech_output = "You can configure your device anytime by opening device settings. Goodbye."
                    return build_response({}, build_speechlet_response(card_title, speech_output, "" , True))  
                else:
                    speech_output = "Sorry, I did not get you. Would you like to Configure the Device Now?"
                    return build_response({}, elicit_slot2("", speech_output , "choiceTwo"))
        elif choice.lower() == "no":
            card_title = ""
            speech_output = "Reconfiguration Cancelled."
            reprompt_string = "Reconfiguration Cancelled"
            return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_string , True))
        else:
           speech_output = "Sorry, I did not catch you. Are you sure you want to reconfigure this Device? This Action is Irreversable and your Current Settings will be removed."
           return build_response({}, elicit_slot2("", speech_output , "choice"))
            
"""For Updating Device Settings"""    
def update_device_settings(event):
    deviceID = event['context']['System']['device']['deviceId']
    configured = device_configured(deviceID)
    if not configured:
        card_title = "Device Not Yet Configured"
        speech_output = "This device has not been Configured yet -- Please configure this device first. -- To configure this device --,  open -- device settings.-- "
        return build_response({},build_speechlet_response(card_title, speech_output, speech_output , False))
    if configured:
        device = get_device_settings(deviceID)
        for item in device["Items"]:
            archivedBedNo = item["bedNo"]
            archivedWardNo = item["wardNo"]
            
        if not event['request']['intent']['slots']['DeviceSettings'].get('value'):
            speech_output = "Which setting would you like to change? Ward, Bed or Both"
            return build_response({}, elicit_slot2("", speech_output , "DeviceSettings"))
            
        if event['request']['intent']['slots']['DeviceSettings'].get('value'):
            settingField = event['request']['intent']['slots']['DeviceSettings']['value']
            if settingField.lower() == "both" or settingField.lower() == "ward":
                if not event['request']['intent']['slots']['ward'].get('value'):
                    speech_output = "Tell me the new ward number of this device. "
                    return build_response({}, elicit_slot2("", speech_output , "ward"))
                if event['request']['intent']['slots']['ward'].get('value'):
                    wardNo = event['request']['intent']['slots']['ward']['value']
                    if not validateAnswer(wardNo):
                        speech_output = "Sorry, Please say a number. Tell me the new ward number of this device. "
                        return build_response({}, elicit_slot2("", speech_output , "ward"))
                    if validateAnswer(wardNo):
                        if settingField.lower() == "ward":
                            if archivedWardNo == wardNo:
                                speech_output = "This Device is already configured in Ward --" +wardNo +"-- at Bed --" +archivedBedNo +"-- . No Changes were made."
                                return build_response({},build_speechlet_response("",speech_output,"",True))
                            elif get_bed(archivedBedNo, wardNo):
                                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                table = dynamodb.Table('Devices')
                                response = table.update_item(
                                    Key={
                                    "deviceID" : deviceID
                                    },
                                    UpdateExpression="SET wardNo =:q",
                                    ExpressionAttributeValues={
                                    ':q' : wardNo
                                    },
                                    ReturnValues="UPDATED_NEW"
                                )
                                card_title = "Update Complete"
                                speech_output = "Completed. Your Settings has been updated. This device's location is now in Ward " +wardNo
                                return build_response({},build_speechlet_response(card_title, speech_output, speech_output , True))
                            elif not get_bed(archivedBedNo, wardNo):
                                if not event['request']['intent']['slots']['choice'].get('value'):
                                    speech_output = "There is already a device configured in Bed --" +archivedBedNo +" --in Ward-- " +wardNo +".-- Would you like to replace the existing device with this one?" 
                                    return build_response({}, elicit_slot2("", speech_output , "choice"))      
                                elif event['request']['intent']['slots']['choice'].get('value'):
                                    choice = event['request']['intent']['slots']['choice']['value']
                                    if choice.lower() == "yes":
                                        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                        table = dynamodb.Table('Devices')
                                        response = table.update_item(
                                            Key={
                                            "deviceID" : deviceID
                                            },
                                            UpdateExpression="SET wardNo =:q",
                                            ExpressionAttributeValues={
                                            ':q' : wardNo
                                            },
                                            ReturnValues="UPDATED_NEW"
                                        )
                                        card_title = "Update Complete"
                                        speech_output = "Completed. Your Settings has been updated. This device's location is now in Ward " +wardNo
                                        return build_response({},build_speechlet_response(card_title, speech_output, speech_output , True))
                                    elif choice.lower() == "no":
                                        return statement("OK","Ok. Setup Cancelled, you can choose to setup this device anytime by opening device settings.")
                                    else:
                                        speech_output = "Sorry, I did not hear you. Please Tell me Yes, or No. Would you like to replace the existing device with this one?" 
                                        return build_response({}, elicit_slot2("", speech_output , "choice"))
                        elif settingField.lower() == "both":
                            if not event['request']['intent']['slots']['bed'].get('value'):
                                speech_output = "Tell me the new bed number of this device. "
                                return build_response({}, elicit_slot2("", speech_output , "bed"))  
                            elif event['request']['intent']['slots']['bed'].get('value'):
                                bedNo = event['request']['intent']['slots']['bed']['value']
                                if not validateAnswer(bedNo):
                                    speech_output = "Sorry, I did not get you. Please say a number. What is the new ward number of this device? "
                                    return build_response({}, elicit_slot2("", speech_output , "bed"))
                                elif validateAnswer(bedNo):
                                     #If Bed/Ward is the Same as Previous Configuration
                                    if archivedBedNo == bedNo and archivedWardNo == wardNo:
                                        speech_output = "This Device is already configured in Ward --" +wardNo +"-- and Bed --" +bedNo +"-- . No Changes were made."
                                        return build_response({},build_speechlet_response("",speech_output,"",True))
                                    #Check if Bed is clear
                                    elif get_bed(bedNo, archivedWardNo): 
                                        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                        table = dynamodb.Table('Devices')
                                        response = table.update_item(
                                            Key={
                                            "deviceID" : deviceID
                                            },
                                            UpdateExpression="SET bedNo =:q, wardNo = :w",
                                            ExpressionAttributeValues={
                                            ':q' : bedNo,
                                            ':w' : wardNo
                                            },
                                            ReturnValues="UPDATED_NEW"
                                        )
                                        card_title = "Update Complete"
                                        speech_output = "Completed. Your Settings has been updated. This device's location is now in Ward " +wardNo +" and Bed " +bedNo 
                                        return build_response({},build_speechlet_response(card_title, speech_output, speech_output , True))
                                    #If Bed Not Clear
                                    elif not get_bed(bedNo, archivedWardNo):
                                        if not event['request']['intent']['slots']['choice'].get('value'):
                                            speech_output = "There is already a device configured in Bed --" +archivedBedNo +"-- in Ward --" +archivedWardNo +".-- Would you like to replace the existing device with this one?" 
                                            return build_response({}, elicit_slot2("", speech_output , "choice"))      
                                        elif event['request']['intent']['slots']['choice'].get('value'):
                                            choice = event['request']['intent']['slots']['choice']['value']
                                            if choice.lower() == "yes":
                                                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                                table = dynamodb.Table('Devices')
                                                response = table.update_item(
                                                    Key={
                                                    "deviceID" : deviceID
                                                    },
                                                    UpdateExpression="SET bedNo =:q, wardNo = :w",
                                                    ExpressionAttributeValues={
                                                    ':q' : bedNo,
                                                    ':w' : wardNo
                                                    },
                                                    ReturnValues="UPDATED_NEW"
                                                )
                                                card_title = "Update Complete"
                                                speech_output = "Completed. Your Settings has been updated. This device's location is now in Ward " +wardNo +" and Bed " +bedNo 
                                                return build_response({},build_speechlet_response(card_title, speech_output, speech_output , True))
                                            elif choice.lower() == "no":
                                                return statement("OK","Ok. Setup Cancelled, you can choose to setup this device anytime by opening device settings.")
                                            else:
                                                speech_output = "Sorry, I did not hear you. Please Tell me Yes, or No. Would you like to replace the existing device with this one?" 
                                                return build_response({}, elicit_slot2("", speech_output , "choice"))
            elif settingField.lower() == "bed":
                if not event['request']['intent']['slots']['bed'].get('value'):
                    speech_output = "Tell me the new bed number of this device. "
                    return build_response({}, elicit_slot2("", speech_output , "bed"))  
                elif event['request']['intent']['slots']['bed'].get('value'):
                    bedNo = event['request']['intent']['slots']['bed']['value']
                    if not validateAnswer(bedNo):
                        speech_output = "Sorry, I did not get you. Please say a number. What is the new ward number of this device? "
                        return build_response({}, elicit_slot2("", speech_output , "bed"))  
                    elif validateAnswer(bedNo):
                        if archivedBedNo == bedNo:
                            speech_output = "This Device is already configured in Bed --" +bedNo +"-- in Ward --" +archivedWardNo +"-- . No Changes were made."
                            return build_response({},build_speechlet_response("",speech_output,"",True))
                        elif get_bed(bedNo, archivedWardNo):
                            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                            table = dynamodb.Table('Devices')
                            response = table.update_item(
                                Key={
                                "deviceID" : deviceID
                                },
                                UpdateExpression="SET bedNo =:q",
                                ExpressionAttributeValues={
                                ':q' : bedNo
                                },
                                ReturnValues="UPDATED_NEW"
                            )
                            card_title = "Update Complete"
                            speech_output = "Completed. Your Settings has been updated. This device's location is now in Bed " +bedNo
                            return build_response({},build_speechlet_response(card_title, speech_output, speech_output , False))
                        elif not get_bed(bedNo, archivedWardNo):
                            if not event['request']['intent']['slots']['choice'].get('value'):
                                speech_output = "There is already a device configured in Bed " +archivedBedNo +" in Ward " +archivedWardNo +" Would you like to replace the existing device with this one?" 
                                return build_response({}, elicit_slot2("", speech_output , "choice"))  
                                
                            elif event['request']['intent']['slots']['choice'].get('value'):
                                choice = event['request']['intent']['slots']['choice']['value']
                                if choice.lower() == "yes":
                                    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                    table = dynamodb.Table('Devices')
                                    response = table.update_item(
                                        Key={
                                        "deviceID" : deviceID
                                        },
                                        UpdateExpression="SET bedNo =:q, wardNo = :w",
                                        ExpressionAttributeValues={
                                        ':q' : bedNo,
                                        ':w' : wardNo
                                        },
                                        ReturnValues="UPDATED_NEW"
                                    )
                                    card_title = "Update Complete"
                                    speech_output = "Completed. Your Settings has been updated. This device's location is now in Ward " +wardNo +" and Bed " +bedNo 
                                    return build_response({},build_speechlet_response(card_title, speech_output, speech_output , False))
                                elif choice.lower() == "no":
                                    return statement("OK","Ok. Setup Cancelled, you can choose to setup this device anytime by opening device settings.")
                                else:
                                    speech_output = "Sorry, I did not hear you. Please Tell me Yes, or No. Would you like to replace the existing device with this one?" 
                                    return build_response({}, elicit_slot2("", speech_output , "choice"))    
            else:
                speech_output = "Sorry I did not catch you, Please tell me which setting would you like to change "
                return build_response({}, elicit_slot2("", speech_output , "DeviceSettings")) 

#===== Who is in the Ward (ENGLISH ONLY) =====
"""Get all the Devices in a Ward (COMPLETED)"""
def get_names_from_ward(wardNo):
    patients = []
    empty = []
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Devices')
    response = table.scan(
        FilterExpression = Attr('wardNo').eq(wardNo)
        )
    for idx, item in enumerate(response['Items']):
        value = item['deviceID']
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('Patients')
        response2 = table.scan(
            FilterExpression = Attr('DeviceID').eq(value) & Attr('inUse').eq(1)
            )
        for item in response2['Items']:
            if len(response2['Items']) > 0:
                patients.extend([item['patientname']])
    if patients == empty:
        return 0 
    elif patients != empty:
        if len(patients) > 1:
            return ", ".join(patients)
        elif len(patients) == 1:
            return patients[0]

def whos_in_ward(event):
    attributes = {}
    if event['request']['intent']['slots']['ward'].get('value'):
        wardNo = event['request']['intent']['slots']['ward']['value']
        if get_names_from_ward(wardNo) == 0:
            card_title = "Ward" +str(wardNo) +" Empty"
            speech_output = "There are no active patients in Ward " +str(wardNo)
            return build_response(attributes, build_speechlet_response(card_title,speech_output,speech_output, False))
        elif get_names_from_ward(wardNo) != 0:
            speech_output = "Here are The Patients in Ward " +str(wardNo) +" : " +get_names_from_ward(wardNo)
            card_title = "Patients in Ward " +str(wardNo)
            return build_response(attributes, build_speechlet_response(card_title,speech_output,speech_output, False))
    elif not event['request']['intent']['slots']['ward'].get('value'):
        deviceID = event['context']['System']['device']['deviceId']
        if get_ward_from_DeviceID(deviceID) == 0:
            speech_output = "This Device is not associated with any ward as it not been configured. Please configure the device first by --opening device settings--. If you wish to retrieve patients from a particular ward, please say --who's in ward--, followed by the Ward Number."
            card_title = "Device not configured"
            return build_response(attributes, build_speechlet_response(card_title,speech_output,speech_output, False))
        elif get_ward_from_DeviceID(deviceID)!=0:
            wardNo = get_ward_from_DeviceID(deviceID)
            speech_output = "You are in Ward " +str(wardNo) +". Say Hello to your friends! -- They are " +get_names_from_ward(wardNo)
            card_title = "Patients in Ward " +str(wardNo)
            return build_response(attributes, build_speechlet_response(card_title,speech_output,speech_output, False))

def get_ward_from_DeviceID(deviceID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Devices')
    response = table.scan(
        FilterExpression = Attr("deviceID").eq(deviceID)
        )
    if len(response["Items"]) == 1:
        for item in response["Items"]:
            wardNo = item["wardNo"]
            return wardNo
    elif len(response["Items"]) == 0:
        return 0

def get_bed_from_DeviceID(deviceID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Devices')
    response = table.scan(
        FilterExpression = Attr("deviceID").eq(deviceID)
        )
    if len(response["Items"]) == 1:
        for item in response["Items"]:
            bedNo = item["bedNo"]
            return bedNo
    elif len(response["Items"]) == 0:
        return 0
    
"""Get Number of Devices in a Ward"""
def get_device_count_in_ward(wardNo):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Devices')
    response = table.scan(
        FilterExpression = Attr('wardNo').eq(wardNo)
        )
    return len(response['Items'])

#===== DELETE PATIENT (ENGLISH) =====
"""Delete Patient (ENGLISH ONLY) - WHEN NOT LOGGED IN """
def delete_patient(event, userID):
    if not event['request']['intent']['slots']['fullname'].get('value'):
        signedIn = get_session(userID,event)
        if signedIn == 0:
            attributes = {}
            speech_output = "Tell me the name of the User you would like to delete."
            card_title = ""
            return build_response(attributes,elicit_slot2(card_title,speech_output,"fullname"))
        if signedIn == 1:
            roundingID = get_roundID(userID)
            fullname = get_username(roundingID)
            phoneNumber = get_User_Phone(roundingID)
            if not event['request']['intent']['slots']['choice'].get('value'):
                attributes = {}
                card_title = "Delete " +str(fullname) +"? "
                speech_output = "You are signed in as " +str(fullname) +". Is this the account you would like to delete?"
                return build_response(attributes, elicit_slot2(card_title,speech_output,"choice"))
            elif event['request']['intent']['slots']['choice'].get('value'):
                choice =  event['request']['intent']['slots']['choice']['value']
                if choice.lower()=="yes":
                    #Edit Slot Value
                    event['request']['intent']['slots']['phoneNumber']['value'] = int(phoneNumber)
                    event['request']['intent']['slots']['fullname']['value'] = str(fullname)
                    return delete_patient(event, userID)
                elif choice.lower()=="no":
                    attributes = {}
                    speech_output = "Tell me the name of the User you would like to delete."
                    card_title = ""
                    return build_response(attributes,elicit_slot2(card_title,speech_output,"fullname"))
                else:
                    attributes = {}
                    card_title = "Delete " +str(fullname) +"? "
                    speech_output = "You are signed in as " +str(fullname) +". Is this the account you would like to delete?"
                    return build_response(attributes, elicit_slot2(card_title,speech_output,"choice"))
    if event['request']['intent']['slots']['fullname'].get('value'):
        fullname = event['request']['intent']['slots']['fullname']['value']
        #Return roundingID if Only 1 Account Exists, returns 0/-1 otherwise (-1 means more than 1 account), (0 means no account)
        exists = get_RoundingID_from_Name(fullname)
        #If Only One Account Exists
        if exists > 0:
            roundingID = exists
            #Check if user already has an OTP
            hasOTP = has_OTP(roundingID)
            #User doesnt have OTP, so generate one
            if hasOTP == 0:
                phoneNumber = get_User_Phone(roundingID)
                
                #Generate OTP
                Numbers = range(1000, 9999)
                OneTimePin = random.choice(Numbers)
                
                #Check that OTP does not exist
                OTPinDB = OTP_Exists(OneTimePin)
                while OTP_Exists(OneTimePin):
                    #Generate new OTP
                    OneTimePin = random.choice(Numbers)
                
                
                #Generate Epoch
                epochDate = datetime.datetime(1970,1,1)
                epoch = epochDate.timestamp()
                
                dateTimeNow = datetime.datetime.now()
                epochDateTimeNow = int(round(dateTimeNow.timestamp()))
                
                expiryDateTime = dateTimeNow + datetime.timedelta(minutes=5)
                epochexpiryDateTime = int(round(expiryDateTime.timestamp()))
                
                #Store OTP in DB
                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                table = dynamodb.Table('OneTimePins')
                response = table.put_item(
                        Item = {
                            "OTP" : OneTimePin,
                            "expiry": epochexpiryDateTime,
                            "generated": epochDateTimeNow,
                            "patientID" : roundingID
                        }
                    )
                #Send the SMS to Tell User the OTP
                sms_body = fullname+ ", Your One-Time Passcode (OTP) is :" +\
                           str(OneTimePin)
                sendSMS = send_sms(phoneNumber, sms_body)
                return delete_patient(event,userID)
            #User has OTP    
            elif hasOTP > 0:
                OneTimePin = hasOTP
                #Elicit OTP Slot
                if not event['request']['intent']['slots']['OneTimePinSlot'].get('value'):
                    card_title = "Patient " +str(roundingID) + ":One Time Pin Sent"
                    speech_output = "Please Tell me the One Time Passcode sent to the phone associated with this account. You can also choose to tell me later."
                    return build_response({}, elicit_slot2(card_title,speech_output, "OneTimePinSlot"))
                elif event['request']['intent']['slots']['OneTimePinSlot'].get('value'):
                    OneTimePinSlotValue = int(event['request']['intent']['slots']['OneTimePinSlot']['value'])
                    if OneTimePinSlotValue == OneTimePin:
                        #If Elicit OTP Slot is Valid
                        #Delete Function Codes
                        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                        table = dynamodb.Table('Patients')
                        response = table.delete_item(
                                Key = {
                                    'RoundingID' : roundingID
                                }
                            )
                        card_title = "Patient " +str(roundingID) +" Removed"
                        speech_output = "The Account " + fullname + " has been deleted. Goodbye!"
                        reprompt_string = ""
                        return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_string , True))
                    elif OneTimePinSlotValue != OneTimePin:
                        card_title = "Patient " +str(roundingID) + ":One Time Pin Sent"
                        speech_output = "Please Tell me the One Time Passcode sent to the phone associated with this account. You can also choose to tell me later."
                        return build_response({},elicit_slot2(card_title,speech_output, "OneTimePinSlot"))
        #More than one Account with the same name
        elif exists == -1:
            #-- Ask for Phone Number --
            if not event['request']['intent']['slots']['phoneNumber'].get('value'):
                card_title = "More than One User with the name" +fullname
                speech_output = "There is more than one account with the name " +fullname + ". To continue with the deletion process, tell me the phone number of the account you would like to delete."
                return build_response({},elicit_slot2(card_title,speech_output,"phoneNumber"))
            if event['request']['intent']['slots']['phoneNumber'].get('value'):
                providedPhoneNumber = event['request']['intent']['slots']['phoneNumber']['value']
                #If exists return one else zero
                phoneExists = validateNumber(providedPhoneNumber)
                #Phone Number Exists
                if phoneExists == 1:
                    roundingID = get_RoundingID_from_Phone(providedPhoneNumber)
                    #Check if User has an OTP
                    hasOTP = has_OTP(roundingID)
                    #no OTP
                    if hasOTP == 0:
                        phoneNumber = get_User_Phone(roundingID)
                        #Generate OTP
                        Numbers = range(1000, 9999)
                        OneTimePin = random.choice(Numbers)
                        
                        #Check that OTP does not exist
                        OTPinDB = OTP_Exists(OneTimePin)
                        while OTP_Exists(OneTimePin):
                            #Generate new OTP
                            OneTimePin = random.choice(Numbers)
                        
                        
                        #Generate Epoch
                        epochDate = datetime.datetime(1970,1,1)
                        epoch = epochDate.timestamp()
                        
                        dateTimeNow = datetime.datetime.now()
                        epochDateTimeNow = int(round(dateTimeNow.timestamp()))
                        
                        expiryDateTime = dateTimeNow + datetime.timedelta(minutes=5)
                        epochexpiryDateTime = int(round(expiryDateTime.timestamp()))
                        
                        #Store OTP in DB
                        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                        table = dynamodb.Table('OneTimePins')
                        response = table.put_item(
                                Item = {
                                    "OTP" : OneTimePin,
                                    "expiry": epochexpiryDateTime,
                                    "generated": epochDateTimeNow,
                                    "patientID" : roundingID
                                }
                            )
                        #Send the SMS to Tell User the OTP
                        sms_body = fullname+ ", Your One-Time Passcode (OTP) is :" +\
                                   str(OneTimePin)
                        sendSMS = send_sms(phoneNumber, sms_body)
                        
                        return delete_patient(event,userID)
                    #hasOTP    
                    elif hasOTP > 0:
                        OneTimePin = hasOTP
                        #Elicit OTP Slot
                        if not event['request']['intent']['slots']['OneTimePinSlot'].get('value'):
                            card_title = "Patient " +str(roundingID) + ":One Time Pin Sent"
                            speech_output = "Please Tell me the One Time Passcode sent to the phone associated with this account. You can also choose to tell me later."
                            return build_response({}, elicit_slot2(card_title,speech_output, "OneTimePinSlot"))
                        elif event['request']['intent']['slots']['OneTimePinSlot'].get('value'):
                            OneTimePinSlotValue = int(event['request']['intent']['slots']['OneTimePinSlot']['value'])
                            if OneTimePinSlotValue == OneTimePin:
                                #If Elicit OTP Slot is Valid
                                #Delete Function Codes
                                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                table = dynamodb.Table('Patients')
                                response = table.delete_item(
                                        Key = {
                                            'RoundingID' : roundingID
                                        }
                                    )
                                card_title = "Patient " +str(roundingID) +" Removed"
                                speech_output = "The Account " + fullname + " has been deleted. Goodbye!"
                                reprompt_string = ""
                                return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_string , True))
                            elif OneTimePinSlotValue != OneTimePin:
                                card_title = "Patient " +str(roundingID) + ":One Time Pin Sent"
                                speech_output = "Please Tell me the One Time Passcode sent to the phone associated with this account. You can also choose to tell me later."
                                return build_response({},elicit_slot2(card_title,speech_output, "OneTimePinSlot"))
                #Phone Number Doesn't Exist    
                elif phoneExists == 0:
                    attributes = {}
                    card_title = "Phone Number doesn't exist"
                    speech_output = "The Phone Number you gave does not exist. Please Try again or to Cancel, say Stop."
                    return build_response(attributes, elicit_slot2(card_title,speech_output,"phoneNumber"))
        #no Account
        elif exists == 0:
            card_title = ""
            speech_output = "Sorry, there is no account with the name " +fullname +". Please tell me another name or to cancel, say Stop"
            attributes = {}
            return build_response(attributes,elicit_slot2(card_title,speech_output,"fullname"))

"""Check if User already has an OTP (returns the OTP if exists else 0)"""
def has_OTP(roundingID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('OneTimePins')
    response = table.scan(
        FilterExpression = Attr("patientID").eq(roundingID)
        )
    if len(response["Items"]) == 1:
        for item in response["Items"]:
            oneTimePin = item["OTP"]
            return oneTimePin
    elif len(response["Items"]) == 0:
        oneTimePin = 0
        return oneTimePin
    else:
        oneTimePin = 0
        return oneTimePin

"""Check if the OTP exists since it is the Primary Key. Why?
There should not be any duplicates"""
def OTP_Exists(OneTimePin):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('OneTimePins')
    response = table.scan(
        FilterExpression = Attr("OTP").eq(OneTimePin)
        )
    if len(response["Items"]) == 1:
        result = True
        return result
    elif len(response["Items"]) == 0:
        result = False
        return result
    else:
        #Error (This line of code should not be reachable in a case)
        result = False
        return result

#===== Get User's Lastest Rounding (ENGLISH ONLY)=====        
"""Show Last Rounding"""
def myLastRounding(event):
    userID = event['session']['user']['userId']
    patientID = get_roundID(userID)
    lastRoundingID = get_lastRounding(patientID)
    #Has a Last Rounding
    if lastRoundingID > 0:
        roundingID = lastRoundingID
        roundingDetails = getLastRounding(patientID)
        if roundingDetails !=0:
            WashRoom = 0
            Glasses = 0
            CompletedTime = 0
            NextTime = 0
            for item in roundingDetails["Items"]:
                WashRoom = item["WashRoom"]
                Glasses = item["WaterGlasses"]
                CompletedTime = item["Completed"]
                NextTime = item["NextRounding"]
                
                dateTimeCompleted = datetime.datetime.strptime(CompletedTime, '%H:%M %d-%m-%Y')
                stringTimeCompleted = str(dateTimeCompleted.strftime('%H:%M'))
                
                dateTimeNext = datetime.datetime.strptime(NextTime, '%H:%M %d-%m-%Y')
                stringTimeNext = str(dateTimeNext.strftime('%H:%M'))
                
                datetimeNow = str(datetime.datetime.now().strftime('%H:%M %d-%m-%Y'))
                currentTime = datetime.datetime.strptime(datetimeNow, '%H:%M %d-%m-%Y')
                    
                datetimeThen = get_lastRounding_Time(lastRoundingID)
                lastRoundingTime = datetime.datetime.strptime(datetimeThen, '%H:%M %d-%m-%Y')
                
            if currentTime < lastRoundingTime:
                attributes = {}
                card_title = "Patient " +str(patientID) +" Last Rounding Details"
                speech_output = "Here is your last rounding session, Completed at " +stringTimeCompleted +". " +\
                                "You Drank " +str(Glasses) +" Glasses of Water and you made " +\
                                str(WashRoom) +" trips to the washroom. " +\
                                "Your Next Rounding Session will be at " + stringTimeNext + ". "
                reprompt_text = str(Glasses) + " Glasses of Water and Made " +\
                                str(WashRoom) + " Trips to the Washroom." +\
                                " Your Rounding was completed at " +stringTimeCompleted +". " +\
                                "Your Next Rounding is due at " +stringTimeNext +". "
                should_end_session = False
                return build_response(attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
            elif currentTime > lastRoundingTime:
                attributes = {}
                card_title = "Patient " +str(patientID) +" Last Rounding Details"
                speech_output = "Here is your last rounding session, Completed at " +stringTimeCompleted +". " +\
                                "You Drank " +str(Glasses) +" Glasses of Water and you made " +\
                                str(WashRoom) +" trips to the washroom. " +\
                                "Your next Rounding Session is Ready."
                reprompt_text = str(Glasses) + " Glasses of Water and Made " +\
                                str(WashRoom) + " Trips to the Washroom." +\
                                " Your Rounding was completed at " +stringTimeCompleted +". " +\
                                "Your next Rounding Session is Ready."
                should_end_session = False
                return build_response(attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
        elif roundingDetails == 0:
            attributes = {}
            title = "An Unknown Error Occured."
            body = "An Unknown Error Occured. Please try again later"
            return build_response(attributes,build_speechlet_response(title,body,body,True))
        else:
            attributes = {}
            title = "An Unknown Error Occured."
            body = "An Unknown Error Occured. Please try again later"
            return build_response(attributes,build_speechlet_response(title,body,body,True))
    #Has not done a Rounding at all    
    elif lastRoundingID == 0:
        attributes = {}
        card_title = "No Rounding Record Found"
        speech_output = "You have not completed any rounding sessions. Say Start Rounding to Begin one."
        reprompt_string = "You have no roundings. Say Start Rounding to Start your Rounding Session. "
        return build_response(attributes,build_speechlet_response(card_title,speech_output,reprompt_string,False))   
    else:
        attributes = {}
        title = "An Unknown Error Occured."
        body = "An Unknown Error Occured. Please try again later"
        return build_response(attributes,build_speechlet_response(title,body,body,True))

"""Get Response of a User's Last Rounding"""
def getLastRounding(roundingID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Roundings')
    response = table.scan(
        FilterExpression = Attr("PatientID").eq(roundingID) & Attr("Latest").eq(1)
        )
    if len(response["Items"]) == 1:
        return response
    elif len(response["Items"]) == 0:
        result = 0
        return result
    else:
        #Error (This line of code should not be reachable in a case)
        result = 0
        return result
        
#===== Who's in Bed (ENGLISH ONLY)=====
"""Who is in Bed"""
def whos_in_Bed(event):
    #-No Ward, No Bed Provided
    if not event['request']['intent']['slots']['wardNo'].get('value') and not event['request']['intent']['slots']['bedNo'].get('value'):
        card_title = "No Ward & Bed"
        speech_output = "Sorry, I did not hear a Ward or Bed Number. To find out an occupant of a bed, please provide a ward and bed number."
        reprompt_string = "Please Provide a Bed and Ward Number."
        attributes = {}
        return build_response(attributes,build_speechlet_response(card_title,speech_output,reprompt_string,False))
    #- Bed Provided, but Not Ward.
    elif event['request']['intent']['slots']['bedNo'].get('value') and not event['request']['intent']['slots']['wardNo'].get('value'):
        #Check if bedNo is an Int
        bedNo = event['request']['intent']['slots']['bedNo']['value']
        bedVerify = validateAnswer(bedNo)
        if bedVerify:
            card_title = "Bed "+ str(bedNo) +", No Ward Provided."
            speech_output = "In which ward would you like to retrieve the patient in bed " +str(bedNo)
            attributes = {}
            slotToElicit = "wardNo"
            return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit))
        else:
            card_title = "Bed Provided, But an Error Occured." +" No Ward Provided."
            speech_output = "You were providing a Bed Number, But I did not catch you. Please Tell me the bed Number again."
            attributes = {}
            slotToElicit = "bedNo"
            return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit))
    #- Ward Provided, but no Bed 
    #- Will go to Whos_in_Ward Intent anyways HAHA (So Don't need to write any codes)
    
    #Bed Provided, Ward Provided.
    elif event['request']['intent']['slots']['bedNo'].get('value') and event['request']['intent']['slots']['wardNo'].get('value'):
        bedNo = event['request']['intent']['slots']['bedNo']['value']
        bedVerify = validateAnswer(bedNo)
        wardNo = event['request']['intent']['slots']['wardNo']['value']
        wardVerify = validateAnswer(wardNo)
        #- If BedNo not Valid
        if not bedVerify:
            card_title = "Bed Provided, But an Error Occured."
            speech_output = "You provided a Bed Number, But an error occured. Please Tell me the bed Number again."
            attributes = {}
            slotToElicit = "bedNo"
            return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit))
        #- If WardNo not Valid
        elif not wardVerify:
            card_title = "Ward Provided, But an Error Occured."
            speech_output = "You provided a Ward Number, But an error occured. Please Tell me the Ward Number again."
            attributes = {}
            slotToElicit = "wardNo"
            return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit))
        #- If Both Valid
        elif wardVerify and bedVerify:
            BedWardDevice = get_DeviceID_From_Bed_and_Ward(bedNo,wardNo)
            if BedWardDevice is not False:
                patientID = get_Patient_in_DeviceID_InUse(BedWardDevice)
                if patientID is False:
                    card_title = "No Active Patient Found in Ward " +str(wardNo) +", Bed " +str(bedNo) + "."
                    speech_output = "There is no Patient currently in Ward "+str(wardNo) +" and Bed " +str(bedNo) +"." 
                    reprompt_string = "No Patient Currently found in Ward " +str(wardNo) +" and Bed " +str(bedNo) + "."
                    attributes = {}
                    return build_response(attributes,build_speechlet_response(card_title,speech_output,reprompt_string,False))
                else:
                    patientName = get_username(patientID)
                    card_title = "Patient in Ward " +str(wardNo) +", Bed " +str(bedNo) + " is " +patientName +"."
                    speech_output = "The patient in Ward "+str(wardNo) +" and Bed " +str(bedNo) +" is " +patientName +"." 
                    reprompt_string = patientName + " is in Ward " +str(wardNo) +" and Bed " +str(bedNo) + "."
                    attributes = {}
                    return build_response(attributes,build_speechlet_response(card_title,speech_output,reprompt_string,False))
            elif BedWardDevice is False:
                card_title = "No Device Found in Ward " +str(wardNo) +", Bed " +str(bedNo) + "."
                speech_output = "There is no device configured in Ward "+str(wardNo) +"and Bed " +str(bedNo) +"." 
                reprompt_string = "No device found in Ward " +str(wardNo) +"and Bed " +str(bedNo) + "."
                attributes = {}
                return build_response(attributes,build_speechlet_response(card_title,speech_output,reprompt_string,False))

"Get device ID from Bed and Ward"
def get_DeviceID_From_Bed_and_Ward(bedNo, wardNo):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Devices')
    response = table.scan(
        FilterExpression = Attr("bedNo").eq(bedNo) & Attr('wardNo').eq(wardNo)
        )
    if len(response["Items"]) > 0:
        for item in response['Items']:
            deviceID = item['deviceID']
            return deviceID
    elif len(response["Items"]) == 0:
        return False
        
"""Get Patient from the DeviceID and the InUse is 1"""
def get_Patient_in_DeviceID_InUse(deviceID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
        FilterExpression = Attr("DeviceID").eq(deviceID) & Attr('inUse').eq(1)
        )
    if len(response["Items"]) > 0:
        for item in response['Items']:
            patientID = item['RoundingID']
            return patientID
    elif len(response["Items"]) == 0:
        return False

"""Where are We (ENGLISH)"""
def where_am_I(event):
    deviceID = event['context']['System']['device']['deviceId']
    wardNo = get_ward_from_DeviceID(deviceID)
    bedNo = get_bed_from_DeviceID(deviceID)
    if wardNo != 0 and bedNo != 0:
        card_title = "Ward "+ " Bed " +"."
        speech_output = "You are in Ward " +str(wardNo) +" and Bed " +str(bedNo) +"."
        reprompt_string = "We are in Ward " +str(wardNo) +" and Bed " +str(bedNo) +"."
        attributes = {}
        return build_response(attributes,build_speechlet_response(card_title,speech_output,reprompt_string,False)) 
    elif wardNo == 0 or bedNo == 0:
        card_title = "Error"
        speech_output = "Sorry, I do not know where we are."
        reprompt_string = "Where are we? Sorry, but I don't know as well."
        attributes = {}
        return build_response(attributes,build_speechlet_response(card_title,speech_output,reprompt_string,False))

"""Send Feedback"""
def send_Feedback(event):
    #Prompt User to Speak
    if not event['request']['intent']['slots']['speech'].get('value'):
        speech_output = "Please Speak, but keep it short."
        card_title = ""
        slotToElicit = "speech"
        attributes = {}
        return build_response(attributes, elicit_slot2(card_title,speech_output,slotToElicit))
    #Once user Speaks Confirm
    elif event['request']['intent']['slots']['speech'].get('value'):
        if not event['request']['intent']['slots']['choice'].get('value'):
            userSpeech = event['request']['intent']['slots']['speech']['value']
            speech_output = "You Said-- : " +str(userSpeech) +". Is that correct?"
            card_title = ""
            slotToElicit = "choice"
            attributes = {}
            return build_response({}, elicit_slot2(card_title,speech_output,slotToElicit))
        elif event['request']['intent']['slots']['choice'].get('value'):
            if event['session'].get('attributes'):
                if event['session']['attributes'].get('FeedbackLoop'):
                    loop = 1
            else:
                loop = 0
                
            choice = event['request']['intent']['slots']['choice']['value']
            if loop == 1:
                userSpeech = event['request']['intent']['slots']['speech']['value']
                speech_output = "You Said-- : " +str(userSpeech) +". Is that correct?"
                card_title = ""
                slotToElicit = "choice"
                attributes = {}
                return build_response({}, elicit_slot2(card_title,speech_output,slotToElicit))
            elif choice.lower() == "yes":
                deviceID = event['context']['System']['device']['deviceId']
                userID = event['session']['user']['userId']
                
                bedNo = get_bed_from_DeviceID(deviceID)
                wardNo = get_ward_from_DeviceID(deviceID)
                patientID = get_roundID(userID)
                patientName = get_username(patientID)
                patientPhone = get_User_Phone(patientID)
                
                userSpeech = event['request']['intent']['slots']['speech']['value']
                #=====Send the Email=====
                #Define SMTP Library
                mail = smtplib.SMTP('smtp.gmail.com', 587)
                #Verification
                mail.ehlo()
                #Any SMTP Command To Encrypt as we are logging in
                mail.starttls()
                #Log in
                mail.login('email@gmail.com','censored')
                #Define Message
                subject = "HealthBuddy Feedback/Report System"
                
                msg = "Patient Name: " +patientName +"\n" +\
                      "Patient ID: " +str(patientID) +"\n" +\
                      "Patient Phone Number: " +str(patientPhone) +"\n" +\
                      "\nWard Number: " +str(wardNo) + "\n" +\
                      "Bed Number: " + str(bedNo) + "\n" +\
                      "\nMessage: " +"\n\t" +\
                      userSpeech +". \n \n" +\
                      "\n\nSent to Ernest, HealthBuddy(C) \nAll Rights Reserved, 2018"
                      
                message = 'Subject: {}\n\n{}'.format(subject,msg)
                #Send Mail
                mail.sendmail('HealthBuddySG@gmail.com','HealthBuddySG@gmail.com',message)
                mail.close()
                
                speech_output = "Thank You, your request has been forwarded to HealthBuddy. Your Responses are Key as we look forward to serving you better."
                card_title = ""
                attributes = {}
                return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output, False))
            elif choice.lower() == "no":
                #Clear the Slot
                speech_output = "Sorry, please Speak again, but keep it short."
                card_title = ""
                slotToElicit = "speech"
                attributes = {
                    'FeedbackLoop' : True
                }
                return build_response(attributes, elicit_slot2(card_title,speech_output,slotToElicit))
            else:
                userSpeech = event['request']['intent']['slots']['speech']['value']
                speech_output = "Sorry, I did not catch you. You Said-- : " +str(userSpeech) +". Is that correct?"
                card_title = ""
                slotToElicit = "choice"
                attributes = {}
                return build_response({}, elicit_slot2(card_title,speech_output,slotToElicit))
                    
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Requires Testing !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""Forgot Name/Number"""
def forgot_account(event):
    if not event['request']['intent']['slots']['userSettings'].get('value'):
        speech_output = "Did you forget your name or your number?"
        slotToElicit = "userSettings"
        card_title = ""
        attributes = {}
        return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit))
    elif event['request']['intent']['slots']['userSettings'].get('value'):
        userSettings =  event['request']['intent']['slots']['userSettings']['value']
        #If Forgot Name
        if userSettings.lower() == "name":
            #Ask for Number
            if not event['request']['intent']['slots']['number'].get('value'):
                speech_output = "Please tell me your phone number."
                slotToElicit = "number"
                card_title = ""
                attributes = {}
                return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit))
            elif event['request']['intent']['slots']['number'].get('value'):
                phoneNumber = event['request']['intent']['slots']['number']['value']
                phoneExists = get_name_from_Phone(phoneNumber)
                if phoneExists is False:
                    card_title = "Account Doesn't Exist with that Number"
                    speech_output = "There is no account associated with that number. Please Create an Account or Try again."
                    attributes = {}
                    shouldEndSession = False
                    return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,shouldEndSession))
                elif phoneExists is not False:
                    patientName = phoneExists
                    card_title = "Account Found"
                    speech_output = "Your name is " +str(patientName) + "."
                    shouldEndSession = False
                    attributes = {}
                    return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,False))
        #If Forgot Number    
        elif userSettings.lower() == "phone number" or userSettings.lower() == "phone" or userSettings.lower() == "number":
            if not event['request']['intent']['slots']['name'].get('value'):
                card_title = ""
                speech_output = "What is your name?"
                attributes = {}
                slotToElicit = "name"
                return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit))
            elif event['request']['intent']['slots']['name'].get('value'):
                patientName = event['request']['intent']['slots']['name']['value']
                nameExists = get_phone_number_from_name(patientName)
                if nameExists is not False and nameExists >0:
                    phoneNumber = nameExists
                    card_title = "Account Phone Number Found"
                    speech_output = "<speak>Your Phone Number is <say-as interpret-as='digits'>" +phoneNumber +"</say-as></speak>"
                    attributes = {}
                    return build_response(attributes,build_special_speechlet_response(card_title,speech_output,speech_output,False))
                elif nameExists is not False and nameExists == 0:
                    if not event['request']['intent']['slots']['wardNo'].get('value'):
                        slotToElicit = "wardNo"
                        speech_output = "There is more than one account with your name, Instead, please tell me your ward Number."
                        card_title = ""
                        attributes = {}
                        return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit))
                    elif event['request']['intent']['slots']['wardNo'].get('value'):
                        wardNo = event['request']['intent']['slots']['wardNo']['value']
                        validate1 = validateAnswer(wardNo)
                        if validate1:
                            if not event['request']['intent']['slots']['bedNo'].get('value'):
                                slotToElicit = "bedNo"
                                speech_output = "Please tell me your Bed Number."
                                card_title = ""
                                attributes = {}
                                return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit))
                            if event['request']['intent']['slots']['bedNo'].get('value'):
                                bedNo =  event['request']['intent']['slots']['bedNo']['value']
                                validate2 = validateAnswer(bedNo)
                                if validate2:
                                    deviceID2 = get_deviceID_from_bed_ward(wardNo,bedNo)
                                    if deviceID2 is not False:
                                        phoneNumber = get_phone_from_deviceID(deviceID2,patientName)
                                        speech_output = "<speak>Your Phone Number is <say-as interpret-as='digits'>"+ str(phoneNumber) + "</say-as></speak>"
                                        card_title = "Account Found"
                                        attributes = {}
                                        shouldEndSession = False
                                        return build_response(attributes,build_special_speechlet_response(card_title,speech_output,speech_output,shouldEndSession))
                                    else:
                                        speech_output = "No Account found in that Ward / Device, Please Contact the Admin by Saying Send feedback"
                                        card_title = "No account Found"
                                        attributes = {}
                                        shouldEndSession = True
                                        return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,shouldEndSession))
                                elif not validate2:
                                    slotToElicit = "bedNo"
                                    speech_output = "Sorry an error occured. Please tell me your Bed Number."
                                    card_title = ""
                                    attributes = {}
                                    return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit)) 
                        elif not validate1:
                            slotToElicit = "wardNo"
                            speech_output = "Sorry an error occured. Please tell me your ward Number."
                            card_title = ""
                            attributes = {}
                            return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit)) 
                elif nameExists is False:
                    speech_output = "There is no account found with the name " +fullname + ". "
                    card_title = "No Account Found"
                    shouldEndSession = False
                    attributes = {}
                    return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,False))
        #If Forgot Both
        #If did not catch user
        else:
            speech_output = "Sorry, I did not catch you. Did you forget your name, your number or both?"
            slotToElicit = "userSettings"
            card_title = ""
            attributes = {}
            return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit))
    else:
        speech_output = "A Fatal Error Occured, Please report it by saying Send feedback."
        card_title = "Fatal Error: Forgot Account"
        attributes = {}
        shouldEndSession = True
        return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,shouldEndSession))

"""Get Patient Name from Phone Number"""
def get_name_from_Phone(phoneNumber):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
        FilterExpression = Attr("phoneNumber").eq(phoneNumber)
        )
    if len(response["Items"]) > 0:
        for item in response['Items']:
            patientname = item['patientname']
            return patientname
    elif len(response["Items"]) == 0:
        return False    

"""Get Patient Phone Number from Patient Name"""     
def get_phone_number_from_name(name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
        FilterExpression = Attr("patientname").eq(name)
        )
    if len(response["Items"]) > 0:
        for item in response['Items']:
            if len(response["Items"]) == 1:
                phoneNumber = item['phoneNumber']
                return phoneNumber
            elif len(response["Items"]) > 1:
                return 0
    elif len(response["Items"]) == 0:
        return False    

"""Get Device ID from Bed,Ward"""
def get_deviceID_from_bed_ward(wardNo,bedNo):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Devices')
    response = table.scan(
        FilterExpression = Attr("bedNo").eq(bedNo) & Attr('wardNo').eq(wardNo)
        )
    if len(response["Items"]) > 0:
        for items in response["Items"]:
            deviceID = items['deviceID']
            return deviceID
    elif len(response["Items"]) == 0:
        return False
        
"""Get Phone from Device ID"""
def get_phone_from_deviceID(deviceID,name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan(
        FilterExpression = Attr("DeviceID").eq(deviceID) & Attr("patientname").eq(name)
        )
    if len(response["Items"]) > 0:
        for item in response['Items']:
            if len(response["Items"]) == 1:
                phoneNumber = item['phoneNumber']
                return phoneNumber
            elif len(response["Items"]) > 1:
                return 0
    elif len(response["Items"]) == 0:
        return False   

"""Update User Settings (Chinese)"""
def update_user_settings_Chinese(event):
    if event['session'].get('attributes'):
        if not event['session']['attributes'].get('current_question_no'):
            attributes = event['session']['attributes']
    else:
        attributes = {}
    
    userSettings = "null"    
    userID = event['session']['user']['userId']
    signedIn = get_session(userID,event)
    roundingID = get_roundID(userID)
    if signedIn == 1:
        if not event['request']['intent']['slots']['ZH_UserSettings'].get('value'):
            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_Welcome.mp3"
            audioBuilder = "<audio src = '" + audioFileURL + "'/>"
        
            speech_output = "<speak>" + audioBuilder + "</speak>"
            return build_response(attributes, elicit_slot("", speech_output , "ZH_UserSettings"))
        elif event['request']['intent']['slots']['ZH_UserSettings'].get('value'):
            userSettings = event['request']['intent']['slots']['ZH_UserSettings']['resolutions']['resolutionsPerAuthority']
            for items in userSettings:
                if items.get('values'):
                    for items in items['values']:
                        userSettings = str(items['value']['name'])
           
            # -- Change Name --
            if userSettings.lower() == "name":
                if event['session'].get('attributes'):
                    if event['session']['attributes'].get('newName'):
                        if event['request']['intent']['slots']['choiceTwo'].get('value'):
                            clear = event['request']['intent']['slots']['choiceTwo']
                            clear.pop('value')
                            clear.pop('resolutions')
                            attributes = {
                                'NameLoop' : True
                            }
                            
                        if event['request']['intent']['slots']['choice'].get('value'):
                            clear2 = event['request']['intent']['slots']['choice']
                            clear2.pop('value')
                            clear2.pop('resolutions')
                            clear3 = event['session']['attributes']
                            clear3.pop('newName')
                            
                #- Prompt User for new name -
                if not event['request']['intent']['slots']['newName'].get('value'):
                    audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_GetName.mp3" #--New Name Prompt
                    audioBuilder = "<audio src ='" + audioFileURL + "'/>"
                    
                    speech_output = "<speak>"
                    speech_output_end = "</speak>"
                    
                    returnSpeech = speech_output + audioBuilder + speech_output_end
                    return build_response(attributes, elicit_slot("", returnSpeech , "newName"))
                elif event['request']['intent']['slots']['newName'].get('value'):
                    oldName = get_username(roundingID)
                    newName = event['request']['intent']['slots']['newName']['value']
                    if oldName != newName:
                    #- Ask User if he/she is sure that he want to change the name to newName.
                        if not event['request']['intent']['slots']['choice'].get('value'):
                            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_newName.mp3" #--Confirm Name Change (Ni de xing min zhi shi..)
                            audioBuilder = "<audio src ='" + audioFileURL + "'/>"
                            
                            audioFileURL2 = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_Confirmation.mp3" #(DUI MA ?)
                            audioBuilder2 = "<audio src ='" + audioFileURL2 + "'/>"
                            
                            stringBuilder = audioBuilder + newName +"." + audioBuilder2 +"?"
                            ssmlWrapper = "<speak>" + stringBuilder + "</speak>"
                            speech_output = ssmlWrapper
                            return build_response(attributes, elicit_slot("", speech_output , "choice"))
                        elif event['request']['intent']['slots']['choice'].get('value'):
                            choice = "null"
                            choiceList = event['request']['intent']['slots']['choice']['resolutions']['resolutionsPerAuthority']
                            for items in choiceList:
                                if items.get('values'):
                                    for items in items['values']:
                                        choice = str(items['value']['name'])

                            if choice.lower() == "yes":
                                dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                table = dynamodb.Table('Patients')
                                response = table.update_item(
                                    Key={
                                        "RoundingID" : roundingID
                                    },
                                    UpdateExpression="SET patientname =:q",
                                    ExpressionAttributeValues={
                                        ':q' : newName
                                    },
                                    ReturnValues="UPDATED_NEW"
                                    )
                                card_title = "Patient ID " +str(roundingID) +": Name Changed"
                                
                                audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_NameUpdated.mp3" #--(Wan Cheng, ni de xing ming zhi shi)
                                audioBuilder = "<audio src = ' " +audioFileURL + "' />"
                                audioFileURL2 = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_YourOldName.mp3" #--(Ni de jiu ming zhi shi)
                                audioBuilder2 = "<audio src = ' " +audioFileURL2 + "' />"

                                returnString = audioBuilder + newName + "." + audioBuilder2 + oldName
                                
                                speech_output = "<speak>" + returnString + "</speak>"
                                return build_response(attributes, build_special_speechlet_response(card_title,speech_output,speech_output, False))
                                
                            elif choice.lower() == "no":
                                #ask User if they wanna give a new name. (Use ChoiceTwo)
                                if event['session'].get('attributes'):
                                    if event['session']['attributes'].get('NameLoop'):
                                        loop = 1
                                else:
                                    loop = 0
                                
                                if not event['request']['intent']['slots']['choiceTwo'].get('value'):
                                    audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_NameRePrompt.mp3" #(Wo Ke Neng Ting Cuo Le. Ni Yao ba ming zi zai jiang yi ci ma)
                                    audioBuilder = "<audio src =' " + audioFileURL + "'/> "
                                    
                                    returnString = audioBuilder
                                    
                                    speech_output = "<speak>" + returnString + "</speak>"
                                    return build_response(attributes, elicit_slot("", speech_output , "choiceTwo")) 
                                elif loop == 1:
                                    audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_NameRePrompt.mp3" #(Wo Ke Neng Ting Cuo Le. Ni Yao ba ming zi zai jiang yi ci ma)
                                    audioBuilder = "<audio src =' " + audioFileURL + "'/> "
                                    
                                    returnString = audioBuilder
                                    
                                    speech_output = "<speak>" + returnString + "</speak>"
                                    
                                    attributes= {}
                                    return build_response(attributes, elicit_slot("", speech_output , "choiceTwo")) 
                                elif event['request']['intent']['slots']['choiceTwo'].get('value'):
                                    choiceTwo = "null"
                                    choiceTwoList = event['request']['intent']['slots']['choiceTwo']['resolutions']['resolutionsPerAuthority']
                                    for items in choiceList:
                                        if items.get('values'):
                                            for items in items['values']:
                                                choiceTwo= str(items['value']['name'])
                                                    
                                    #If Yes Ask user to Give new name
                                    if choiceTwo.lower() == "yes":
                                        #Do the Attributes
                                        attributes = {
                                            'newName' : True
                                        }
                                        
                                        audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_nameRePrompt2.mp3" #-(WO TING CUO LE, HENG BAO QIAN. QING GAO SU WO NI DE XIN MING ZI)
                                        audioBuilder = "<audio src = '" + audioFileURL + "'/>"
                                        
                                        returnString = audioBuilder
                                        
                                        speech_output = "<speak>" + returnString + "</speak>"
                                        return build_response(attributes, elicit_slot("", speech_output , "newName"))
                                    #no new name, so cancel change
                                    elif choiceTwo.lower() == "no":
                                        card_title = " Name Change Cancelled."
                                        
                                        audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_NameChangeCancelled.mp3"#(Name Change Cancelled, Update User Settings anytime by opening user Settings)
                                        audioBuilder = "<audio src = '" + audioFileURL + "'/>"
                                        
                                        returnString = audioBuilder
                                        
                                        speech_output = "<speak>" + returnString + "</speak>"
                                        reprompt_string = speech_output
                                        return build_response(attributes,build_special_speechlet_response(card_title, speech_output, reprompt_string, False))
                                    else:
                                        audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_NameRePrompt.mp3" #(Wo Ke Neng Ting Cuo Le. Ni Yao ba ming zi zai jiang yi ci ma)
                                        audioBuilder = "<audio src =' " + audioFileURL + "'/> "
                                        
                                        returnString = audioBuilder
                                        
                                        speech_output = "<speak>" + returnString + "</speak>"
                                        return build_response(attributes, elicit_slot("", speech_output , "choiceTwo")) 
                            else:
                                audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_newName.mp3" #--Confirm Name Change (Ni de xing min zhi shi..)
                                audioBuilder = "<audio src ='" + audioFileURL + "'/>"
                                
                                audioFileURL2 = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_Confirmation.mp3" #(DUI MA ?)
                                audioBuilder2 = "<audio src ='" + audioFileURL2 + "'/>"
                                
                                stringBuilder = audioBuilder + newName +"." + audioBuilder2 +"?"
                                ssmlWrapper = "<speak>" + stringBuilder + "</speak>"
                                speech_output = ssmlWrapper
                                return build_response(attributes, elicit_slot2("", speech_output , "choice"))
                    else:
                        card_title = "Name already "+newName +", no Changes made."
                        
                        audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_NameSame.mp3" #--name the same
                        audioBuilder = "<audio src ='" + audioFileURL + "'/>"
                        
                        stringBuilder = audioBuilder + newName +"."
                        ssmlWrapper = "<speak>" + stringBuilder + "</speak>"
                        
                        speech_output = ssmlWrapper
                        return build_response(attributes,build_special_speechlet_response(card_title,speech_output,speech_output, False))
            #-- Change Language --
            elif userSettings.lower() == "language settings" or userSettings.lower() == "language":
                if event['session'].get('attributes'):
                    if event['session']['attributes'].get('newLanguage'):
                        if event['request']['intent']['slots']['choiceTwo'].get('value'):
                            clear = event['request']['intent']['slots']['choiceTwo']
                            clear.pop('value')
                            clear.pop('resolutions')
                            attributes = {
                                'LanguageLoop' : True
                            }
                            
                        if event['request']['intent']['slots']['choice'].get('value'):
                            clear2 = event['request']['intent']['slots']['choice']
                            clear2.pop('value')
                            clear2.pop('resolutions')
                            clear3 = event['session']['attributes']
                            clear3.pop('newLanguage')

                #- Prompt User for new Language -
                if not event['request']['intent']['slots']['newLanguage'].get('value'):
                    audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignUp/ZH_SignUp1.mp3"
                    audioBuilder = "<audio src ='"+ audioFileURL + "'/>"
                    
                    speech_output = "<speak>" +audioBuilder + "</speak>"
                    
                    slotToElicit = "newLanguage"
                    
                    card_title = ""
                    return build_response(attributes, elicit_slot(card_title, speech_output , slotToElicit))
                elif event['request']['intent']['slots']['newLanguage'].get('value'):
                    oldLanguageSettings = get_User_LanguageSettings(roundingID)
    
                    languageSettings = event['request']['intent']['slots']['newLanguage']['resolutions']['resolutionsPerAuthority']
                    for items in languageSettings:
                        if items.get('values'):
                            for items in items['values']:
                                newLanguageSettings = items['value']['name']
                        else:
                            newLanguageSettings = event['request']['intent']['slots']['newLanguage']['value']
                    
                    if newLanguageSettings == "English" or newLanguageSettings == "Mandarin":
                        if oldLanguageSettings == "Mandarin":
                            #- Ask User if he/she is sure that he want to change the old language to new Language.
                            if not event['request']['intent']['slots']['choice'].get('value'):
                                audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_LanguageConfirm.mp3"
                                audioBuilder = "<audio src='" +audioFileURL +"'/>"
                                
                                speech_output = "<speak>" + audioBuilder +"</speak>"
                                
                                card_title = ""
                                
                                slotToElicit = "choice"
                                return build_response(attributes, elicit_slot("", speech_output , slotToElicit))
                            elif event['request']['intent']['slots']['choice'].get('value'):
                                choice = event['request']['intent']['slots']['choice']['resolutions']['resolutionsPerAuthority']
                                for items in choice:
                                    if items.get('values'):
                                        for items in items['values']:
                                            choice = items['value']['name']
                                    else:
                                        choice = event['request']['intent']['slots']['newLanguage']['value']
                                if choice.lower() == "yes":
                                    if newLanguageSettings != oldLanguageSettings:
                                        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
                                        table = dynamodb.Table('Patients')
                                        response = table.update_item(
                                            Key={
                                                "RoundingID" : roundingID
                                            },
                                            UpdateExpression="SET LanguageSettings =:q",
                                            ExpressionAttributeValues={
                                                ':q' : newLanguageSettings
                                            },
                                            ReturnValues="UPDATED_NEW"
                                            )
                                        if newLanguageSettings == "English":
                                            card_title = "Patient ID " +str(roundingID) +": LanguageSettings Changed"
                                            speech_output = "Your Language has now been changed to English"
                                            return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,False))
                                        else:
                                            return build_response(attributes,build_speechlet_response("Error","An Error Occurred","",True))
                                    elif newLanguageSettings == oldLanguageSettings:
                                        if oldLanguageSettings == "Mandarin":
                                            card_title = "New Language Setting same as Previous Language Setting. No Changes were made."
                                            
                                            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_LanguageSettingSame.mp3"
                                            audioBuilder = "<audio src='" +audioFileURL +"'/>"
                                            
                                            speech_output = "<speak>" +audioBuilder +"</speak>"
                                            return build_response(attributes,build_special_speechlet_response(card_title,speech_output,speech_output,False))
                                elif choice.lower() == "no":
                                    if event['session'].get('attributes'):
                                        if event['session']['attributes'].get('LanguageLoop'):
                                            loop = 1
                                    else:
                                        loop = 0
                                    #ask User if they wanna give a new Language. (Use ChoiceTwo)
                                    if not event['request']['intent']['slots']['choiceTwo'].get('value'):
                                        audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_LanguageReprompt.mp3"
                                        audioBuilder = "<audio src='" +audioFileURL + "'/>"
                                        
                                        card_title = ""
                                        slotToElicit = "choiceTwo"
                                        speech_output = "<speak>" +audioBuilder +"</speak>"
                                        
                                        return build_response(attributes, elicit_slot("", speech_output , "choiceTwo")) 
                                    elif loop == 1:
                                        audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_LanguageReprompt.mp3"
                                        audioBuilder = "<audio src='" +audioFileURL + "'/>"
                                        
                                        card_title = ""
                                        slotToElicit = "choiceTwo"
                                        speech_output = "<speak>" +audioBuilder +"</speak>"
                                        
                                        return build_response(attributes, elicit_slot("", speech_output , "choiceTwo"))
                                    elif event['request']['intent']['slots']['choiceTwo'].get('value'): 
                                        choiceTwo = event['request']['intent']['slots']['choice']['resolutions']['resolutionsPerAuthority']
                                        for items in choiceTwo:
                                            if items.get('values'):
                                                for items in items['values']:
                                                    choiceTwo = items['value']['name']
                                            else:
                                                choiceTwo = event['request']['intent']['slots']['newLanguage']['value']
                                        #If Yes Ask user to Give new Language
                                        if choiceTwo.lower() == "yes":
                                            #Do the Attributes
                                            attributes = {
                                                'newLanguage' : True
                                            }
                                            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_LanguageReprompt2.mp3"
                                            audioBuilder = "<audio src='" +audioFileURL + "'/>"
                                            
                                            card_title = ""
                                            slotToElicit = "newLanguage"
                                            speech_output = "<speak>" +audioBuilder +"</speak>"
                                            
                                            return build_response(attributes, elicit_slot("", speech_output , "newLanguage"))
                                        #no new Language, so cancel change
                                        elif choiceTwo.lower() == "no":
                                            card_title="Language Change Cancelled"
                                            
                                            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_NameChangeCancelled.mp3"
                                            audioBuilder = "<audio src='" + audioFileURL +"'/>"
                                            
                                            speech_output = "<speak>"+ audioBuilder +"</speak>"
                                            
                                            return build_response(attributes,build_special_speechlet_response(card_title, speech_output, reprompt_string, False))
                                        else:
                                            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_LanguageReprompt.mp3"
                                            audioBuilder = "<audio src='" +audioFileURL + "'/>"
                                            
                                            card_title = ""
                                            slotToElicit = "choiceTwo"
                                            speech_output = "<speak>" +audioBuilder +"</speak>"
                                            
                                            return build_response(attributes, elicit_slot("", speech_output , "choiceTwo"))
                                else:
                                    audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_LanguageConfirm.mp3"
                                    audioBuilder = "<audio src='" +audioFileURL +"'/>"
                                    
                                    speech_output = "<speak>" + audioBuilder +"</speak>"
                                    
                                    card_title = ""
                                    
                                    slotToElicit = "choice"
                                    return build_response(attributes, elicit_slot("", speech_output , slotToElicit))
                    else:
                        audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignUp/ZH_SignUp1.mp3"
                        audioBuilder = "<audio src ='"+ audioFileURL + "'/>"
                        
                        speech_output = "<speak>" +audioBuilder + "</speak>"
                        
                        slotToElicit = "newLanguage"
                        
                        card_title = ""
                        return build_response(attributes, elicit_slot(card_title, speech_output , slotToElicit))
            #-- Change Number --
            elif userSettings.lower() == "phone number" or userSettings.lower() == "phone" or userSettings.lower() == "number":
                if event['session'].get('attributes'):
                    if event['session']['attributes'].get('newNumber'):
                        if event['request']['intent']['slots']['choiceTwo'].get('value'):
                            clear = event['request']['intent']['slots']['choiceTwo']
                            clear.pop('value')
                            clear.pop('resolutions')
                            attributes = {
                                'PhoneLoop' : True
                            }
                            
                        if event['request']['intent']['slots']['choice'].get('value'):
                            clear2 = event['request']['intent']['slots']['choice']
                            clear2.pop('value')
                            clear2.pop('resolutions')
                            clear3 = event['session']['attributes']
                            clear3.pop('newNumber')
                        
                        if not event['request']['intent']['slots']['ZH_newNumber'].get('value'):
                            attributes = {
                                'idx' : 0,
                                'value': "",
                                'speech': []
                            }
                            audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_GetPhoneNumber.mp3"
                            audioBuilder = "<audio src='" +audioFileURL +"'/>"
                            
                            card_title = ""
                            
                            slotToElicit = "ZH_newNumber"
                            
                            speech_output = "<speak>" +audioBuilder +"</speak>"
                            return build_response(attributes,elicit_slot(card_title,speech_output,slotToElicit))
                        if event['request']['intent']['slots']['ZH_newNumber'].get('value'):
                            previousNo = str(event['request']['intent']['slots']['ZH_newNumber']['value'])
                            NumberMatch = "ER_SUCCESS_NO_MATCH"
                            providedNumber = event['request']['intent']['slots']['ZH_newNumber']['resolutions']['resolutionsPerAuthority']
                            for items in providedNumber:
                            	if items.get('values'):
                            		for items in items['values']:
                            			previousNo = str(items['value']['name'])
                            for items in providedNumber:    
                            	if items.get('status'):
                            		NumberMatch = items['status']['code']
                            idxValue = int(event['session']['attributes']['idx'])
                            spoken = list(event['session']['attributes']['speech'])
                            #If match will be ER_SUCCESS_MATCH . If no match then ER_SUCCESS_NO_MATCH
                            if NumberMatch == "ER_SUCCESS_MATCH" and previousNo != "10": 
                            	if idxValue == 0:
                            		idx =  idxValue + 1
                            		spoken.extend([previousNo])
                            		attributes = {
                            			'idx': idx ,
                            			'value': previousNo,
                            			'speech': spoken
                            		}
                            		speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/" +previousNo +".mp3'/></speak>"
                            		return build_response(attributes, elicit_slot("",speech_output,"ZH_newNumber"))
                            	while idxValue > 0 and idxValue < 7:
                            		idx = idxValue + 1
                            		spoken.extend([previousNo])
                            		phoneNumber = event['session']['attributes']['value']
                            		newNumber = phoneNumber + previousNo
                            		attributes = {
                            			  'idx': idx,
                            			  'value': newNumber,
                            			  'speech': spoken
                            			}
                            		speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/" +previousNo +".mp3'/></speak>"
                            		return build_response(attributes,elicit_slot("",speech_output,"ZH_newNumber"))
                            	else:
                            		index = 0
                            		number = str(event['session']['attributes']['value'])
                            		spoken.extend([previousNo])
                            		chineseList = spoken
                            		for items in chineseList:
                            			if items == "0":
                            				audio_output += "<emphasis level='strong'>lin -- </emphasis> "
                            			elif items == "1":
                            				audio_output += "<emphasis level='strong'>y'all -- </emphasis>"
                            			elif items == "2":
                            				audio_output += "<emphasis level='strong'>aer -- </emphasis>"
                            			elif items == "3":
                            				audio_output += "<emphasis level='strong'>sun -- </emphasis>"
                            			elif items == "4":
                            				audio_output += "<emphasis level='strong'>shi -- </emphasis>"
                            			elif items == "5":
                            				audio_output += "<emphasis level='strong'>wu -- </emphasis>"
                            			elif items == "6":
                            				audio_output += "<emphasis level='strong'>leo -- </emphasis>"
                            			elif items == "7":
                            				audio_output += "<emphasis level='strong'>qi -- </emphasis>"
                            			elif items == "8":
                            				audio_output += "<emphasis level='strong'>bhar -- </emphasis>"
                            			elif items == "9":
                            				audio_output += "<emphasis level='strong'>jail -- </emphasis>"
                            
                            				
                            		returnNumber = number + previousNo
                            		
                            		attributes = {
                            			'idx': idxValue,
                            			'value': returnNumber,
                            		}
                            		
                            		speech_output = "<speak><audio src='https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/ZH_newPhoneIs.mp3'/> "
                            		speech_output_end = "</speak>"
                            		
                            		returnSpeech = speech_output + audio_output + speech_output_end
                            		
                            		return build_response({}, build_special_speechlet_response_noCard(returnSpeech,returnSpeech,False))
                            elif NumberMatch == "ER_SUCCESS_NO_MATCH" or previousNo == "10":
                            	phoneNumber = event['session']['attributes']['value']
                            	attributes = {
                            		'idx': idxValue,
                            		'value': phoneNumber,
                            		'speech': spoken
                            	}
                            	if previousNo == "10":
                            		audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/ZH_PhoneNoTens.mp3"
                            		speech_output = "<speak><audio src = '" +audioFileURL +"' /></speak>"
                            		return build_response(attributes, build_special_speechlet_response_noCard(speech_output,speech_output,False))
                            elif NumberMatch == "ER_SUCCESS_NO_MATCH":
                                speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/ZH_TellNumber.mp3'/></speak>"
                                return build_response(attributes, build_special_speechlet_response_noCard(speech_output,speech_output,False))  
                            else:
                                audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_UserError.mp3"
                                audioBuilder = "<audio src='" +audioFileURL +"'/>"
                                
                                speech_output = "<speak>" +audioBuilder +"</speak>"
                                
                                card_title = ""
                                slotToElicit = "ZH_UserSettings"
                                
                                return build_response({},elicit_slot(card_title,speech_output,slotToElicit))
                                            
    elif signedIn == 0:
        attributes = {}
        audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_SignInError.mp3"
        audioBuilder = "<audio src = '" + audioFileURL + " '/>"
        
        speech_output = "<speak>" + audioBuilder + "</speak>"
        card_title = "Update Failed: No User Signed In"
        return build_response(attributes,build_special_speechlet_response(card_title,speech_output,speech_output, False))
   
    else:
        attributes = {}
        audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_Error.mp3"
        audioBuilder = "<audio src = '" + audioFileURL + " '/>"
        
        speech_output = "<speak>" + audioBuilder + "</speak>"
        card_title = "An Unknown Error Occurred."
        return build_response(attributes,build_special_speechlet_response(card_title,speech_output,speech_output, False))

"""Find out Medical Condition"""
def get_Condition(event):
    if event['request']['intent']['slots']['medicalCondition'].get('value'):
        MedicalCondition = event['request']['intent']['slots']['medicalCondition']['resolutions']['resolutionsPerAuthority']
        status = "ER_SUCCESS_NO_MATCH"
        for items in MedicalCondition:
            if items.get('status'):
                status = str(items['status']['code'])
       
        if status == "ER_SUCCESS_NO_MATCH":
            value = event['request']['intent']['slots']['medicalCondition']['value']
            card_title = "Condition Search not Found";
            speech_output = "Sorry, There is no information found for " +value +". Please Try Again."
            attributes = {}
            return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,False))
        elif status == "ER_SUCCESS_MATCH":
            for items in MedicalCondition:
                if items.get('values'):
                    for stuff in items['values']:
                        medcondition = str(stuff['value']['name'])
                        
            card_title = medcondition
            audioFileURL = "https://s3.amazonaws.com/healthbuddy/MedicalConditions/" +medcondition +".mp3"
            audioBuilder = "<audio src='" +audioFileURL +"'/>"
            speech_output = "<speak>" +audioBuilder +"</speak>"
            attributes = {}
            return build_response(attributes,build_special_speechlet_response(card_title,speech_output,speech_output,False))
    else:
        attributes = {}
        card_title = ""
        speech_output = "Please say Tell me about, followed by the name of the condition you would like to know about."
        return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,False))
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  
"""Rounding Summary"""
def roundingSummary(event):
    userID = event['session']['user']['userId']
    patientID = get_roundID(userID)
    
    roundingCount = get_Patient_Rounding_Count(patientID)
    if roundingCount !=0:
        totalWater = get_total_Water_Count(patientID)
        totalToilet = get_total_Washroom_Count(patientID)
        
        avgWater = totalWater/roundingCount
        avgToilet = totalToilet/roundingCount
        avgWater = str(round(avgWater, 2))
        avgToilet = str(round(avgToilet, 2))
        
        mostWater = get_most_water(patientID)
        
        card_title= "Rounding Report"
        speech_output = "<speak>Hello, you have completed "+str(roundingCount) +" rounding Sessions. "+\
                        "You have drank a total of "+str(totalWater) +" Glasses of water, and gone to the washroom a total of "+\
                        str(totalToilet) +" Times. <say-as interpret-as='interjection'>Wow</say-as>, The most glasses of water you have drank is " +str(mostWater) +"! " +\
                        "On average, you go to the washroom-" +str(avgToilet) +"times and drink " +str(avgWater) +" glasses of water.</speak>"
        attributes = {}
        return build_response(attributes,build_special_speechlet_response_noCard(speech_output,speech_output,False))
    elif roundingCount ==0:
        speech_output="You have not completed any rounding session, to start one, say start rounding."
        card_title="No Rounding Session Record Found"
        attributes={}
        return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,False))

"""Get Count of Rounding Done"""
def get_Patient_Rounding_Count(patientID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Roundings')
    response = table.scan(
        FilterExpression = Attr("PatientID").eq(patientID)
    )
    return len(response["Items"])
    
"""Get Total Water Drank"""
def get_total_Water_Count(patientID):
    water = 0
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Roundings')
    response = table.scan(
        FilterExpression = Attr("PatientID").eq(patientID)
    )
    if len(response["Items"]) > 0:
        for item in response["Items"]:
            glasses = int(item["WaterGlasses"])
            water = water+ glasses
        return water
    else:
        return water

"""Get Total Toilet Went"""
def get_total_Washroom_Count(patientID):
    water = 0
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Roundings')
    response = table.scan(
        FilterExpression = Attr("PatientID").eq(patientID)
    )
    if len(response["Items"]) > 0:
        for item in response["Items"]:
            glasses = int(item["WashRoom"])
            water = water+ glasses
        return water
    else:
        return water

"""Get Most Water Drank"""
def get_most_water(patientID):
    water = 0
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Roundings')
    response = table.scan(
        FilterExpression = Attr("PatientID").eq(patientID)
    )
    if len(response["Items"]) > 0:
        for item in response["Items"]:
            glasses = int(item["WaterGlasses"])
            if glasses>water:
                water = glasses
        return water
    else:
        return water
        
"""Call for Assistance"""
def call_urgent(event):
    deviceID = event['context']['System']['device']['deviceId']
    count = get_urgent(deviceID)
    if count == 0:
        wardNo = get_ward_from_DeviceID(deviceID)
        bedNo = get_bed_from_DeviceID(deviceID)
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('Emergencies')
        response = table.put_item(
            Item = {
                "deviceID": deviceID,
                "bedNo": bedNo,
                "wardNo": wardNo
            }
        )
        card_title = "Help called in Ward "+wardNo +": Bed "+bedNo
        speech_output = "A Staff has been allocated to attend to you in ward " +wardNo +" bed " +bedNo
        attributes= {}
        return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,False))
    elif count > 0:
        attributes = {}
        card_title = "Emergency called."
        speech_output = "Help has already been called, help is on their way."
        return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,False))
        
"""Check if Assistance is already called"""        
def get_urgent(deviceID):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Emergencies')
    response = table.scan(
        FilterExpression = Attr("deviceID").eq(deviceID)
        )
    count = len(response["Items"])
    return count
#!!!!!!!!!!!!!!!!!!!!        
def get_menu():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Diets')
    response = table.scan(
        FilterExpression = Attr("dietOption").eq("0")
        )
    return response
    
def set_diet(event):
    #Get the Name
    userID = event['session']['user']['userId']
    patientID = get_roundID(userID)
    hourNow = str(datetime.datetime.now().strftime('%H'))
    LunchcutOffHour = 11
    DinnerCutOffHour = 18
    western = 'Nothing'
    chinese = 'Nothing'
    muslim = 'Nothing'
    vegetarian = 'Nothing'
    menu = get_menu()
    for items in menu["Items"]:
        western = items["Western"]
        chinese = items["Chinese"]
        muslim = items["Muslim"]
        vegetarian = items["Vegetarian"]
    if int(hourNow) >= DinnerCutOffHour or int(hourNow) < 7:
        card_title = "Menu unavaliable"
        speech_output = "The Menu is not ready yet, you can choose your lunch from 8 to 11 A M and Dinner from 12 to 5 P M daily."
        attributes = {}
        return build_response(attributes,build_special_speechlet_response(card_title,speech_output,speech_output,True))
    elif int(hourNow) <= LunchcutOffHour :
        if not event['request']['intent']['slots']['Diet'].get('value'):
            card_title = ""
            speech_output = "You are choosing the Lunch Menu. " +\
                            "Here are today's Lunch Options: "+\
                            "For Western, " +str(western) +\
                            ". For Chinese, " +str(chinese)  +\
                            ". For Muslim, " +str(muslim) +\
                            ". For Vegetarian, " +str(vegetarian)  +\
                            ". Would you like Western, Chinese, Muslim or Vegetarian?"
            slotToElicit = "Diet"
            attributes = {}
            return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit))
        elif event['request']['intent']['slots']['Diet'].get('value'):
            dietChoice = ""
            dietList = event['request']['intent']['slots']['Diet']['resolutions']['resolutionsPerAuthority']
            for item in dietList:
                code = item['status']['code']
                if code=="ER_SUCCESS_MATCH":
                    for value in item['values']:
                        dietChoice = value['value']['name']
                
                    
            if dietChoice.lower()=="western" or dietChoice.lower()=="chinese" or dietChoice.lower()=="muslim"  or dietChoice.lower()=="vegetarian":
                response = updateMenu(patientID,dietChoice)
                attributes = {}
                card_title = "Diet Changed"
                speech_output = "Ok, We will serve you " +str(dietChoice) +" for lunch today. Remember you can choose your lunch from 8 to 11 A M and Dinner from 12 to 5 P M daily."
                return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,False))
            else:
                card_title = ""
                speech_output = "Sorry, Did not hear you. You are choosing the Lunch Menu. " +\
                                "Here are today's Lunch Options: "+\
                                "For Western, " +str(western) +\
                                ". For Chinese, " +str(chinese)  +\
                                ". For Muslim, " +str(muslim) +\
                                ". For Vegetarian, " +str(vegetarian)  +\
                                ". Would you like Western, Chinese, Muslim or Vegetarian?"
                attributes = {}
                return build_response(attributes,elicit_slot2(card_title,speech_output,"Diet"))
    elif int(hourNow) > LunchcutOffHour and int(hourNow) < DinnerCutOffHour:
        if not event['request']['intent']['slots']['Diet'].get('value'):
            card_title = ""
            speech_output = "You are choosing the Dinner Menu. " +\
                            "Here are today's Dinner Options: "+\
                            "For Western, " +str(western) +\
                            ". For Chinese, " +str(chinese)  +\
                            ". For Muslim, " +str(muslim) +\
                            ". For Vegetarian, " +str(vegetarian)  +\
                            ". Would you like Western, Chinese, Muslim or Vegetarian?"
            slotToElicit = "Diet"
            attributes = {}
            return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit))
        elif event['request']['intent']['slots']['Diet'].get('value'):
            dietChoice = ""
            dietList = event['request']['intent']['slots']['Diet']['resolutions']['resolutionsPerAuthority']
            for item in dietList:
                code = item['status']['code']
                if code=="ER_SUCCESS_MATCH":
                    for value in item['values']:
                        dietChoice = value['value']['name']
                
                    
            if dietChoice.lower()=="western" or dietChoice.lower()=="chinese" or dietChoice.lower()=="muslim"  or dietChoice.lower()=="vegetarian":
                response = updateMenu(patientID,dietChoice)
                attributes = {}
                card_title = "Diet Changed"
                speech_output = "Ok, We will serve you " +str(dietChoice) +" for dinner today. Remember you can choose your lunch from 8 to 11 A M and Dinner from 12 to 5 P M daily."
                return build_response(attributes,build_speechlet_response(card_title,speech_output,speech_output,False))
            else:
                card_title = ""
                speech_output = "Sorry, Did not hear you. You are choosing the Dinner Menu. " +\
                            "Here are today's Dinner Options: "+\
                            "For Western, " +str(western) +\
                            ". For Chinese, " +str(chinese)  +\
                            ". For Muslim, " +str(muslim) +\
                            ". For Vegetarian, " +str(vegetarian)  +\
                            ". Would you like Western, Chinese, Muslim or Vegetarian?"
                slotToElicit = "Diet"
                attributes = {}
                return build_response(attributes,elicit_slot2(card_title,speech_output,slotToElicit))

def updateMenu(patientID,dietChoice):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.update_item(
        Key={
            "RoundingID" : patientID
        },
        UpdateExpression="SET Diet =:q",
        ExpressionAttributeValues={
            ':q' : dietChoice
        },
        ReturnValues="UPDATED_NEW"
        )
    return response
    
#-CHINESE PHONE NUMBERS TEST
def Numbers_Chinese_Test2(event):
    audio_output = ""
    if event['request']['intent']['slots']['testSlot'].get('value'):
        previousNo = str(event['request']['intent']['slots']['testSlot']['value'])
        NumberMatch = "ER_SUCCESS_NO_MATCH"
        providedNumber = event['request']['intent']['slots']['testSlot']['resolutions']['resolutionsPerAuthority']
        for items in providedNumber:
            if items.get('values'):
                for items in items['values']:
                    previousNo = str(items['value']['name'])
        for items in providedNumber:    
            if items.get('status'):
                NumberMatch = items['status']['code']
        idxValue = int(event['session']['attributes']['idx'])
        spoken = list(event['session']['attributes']['speech'])
        #If match will be ER_SUCCESS_MATCH . If no match then ER_SUCCESS_NO_MATCH
        if NumberMatch == "ER_SUCCESS_MATCH" and previousNo != "10": 
            if idxValue == 0:
                idx =  idxValue + 1
                spoken.extend([previousNo])
                attributes = {
                    'idx': idx ,
                    'value': previousNo,
                    'speech': spoken
                }
                speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/" +previousNo +".mp3'/></speak>"
                return build_response(attributes, elicit_slot("",speech_output,"testSlot"))
            while idxValue > 0 and idxValue < 7:
                idx = idxValue + 1
                spoken.extend([previousNo])
                phoneNumber = event['session']['attributes']['value']
                newNumber = phoneNumber + previousNo
                attributes = {
                      'idx': idx,
                      'value': newNumber,
                      'speech': spoken
                    }
                speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/" +previousNo +".mp3'/></speak>"
                return build_response(attributes,elicit_slot("",speech_output,"testSlot"))
            else:
                index = 0
                number = str(event['session']['attributes']['value'])
                spoken.extend([previousNo])
                chineseList = spoken
                for items in chineseList:
                    if items == "0":
                        audio_output += "<emphasis level='strong'>lin -- </emphasis> "
                    elif items == "1":
                        audio_output += "<emphasis level='strong'>y'all -- </emphasis>"
                    elif items == "2":
                        audio_output += "<emphasis level='strong'>aer -- </emphasis>"
                    elif items == "3":
                        audio_output += "<emphasis level='strong'>sun -- </emphasis>"
                    elif items == "4":
                        audio_output += "<emphasis level='strong'>shi -- </emphasis>"
                    elif items == "5":
                        audio_output += "<emphasis level='strong'>wu -- </emphasis>"
                    elif items == "6":
                        audio_output += "<emphasis level='strong'>leo -- </emphasis>"
                    elif items == "7":
                        audio_output += "<emphasis level='strong'>qi -- </emphasis>"
                    elif items == "8":
                        audio_output += "<emphasis level='strong'>bhar -- </emphasis>"
                    elif items == "9":
                        audio_output += "<emphasis level='strong'>jail -- </emphasis>"

                        
                returnNumber = number + previousNo
                
                attributes = {
                    'idx': idxValue,
                    'value': returnNumber,
                }
                
                speech_output = "<speak><audio src='https://s3.amazonaws.com/healthbuddy/goblin2.mp3'/> "
                speech_output_end = "</speak>"
                
                returnSpeech = speech_output + audio_output + speech_output_end
                
                return build_response({}, build_special_speechlet_response_noCard(returnSpeech,returnSpeech,False))
        elif NumberMatch == "ER_SUCCESS_NO_MATCH" or previousNo == "10":
            phoneNumber = event['session']['attributes']['value']
            attributes = {
                'idx': idxValue,
                'value': phoneNumber,
                'speech': spoken
            }
            if previousNo == "10":
                audioFileURL = "https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/ZH_PhoneNoTens.mp3"
                speech_output = "<speak><audio src = '" +audioFileURL +"' /></speak>"
                return build_response(attributes, build_special_speechlet_response_noCard(speech_output,speech_output,False))
            elif NumberMatch == "ER_SUCCESS_NO_MATCH":
                speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_PhoneNumbers/ZH_TellNumber.mp3' /></speak>"
                return build_response(attributes, build_special_speechlet_response_noCard(speech_output,speech_output,False))


    elif not event['request']['intent']['slots']['testSlot'].get('value'):
        attributes = {
            'idx' : 0,
            'value': "",
            'speech': []
        }
        speech = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_UserSettings/ZH_GetPhoneNumber.mp3'/></speak>"
        return build_response(attributes,elicit_slot("",speech,"testSlot"))
    else:
        attributes = {}
        card_title = "Error"
        speech_output = "<speak><audio src = 'https://s3.amazonaws.com/healthbuddy/ZH/ZH_Error.mp3'/></speak>"
        return build_response(attributes,build_special_speechlet_response(card_title,speech_output,speech_output,False ))

#-LITERAL SLOT TEST (LIKE TO SEND EMAIL FEEDBACK TO ERNEST !!)
def Numbers_Chinese_Test(event):
    if not event['request']['intent']['slots']['testSlot'].get('value'):
        speech_output = "Please Speak, but keep it short."
        return build_response({}, elicit_slot2("speak",speech_output,"testSlot"))
    elif event['request']['intent']['slots']['testSlot'].get('value'):
        userSpeech = event['request']['intent']['slots']['testSlot']['value']
        speech_output = "You Said-- : " +str(userSpeech)
        return build_response({}, build_speechlet_response("spoken",speech_output,speech_output,False))

def email_Test():
    #Define SMTP Library
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    #Verification
    mail.ehlo()
    #Any SMTP Command To Encrypt as we are logging in
    mail.starttls()
    #Log in
    mail.login('email@gmail.com','password')
    #Define Message
    subject = "HealthBuddy"
    msg = "Hello There How are You?"
    message = 'Subject: {}\n\n{}'.format(subject,msg)
    #Send Mail
    mail.sendmail('email@gmail.com','email@gmail.com',message)
    mail.close()

"""GET ALL PATIENTS"""
def allPatients():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Patients')
    response = table.scan()
    if len(response["Items"]) > 0:
        for item in response['Items']:
            return response
    elif len(response["Items"]) == 0:
        return False
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
#============= Events ==================
def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session. Is not called when the skill returns should_end_session=true """
    #print("on_session_ended requestId=" + session_ended_request['requestId'] +
    #      ", sessionId=" + session['sessionId'])
          
def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they want """
    # Dispatch to your skill's launch
    return get_welcome_response(launch_request)

#========= Handler =================
def lambda_handler(event, context):
    os.environ['TZ'] = 'Asia/Singapore'
    time.tzset()
    
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
          
    """This is to prevent someone else from configuring a skill that sends requests to this function."""
    
    if (event['session']['application']['applicationId'] != "amzn1.ask.skill.22cf8ba3-f102-414a-91c9-e11fa6af6637"):
        raise ValueError("Invalid Application ID")
    
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])

    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event, context)
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event, context)
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], context)

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

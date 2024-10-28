from dotenv import load_dotenv
import os
from datetime import datetime, date
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

def GetTime(location):
    # This is a mockup function. Ideally, you would integrate a service to get time for a location.
    # You can use an API or a local function to fetch time based on the location.
    current_time = datetime.now().strftime('%H:%M:%S')
    return f"The current time in {location} is {current_time}"

def GetDay(date_string):
    # Parse the date_string and return the day of the week.
    try:
        parsed_date = datetime.strptime(date_string, "%m/%d/%Y")
    except ValueError:
        return "Invalid date format. Please use MM/DD/YYYY."
    return f"The day for {date_string} is {parsed_date.strftime('%A')}"

def GetDate(day):
    # Map input day (e.g., 'today', 'Monday') to a date. Simple example for 'today' and 'tomorrow'.
    if day.lower() == 'today':
        return f"Today's date is {date.today().strftime('%m/%d/%Y')}"
    elif day.lower() == 'tomorrow':
        tomorrow = date.today() + timedelta(days=1)
        return f"Tomorrow's date is {tomorrow.strftime('%m/%d/%Y')}"
    else:
        return "I can only tell you the dates for today or tomorrow in this example."

def main():
    try:
        # Load configuration settings from the .env file
        load_dotenv()
        ls_prediction_endpoint = os.getenv('LS_CONVERSATIONS_ENDPOINT')
        ls_prediction_key = os.getenv('LS_CONVERSATIONS_KEY')

        # Get user input until they enter "quit"
        userText = ''
        while userText.lower() != 'quit':
            userText = input('\nEnter some text ("quit" to stop)\n')
            if userText.lower() != 'quit':
                # Create a client for the language service model
                client = ConversationAnalysisClient(ls_prediction_endpoint, AzureKeyCredential(ls_prediction_key))

                # Define project and deployment for your Azure Language Service
                cls_project = 'Clock'
                deployment_slot = 'production'

                with client:
                    query = userText
                    result = client.analyze_conversation(
                        task={
                            "kind": "Conversation",
                            "analysisInput": {
                                "conversationItem": {
                                    "participantId": "1",
                                    "id": "1",
                                    "modality": "Text",
                                    "language": "en",
                                    "text": query
                                },
                                "isLoggingEnabled": False
                            },
                            "parameters": {
                                "projectName": cls_project,
                                "deploymentName": deployment_slot,
                                "verbose": True
                            }
                        }
                    )

                    # Extract top intent and entities from the result
                    top_intent = result["result"]["prediction"]["topIntent"]
                    entities = result["result"]["prediction"]["entities"]

                    print("\nView top intent:")
                    print(f"\tTop intent: {top_intent}")
                    print(f"\tConfidence score: {result['result']['prediction']['intents'][0]['confidenceScore']}")

                    print("\nView entities:")
                    for entity in entities:
                        print(f"\tCategory: {entity['category']}")
                        print(f"\tText: {entity['text']}")
                        print(f"\tConfidence score: {entity['confidenceScore']}")

                    # Apply the appropriate action based on top intent
                    if top_intent == 'GetTime':
                        location = 'local'
                        # Check for entities
                        if len(entities) > 0:
                            # Check for a Location entity
                            for entity in entities:
                                if 'Location' == entity["category"]:
                                    location = entity["text"]
                        # Get the time for the specified location
                        print(GetTime(location))

                    elif top_intent == 'GetDay':
                        date_string = date.today().strftime("%m/%d/%Y")
                        # Check for entities
                        if len(entities) > 0:
                            # Check for a Date entity
                            for entity in entities:
                                if 'Date' == entity["category"]:
                                    date_string = entity["text"]
                        # Get the day for the specified date
                        print(GetDay(date_string))

                    elif top_intent == 'GetDate':
                        day = 'today'
                        # Check for entities
                        if len(entities) > 0:
                            # Check for a Weekday entity
                            for entity in entities:
                                if 'Weekday' == entity["category"]:
                                    day = entity["text"]
                        # Get the date for the specified day
                        print(GetDate(day))

                    else:
                        # Some other intent (e.g., "None") was predicted
                        print('Try asking me for the time, the day, or the date.')

    except Exception as ex:
        print(f"An error occurred: {str(ex)}")

if _name_ == "_main_":
    main()
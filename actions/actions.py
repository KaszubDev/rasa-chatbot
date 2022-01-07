from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json

class ActionAskForOpeningHours(Action):
    def name(self) -> Text:
        return "action_opening_hours"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        with open('info/opening_hours.json') as opening_hours_file:
            opening_hours_file_content = json.load(opening_hours_file)

        hours_items = opening_hours_file_content.get('items')
        response = 'Below you can find our opening hours:'
        dispatcher.utter_message(text=response)
        for day in hours_items:
            response = f"{day}: Open: {hours_items.get(day).get('open')} Close: {hours_items.get(day).get('close')} \n"
            dispatcher.utter_message(text=response)

        return []

class ActionListMenuItems(Action):

    def name(self) -> Text:
        return "action_list_menu_items"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        with open('info/menu.json') as menu_file:
            menu = json.load(menu_file)

        menu_items = menu.get('items')
        menu_to_show = 'The menu is: \n'
        for item in menu_items:
            meal = item.get('name')
            price = item.get('price')
            prep_time = item.get('preparation_time')
            menu_to_show = menu_to_show + f'{meal} for {price} PLN and with preparation time of {int(prep_time*60)} minutes \n'

        dispatcher.utter_message(text=menu_to_show)

        return []

class ActionAskIfOpenGivenTime(Action):

    def name(self) -> Text:
        return "action_answer_if_open"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        day = ''
        hour = ''

        for item in tracker.latest_message['entities']:
            if item['entity'] == 'day':
                day = item['value']

            if item['entity'] == 'hour':
                hour = item['value']

        with open('info/opening_hours.json') as opening_hours_file:
            opening_hours_file_content = json.load(opening_hours_file)

        opening_time_items = opening_hours_file_content.get('items')
        hours = opening_time_items.get(day.capitalize())

        if hours is None:
            dispatcher.utter_message(text=f"{day} was no recognized")
            return []

        if hour == '':
            dispatcher.utter_message(
                text=f"The restaurant is open from {hours.get('open')} to {hours.get('close')} on {day}"
            )
            return []

        if (int(hour) < 0) or (int(hour) > 24):
            dispatcher.utter_message(text=f"Given hour is incorrect")
            return []

        opening_hour = hours.get('open')
        close_hour = hours.get('close')

        if (int(hour) >= int(opening_hour)) and (int(close_hour) >= int(hour)):
            dispatcher.utter_message(text=f"Yes, the restaurant is open on {day} at {hour}")
        else:
            dispatcher.utter_message(text=f"No, the restaurant is not open on {day} at {hour}")

        return []
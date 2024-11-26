# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, List, Dict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionTemperatureByLocation(Action):

    def name(self) -> Text:
        return "action_temperature_by_location"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        location_entity = next(tracker.get_latest_entity_values("location"), None)
        if location_entity is None:
            dispatcher.utter_message("Location not given")
        else:
            dispatcher.utter_message(response="utter_temperature_by_location", location=location_entity)
        return []
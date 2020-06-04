from typing import List
from smart_intervention.models.actors.bases.base_actor import BaseActor
from smart_intervention import Notifications


class SimulationManager:
    """
    This class acts as a simulation supervisor, to provide control over flow of actions
    It emulates smart-system's behaviour by re-purposing actors which do not require headquarter supervision
    It also needs to give the user ability to pause actions at any given time
    """

    def __init__(self, actors: List[BaseActor] = None):
        if not actors:
            actors = []
        self.actors = actors

    def do_tick(self):
        """
        Performs a tick of the simulation
        :return TODO Preferably some kind of a snapshot for our simulation or a step-artifact for UI (like screen shot):
        """
        notifications = Notifications.flush()
        Notifications.clear()  # Super important, to have a clear store for each tick
        actions = [actor.tick_action(notifications) for actor in self.actors]
        for action in actions:
            action()

    def add_actor(self, actor: BaseActor):
        self.actors.append(actor)

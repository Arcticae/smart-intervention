from abc import abstractmethod

from smart_intervention.models.actors.bases import BaseActor
from smart_intervention.models.actors.bases.purpose import Purpose


class PurposefulActor(BaseActor):
    def __init__(self, purpose: Purpose):
        self.purpose = purpose

    @abstractmethod
    def re_purpose(self, purpose: Purpose):
        """
        Primary purpose change of the actor
        """
        self.purpose = purpose
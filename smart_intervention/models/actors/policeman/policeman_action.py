from smart_intervention.models.actors.action import Action
from smart_intervention.models.actors.policeman.policeman import Policeman, PolicemanError

from smart_intervention.models.actors.policeman.policeman_notification import PolicemanNotification


def return_to_duty_if_inactive(callback):
    def decorated(self, *args, **kwargs):
        if self._policeman.intervention_event.active:
            callback(self, *args, **kwargs)
        else:
            self._policeman.return_to_duty()

    return decorated


class PolicemanAction(Action):
    def __init__(self, policeman: Policeman):
        self._policeman = policeman

        self._after_init()

    def _after_init(self):
        self._action = self._get_action(self._policeman.purpose)

    def execute(self):
        self._action()

    def _get_action(self, purpose):
        return {
            Policeman.PolicemanPurpose.IDLE: lambda: None,
            Policeman.PolicemanPurpose.PATROL: self._patrol_actions,
            Policeman.PolicemanPurpose.INTERVENTION: self._intervention_actions,
            Policeman.PolicemanPurpose.GUNFIGHT: self._gunfight_actions,
            Policeman.PolicemanPurpose.ROUTING_TO_INTERVENTION: self._routing_actions,
            Policeman.PolicemanPurpose.ROUTING_TO_GUNFIGHT: self._routing_actions,
        }[purpose]

    def _patrol_actions(self):
        policeman = self._policeman
        if not policeman.current_route:
            policeman.current_route = policeman.patrol_route.copy()

        policeman.move_forward(policeman.current_route)

    @return_to_duty_if_inactive
    def _intervention_actions(self):
        policeman = self._policeman
        if policeman.intervention_event.armed_combat:
            policeman.re_purpose(Policeman.PolicemanPurpose.GUNFIGHT)
        else:
            policeman.intervention_event.mitigate(policeman)
            policeman.send_notification(notification_type=PolicemanNotification.INTERVENTION)

    @return_to_duty_if_inactive
    def _gunfight_actions(self):
        policeman = self._policeman
        if not policeman.intervention_event.backup_sufficient:
            notification_type = PolicemanNotification.BACKUP_NEEDED
        else:
            notification_type = PolicemanNotification.GUNFIGHT

        policeman.intervention_event.mitigate(policeman)
        policeman.send_notification_with_location(notification_type=notification_type)

    def _routing_actions(self):
        policeman = self._policeman
        try:
            policeman.move_and_join_event()
        except PolicemanError as p_err:
            print(p_err)  # TODO: logging mechanism
            policeman.re_purpose(Policeman.PolicemanPurpose.IDLE)

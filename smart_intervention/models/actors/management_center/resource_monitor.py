from collections import defaultdict
from enum import Enum


class ResourceState(Enum):
    INTERVENTION = 'intervention'
    GUNFIGHT = 'gunfight'
    DISPATCHED = 'dispatched'
    DISPATCHED_TO_GUNFIGHT = 'dispatched_to_gunfight'
    DISPATCHED_TO_INTERVENTION = 'dispatched_to_intervention'
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    REQUESTED = 'requested'


class ManagementCenterResourceMonitor:

    def __init__(self, managed_units):
        self._units = {
            ResourceState.INTERVENTION: [],
            ResourceState.GUNFIGHT: [],
            ResourceState.DISPATCHED_TO_INTERVENTION: [],
            ResourceState.DISPATCHED_TO_GUNFIGHT: [],
            ResourceState.AVAILABLE: managed_units,
        }
        self._units_by_event = defaultdict(lambda: defaultdict(lambda: []))
        self._ambulances = {
            ResourceState.DISPATCHED: [],
            ResourceState.INTERVENTION: [],
        }
        self._ambulances_by_event = defaultdict(
            lambda: {ResourceState.UNAVAILABLE: False, ResourceState.REQUESTED: False}
        )

    def set_unit_state(self, unit, state, event=None):
        self._remove_from_other_states(unit, self._units, self._units_by_event)
        self._set_state(unit, state, event, self._units, self._units_by_event)

    def get_available_units(self):
        return self._units[ResourceState.AVAILABLE]

    def get_intervening_units(self):
        return self._units[ResourceState.INTERVENTION]

    def get_dispatched_to_intervention_units(self, event=None):
        if event:
            return self._units_by_event[event][ResourceState.DISPATCHED_TO_INTERVENTION]
        else:
            return self._units[ResourceState.DISPATCHED_TO_INTERVENTION]

    def get_dispatched_ambulances(self, event=None):
        if event:
            return self._ambulances_by_event[event][ResourceState.DISPATCHED]
        else:
            return self._units[ResourceState.DISPATCHED]

    def set_ambulance_state(self, ambulance, state, event):
        self._remove_from_other_states(ambulance, self._ambulances, self._ambulances_by_event)
        self._set_state(ambulance, state, event, self._ambulances, self._ambulances_by_event)

    def set_ambulances_unavailable(self, event):
        self._ambulances_by_event[event][ResourceState.UNAVAILABLE] = True

    def set_ambulance_requested(self, event):
        self._ambulances_by_event[event][ResourceState.REQUESTED] = True

    def ambulances_available(self, event):
        return not self._ambulances_by_event[event][ResourceState.UNAVAILABLE]

    def ambulance_requested(self, event):
        return self._ambulances_by_event[event][ResourceState.REQUESTED]

    def _set_state(self, actor, state, event, by_state, by_event):
        by_state[state].append(actor)
        if event:
            self._add_by_event(actor, event, state, by_event)

    def _remove_from_other_states(self, actor, by_state, by_event):
        self._filter_from_state_dict(by_state, actor)

        for state_dict in by_event.values():
            self._filter_from_state_dict(state_dict, actor)

    @staticmethod
    def _add_by_event(unit, event, state, by_event):
        by_event[event][state].append(unit)

    @staticmethod
    def _filter_from_state_dict(state_dict, unit):
        for state, units_in_state in state_dict.items():
            if unit in units_in_state:
                state_dict[state] = [unit_in_state for unit_in_state in units_in_state if unit_in_state != unit]
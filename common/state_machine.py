class StateMachine:
    """A StateMachine handles state transitions.
    Several objects in `cognitive apprenticeship` progress through states. 
    StateMachine centralizes their transitions to ensure that they are done
    consistently across views.

    StateMachine is broken out from the respective models because state
    transitions belong at the view layer, acting on models in context. 
    """

    states = []
    transitions = {}

    def __init__(self, request=None):
        """Optionally initialized with a request.
        """
        self.request = request

    def transition(self, obj, new_state):
        """Transitions the object from its current state to the new state, 
        checking that the transition is allowed and calling the side effects
        function (which should at a minimum persist the new state information).
        """
        if not self.transition_allowed(obj, new_state):
            raise self.IllegalTransition("Transition to {} not allowed".format(new_state))
        old_state = self.get_state(obj)
        try:
            side_effects = self.transitions[old_state][new_state]
        except (KeyError, TypeError):
            msg = "Invalid state transition from {} to {}".format(old_state, new_state)
            raise self.IllegalTransition(msg)
        side_effects(self, obj, old_state, new_state)

    def allowed_transitions(self, obj):
        """Returns a list of available transitions.
        By default, uses self.transitions.
        """
        old_state = self.get_state(obj)
        try:
            return self.transitions[old_state].keys()
        except (KeyError, AttributeError):
            return []

    def transition_allowed(self, obj, new_state):
        """Checks whether the proposed transition is allowed.
        """
        return new_state in self.allowed_transitions(obj)

    def get_state(self, obj):
        """Maps an object to a state.
        """
        return None

    class IllegalTransition(Exception):
        pass

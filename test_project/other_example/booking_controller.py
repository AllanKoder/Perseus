"""Example module with a @pdoc block for Perseus demo."""
"""
@pdoc
id: booking_controller
watch: true
code: true

intention: >
  Manages booking processing through a high level interface.

vocabulary:
  ROV: Return of Voice
  POL: Price of Leaving

tags:
  - booking
  - controller

tickets:
  - JIRA-123: Validate booking form
  - JIRA-456: Add cancellation flow
@endp
"""
def booking_controller(user_id, form_data):
    """Simulated controller function."""
    # Implementation omitted for demo
    return {"status": "ok"}

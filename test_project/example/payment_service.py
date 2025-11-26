"""Example module with a @pdoc block for Perseus demo, including extra fields."""
"""
@pdoc
id: payment_service
watch: false
code: true

intention: >
  Handles payment processing and transaction validation.

vocabulary:
  CVV: Card Verification Value
  ACH: Automated Clearing House

tags:
  - payment
  - service

feature_flags:
  - enable_ach_payments
  - enable_card_validation

# Custom context could be used in the future
business_requirement: >
  Must comply with PCI DSS and support refunds.

tickets:
  - KAN-5
  - KAN-6
@endp
"""
def payment_service(user_id, payment_data):
    """Simulated payment service function."""
    # Implementation omitted for demo
    return {"status": "paid"}

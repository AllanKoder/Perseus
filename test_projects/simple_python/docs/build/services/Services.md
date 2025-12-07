# Core Services Documentation

This module contains the primary business logic services for the hotel booking platform.

---

## Service Overview

### Booking Controller

Primary entry point for all booking operations. Orchestrates validation, inventory checks, payment processing, and confirmation workflows.

**Classification:** `booking`, `controller`, `api-endpoint`

**Business Requirements**

Support same-day bookings with instant confirmation. Implement tiered cancellation policies based on booking class and loyalty status.

**Feature Capabilities**

- `enable_instant_booking`

- `enable_flexible_cancellation`

- `enable_loyalty_pricing`

**Development Status**

| Ticket | Summary | Status | Owner | Priority |
|--------|---------|--------|-------|----------|
| [KAN-1](https://perseus-test-tickets.atlassian.net/browse/KAN-1) | Validate booking form | `In Review` | Unassigned | None |
| [KAN-4](https://perseus-test-tickets.atlassian.net/browse/KAN-4) | Add cancellation flow | `To Do` | Unassigned | Medium |
| [KAN-7]() | KAN-7 | `` |  |  |

---

### Notification Service

Manages all customer communications including booking confirmations, reminders, updates, and promotional messages across email, SMS, and push.

**Classification:** `notification`, `communication`, `messaging`

**Business Requirements**

Send booking confirmations within 30 seconds. Support customer preference management for notification channels. Maintain audit trail of all communications for compliance. Rate limit to prevent notification spam.

**Feature Capabilities**

- `enable_sms_notifications`

- `enable_push_notifications`

- `enable_whatsapp_notifications`

- `enable_notification_preferences`

**Development Status**

| Ticket | Summary | Status | Owner | Priority |
|--------|---------|--------|-------|----------|
| [KAN-8]() | KAN-8 | `` |  |  |
| [KAN-9]() | KAN-9 | `` |  |  |
| [KAN-15]() | KAN-15 | `` |  |  |

---

### Payment Service

Secure payment gateway integration supporting multiple payment methods. Handles authorization, capture, refunds, and fraud detection.

**Classification:** `payment`, `security`, `pci-compliant`, `financial`

**Business Requirements**

Full PCI DSS Level 1 compliance required. Support instant refunds for cancellations within 24 hours. Integrate fraud detection scoring. Process payments in multiple currencies with real-time conversion.

**Feature Capabilities**

- `enable_ach_payments`

- `enable_3ds_verification`

- `enable_saved_payment_methods`

- `enable_split_payments`

**Development Status**

| Ticket | Summary | Status | Owner | Priority |
|--------|---------|--------|-------|----------|
| [KAN-5](https://perseus-test-tickets.atlassian.net/browse/KAN-5) | Integrate ACH payments | `In Progress` | Ana | Medium |
| [KAN-6](https://perseus-test-tickets.atlassian.net/browse/KAN-6) | Add refund support | `Done` | Unassigned | Medium |
| [KAN-12]() | KAN-12 | `` |  |  |

---

## Service Domain Terminology

**Reservation Window:** Time period between booking creation and check-in date

**Hold Period:** Duration a pending booking remains valid before auto-cancellation

**Occupancy Rate:** Percentage of available rooms currently booked

**Available Inventory:** Rooms not currently booked or blocked

**Overbooking Buffer:** Additional bookings beyond physical capacity

**Rate Plan:** Pricing strategy with associated rules and restrictions

**Block Date:** Period when rooms are reserved for groups or maintenance

**Dynamic Pricing:** Rate adjustment based on demand and occupancy

**Transactional Email:** Automated messages triggered by user actions

**Push Notification:** Mobile app alert sent via APNS or FCM

**Delivery Rate:** Percentage of sent messages successfully delivered

**Opt-in Status:** Customer's communication preference settings

**PCI DSS:** Payment Card Industry Data Security Standard

**CVV:** Card Verification Value - 3 or 4 digit security code

**ACH:** Automated Clearing House - electronic bank-to-bank transfers

**3DS:** Three-Domain Secure authentication protocol

**Chargeback:** Customer dispute resulting in transaction reversal

## Service Architecture

### Request Flow

```
Client Request
     ↓
Booking Controller
     ↓
┌────┴────┬─────────┬──────────┐
↓         ↓         ↓          ↓
Inventory Payment  Customer  Notification
Service   Service  Profile   Service
```

### Key Responsibilities

- **Booking Services**: Reservation lifecycle, availability management
- **Payment Services**: Transaction processing, fraud detection, refunds
- **Notification Services**: Multi-channel customer communications
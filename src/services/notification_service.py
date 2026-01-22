"""
Notification Service for sending alerts and messages to users.

This module provides functionality for sending notifications through
various channels including email, push notifications, and in-app messages.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class NotificationType(Enum):
    """Types of notifications that can be sent."""
    EMAIL = "email"
    PUSH = "push"
    IN_APP = "in_app"
    SMS = "sms"


class NotificationPriority(Enum):
    """Priority levels for notifications."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """Represents a notification to be sent to a user."""
    id: str
    user_id: str
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    created_at: datetime = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class NotificationService:
    """
    Service for managing and sending notifications to users.

    Supports multiple notification channels and priority levels.
    Handles notification queuing, delivery tracking, and user preferences.
    """

    def __init__(self):
        """Initialize the notification service."""
        self._notifications: dict[str, Notification] = {}
        self._user_preferences: dict[str, dict] = {}
        self._notification_counter = 0

    def _generate_id(self) -> str:
        """Generate a unique notification ID."""
        self._notification_counter += 1
        return f"notif_{self._notification_counter}"

    def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.IN_APP,
        priority: NotificationPriority = NotificationPriority.NORMAL,
    ) -> Notification:
        """
        Send a notification to a user.

        Args:
            user_id: The ID of the user to notify
            title: The notification title
            message: The notification message body
            notification_type: The channel to use for delivery
            priority: The priority level of the notification

        Returns:
            The created Notification object
        """
        notification = Notification(
            id=self._generate_id(),
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
        )

        self._notifications[notification.id] = notification
        self._deliver_notification(notification)

        return notification

    def _deliver_notification(self, notification: Notification) -> bool:
        """
        Deliver a notification through its specified channel.

        Args:
            notification: The notification to deliver

        Returns:
            True if delivery was successful
        """
        # Check user preferences
        prefs = self._user_preferences.get(notification.user_id, {})
        if not prefs.get(f"{notification.notification_type.value}_enabled", True):
            return False

        # Simulate delivery based on type
        if notification.notification_type == NotificationType.EMAIL:
            success = self._send_email(notification)
        elif notification.notification_type == NotificationType.PUSH:
            success = self._send_push(notification)
        elif notification.notification_type == NotificationType.SMS:
            success = self._send_sms(notification)
        else:
            success = True  # IN_APP is always available

        if success:
            notification.sent_at = datetime.utcnow()

        return success

    def _send_email(self, notification: Notification) -> bool:
        """Send notification via email."""
        # Email sending implementation would go here
        print(f"[EMAIL] To: {notification.user_id} - {notification.title}")
        return True

    def _send_push(self, notification: Notification) -> bool:
        """Send push notification."""
        # Push notification implementation would go here
        print(f"[PUSH] To: {notification.user_id} - {notification.title}")
        return True

    def _send_sms(self, notification: Notification) -> bool:
        """Send SMS notification."""
        # SMS sending implementation would go here
        print(f"[SMS] To: {notification.user_id} - {notification.title}")
        return True

    def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
    ) -> list[Notification]:
        """
        Get all notifications for a user.

        Args:
            user_id: The user's ID
            unread_only: If True, only return unread notifications

        Returns:
            List of notifications for the user
        """
        notifications = [
            n for n in self._notifications.values()
            if n.user_id == user_id
        ]

        if unread_only:
            notifications = [n for n in notifications if n.read_at is None]

        return sorted(notifications, key=lambda n: n.created_at, reverse=True)

    def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read.

        Args:
            notification_id: The notification ID

        Returns:
            True if the notification was found and marked
        """
        if notification_id in self._notifications:
            self._notifications[notification_id].read_at = datetime.utcnow()
            return True
        return False

    def set_user_preferences(
        self,
        user_id: str,
        email_enabled: bool = True,
        push_enabled: bool = True,
        sms_enabled: bool = False,
    ) -> None:
        """
        Set notification preferences for a user.

        Args:
            user_id: The user's ID
            email_enabled: Whether email notifications are enabled
            push_enabled: Whether push notifications are enabled
            sms_enabled: Whether SMS notifications are enabled
        """
        self._user_preferences[user_id] = {
            "email_enabled": email_enabled,
            "push_enabled": push_enabled,
            "sms_enabled": sms_enabled,
            "in_app_enabled": True,  # Always enabled
        }

    def get_unread_count(self, user_id: str) -> int:
        """
        Get the count of unread notifications for a user.

        Args:
            user_id: The user's ID

        Returns:
            Number of unread notifications
        """
        return len(self.get_user_notifications(user_id, unread_only=True))


# Singleton instance
notification_service = NotificationService()

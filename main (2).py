#***************************************************
# MSSV: 20248977
# Họ và tên: Đào Quý Sang
#***************************************************
from abc import ABC
from datetime import datetime
from enum import Enum
from typing import Callable


class DeviceStatus(Enum):
    AVAILABLE = "Available"
    BORROWED = "Borrowed"
    UNDER_MAINTENANCE = "UnderMaintenance"


class AlertSeverity(Enum):
    INFORMATION = "Information"
    WARNING = "Warning"
    CRITICAL = "Critical"


# ---- dữ liệu sự kiện ----
class DeviceStatusChangedEventArgs:
    def __init__(self, device_id, old_status, new_status, changed_at):
        self.device_id = device_id
        self.old_status = old_status
        self.new_status = new_status
        self.changed_at = changed_at


class DeviceAlertEventArgs:
    def __init__(self, device_id, message, severity, occurred_at):
        self.device_id = device_id
        self.message = message
        self.severity = severity
        self.occurred_at = occurred_at


class InvalidDeviceReadingException(Exception):
    pass


# Python không có từ khóa event nên tự làm một lớp giữ danh sách handler
class Event:
    def __init__(self):
        self._handlers = []

    def subscribe(self, handler):
        pass

    def unsubscribe(self, handler):
        pass

    def invoke(self, sender, args):
        pass


# ---- publisher ----
class TeachingDevice(ABC):
    def __init__(self, device_id, name):
        self.id = device_id
        self.name = name
        self._status = DeviceStatus.AVAILABLE
        self.status_changed = Event()
        self.alert_raised = Event()

    @property
    def status(self):
        return self._status

    def change_status(self, new_status):
        pass

    def _raise_alert(self, message, severity):
        pass

    def _on_status_changed(self, e):
        pass

    def _on_alert_raised(self, e):
        pass


class ProjectorRemote(TeachingDevice):
    def __init__(self, device_id, name, battery_level):
        super().__init__(device_id, name)
        self._battery_level = battery_level

    @property
    def battery_level(self):
        return self._battery_level

    def update_battery_level(self, new_level):
        pass


class AirConditionerRemote(TeachingDevice):
    def __init__(self, device_id, name, assigned_room):
        super().__init__(device_id, name)
        self.assigned_room = assigned_room
        self._is_responsive = True

    @property
    def is_responsive(self):
        return self._is_responsive

    def update_response_state(self, is_responsive):
        pass


class WirelessMicrophone(TeachingDevice):
    def __init__(self, device_id, name, battery_level, signal_quality):
        super().__init__(device_id, name)
        self._battery_level = battery_level
        self._signal_quality = signal_quality

    @property
    def battery_level(self):
        return self._battery_level

    @property
    def signal_quality(self):
        return self._signal_quality

    def update_battery_level(self, new_level):
        pass

    def update_signal_quality(self, new_quality):
        pass


# ---- subscriber ----
class ConsoleNotificationService:
    def handle_alert(self, sender, e):
        pass


class DeviceAuditLogger:
    def __init__(self):
        self._entries = []

    def handle_status_changed(self, sender, e):
        pass


class MaintenanceService:
    def __init__(self):
        self._requests = []

    def handle_critical_alert(self, sender, e):
        pass


# delegate trong C# tương ứng một kiểu hàm
AlertFilter = Callable[[DeviceAlertEventArgs], bool]


class FilteredAlertSubscriber:
    def __init__(self, alert_filter, action):
        self._filter = alert_filter
        self._action = action

    def handle_alert(self, sender, e):
        pass


class DeviceMonitoringCoordinator:
    def __init__(self, devices, notification_service, audit_logger, maintenance_service):
        self._devices = list(devices)
        self._notification_service = notification_service
        self._audit_logger = audit_logger
        self._maintenance_service = maintenance_service
        self._subscribed = False

    def subscribe(self):
        pass

    def unsubscribe(self):
        pass

    def dispose(self):
        pass


def main():
    pass


if __name__ == "__main__":
    main()

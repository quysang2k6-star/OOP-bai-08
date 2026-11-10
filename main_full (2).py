#***************************************************
# MSSV: 202418977
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
    def __init__(self, device_id, invalid_value):
        super().__init__(f"Thiết bị {device_id}: giá trị {invalid_value} ngoài khoảng 0..100")  
        self.device_id = device_id
        self.invalid_value = invalid_value


def _check_reading(device_id, value):
    if not 0 <= value <= 100:
        raise InvalidDeviceReadingException(device_id, value)


class Event:
    def __init__(self):
        self._handlers = []
        self.errors = []  # ( ) ghi lại handler bị lỗi

    def subscribe(self, handler):
        if not callable(handler):
            raise TypeError("Handler phải là hàm hoặc phương thức")
        if handler not in self._handlers:  
            self._handlers.append(handler)

    def unsubscribe(self, handler):
        if handler in self._handlers:  
            self._handlers.remove(handler)

    def invoke(self, sender, args):

        for handler in list(self._handlers):
            try:
                handler(sender, args)
            except Exception as ex:
                self.errors.append((handler, ex))

    @property
    def handler_count(self):
        return len(self._handlers)


class EventAccess:
    def __init__(self, event):
        self._event = event

    def subscribe(self, handler):
        self._event.subscribe(handler)

    def unsubscribe(self, handler):
        self._event.unsubscribe(handler)

    @property
    def handler_count(self):
        return self._event.handler_count

    @property
    def errors(self):
        return tuple(self._event.errors)



OK, LOW, ZERO = 0, 1, 2  


def _zone(value, low_limit):
    if value == 0:
        return ZERO
    return LOW if value < low_limit else OK


class TeachingDevice(ABC):
    def __init__(self, device_id, name):
        if not device_id or not device_id.strip():
            raise ValueError("Mã thiết bị không được rỗng")
        if not name or not name.strip():
            raise ValueError("Tên thiết bị không được rỗng")
        self.id = device_id.strip()
        self.name = name.strip()
        self._status = DeviceStatus.AVAILABLE
        self._status_changed = Event()   
        self._alert_raised = Event()
        self.status_changed = EventAccess(self._status_changed)  
        self.alert_raised = EventAccess(self._alert_raised)

    @property
    def status(self):
        return self._status

    def change_status(self, new_status):
        if new_status == self._status:  
            return
        old_status = self._status
        self._status = new_status       
        self._on_status_changed(DeviceStatusChangedEventArgs(self.id, old_status, new_status, datetime.now()))

    def _raise_alert(self, message, severity):
        self._on_alert_raised(DeviceAlertEventArgs(self.id, message, severity, datetime.now()))

    def _check_zone_alert(self, old_zone, new_zone, what, value):
        if new_zone <= old_zone:
            return
        if new_zone == ZERO:
            self._raise_alert(f"{what} bằng 0%", AlertSeverity.CRITICAL)
        else:
            self._raise_alert(f"{what} xuống thấp ({value}%)", AlertSeverity.WARNING)

    def _on_status_changed(self, e):
        self._status_changed.invoke(self, e)

    def _on_alert_raised(self, e):
        self._alert_raised.invoke(self, e)


class ProjectorRemote(TeachingDevice):
    LOW_BATTERY = 20  # ( )

    def __init__(self, device_id, name, battery_level):
        super().__init__(device_id, name)
        _check_reading(self.id, battery_level)
        self._battery_level = battery_level

    @property
    def battery_level(self):
        return self._battery_level

    def update_battery_level(self, new_level):
        _check_reading(self.id, new_level)  
        old_zone = _zone(self._battery_level, self.LOW_BATTERY)
        self._battery_level = new_level     
        self._check_zone_alert(old_zone, _zone(new_level, self.LOW_BATTERY), "Pin", new_level)


class AirConditionerRemote(TeachingDevice):
    def __init__(self, device_id, name, assigned_room):
        super().__init__(device_id, name)
        if not assigned_room or not assigned_room.strip():
            raise ValueError("Phòng được gán không được rỗng")
        self.assigned_room = assigned_room.strip()
        self._is_responsive = True

    @property
    def is_responsive(self):
        return self._is_responsive

    def update_response_state(self, is_responsive):
        was_responsive = self._is_responsive
        self._is_responsive = is_responsive
        if was_responsive and not is_responsive:  
            self._raise_alert("Điều khiển điều hòa không phản hồi", AlertSeverity.CRITICAL)


class WirelessMicrophone(TeachingDevice):
    LOW_BATTERY = 30  # ( )
    LOW_SIGNAL = 40   # ( )

    def __init__(self, device_id, name, battery_level, signal_quality):
        super().__init__(device_id, name)
        _check_reading(self.id, battery_level)
        _check_reading(self.id, signal_quality)
        self._battery_level = battery_level
        self._signal_quality = signal_quality

    @property
    def battery_level(self):
        return self._battery_level

    @property
    def signal_quality(self):
        return self._signal_quality

    def update_battery_level(self, new_level):
        _check_reading(self.id, new_level)
        old_zone = _zone(self._battery_level, self.LOW_BATTERY)
        self._battery_level = new_level
        self._check_zone_alert(old_zone, _zone(new_level, self.LOW_BATTERY), "Pin", new_level)

    def update_signal_quality(self, new_quality):
        _check_reading(self.id, new_quality)
        old_zone = _zone(self._signal_quality, self.LOW_SIGNAL)
        self._signal_quality = new_quality
        self._check_zone_alert(old_zone, _zone(new_quality, self.LOW_SIGNAL), "Tín hiệu", new_quality)



class ConsoleNotificationService:
    def handle_alert(self, sender, e):
        print(f"  [{e.severity.value}] {e.device_id}: {e.message}")


class DeviceAuditLogger:
    def __init__(self):
        self._entries = []

    @property
    def entries(self):
        return tuple(self._entries)

    def handle_status_changed(self, sender, e):
        self._entries.append(f"{e.changed_at:%H:%M:%S}: {e.device_id}, {e.old_status.value} -> {e.new_status.value}")


class MaintenanceService:
    def __init__(self):
        self._requests = []

    @property
    def requests(self):
        return tuple(self._requests)

    def handle_critical_alert(self, sender, e):
        if e.severity != AlertSeverity.CRITICAL:  
            return
        self._requests.append(f"Yêu cầu bảo trì {e.device_id}: {e.message}")



AlertFilter = Callable[[DeviceAlertEventArgs], bool]


class FilteredAlertSubscriber:
    def __init__(self, alert_filter, action):
        if alert_filter is None or action is None:
            raise ValueError("Hàm lọc và hàm hành động không được None")
        self._filter = alert_filter
        self._action = action

    def handle_alert(self, sender, e):
        if self._filter(e):
            self._action(e)



class DeviceMonitoringCoordinator:
    def __init__(self, devices, notification_service, audit_logger, maintenance_service):
        self._devices = list(devices)
        self._notification_service = notification_service
        self._audit_logger = audit_logger
        self._maintenance_service = maintenance_service
        self._registrations = []
        self._subscribed = False

    def subscribe(self):
        if self._subscribed:  
            return
        for device in self._devices:
            self._register(device.alert_raised, self._notification_service.handle_alert)
            self._register(device.alert_raised, self._maintenance_service.handle_critical_alert)
            self._register(device.status_changed, self._audit_logger.handle_status_changed)
        self._subscribed = True

    def _register(self, event_access, handler):
        event_access.subscribe(handler)
        self._registrations.append((event_access, handler))

    def unsubscribe(self):
        for event_access, handler in self._registrations:
            event_access.unsubscribe(handler)
        self._registrations.clear()
        self._subscribed = False

    def dispose(self):
        self.unsubscribe()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.dispose()



class EmailNotifier:  # ( ) tên tùy ý
    def __init__(self):
        self.sent = []

    def handle_alert(self, sender, e):
        if e.severity != AlertSeverity.INFORMATION:
            self.sent.append(f"Email: {e.device_id} - {e.message}")



def thu(nhan, ham, *tham_so):
    try:
        ham(*tham_so)
        print(f"{nhan}: KHÔNG có lỗi (không đúng kỳ vọng)")
    except (InvalidDeviceReadingException, ValueError, AttributeError, TypeError) as e:
        print(f"{nhan}: {type(e).__name__} - {e}")


def main():
    pj = ProjectorRemote("PJ01", "ĐK máy chiếu Epson", 50)           
    ac = AirConditionerRemote("AC01", "ĐK điều hòa Daikin", "A203")
    mic = WirelessMicrophone("MIC01", "Micro Shure", 80, 90)
    console, audit, maintenance = ConsoleNotificationService(), DeviceAuditLogger(), MaintenanceService()
    coordinator = DeviceMonitoringCoordinator([pj, ac, mic], console, audit, maintenance)
    coordinator.subscribe()
    coordinator.subscribe()  
    print(f"Số handler cảnh báo của PJ01: {pj.alert_raised.handler_count} (mong đợi 2: Console và Maintenance)")

    print("\n== 1. Đổi trạng thái ==")
    pj.change_status(DeviceStatus.BORROWED)
    pj.change_status(DeviceStatus.BORROWED)     
    pj.change_status(DeviceStatus.AVAILABLE)
    ac.change_status(DeviceStatus.UNDER_MAINTENANCE)
    print(f"Số dòng log: {len(audit.entries)} (mong đợi 3)")

    print("\n== 2. Pin máy chiếu: 50 -> 30 -> 15 -> 10 -> 0 -> 60 ==")
    for level in (30, 15, 10, 0, 60):
        print(f"- pin {level}%")
        pj.update_battery_level(level)          

    print("\n== 3. Micro ==")
    print("- pin 80 -> 25"); mic.update_battery_level(25)
    print("- tín hiệu 90 -> 35"); mic.update_signal_quality(35)
    print("- tín hiệu 35 -> 0"); mic.update_signal_quality(0)
    print("- pin 25 -> 0"); mic.update_battery_level(0)

    print("\n== 4. Điều hòa ==")
    print("- không phản hồi"); ac.update_response_state(False)
    print("- vẫn không phản hồi (không báo lặp)"); ac.update_response_state(False)

    print("\n== 5. Giá trị sai và phát sinh event từ ngoài ==")
    thu("Pin 120", pj.update_battery_level, 120)
    thu("Tín hiệu -5", mic.update_signal_quality, -5)
    print(f"Pin máy chiếu vẫn là {pj.battery_level}%")
    thu("Phát event từ ngoài", lambda: pj.alert_raised.invoke(pj, None))

    print("\n== 6. Delegate lọc + subscriber thêm mới (không sửa lớp thiết bị) ==")
    chi_nghiem_trong = FilteredAlertSubscriber(
        lambda a: a.severity == AlertSeverity.CRITICAL,
        lambda a: print(f"  CRITICAL (đã lọc): {a.device_id} - {a.message}"))
    email = EmailNotifier()
    pj.alert_raised.subscribe(chi_nghiem_trong.handle_alert)
    pj.alert_raised.subscribe(email.handle_alert)
    print("- pin 60 -> 10 (Warning, bộ lọc bỏ qua)"); pj.update_battery_level(10)
    print("- pin 10 -> 0 (Critical, bộ lọc nhận)"); pj.update_battery_level(0)
    print(f"Email đã gửi: {len(email.sent)}")

    print("\n== 7. Hủy đăng ký ==")
    coordinator.unsubscribe()
    print(f"Handler còn lại của PJ01: {pj.alert_raised.handler_count} (mong đợi 2: bộ lọc và Email)")
    pj.update_battery_level(50)
    print("- pin 50 -> 10 sau khi hủy (Console không còn in)"); pj.update_battery_level(10)
    coordinator.subscribe()
    print(f"Đăng ký lại: {pj.alert_raised.handler_count} handler")
    ac2 = AirConditionerRemote("AC02", "ĐK điều hòa LG", "B105")
    with DeviceMonitoringCoordinator([ac2], console, audit, maintenance) as c2:
        c2.subscribe()
        print("- AC02 không phản hồi (trong khối with)"); ac2.update_response_state(False)
    ac2.update_response_state(True)
    print("- sau khối with (đã Dispose), AC02 không phản hồi lần nữa: không còn in"); ac2.update_response_state(False)
    print(f"Handler cảnh báo của AC02 sau Dispose: {ac2.alert_raised.handler_count}")

    print("\n== 8. Một handler lỗi không chặn handler khác ==")
    mic3 = WirelessMicrophone("MIC03", "Micro Rode", 80, 90)
    nhan_duoc = []

    def handler_hong(sender, e):
        raise RuntimeError("handler hỏng")

    mic3.alert_raised.subscribe(handler_hong)
    mic3.alert_raised.subscribe(lambda s, e: nhan_duoc.append(e.message))
    mic3.update_battery_level(20)
    print(f"Handler tốt vẫn nhận: {nhan_duoc}; lỗi đã ghi lại: {len(mic3.alert_raised.errors)}")

    print("\n== Tổng kết ==")
    print("Nhật ký trạng thái:", *audit.entries, sep="\n  ")
    print("Yêu cầu bảo trì:", *maintenance.requests, sep="\n  ")


if __name__ == "__main__":
    main()

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4, UUID
import tkinter as tk
from tkinter import ttk, messagebox


@dataclass
class Device:
    id: UUID
    name: str
    state: bool = False
    value: float = 0.0
    unit: str = ""
    energyConsumption: float = 0.0

    def turnOn(self) -> None:
        self.state = True

    def turnOff(self) -> None:
        self.state = False

    def setValue(self, value: float) -> None:
        self.value = value

    def getState(self) -> bool:
        return self.state

    def getValue(self) -> float:
        return self.value


@dataclass
class Room:
    id: UUID
    name: str
    devices: List[Device] = field(default_factory=list)

    def addDevice(self, device: Device) -> None:
        if all(existing.id != device.id for existing in self.devices):
            self.devices.append(device)

    def removeDevice(self, device: Device) -> None:
        self.devices = [existing for existing in self.devices if existing.id != device.id]

    def getDevices(self) -> List[Device]:
        return list(self.devices)


@dataclass
class Automation:
    id: UUID
    name: str
    active: bool
    schedule: datetime
    condition: str
    action: str
    devices: List[Device] = field(default_factory=list)

    def activate(self) -> None:
        self.active = True

    def deactivate(self) -> None:
        self.active = False

    def checkCondition(self) -> bool:
        normalized = self.condition.strip().lower()
        if normalized in {"always", "sempre"}:
            return True
        if normalized in {"never", "mai"}:
            return False
        if normalized.startswith("hour>="):
            try:
                threshold = int(normalized.split(">=")[1].strip())
                return datetime.now().hour >= threshold
            except ValueError:
                return False
        if normalized.startswith("hour<="):
            try:
                threshold = int(normalized.split("<=")[1].strip())
                return datetime.now().hour <= threshold
            except ValueError:
                return False
        return False

    def execute(self) -> bool:
        if not self.active or not self.checkCondition():
            return False

        normalized_action = self.action.strip().lower()
        for device in self.devices:
            if normalized_action == "on":
                device.turnOn()
            elif normalized_action == "off":
                device.turnOff()
            elif normalized_action.startswith("set:"):
                try:
                    new_value = float(normalized_action.split(":", 1)[1].strip())
                    device.setValue(new_value)
                except ValueError:
                    return False
            else:
                return False
        return True


@dataclass
class Event:
    id: UUID
    timestamp: datetime
    type: str
    description: str
    source: str


@dataclass
class EventLog:
    events: List[Event] = field(default_factory=list)

    def addEvent(self, event: Event) -> None:
        self.events.append(event)

    def getEvents(self) -> List[Event]:
        return list(self.events)

    def filterByDate(self, date_value: datetime) -> List[Event]:
        return [event for event in self.events if event.timestamp.date() == date_value.date()]

    def filterByType(self, type_value: str) -> List[Event]:
        normalized = type_value.strip().lower()
        return [event for event in self.events if event.type.strip().lower() == normalized]


@dataclass
class User:
    id: UUID
    username: str
    password: str
    email: str
    role: str
    logged_in: bool = False

    def login(self, username: str, password: str) -> bool:
        if self.username == username and self.password == password:
            self.logged_in = True
            return True
        return False

    def logout(self) -> None:
        self.logged_in = False

    def updateProfile(self, email: Optional[str] = None, password: Optional[str] = None) -> None:
        if email:
            self.email = email
        if password:
            self.password = password

    def accessDashboard(self) -> bool:
        return self.logged_in


class SmartHomeSystem:
    def __init__(self) -> None:
        self.rooms: List[Room] = []
        self.devices: List[Device] = []
        self.automations: List[Automation] = []
        self.users: List[User] = []
        self.eventLog = EventLog()

    def addRoom(self, room: Room) -> None:
        if all(existing.id != room.id for existing in self.rooms):
            self.rooms.append(room)

    def findRoomByName(self, name: str) -> Optional[Room]:
        normalized = name.strip().lower()
        for room in self.rooms:
            if room.name.strip().lower() == normalized:
                return room
        return None

    def createRoom(self, name: str) -> Room:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Il nome stanza non puo essere vuoto")
        if self.findRoomByName(normalized) is not None:
            raise ValueError("Esiste gia una stanza con questo nome")
        room = Room(id=uuid4(), name=normalized)
        self.addRoom(room)
        self.generateEvent("ROOM_CREATED", f"Stanza '{room.name}' creata", source="SmartHomeSystem")
        return room

    def addDevice(self, device: Device, room: Optional[Room] = None) -> None:
        if all(existing.id != device.id for existing in self.devices):
            self.devices.append(device)
        if room is not None:
            room.addDevice(device)

    def createDeviceInRoom(self, room: Room, name: str) -> Device:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Il nome dispositivo non puo essere vuoto")
        if any(device.name.strip().lower() == normalized.lower() for device in room.devices):
            raise ValueError("Esiste gia un dispositivo con questo nome nella stanza")
        device = Device(id=uuid4(), name=normalized, state=False, value=0.0, unit="", energyConsumption=0.0)
        self.addDevice(device, room)
        self.generateEvent("DEVICE_ADDED", f"Dispositivo '{device.name}' aggiunto in '{room.name}'", source=room.name)
        return device

    def removeDeviceFromRoom(self, room: Room, device: Device) -> None:
        room.removeDevice(device)
        still_used = any(any(existing.id == device.id for existing in target_room.devices) for target_room in self.rooms)
        if not still_used:
            self.devices = [existing for existing in self.devices if existing.id != device.id]
        self.generateEvent("DEVICE_REMOVED", f"Dispositivo '{device.name}' rimosso da '{room.name}'", source=room.name)

    def addAutomation(self, automation: Automation) -> None:
        if all(existing.id != automation.id for existing in self.automations):
            self.automations.append(automation)
            self.generateEvent(
                "AUTOMATION_CREATED",
                f"Automazione '{automation.name}' creata",
                source="SmartHomeSystem",
            )

    def addUser(self, user: User) -> None:
        if all(existing.id != user.id for existing in self.users):
            self.users.append(user)

    def findDeviceByName(self, name: str) -> Optional[Device]:
        normalized = name.strip().lower()
        for device in self.devices:
            if device.name.strip().lower() == normalized:
                return device
        return None

    def findAutomationByName(self, name: str) -> Optional[Automation]:
        normalized = name.strip().lower()
        for automation in self.automations:
            if automation.name.strip().lower() == normalized:
                return automation
        return None

    def controlDevice(self, device: Device, command: str = "toggle", value: Optional[float] = None) -> bool:
        normalized = command.strip().lower()
        if normalized == "on":
            device.turnOn()
            self.generateEvent("DEVICE", f"{device.name} acceso", source=device.name)
            return True
        if normalized == "off":
            device.turnOff()
            self.generateEvent("DEVICE", f"{device.name} spento", source=device.name)
            return True
        if normalized == "set" and value is not None:
            device.setValue(value)
            self.generateEvent("DEVICE", f"{device.name} valore aggiornato a {value}{device.unit}", source=device.name)
            return True
        return False

    def executeAutomation(self, automation: Automation) -> bool:
        result = automation.execute()
        if result:
            self.generateEvent(
                "AUTOMATION_EXECUTED",
                f"Automazione '{automation.name}' eseguita",
                source=automation.name,
            )
        else:
            self.generateEvent(
                "AUTOMATION_SKIPPED",
                f"Automazione '{automation.name}' non eseguita",
                source=automation.name,
            )
        return result

    def executeAutomations(self) -> None:
        now = datetime.now()
        for automation in self.automations:
            if automation.active and automation.schedule <= now:
                self.executeAutomation(automation)

    def generateEvent(self, type_value: str, description: str, source: str = "System") -> Event:
        event = Event(
            id=uuid4(),
            timestamp=datetime.now(),
            type=type_value,
            description=description,
            source=source,
        )
        self.eventLog.addEvent(event)
        return event

    def getSystemStatus(self) -> str:
        active_devices = sum(1 for device in self.devices if device.getState())
        total_devices = len(self.devices)
        active_automations = sum(1 for automation in self.automations if automation.active)
        total_automations = len(self.automations)
        total_rooms = len(self.rooms)
        total_events = len(self.eventLog.events)
        return (
            f"Stanze: {total_rooms}\n"
            f"Dispositivi attivi: {active_devices}/{total_devices}\n"
            f"Automazioni attive: {active_automations}/{total_automations}\n"
            f"Eventi registrati: {total_events}"
        )


class SmartHomeApp:
    def __init__(self, root: tk.Tk, system: SmartHomeSystem) -> None:
        self.root = root
        self.system = system
        self.current_user: Optional[User] = None
        self.room_widgets: dict[UUID, dict[str, object]] = {}

        self.root.title("Smart Home Control System")
        self.root.geometry("980x680")
        self.root.minsize(980, 680)

        self.main_container = ttk.Frame(self.root, padding=12)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.login_frame = ttk.LabelFrame(self.main_container, text="Login")
        self.dashboard_frame = ttk.Frame(self.main_container)

        self._build_login()
        self._build_dashboard()
        self._show_login()

    def _build_login(self) -> None:
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        inner = ttk.Frame(self.login_frame, padding=20)
        inner.pack(expand=True)

        ttk.Label(inner, text="Username").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(inner, text="Password").grid(row=1, column=0, sticky="w", pady=4)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        ttk.Entry(inner, textvariable=self.username_var, width=30).grid(row=0, column=1, pady=4)
        ttk.Entry(inner, textvariable=self.password_var, width=30, show="*").grid(row=1, column=1, pady=4)
        ttk.Button(inner, text="Accedi", command=self._handle_login).grid(row=2, column=0, columnspan=2, pady=10)

    def _build_dashboard(self) -> None:
        header = ttk.Frame(self.dashboard_frame)
        header.pack(fill=tk.X, pady=(0, 8))

        self.welcome_label = ttk.Label(header, text="Dashboard", font=("Arial", 12, "bold"))
        self.welcome_label.pack(side=tk.LEFT)
        ttk.Button(header, text="Logout", command=self._handle_logout).pack(side=tk.RIGHT)

        self.notebook = ttk.Notebook(self.dashboard_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.devices_tab = ttk.Frame(self.notebook, padding=10)
        self.automations_tab = ttk.Frame(self.notebook, padding=10)
        self.events_tab = ttk.Frame(self.notebook, padding=10)
        self.status_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.devices_tab, text="Dispositivi")
        self.notebook.add(self.automations_tab, text="Automazioni")
        self.notebook.add(self.events_tab, text="Eventi")
        self.notebook.add(self.status_tab, text="Stato Sistema")

        self._build_devices_tab()
        self._build_automations_tab()
        self._build_events_tab()
        self._build_status_tab()

    def _build_devices_tab(self) -> None:
        top_bar = ttk.LabelFrame(self.devices_tab, text="Gestione stanze", padding=10)
        top_bar.pack(fill=tk.X, pady=(0, 8))

        self.new_room_name_var = tk.StringVar()
        ttk.Label(top_bar, text="Nome stanza").pack(side=tk.LEFT, padx=(0, 6))
        ttk.Entry(top_bar, textvariable=self.new_room_name_var, width=30).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(top_bar, text="Aggiungi stanza", command=self._add_room).pack(side=tk.LEFT)

        self.rooms_notebook = ttk.Notebook(self.devices_tab)
        self.rooms_notebook.pack(fill=tk.BOTH, expand=True)
        self._refresh_room_tabs()

    def _refresh_room_tabs(self) -> None:
        for tab_id in self.rooms_notebook.tabs():
            self.rooms_notebook.forget(tab_id)
        self.room_widgets.clear()

        for room in self.system.rooms:
            tab = ttk.Frame(self.rooms_notebook, padding=10)
            self.rooms_notebook.add(tab, text=room.name)

            left = ttk.Frame(tab)
            left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
            right = ttk.LabelFrame(tab, text="Controllo", padding=10)
            right.pack(side=tk.RIGHT, fill=tk.Y)

            add_row = ttk.Frame(left)
            add_row.pack(fill=tk.X, pady=(0, 6))
            new_device_var = tk.StringVar()
            ttk.Label(add_row, text="Nome dispositivo").pack(side=tk.LEFT, padx=(0, 6))
            ttk.Entry(add_row, textvariable=new_device_var, width=26).pack(side=tk.LEFT, padx=(0, 6))
            ttk.Button(
                add_row, text="Aggiungi dispositivo", command=lambda target_room=room: self._add_device_to_room(target_room)
            ).pack(side=tk.LEFT, padx=(0, 6))
            ttk.Button(
                add_row, text="Elimina dispositivo selezionato", command=lambda target_room=room: self._remove_selected_device(target_room)
            ).pack(side=tk.LEFT)

            devices_list = tk.Listbox(left, height=18)
            devices_list.pack(fill=tk.BOTH, expand=True)
            devices_list.bind(
                "<<ListboxSelect>>", lambda _event, target_room=room: self._on_room_device_select(target_room)
            )

            ttk.Button(
                right, text="Accendi", command=lambda target_room=room: self._control_room_selected_device(target_room, "on")
            ).pack(fill=tk.X, pady=2)
            ttk.Button(
                right, text="Spegni", command=lambda target_room=room: self._control_room_selected_device(target_room, "off")
            ).pack(fill=tk.X, pady=2)
            ttk.Label(right, text="Valore").pack(anchor="w", pady=(8, 2))
            value_var = tk.StringVar()
            ttk.Entry(right, textvariable=value_var, width=16).pack(fill=tk.X, pady=2)
            ttk.Button(
                right, text="Aggiorna valore", command=lambda target_room=room: self._set_room_selected_device_value(target_room)
            ).pack(fill=tk.X, pady=2)

            self.room_widgets[room.id] = {
                "frame": tab,
                "devices_list": devices_list,
                "new_device_var": new_device_var,
                "value_var": value_var,
            }

            self._refresh_room_devices(room)

    def _refresh_room_devices(self, room: Room) -> None:
        widgets = self.room_widgets.get(room.id)
        if widgets is None:
            return
        devices_list = widgets["devices_list"]
        assert isinstance(devices_list, tk.Listbox)
        devices_list.delete(0, tk.END)
        for device in room.getDevices():
            state = "ON" if device.getState() else "OFF"
            devices_list.insert(tk.END, f"{device.name} | {state} | {device.getValue()}{device.unit}")

    def _add_room(self) -> None:
        room_name = self.new_room_name_var.get().strip()
        try:
            self.system.createRoom(room_name)
        except ValueError as error:
            messagebox.showerror("Errore stanza", str(error))
            return
        self.new_room_name_var.set("")
        self._refresh_room_tabs()
        self._refresh_events()
        self._refresh_status()

    def _add_device_to_room(self, room: Room) -> None:
        widgets = self.room_widgets.get(room.id)
        if widgets is None:
            return
        new_device_var = widgets["new_device_var"]
        assert isinstance(new_device_var, tk.StringVar)
        name = new_device_var.get().strip()
        try:
            self.system.createDeviceInRoom(room, name)
        except ValueError as error:
            messagebox.showerror("Errore dispositivo", str(error))
            return
        new_device_var.set("")
        self._refresh_room_devices(room)
        self._refresh_events()
        self._refresh_status()

    def _selected_device_in_room(self, room: Room) -> Optional[Device]:
        widgets = self.room_widgets.get(room.id)
        if widgets is None:
            return None
        devices_list = widgets["devices_list"]
        assert isinstance(devices_list, tk.Listbox)
        index = devices_list.curselection()
        if not index:
            return None
        selected_text = devices_list.get(index[0])
        device_name = selected_text.split("|")[0].strip()
        for device in room.devices:
            if device.name.strip().lower() == device_name.lower():
                return device
        return None

    def _remove_selected_device(self, room: Room) -> None:
        device = self._selected_device_in_room(room)
        if device is None:
            messagebox.showwarning("Selezione", "Seleziona un dispositivo nella stanza")
            return
        self.system.removeDeviceFromRoom(room, device)
        self._refresh_room_devices(room)
        self._refresh_events()
        self._refresh_status()

    def _on_room_device_select(self, room: Room) -> None:
        device = self._selected_device_in_room(room)
        if device is None:
            return
        widgets = self.room_widgets.get(room.id)
        if widgets is None:
            return
        value_var = widgets["value_var"]
        assert isinstance(value_var, tk.StringVar)
        value_var.set(str(device.getValue()))

    def _control_room_selected_device(self, room: Room, command: str) -> None:
        device = self._selected_device_in_room(room)
        if device is None:
            messagebox.showwarning("Selezione", "Seleziona un dispositivo nella stanza")
            return
        self.system.controlDevice(device, command=command)
        self._refresh_room_devices(room)
        self._refresh_events()
        self._refresh_status()

    def _set_room_selected_device_value(self, room: Room) -> None:
        device = self._selected_device_in_room(room)
        if device is None:
            messagebox.showwarning("Selezione", "Seleziona un dispositivo nella stanza")
            return
        widgets = self.room_widgets.get(room.id)
        if widgets is None:
            return
        value_var = widgets["value_var"]
        assert isinstance(value_var, tk.StringVar)
        try:
            value = float(value_var.get().strip())
        except ValueError:
            messagebox.showerror("Valore non valido", "Inserisci un numero")
            return
        self.system.controlDevice(device, command="set", value=value)
        self._refresh_room_devices(room)
        self._refresh_events()
        self._refresh_status()

    def _build_automations_tab(self) -> None:
        form = ttk.LabelFrame(self.automations_tab, text="Nuova automazione", padding=10)
        form.pack(fill=tk.X, pady=(0, 8))

        self.auto_name_var = tk.StringVar()
        self.auto_condition_var = tk.StringVar(value="always")
        self.auto_action_var = tk.StringVar(value="on")
        self.auto_schedule_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M"))

        ttk.Label(form, text="Nome").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.auto_name_var, width=25).grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(form, text="Condizione").grid(row=0, column=2, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.auto_condition_var, width=20).grid(row=0, column=3, padx=4, pady=4)
        ttk.Label(form, text="Azione").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        ttk.Combobox(form, textvariable=self.auto_action_var, values=["on", "off", "set:22"], width=22).grid(
            row=1, column=1, padx=4, pady=4
        )
        ttk.Label(form, text="Schedule (YYYY-MM-DD HH:MM)").grid(row=1, column=2, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.auto_schedule_var, width=20).grid(row=1, column=3, padx=4, pady=4)
        ttk.Button(form, text="Crea automazione", command=self._create_automation).grid(
            row=2, column=0, columnspan=4, sticky="ew", pady=6
        )

        list_frame = ttk.Frame(self.automations_tab)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.automations_list = tk.Listbox(list_frame, height=16)
        self.automations_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        actions = ttk.Frame(list_frame)
        actions.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        ttk.Button(actions, text="Attiva", command=lambda: self._toggle_selected_automation(True)).pack(fill=tk.X, pady=2)
        ttk.Button(actions, text="Disattiva", command=lambda: self._toggle_selected_automation(False)).pack(
            fill=tk.X, pady=2
        )
        ttk.Button(actions, text="Esegui ora", command=self._execute_selected_automation).pack(fill=tk.X, pady=2)
        ttk.Button(actions, text="Esegui automazioni", command=self._execute_due_automations).pack(fill=tk.X, pady=2)

    def _build_events_tab(self) -> None:
        controls = ttk.Frame(self.events_tab)
        controls.pack(fill=tk.X, pady=(0, 6))

        self.event_filter_type_var = tk.StringVar()
        self.event_filter_date_var = tk.StringVar()

        ttk.Label(controls, text="Tipo").pack(side=tk.LEFT, padx=4)
        ttk.Entry(controls, textvariable=self.event_filter_type_var, width=18).pack(side=tk.LEFT, padx=4)
        ttk.Label(controls, text="Data (YYYY-MM-DD)").pack(side=tk.LEFT, padx=4)
        ttk.Entry(controls, textvariable=self.event_filter_date_var, width=16).pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Filtra", command=self._refresh_events).pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Reset", command=self._reset_event_filters).pack(side=tk.LEFT, padx=4)

        self.events_list = tk.Listbox(self.events_tab, height=24)
        self.events_list.pack(fill=tk.BOTH, expand=True)

    def _build_status_tab(self) -> None:
        self.status_text = tk.Text(self.status_tab, height=16, width=60)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        ttk.Button(self.status_tab, text="Aggiorna stato", command=self._refresh_status).pack(pady=8)

    def _show_login(self) -> None:
        self.dashboard_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH, expand=True)

    def _show_dashboard(self) -> None:
        self.login_frame.pack_forget()
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)

    def _handle_login(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get()
        for user in self.system.users:
            if user.login(username, password):
                self.current_user = user
                self.system.generateEvent("LOGIN", f"Utente {user.username} autenticato", source=user.username)
                self.welcome_label.config(text=f"Dashboard - {user.username} ({user.role})")
                self._show_dashboard()
                self._refresh_room_tabs()
                self._refresh_automations()
                self._refresh_events()
                self._refresh_status()
                return
        messagebox.showerror("Login fallito", "Credenziali non valide")

    def _handle_logout(self) -> None:
        if self.current_user:
            self.current_user.logout()
            self.system.generateEvent("LOGOUT", f"Utente {self.current_user.username} disconnesso", source=self.current_user.username)
        self.current_user = None
        self.username_var.set("")
        self.password_var.set("")
        self._show_login()

    def _create_automation(self) -> None:
        name = self.auto_name_var.get().strip()
        condition = self.auto_condition_var.get().strip()
        action = self.auto_action_var.get().strip()
        schedule_raw = self.auto_schedule_var.get().strip()

        if not name:
            messagebox.showerror("Errore", "Nome automazione obbligatorio")
            return

        try:
            schedule = datetime.strptime(schedule_raw, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Errore", "Formato schedule non valido")
            return

        automation = Automation(
            id=uuid4(),
            name=name,
            active=True,
            schedule=schedule,
            condition=condition,
            action=action,
            devices=list(self.system.devices),
        )
        self.system.addAutomation(automation)
        self._refresh_automations()
        self._refresh_events()
        self._refresh_status()

    def _refresh_automations(self) -> None:
        self.automations_list.delete(0, tk.END)
        for automation in self.system.automations:
            status = "ATTIVA" if automation.active else "DISATTIVA"
            self.automations_list.insert(
                tk.END,
                f"{automation.name} | {status} | {automation.schedule.strftime('%Y-%m-%d %H:%M')} | {automation.condition} | {automation.action}",
            )

    def _selected_automation(self) -> Optional[Automation]:
        index = self.automations_list.curselection()
        if not index:
            return None
        selected_text = self.automations_list.get(index[0])
        automation_name = selected_text.split("|")[0].strip()
        return self.system.findAutomationByName(automation_name)

    def _toggle_selected_automation(self, active: bool) -> None:
        automation = self._selected_automation()
        if automation is None:
            messagebox.showwarning("Selezione", "Seleziona un'automazione")
            return
        if active:
            automation.activate()
            self.system.generateEvent("AUTOMATION", f"Automazione '{automation.name}' attivata", source=automation.name)
        else:
            automation.deactivate()
            self.system.generateEvent("AUTOMATION", f"Automazione '{automation.name}' disattivata", source=automation.name)
        self._refresh_automations()
        self._refresh_events()
        self._refresh_status()

    def _execute_selected_automation(self) -> None:
        automation = self._selected_automation()
        if automation is None:
            messagebox.showwarning("Selezione", "Seleziona un'automazione")
            return
        self.system.executeAutomation(automation)
        self._refresh_room_tabs()
        self._refresh_events()
        self._refresh_status()

    def _execute_due_automations(self) -> None:
        self.system.executeAutomations()
        self._refresh_room_tabs()
        self._refresh_events()
        self._refresh_status()

    def _refresh_events(self) -> None:
        self.events_list.delete(0, tk.END)
        events = self.system.eventLog.getEvents()

        type_filter = self.event_filter_type_var.get().strip()
        date_filter = self.event_filter_date_var.get().strip()

        if type_filter:
            events = self.system.eventLog.filterByType(type_filter)
        if date_filter:
            try:
                parsed_date = datetime.strptime(date_filter, "%Y-%m-%d")
                events = [event for event in events if event.timestamp.date() == parsed_date.date()]
            except ValueError:
                pass

        for event in events:
            self.events_list.insert(
                tk.END,
                f"{event.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {event.type} | {event.source} | {event.description}",
            )

    def _reset_event_filters(self) -> None:
        self.event_filter_type_var.set("")
        self.event_filter_date_var.set("")
        self._refresh_events()

    def _refresh_status(self) -> None:
        self.status_text.delete("1.0", tk.END)
        self.status_text.insert(tk.END, self.system.getSystemStatus())


def build_demo_system() -> SmartHomeSystem:
    system = SmartHomeSystem()

    living_room = Room(id=uuid4(), name="Living Room")
    bedroom = Room(id=uuid4(), name="Bedroom")
    system.addRoom(living_room)
    system.addRoom(bedroom)

    lamp = Device(id=uuid4(), name="Lamp", state=False, value=0.0, unit="%", energyConsumption=8.5)
    thermostat = Device(id=uuid4(), name="Thermostat", state=True, value=21.0, unit="C", energyConsumption=30.0)
    system.addDevice(lamp, living_room)
    system.addDevice(thermostat, bedroom)

    admin = User(id=uuid4(), username="admin", password="admin", email="admin@smarthome.local", role="admin")
    user = User(id=uuid4(), username="user", password="user", email="user@smarthome.local", role="user")
    system.addUser(admin)
    system.addUser(user)

    demo_automation = Automation(
        id=uuid4(),
        name="Morning Warmup",
        active=True,
        schedule=datetime.now(),
        condition="always",
        action="set:22",
        devices=[thermostat],
    )
    system.addAutomation(demo_automation)

    system.controlDevice(lamp, command="on")
    system.executeAutomation(demo_automation)
    system.generateEvent("INFO", "Sistema inizializzato", source="Bootstrap")
    return system


def main() -> None:
    system = build_demo_system()
    root = tk.Tk()
    SmartHomeApp(root, system)
    root.mainloop()


if __name__ == "__main__":
    main()

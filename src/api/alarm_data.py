from datetime import datetime
import pytz

UNKNOWN = "N/A"

class AlarmData:
  def __init__(self, data: dict):
    self.rawData = data
    self.api_data_added = False
    self._own_vehicle_list = []
    self._foreign_vehicle_list = []

  def _prepare(self, message: str):
    start = message.find("Alarmierte Fahrzeuge:")
    if start != -1:
      end = message.find("\n", start)
      if end == -1:
        end = len(message)

      vehicles_str = message[start + len("Alarmierte Fahrzeuge:"):end].strip()
      vehicle_names = [v.strip() for v in vehicles_str.split(",")]
      own_vehicle_names = [v["name"] for v in self._own_vehicle_list]

      for name in vehicle_names:
        if name.startswith("Flo KI") and name.replace("Flo KI", "").strip() in own_vehicle_names:
          continue
        else:
          self._foreign_vehicle_list.append({"id": None, "name": name})
      self.rawData["text"] = message[:start].strip() + "\n" + message[end:].strip()

  def add_api_data(self, vehicle_data: dict):
    self.api_data_added = True
    self._own_vehicle_list = vehicle_data
    message = self.get("text", None)
    if message:
      self._prepare(message)

  def get(self, key, default=None):
    return self.rawData.get(key, default)
  
  def get_formatted_creation_date(self) -> str:
    timestamp = self.get("ts_create", 0)
    tz = pytz.timezone('Europe/Berlin')
    return datetime.fromtimestamp(timestamp, tz).strftime('%d.%m.%Y %H:%M:%S')
  
  def get_operation_no(self) -> str:
    return str(self.get("foreign_id", UNKNOWN))
  
  def get_keyword(self) -> str:
    return self.get("title", UNKNOWN)
  
  def get_address(self) -> str:
    return self.get("address", UNKNOWN)
  
  def get_latitude(self) -> float:
    return self.get("lat", 0.0)
  
  def get_longitude(self) -> float:
    return self.get("lng", 0.0)
  
  def get_message(self) -> str:
    return self.get("text", UNKNOWN)
  
  def get_own_vehicles(self) -> str:
    if not self.api_data_added:
      return "API data not added"
    
    vehicle_ids = self.get("vehicle", [])
    own_vehicles = [v for v in self._own_vehicle_list if v["id"] in vehicle_ids]
    return ", ".join([v["name"] for v in own_vehicles]) if own_vehicles else UNKNOWN
  
  def get_foreign_vehicles(self) -> str:
    if not self.api_data_added:
      return "API data not added"
    return ", ".join([v["name"] for v in self._foreign_vehicle_list]) if self._foreign_vehicle_list else UNKNOWN

def example_alarm_data():
  return {
    "id": 123,
    "foreign_id": "2019-1023",
    "author_id": 123456789,
    "alarmcode_id": 123456789,
    "date": 0,
    "priority": True,
    "title": "FEUER3",
    "text": "Unklare Rauchentwicklung im Hafen. Entstehug wahrscheinlich durch starke Reibung eines Fischers in Kombination mit einem Fisch. Es könnte sich um einen Fischbrand handeln.",
    "address": "Hauptstraße 247, 12345 Musterstadt",
    "lat": 0,
    "lng": 0,
    "scene_object": "string",
    "caller": "string",
    "patient": "string",
    "remark": "string",
    "units": "string",
    "destination": True,
    "destination_address": "string",
    "destination_lat": 0,
    "destination_lng": 0,
    "additional_text_1": "string",
    "additional_text_2": "string",
    "additional_text_3": "string",
    "report": "2 Einsatztabschnitte gebildet, 3 C-Rohre im Einsatz",
    "cluster": [
      0
    ],
    "group": [
      0
    ],
    "user_cluster_relation": [
      0
    ],
    "vehicle": [
      "string"
    ],
    "private_mode": True,
    "notification_type": 0,
    "notification_filter_vehicle": True,
    "notification_filter_status": True,
    "notification_filter_access": True,
    "notification_filter_status_ids": [
      0
    ],
    "send_push": True,
    "send_sms": True,
    "send_call": True,
    "send_mail": True,
    "send_pager": True,
    "response_time": 0,
    "closed": True,
    "new": True,
    "editable": True,
    "answerable": True,
    "hidden": True,
    "deleted": True,
    "ucr_adressed": [
      0
    ],
    "ucr_answered": [
      0
    ],
    "ucr_self_addressed": True,
    "ucr_self_status_id": 0,
    "ucr_self_note": "string",
    "count_recipients": 0,
    "count_read": 0,
    "ts_response": 0,
    "ts_publish": 0,
    "ts_close": 0,
    "ts_create": 0,
    "ts_update": 0,
    "notification_filter_status_access": True,
    "custom": [
      {
        "key": "hydrant-book",
        "title": "Seite und Planquardrat im Planbuch/Hydrantenbuch",
        "value": "15 H2"
      },
      {
        "key": "trigger",
        "title": "Anruferweg",
        "value": "Call to 19222"
      }
    ]
  }

def real_example_alarm_data():
  return {
    'id': 34079584,
    'author_id': 302403,
    'cluster_id': 14802,
    'alarmcode_id': 0,
    'message_channel_id': 10149237,
    'foreign_id': '123456789',
    'title': 'KEINE ALARMIERUNG - NUR EIN TEST',
    'text': 'Bitte zuhause bleiben',
    'report': '',
    'address': 'Edisonstraße 33, Kiel',
    'lat': 54.285156676385135,
    'lng': 10.159935127187117,
    'priority': False,
    'date': 1778006702,
    'new': True,
    'editable': False,
    'answerable': True,
    'notification_type': 4,
    'vehicle': [32816],
    'group': [],
    'cluster': [],
    'user_cluster_relation': [308631],
    'hidden': False,
    'deleted': False,
    'message_channel': True,
    'custom_answers': True,
    'attachment_count': 0,
    'closed': False,
    'close_state': -1,
    'duration': '',
    'ts_response': 1778010300,
    'response_time': 3600,
    'ucr_addressed': [308631],
    'ucr_answered': {},
    'ucr_answeredcount': {},
    'ucr_read': [],
    'ucr_self_addressed': True,
    'count_recipients': 1,
    'count_read': 0,
    'private_mode': False,
    'custom': [],
    'ts_publish': 1778006702,
    'ts_create': 1778006702,
    'ts_update': 1778006703,
    'ts_close': 0,
    'notification_filter_vehicle': False,
    'notification_filter_status': False,
    'notification_filter_shift_plan': 0,
    'notification_filter_access': False,
    'notification_filter_status_access': False,
    'ucr_self_status_id': 0,
    'ucr_self_note': ''
  }

def real2_example_alarm_data():
  return {
    'id': 34079585,
    'author_id': 249979,
    'cluster_id': 14802,
    'alarmcode_id': 0,
    'message_channel_id': 0,
    'foreign_id': '123456789',
    'title': 'FEU 00',
    'text': 'Brennt Kleinobjekt sonstiges am Gebäude/FassadeBrennt Kleinobjekt sonstiges am Gebäude/Fassade\nAuslösung: 01.01.2026 22:50:55\n\nAlarmierte Wachen: B20,F43\nAlarmierte Fahrzeuge: Flo KI 43-18-01,Flo KI 20-11-01,Flo KI 20-32-01,Flo KI 20-48-01,Flo KI 20-48-02,FF Wellsee,Flo KI 43-47-01,Flo KI 20-89-01,Flo KI 20-04-01 A,Flo KI 43-48-01',
    'report': '',
    'address': 'Witzlebenweg 2, Kiel Wellsee',
    'lat': 54.28677192090761,
    'lng': 10.155166124677736,
    'priority': True,
    'date': 1778273456,
    'new': False,
    'editable': True,
    'answerable': True,
    'notification_type': 2,
    'vehicle': [32814, 32816, 32817],
    'group': [],
    'cluster': [],
    'user_cluster_relation': [],
    'hidden': False,
    'deleted': False,
    'message_channel': True,
    'custom_answers': True,
    'attachment_count': 0,
    'closed': True,
    'close_state': 1,
    'duration': '12 Stunden, 1 Minuten',
    'ts_response': 1778277056,
    'response_time': 3600,
    'ucr_addressed': [302395, 302403, 302405, 302924, 302925, 302926, 302927, 308602, 308603, 308606, 308608, 308615, 308619, 308620, 308621, 308622, 308623, 308624, 308626, 308627, 308629, 308631, 308632, 308633, 308644, 320994, 321177, 331331, 418763, 418776, 425542, 459592, 508353, 646169, 707082, 752873],
    'ucr_answered': {'55646': {'308602': {'ts': 1778276614, 'note': ''}, '308621': {'ts': 1778276545, 'note': ''}, '308622': {'ts': 1778274444, 'note': ''}, '418763': {'ts': 1778273545, 'note': ''}, '302926': {'ts': 1778273529, 'note': ''}, '308619': {'ts': 1778273486, 'note': ''}, '320994': {'ts': 1778273470, 'note': ''}}, '55648': {'302395': {'ts': 1778275388, 'note': ''}, '302925': {'ts': 1778274145, 'note': ''}, '308626': {'ts': 1778273649, 'note': ''}, '459592': {'ts': 1778273521, 'note': ''}, '308603': {'ts': 1778273509, 'note': ''}, '308644': {'ts': 1778273508, 'note': ''}, '302403': {'ts': 1778273505, 'note': ''}, '308633': {'ts': 1778273494, 'note': ''}, '321177': {'ts': 1778273490, 'note': ''}, '707082': {'ts': 1778273489, 'note': ''}, '302927': {'ts': 1778273489, 'note': ''}, '308631': {'ts': 1778273481, 'note': ''}, '508353': {'ts': 1778273481, 'note': ''}, '331331': {'ts': 1778273472, 'note': ''}, '302405': {'ts': 1778273470, 'note': ''}, '752873': {'ts': 1778273466, 'note': ''}}}, 'ucr_answeredcount': {'55646': 7, '55648': 16}, 'ucr_read': [302395, 302403, 302405, 302924, 302925, 302926, 302927, 308602, 308603, 308619, 308620, 308621, 308622, 308623, 308624, 308626, 308627, 308629, 308631, 308632, 308633, 308644, 320994, 321177, 331331, 418763, 459592, 508353, 646169, 707082, 752873],
    'ucr_self_addressed': True,
    'count_recipients': 36,
    'count_read': 31,
    'private_mode': False,
    'custom': [],
    'ts_publish': 0,
    'ts_create': 1778273456,
    'ts_update': 1778316661,
    'ts_close': 1778316661,
    'notification_filter_vehicle': False,
    'notification_filter_status': False,
    'notification_filter_shift_plan': 0,
    'notification_filter_access': False,
    'notification_filter_status_access': False,
    'send_mail': False,
    'send_push': False,
    'send_sms': False,
    'send_call': False,
    'send_pager': False,
    'ucr_self_status_id': 55648,
    'ucr_self_note': ''
  }
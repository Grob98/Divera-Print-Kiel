import requests

class BuildingData:
    def __init__(self, coordinates: tuple[float, float], address: str):
        self._coordinates = coordinates
        self._address = address
        self._info_data: list = []
        self._info_address = ""

    def get_info_data_str(self) -> str:
        return "\n".join(self._info_data)

    def load_from_api(self):
        lat, lon = self._coordinates

        headers = {
            'User-Agent': 'Printer-App',
            'Accept': 'application/json',
            'Content-Type': 'text/plain',
        }

        query = f"""
        [out:json][timeout:25];

        (
        way(around:20,{lat},{lon})["building"];
        relation(around:20,{lat},{lon})["building"];
        );

        out tags;
        """

        try:
            url = "https://overpass-api.de/api/interpreter"

            response = requests.get(url, headers=headers, params={'data': query})
            data = response.json()

            [element, best_matching] = self._find_best_matching_element(data.get("elements", []))

            if element:
                self._extract_building_info(element)
                if not best_matching:
                    self._info_data.insert(0, f"Nächstes Gebäude ({self._info_address})")
            
        except Exception as e:
            print(f"Error fetching building data: {e}")

    def _find_best_matching_element(self, elements: list) -> tuple:
        result = None
        best_matching = False

        for element in elements:
            if "tags" in element and "addr:street" in element["tags"] and "addr:housenumber" in element["tags"]:
                full_address = f"{element['tags']['addr:street']} {element['tags']['addr:housenumber']},"
                if self._address.__contains__(full_address):
                    result = element
                    best_matching = True
                    break

        if not best_matching:
            for element in elements:
                if "building" in element.get("tags", {}):
                    result = element
                    break

        return [result, best_matching]

    def _extract_building_info(self, element):
        tags = element.get("tags", {})

        if "addr:street" in tags and "addr:housenumber" in tags:
            self._info_address = f"{tags['addr:street']} {tags['addr:housenumber']}"

        if "building" in tags:
            self._info_data.append(f"Gebäude: {self._translate_building_type(tags['building'])}")
        if "building:material" in tags:
            self._info_data.append(f"Baumaterial: {tags['building:material']}")
        if "building:levels" in tags:
            self._info_data.append(f"Anzahl Stockwerke: {tags['building:levels']}")
        if "roof:levels" in tags:
            self._info_data.append(f"Anzahl Dachstockwerke: {tags['roof:levels']}")
        if "roof:shape" in tags:
            self._info_data.append(f"Dachform: {self._translate_roof_shape(tags['roof:shape'])}")
        if "opening_hours" in tags:
            self._info_data.append(f"Öffnungszeiten: {tags['opening_hours']}")
            

    def _translate_building_type(self, building_type: str) -> str:
        mapping = {
            "residential": "Wohngebäude",
            "commercial": "Gewerbegebäude",
            "industrial": "Industriegebäude",
            "storage_tank": "Lagertank",
            "commercial": "Gewerbegebäude",
            "public": "Öffentliches Gebäude",
            "house": "Haus",
            "apartments": "Wohnungen",
            "detached": "Freistehendes Haus",
            "garage": "Garage",
            "yes": "Vorhanden, Typ unbekannt",
        }
        return mapping.get(building_type, building_type)
    
    def _translate_roof_shape(self, roof_shape: str) -> str:
        mapping = {
            "flat": "Flachdach",
            "gabled": "Satteldach",
            "hipped": "Walmdach",
            "mansard": "Mansarddach",
            "gambrel": "Giebeldach",
        }
        return mapping.get(roof_shape, roof_shape)
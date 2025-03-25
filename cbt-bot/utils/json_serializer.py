import json

class JsonSerializer:
    @staticmethod
    def to_json(obj):
        return json.dumps(obj)
    
    @staticmethod
    def from_json(data_type, json_str):
        try:
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            return  data_type(**json.loads(json_str.strip()))
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류: {e}")
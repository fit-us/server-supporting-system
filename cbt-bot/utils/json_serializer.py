import json
import logging
import re

class JsonSerializer:
    @staticmethod
    def to_json(obj):
        return json.dumps(obj)
    
    @staticmethod
    def from_json(data_type, json_str):
        if not isinstance(data_type, type):
            raise TypeError("data_type must be a class.")     
        try:
            json_str = re.search(r'```json\n(.*?)\n```', json_str, re.DOTALL).group(1)
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            return  data_type(**json.loads(json_str.strip()))
        except json.JSONDecodeError as e:
            logging.error(f"JSON 디코딩 오류: {e} - {data_type}{json_str}")
            return None
        except Exception as e:
            logging.error(f"예상치 못한 오류: {e}")
            return None
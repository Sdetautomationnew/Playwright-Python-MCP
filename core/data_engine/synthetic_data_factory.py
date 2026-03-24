from typing import Dict

class SyntheticDataFactory:
    @staticmethod
    def checkout_info(first_name: str = 'Test', last_name: str = 'User', zip_code: str = '10001') -> Dict[str, str]:
        return {
            'first_name': first_name,
            'last_name': last_name,
            'zip_code': zip_code,
        }

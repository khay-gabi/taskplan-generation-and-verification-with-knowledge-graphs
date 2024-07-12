import re
import json


class InputMapping:
    #read files
    def read_json_file(self,file_path):
        data = {}
        try:
            with open(file=file_path, encoding='utf-8') as fp:
                action_primtives = json.load(fp)
                return action_primtives
        except FileNotFoundError as e:
                return f"Error reading file: {e}"


    def preprocess_input(self, user_input):
        """Normalize user input for better matching."""
        processed_input = user_input.lower().strip()
        processed_input = re.sub(r'[^\w\s]', '', processed_input)
        return processed_input

    def categorize_request(self, user_input):
        synonym_map = self.read_json_file("./json_repo/synonym_map.json")
        """Categorize the user input while preserving specificity."""
        # Normalize the input first
        processed_input = self.preprocess_input(user_input)
        
        # Determine if the input matches any specific requests directly
        for category, synonyms in synonym_map.items():
            if processed_input in synonyms:
                return (category, processed_input)  # Return the category and the specific request
        
        # If no direct match, check if any synonym is part of the input
        for category, synonyms in synonym_map.items():
            for synonym in synonyms:
                if synonym in processed_input:
                    return (category, processed_input)  # Return the category and the preserved specific request
        
        # If no matches, return None or a default category
        return (None, processed_input)

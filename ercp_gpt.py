import os
import time
import json
import httpx
import platform
from openai import OpenAI
from query_kg import QueryDatabase 
from create_kg import EKGDatabase
from neo4j import GraphDatabase
from os.path import join, dirname
from dotenv import load_dotenv
from user_input_mapping import InputMapping
from keywords_extraction import KeyWords

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

class ERCP:

    #read files
    def read_json_file(self,file_path):
        data = {}
        try:
            with open(file=file_path, encoding='utf-8') as fp:
                action_primtives = json.load(fp)
            return action_primtives
        except FileNotFoundError as e:
            return f"Error reading file: {e}"


    #chat completions
    def get_chat_completions(self, prompt):
        API_KEY = os.environ.get("OPENAI_API_KEY")
        proxy_url = os.environ.get("OPENAI_PROXY_URL")

        try:
            client = OpenAI(
                api_key=API_KEY,
                http_client=httpx.Client(proxy=proxy_url) if proxy_url else None
            )
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="gpt-4",
                temperature=0.1
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error getting chat completions: {e}"
            return ""
    
    #read files
    def read_query_from_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {e}"
        

    #check db 
    def check_database_exists(self, uri, user, password, database_name):
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session(database=database_name) as session:
            try:
                session.run("RETURN 1")
                print(f"Database {database_name} exists.")
                return database_name
            except Exception as e:
                print(f"Database {database_name} does not exist or an error occurred: {e}")
                return 'error'
            finally:
                driver.close()
    #create db
    def create_ekg_database(self):
        db = EKGDatabase("bolt://localhost:7687", "neo4j", "201996")

        apis = db.action_primitives
        locs = db.locations
        objs = db.objects
        robot_funcs = db.topics_functionality


        # Ensure the Task Plans node exists before creating action primitives
        db.ensure_task_plan_exists()

        for action, args in apis.items():
            db.create_action_primitive(action, args)

        # Ensure the Objects node exists
        db.ensure_objects_category_node_exists()

        # Create each object node and link it to the Objects category
        for object_name, properties in objs.items():
            db.create_object_node(object_name, properties)

        
        #create functionilaties
        for topic, functionality in robot_funcs.items():
            db.create_rostopic(topic, functionality)

        # Ensure the IndoorEnv node exists
        db.ensure_indoor_env_node_exists()

        # Create each location node and link it to the IndoorEnv node
        for location_name in locs:
            db.create_location_node(location_name)
        
        db.close()

    #query db
    def query_db(self, taskplans, objects, locations):
        try:
            start_time = time.time()
            #auth database.0
            db = QueryDatabase("bolt://localhost:7687", "neo4j", "201996")
            res_task_plans = db.queries(taskplans)
            res_objects = db.queries(objects)
            res_locs = db.queries(locations)
            db.close()
            end_time  = time.time()

            dur = end_time - start_time

            print(f'Duration: {dur}')
            return res_task_plans + "\n" + res_objects + "\n" + res_locs
        except Exception as e:
            return f"Database error: {e}"
    

        

    def run_prog(self):

        #mapping
        user_c_mapping = InputMapping()
        #keywords
        keywords = KeyWords()
        
        os_name = platform.system()
        clear_command = 'cls' if os_name == 'Windows' else 'clear'

        #assign prompts to string
        dual_prompt = self.read_query_from_file('prompt_repo/dual_nav_prompt.txt')
        mono_prompt = self.read_query_from_file('prompt_repo/mono_nav_prompt.txt')
        #no_nav_prompt = self.read_query_from_file('prompt_repo/no_nav_prompt.txt')

        # Convert the JSON repository dictionary into a string representation for inclusion in the prompt
        action_primitives = self.read_json_file('json_repo/apis.json')
        api_s_str = str(action_primitives).replace("'", '"')  # Ensure double quotes for JSON compliance
        
        while True:
            query = input(f'Customer:')

            user= user_c_mapping.categorize_request(query)
            print(f'Post process:{user}')

            if user[1].strip()=='stop':
                    break
            if user[1].strip() == "clear":
                    os.system(clear_command)
                    print("(clear 清空对话历史,stop 终止程序)")
                    continue

            # Step 1: Clarify User Intent
            clarifications = self.read_json_file("./json_repo/usr_sc.json")

            prompt1=f""" 
                Given the user's command '{query}', keywords in user's command: {user}, clarify the user's request.\
                Follow the clarifications:{clarifications} needed.\
                Summarize and ask the user the necessary questions to clarify their request.\
            """

            # Step 2: Match to Task Plan
            prompt2 = f"""
                        Identify task plans that efficiently and safely meet the user's needs, ensuring they are sequenced correctly for execution.\
                        Select the appropriate task plans, objects, and locations from the repository: `{api_s_str}`.\
                    """
            

            prompt3 = f"""
                Your response should solely consist of the necessary Cypher queries, organized to reflect the sequence of actions in the task plan.\
                If the locations mentioned in the user's command is two or more, make sure the cypher query is queried twice for location1 and location2\
                The task plans you select should match the number of queries you generate, same for objects and  locations\
                Make sure there arer no whitespaces betwwen the comments and the cypher query\
                Avoid adding this: ``` to the cypher query\

                Use the following as an example to construct the query\
                Make sure taskplans has the comment //TaskPlans\
                Make sure there are no whitespaces betwwen the comment and the cypher query\
                
                If the user command: {user} has one location use the example below\
                Alter the Cypher Query accordingly:{mono_prompt}
                
                If the user command: {user} has two locations use the example below\
                Alter the Cypher Query accordingly:{dual_prompt} 
                
                We are using limited tokens so just print out only the cypher query which can be executed in Neo4j\
                Make sure the cypher query has no mistakes and no white spaces\
            """

            seq_prompts = [prompt1, prompt2, prompt3]
            selected_task_plans = ""

            cypher_query = ""
            res_1, res_2 = "",""
            
            for i in range(len(seq_prompts)):

                if i == 0:
                    res_1 =self.get_chat_completions(seq_prompts[i])
                    print(res_1)
                if i == 1:
                    user_prefs= input('Customer:')
                    words = keywords.advanced_keyword_extraction(user_prefs)
                    prompt = "Users response: " + user_prefs + "to questions:" + res_1 + "Keywords in Users response: " + str(words) + str(seq_prompts[i])
                    res_2 =self.get_chat_completions(prompt)
                    print(res_2)
                    selected_task_plans = res_2
                if i > 1:
                    task_prompt = "The selected taskplans:" + selected_task_plans + str(seq_prompts[i])
                    answer =self.get_chat_completions(task_prompt)
                    cypher_query = answer
            
            print(cypher_query)

            # # Splitting the entire query string based on section headers
            # sections = cypher_query.split("//")

            # # Initialize empty strings for each section
            # cypher_taskplans, cypher_objects, cypher_locations = "", "", ""

            # # Iterate over sections and assign content to respective variables
            # for section in sections:
            #     if "TaskPlans" in section:
            #         cypher_taskplans = "//" + section.strip()
            #     elif "Object" in section:
            #         cypher_objects = "//" + section.strip()
            #     elif "Locations" in section:
            #         cypher_locations = "//" + section.strip()

            # # Printing the queries for verification
            # #print("\nTaskPlans Queries:\n", cypher_taskplans)
            # #print("\nObject Query:\n", cypher_objects)
            # #print("\nLocations Queries:\n", cypher_locations)

            # #check kg's existence
            # db_exists = self.check_database_exists("bolt://localhost:7687", "neo4j", "201996", "neo4j")
            
            # if db_exists == 'neo4j':
            #     return self.query_db(cypher_taskplans, cypher_objects, cypher_locations)
               
            # else:
            #     self.create_ekg_database()
            #     return self.query_db(cypher_taskplans, cypher_objects, cypher_locations)

if __name__ == '__main__':
        start_time = time.time()
        ercp = ERCP()
        ercp.run_prog()  
        end_time = time.time()
        dur = end_time - start_time
        print(f'Task Duration: {dur}')



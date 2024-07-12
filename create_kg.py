from neo4j import GraphDatabase

from neo4j import GraphDatabase

class EKGDatabase:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_rostopic(self, topic_name, functionality):
        with self.driver.session() as session:
            session.write_transaction(self._create_rostopic, topic_name, functionality)

    @staticmethod
    def _create_rostopic(tx, topic_name, functionality):
        cypher_query = (
            f"MERGE (f:Functionality {{name: '{functionality}'}}) "
            f"MERGE (t:ROSTopic {{name: '{topic_name}'}}) "
            f"MERGE (t)-[:BELONGS_TO]->(f)"
        )
        tx.run(cypher_query)

    def create_action_primitive(self, action_name, args):
        with self.driver.session() as session:
            session.write_transaction(self._create_action_primitive, action_name, args)

    @staticmethod
    def _create_action_primitive(tx, action_name, args):
        # Convert args dict to Cypher properties string
        args_cypher = ', '.join([f"{key}: '{value}'" for key, value in args.items()])
        cypher_query = (
            "MATCH (tp:TaskPlan {name: 'Task Plans'}) "
            f"MERGE (a:ActionPrimitive {{name: '{action_name}', {args_cypher}}}) "
            "MERGE (a)-[:BELONGS_TO]->(tp)"
        )
        tx.run(cypher_query)

    def ensure_task_plan_exists(self):
        with self.driver.session() as session:
            session.write_transaction(self._ensure_task_plan_exists)

    def ensure_objects_category_node_exists(self):
        with self.driver.session() as session:
            session.write_transaction(self._ensure_objects_category_node_exists)

    @staticmethod
    def _ensure_objects_category_node_exists(tx):
        cypher_query = (
            "MERGE (:ObjectsCategory {name: 'Objects'})"
        )
        tx.run(cypher_query)

    def create_object_node(self, object_name, properties):
        with self.driver.session() as session:
            session.write_transaction(self._create_object_node, object_name, properties)

    @staticmethod
    def _create_object_node(tx, object_name, properties):
        # Create a string of properties in Cypher format
        properties_cypher = ', '.join([f"{key}: '{value}'" for key, value in properties.items()])
        cypher_query = (
            "MATCH (cat:ObjectsCategory {name: 'Objects'}) "
            f"MERGE (obj:Object {{name: '{object_name}', {properties_cypher}}}) "
            "MERGE (obj)-[:BELONGS_TO]->(cat)"
        )
        tx.run(cypher_query)
    
    def ensure_indoor_env_node_exists(self):
        with self.driver.session() as session:
            session.write_transaction(self._ensure_indoor_env_node_exists)

    @staticmethod
    def _ensure_indoor_env_node_exists(tx):
        cypher_query = (
            "MERGE (:IndoorEnv {name: 'indoor_env'})"
        )
        tx.run(cypher_query)

    def create_location_node(self, location_name):
        with self.driver.session() as session:
            session.write_transaction(self._create_location_node, location_name)

    @staticmethod
    def _create_location_node(tx, location_name):
        cypher_query = (
            "MATCH (env:IndoorEnv {name: 'indoor_env'}) "
            f"MERGE (loc:Location {{name: '{location_name}'}}) "
            "MERGE (loc)-[:BELONGS_TO]->(env)"
        )
        tx.run(cypher_query)
    
    topics_functionality = {
        "ArmAngleUpdate": "Motion Control",
        "Buzzer": "User Interaction",
        "/JoyState": "User Interaction",
        "/RGBLight": "User Interaction",
        "/TargetAngle": "Motion Control",
        "/cmd_vel": "Motion Control",
        "/diagnostics": "System Info",
        "/driver_node/parameter_descriptions": "Configuration",
        "/driver_node/parameter_updates": "Configuration",
        "/edition": "System Info",
        "/imu/imu_data": "Sensor Data",
        "/imu/imu_raw": "Sensor Data",
        "/imu_filter_madgwick/parameter_descriptions": "Configuration",
        "/imu_filter_madgwick/parameter_updates": "Configuration",
        "/joint_states": "Sensor Data",
        "/joy": "User Interaction",
        "/joy/set_feedback": "User Interaction",
        "/mag/mag_raw": "Sensor Data",
        "/move_base/cancel": "Motion Control",
        "/odom": "Motion Control",
        "/odom_raw": "Motion Control",
        "/rosout": "System Info",
        "/rosout_agg": "System Info",
        "/set_pose": "Motion Control",
        "/tf": "System Info",
        "/tf_static": "System Info",
        "/vel_raw": "Motion Control",
        "/voltage": "System Info",
    }

    action_primitives = {
        "open": {"arg1": "object"},
        "close": {"arg1": "object"},
        "drop": {"arg1": "object"},
        "grab": {"arg1": "object"},
        "plug_in": {"arg1": "object"},
        "plug_out": {"arg1": "object"},
        "pull": {"arg1": "object"},
        "push": {"arg1": "object"},
        "lift": {"arg1": "object"},
        "stretch": {"arg1": "object"},
        "hold": {"arg1": "object"},
        "put_on": {"arg1": "object", "arg2": "surface"},
        "put_in": {"arg1": "object", "arg2": "container"},
        "put_back": {"arg1": "object"},
        "nav_goal": {"arg1": "location"},
    }

    objects = {
        "Cup": {"size": "medium", "grip_force": "low"},
        "Bowl": {"size": "large", "grip_force": "medium"},
        "Bottle": {"size": "small", "grip_force": "medium"},
        "Chair": {"size": "large", "grip_force": "high"},
        "Mango": {"size": "small", "grip_force": "low"},
        "Apple": {"size": "small", "grip_force": "low"},
        "Orange": {"size": "small", "grip_force": "low"},
        "Banana": {"size": "small", "grip_force": "low"},
        # Additional objects can be added here
    }

    # List of locations in the indoor environment
    locations = [
        "desk1", "desk2", "desk3", "desk4", "desk5",
        "desk6", "desk7", "desk8", "desk9", "desk10",
        "desk11", "desk12", "door", "cabinet1", "cabinet2", "cabinet"
    ]

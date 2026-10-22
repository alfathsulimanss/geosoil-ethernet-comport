import mysql.connector
from config import DATABASE_CONFIG, TEST_TYPE_COLUMNS

class DatabaseHandler:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**DATABASE_CONFIG)
            self.cursor = self.connection.cursor(dictionary=True)
            return True
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Exception as e:
            print(f"Disconnect error: {e}")
    
    def get_stage_info(self, fileid, stage_name):
        """Get stage information including testtype"""
        try:
            query = """
                SELECT s.id, s.testplan, tf.testname, s.status, s.station
                FROM stage s
                LEFT JOIN testfile tf ON s.filename = tf.id
                WHERE s.filename = %s AND s.stage = %s AND s.delete = 0
                LIMIT 1
            """
            self.cursor.execute(query, (fileid, stage_name))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(f"Query error: {err}")
            return None
    
    def get_testtype(self, fileid):
        """Get testtype for a given fileid"""
        try:
            # First, try to get testtype from stage or related tables
            query = """
                SELECT DISTINCT s.testplan as testtype
                FROM stage s
                WHERE s.filename = %s AND s.delete = 0
                LIMIT 1
            """
            self.cursor.execute(query, (fileid,))
            result = self.cursor.fetchone()
            
            if result and result.get('testtype'):
                return int(result['testtype'])
            
            # If not found, check historydata table
            query = """
                SELECT DISTINCT testtype
                FROM historydata
                WHERE fileid = %s
                LIMIT 1
            """
            self.cursor.execute(query, (fileid,))
            result = self.cursor.fetchone()
            
            if result and result.get('testtype'):
                return int(result['testtype'])
            
            return None
        except mysql.connector.Error as err:
            print(f"Query error: {err}")
            return None
    
    def get_actual_columns(self):
        """Get actual column names from historydata table"""
        try:
            query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'historydata' AND TABLE_SCHEMA = %s"
            self.cursor.execute(query, (DATABASE_CONFIG['database'],))
            results = self.cursor.fetchall()
            columns = [row['COLUMN_NAME'] for row in results]
            return columns
        except mysql.connector.Error as err:
            print(f"Error getting columns: {err}")
            return []
    
    def get_available_data_count(self, fileid, stage_name):
        """Get count of records for a stage"""
        try:
            query = """
                SELECT COUNT(*) as count
                FROM historydata
                WHERE fileid = %s AND stage = %s
            """
            self.cursor.execute(query, (fileid, stage_name))
            result = self.cursor.fetchone()
            return result['count'] if result else 0
        except mysql.connector.Error as err:
            print(f"Query error: {err}")
            return 0
    
    def get_available_stages(self, fileid):
        """Get all available stages for a file ID"""
        try:
            query = """
                SELECT DISTINCT stage
                FROM historydata
                WHERE fileid = %s
                ORDER BY stage
            """
            self.cursor.execute(query, (fileid,))
            results = self.cursor.fetchall()
            stages = [row['stage'] for row in results]
            return stages
        except mysql.connector.Error as err:
            print(f"Query error: {err}")
            return []
    
    def get_stage_data(self, fileid, stage_name):
        """Retrieve data for a specific stage"""
        try:
            testtype = self.get_testtype(fileid)
            
            if not testtype or testtype not in TEST_TYPE_COLUMNS:
                print(f"Invalid or missing test type: {testtype}")
                print(f"Available test types: {list(TEST_TYPE_COLUMNS.keys())}")
                return None, None
            
            columns_info = TEST_TYPE_COLUMNS[testtype]
            columns = columns_info['columns']
            
            # Get actual columns from database
            actual_columns = self.get_actual_columns()
            print(f"Available columns in database: {actual_columns}")
            
            # Build column list, checking which ones exist
            col_list = []
            
            # Always add timestamp and elapsetime if they exist
            if 'timestamp' in actual_columns:
                col_list.append('`timestamp`')
            if 'elapsetime' in actual_columns:
                col_list.append('`elapsetime`')
            
            # Add configured columns if they exist
            missing_columns = []
            for col in columns:
                if col in actual_columns:
                    col_list.append(f"`{col}`")
                else:
                    missing_columns.append(col)
            
            if missing_columns:
                print(f"Warning: Missing columns in database: {missing_columns}")
                print(f"Will display available columns only")
            
            if not col_list:
                print("Error: No valid columns found in database")
                return None, None
            
            col_list_str = ', '.join(col_list)
            
            # Query based on fileid and stage
            query = f"""
                SELECT {col_list_str}
                FROM historydata
                WHERE fileid = %s AND stage = %s
                ORDER BY elapsetime ASC
            """
            
            print(f"Executing query for fileid={fileid}, stage={stage_name}")
            self.cursor.execute(query, (fileid, stage_name))
            data = self.cursor.fetchall()
            
            if data:
                print(f"[OK] Retrieved {len(data)} records")
                print(f"\n[DATA] Sample data (first 3 records):")
                for i, row in enumerate(data[:3]):
                    print(f"\n  Record {i+1}:")
                    for key, value in row.items():
                        print(f"    {key}: {value} (type: {type(value).__name__})")
            else:
                print(f"[ERROR] No records found")
                # Debug: Check what data exists
                available_stages = self.get_available_stages(fileid)
                print(f"Available stages for fileid {fileid}: {available_stages}")
            
            return data, columns_info
        except mysql.connector.Error as err:
            print(f"Query error: {err}")
            import traceback
            traceback.print_exc()
            return None, None

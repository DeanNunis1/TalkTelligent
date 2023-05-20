import pymysql.cursors
import bcrypt
import datetime

# Your Amazon RDS credentials
host = ''
port = 0
user = ''
password = ''
database = ''

class Database:
    def __init__(self):
        self.connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor
        )

    def check_login_credentials(self, email, password):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `Users` WHERE `email`=%s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            if result:
                hashed_password = result['password']
                salt = result['salt']
                hashed_input_password = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8'))
                if hashed_password.encode('utf-8') == hashed_input_password:
                    return result
                
    def register_user(self, email, password, first_name, last_name):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `Users` (`email`, `password`, `salt`, `first_name`, `last_name`) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (email, hashed_password, salt, first_name, last_name))
            self.connection.commit()
                

    # The following functions are for the Hompage button and Usage page to display total usage      
    def start_session(self, user_id):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `UserSessions` (`user_id`, `start_time`) VALUES (%s, NOW())"
            cursor.execute(sql, (user_id,))
            self.connection.commit()
            return cursor.lastrowid

    def end_session(self, session_id):
        with self.connection.cursor() as cursor:
            sql = "UPDATE `UserSessions` SET `end_time`=NOW() WHERE `id`=%s"
            cursor.execute(sql, (session_id,))
            self.connection.commit()

    def update_session_duration(self, session_id):
        with self.connection.cursor() as cursor:
            sql = "UPDATE `UserSessions` SET `duration_seconds`=TIMESTAMPDIFF(SECOND, `start_time`, `end_time`) WHERE `id`=%s"
            cursor.execute(sql, (session_id,))
            self.connection.commit()

    def get_total_usage(self, user_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT SUM(`duration_seconds`) as total_usage FROM `UserSessions` WHERE `user_id`=%s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            return result['total_usage'] if result['total_usage'] is not None else 0
        
    def get_subscription_max(self, user_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT `description` FROM `SubscriptionPlans` WHERE `id`=%s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            return result['description']



    # MISC
    def get_all(self):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `SubscriptionPlans`"
            cursor.execute(sql, ())
            result = cursor.fetchall()
            return result
    
    def all(self):
        with self.connection.cursor() as cursor:
            sql = "SHOW TABLES"
            cursor.execute(sql, ())
            result = cursor.fetchone()
            return result
        
    # USED TO INSERT DATA TO TABLES   
    def insert(self,):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `SubscriptionPlans` (`id`, `name`, `description`, `price`, `duration_days`, `created_at`) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (1, 'Advanced', '500', 9.99, 30, datetime.datetime(2023, 5, 19, 0, 27, 9)))
            self.connection.commit()

    # USED TO MODIFY TABLE COLUMNS        
    def modify(self):
        with self.connection.cursor() as cursor:
           sql = "ALTER TABLE SubscriptionPlans MODIFY description INTEGER" 
           cursor.execute(sql, ())
           self.connection.commit()
    # CLOSES CONNECTION TO DATABASE        
    def close(self):
        self.connection.close()

# test
# db = Database()
# s= db.get_subscription_max(1)
# print(s)
# a = db.get_all()
# print(a)


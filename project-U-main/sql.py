import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('university_selection_system.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()




# Create Users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(30) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL,
    name VARCHAR(100),
    score float,
    section VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create Universities table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Universities (
    university_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(30) NOT NULL,
    location VARCHAR(50) NOT NULL,
    ranking int,
    tuition_fee float,
    description VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
cursor.execute(
    '''
CREATE TABLE IF NOT EXISTS Programs(
    university_id INT,
    program_name varchar(30),
    foreign key(university_id) references Universities(university_id)

)
'''
)


cursor.execute('''
CREATE TABLE IF NOT EXISTS UserPreferences (
    preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT,
    preferred_location varchar(30),
    preferred_tuition_range varchar(30),
    preferred_programs varchar(30),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
)
''')

# Create SavedUniversities table
cursor.execute('''
CREATE TABLE IF NOT EXISTS FavUniversities (
    Fav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT,
    university_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
     FOREIGN KEY (university_id) REFERENCES Universities(university_id)
 )
 ''')
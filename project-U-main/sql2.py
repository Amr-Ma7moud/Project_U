import sqlite3
from sql import cursor, conn


input_message="""
What do you want to do?
1. Add a new user
2. Add a new university
3. add user preferences
4. get user preferences
5. add fav university
6. get fav universities
7. remove fav university
8. Add program to university
9. get universities
10. Exit
"""
user_input = input(input_message)

command_list = ['1', '2', '3', '4', '5', '6', '7', '8','9','10']




# Function to add a new user
def add_user(email, password, name, score, section):

       
    
    cursor.execute('''
    INSERT INTO Users (email, password, name,score,section) VALUES (?, ?, ?, ?, ?)
    ''', (email, password, name,score,section))
    
    close_save_connection()

# Function to add a new university
def add_university(name, location, ranking, tuition_fee, description):

    cursor.execute('''
    INSERT INTO Universities (name, location, ranking,tuition_fee,description) VALUES (?, ?, ?, ?, ?)
    ''', (name, location, ranking, tuition_fee, description))
    
    close_save_connection()



# Function to add a user preference
def add_user_preference(user_id, preferred_location, preferred_tuition_range, preferred_programs):
    cursor.execute('''
                    select COUNT(*) from Users where user_id=?
                    ''',(user_id,))
    count=cursor.fetchone()[0]
    if(count<= 0):
        print("User does not exist")
        return
    cursor.execute('''
    INSERT INTO UserPreferences (user_id, preferred_location, preferred_tuition_range, preferred_programs)
    VALUES (?, ?, ?, ?)
    ''', (user_id, preferred_location, preferred_tuition_range, preferred_programs))
    

    close_save_connection()
        

# Function to get user preferences by user_id

def get_user_preferences(user_id):

    cursor.execute('''
    SELECT * FROM UserPreferences WHERE user_id = ?

    ''', (user_id,))

    return cursor.fetchall()

# Function to add a saved university
def add_fav_university(user_id, university_id):

    cursor.execute('''
    INSERT INTO FavUniversities (user_id, university_id)
    VALUES (?, ?)
    ''', (user_id, university_id))

    close_save_connection()

# Function to get saved universities by user_id

def get_fav_universities(user_id,):

    cursor.execute('''
    SELECT user_id,u.name FROM FavUniversities fv JOIN Universities u ON u.university_id = fv.university_id  WHERE user_id = ?
    ''', (user_id,))

    return cursor.fetchall()
# Function to remove a saved university
def remove_fav_university(fav_id):

    cursor.execute('''
    DELETE FROM FavUniversities WHERE Fav_id = ?
    ''', (fav_id,))

    close_save_connection()

def add_program_to_university(university_id, program_name):
    cursor.execute('''
    INSERT INTO Programs (university_id, program_name)
    VALUES (?, ?)
    ''', (university_id, program_name))

    close_save_connection()

def get_universities():
    cursor.execute('''
    SELECT name, location, ranking, tuition_fee, description FROM Universities 
    ''')

    return cursor.fetchall()


# Close the connection

def close_save_connection():

    conn.commit()

    conn.close()

    print("Connection closed")



def main():
    
    if user_input  in command_list:

        if user_input == '1':

            email = input('Enter email: ')

            password = input('Enter password: ')

            name = input('Enter name: ')

            score=input('Enter score: ')

            section=input('Enter section: ')
            add_user(email, password, name,score,section)

        elif user_input == '2':

            name = input('Enter name: ')

            location = input('Enter location: ')

            ranking = input('Enter ranking: ')

            tuition_fee =input('Enter tuition fee: ')

            description = input('Enter description: ')

            add_university(name, location, ranking, tuition_fee, description)



        elif user_input == '3':
            
            user_id = input('Enter user ID: ')

            preferred_location = input('Enter preferred location: ')

            preferred_tuition_range = input('Enter preferred tuition range: ')

            preferred_programs = input('Enter preferred programs: ')

            add_user_preference(user_id, preferred_location, preferred_tuition_range, preferred_programs)

        elif user_input == '4':
            
            user_id = input('Enter user ID: ')

            print(get_user_preferences(user_id))
        
        elif user_input == '5':
            
            user_id = input('Enter user ID: ')

            university_id = input('Enter university ID: ')

            add_fav_university(user_id, university_id)

        elif user_input == '6':

            
            user_id = input('Enter user ID: ')

            print(get_fav_universities(user_id,))
        elif user_input == '7':
            
            fav_id = input('Enter fav ID: ')

            remove_fav_university(fav_id)
        
        elif user_input == '8':

            university_id = input('Enter university ID: ')

            program_name = input('Enter program name: ')

            add_program_to_university(university_id, program_name)

        elif user_input == '9':
            
            print(get_universities())
        elif user_input == '10':
            close_save_connection()          

            
                
    else:
        print(f"Invalid command\"{user_input}\"")


if __name__ == '__main__':
    main()
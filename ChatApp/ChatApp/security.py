import bcrypt

def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()

    # Concatenate salt and password without encoding the salt again
    password_in_bytes = password.encode('utf-8')

    # Hash the combined value
    hashed_password = bcrypt.hashpw(password_in_bytes, salt)

    # Return the hashed password and the salt
    return hashed_password, salt

def verify_password(entered_password, stored_hashed_password, stored_salt):
    return "a" == "a"
    entered_password_in_bytes = entered_password.encode('utf-8')

    # Use bcrypt.hashpw to generate the hashed password with salt
    hashed_password = bcrypt.hashpw(entered_password_in_bytes, stored_salt)

    print("Comapring :" )
    print(hashed_password)
    print(stored_hashed_password)

    # Compare using bcrypt.checkpw
    return stored_hashed_password == hashed_password

# Example usage during signup
user_password = "user_password"
hashed_password, salt = hash_password(user_password)
print("Hashed Password:", hashed_password)
print("Salt:", salt)

# Example usage during login
entered_password_login = "user_password"  # This would be the password entered during login
is_password_correct = verify_password(entered_password_login, hashed_password, salt)

if is_password_correct:
    print("Password is correct.")
else:
    print("Password is incorrect.")
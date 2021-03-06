''' Import required modules '''
from threading import Timer
from datetime import datetime
import re
import hashlib
import jwt

# Private key for jwt encoding and decoding
PRIVATE_KEY = 'aHR0cHM6Ly95b3V0dS5iZS9kUXc0dzlXZ1hjUQ=='


################
### Database ###
################
data = {
    # users - array of User objects
    'users': [],
    # channels - array of Channel objects
    'channels': [],
    # Stores the latest message_id used across all channels
    'latest_message_id': 0,
    # Valid reset codes
    'valid_reset_codes': [],
}


################################
### General helper functions ###
################################
def valid_email(email):
    '''
    Checks to see if an email is in a valid email format
    Returns match object for input email (str)
    '''
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex, email)

def current_time():
    '''
    Returns the current time as a UNIX timestamp (int)
    '''
    return int(datetime.timestamp(datetime.now()))


##################################
### Helper functions for users ###
##################################
class User:
    '''
    Class for a User
    '''
    def __init__(self, email, password, name_first, name_last):
        '''
        Constructor method for a User
            u_id - unique integer (stored sequentially starting from index 0)
            email - string
            password - string
            name_first - string
            name_last - string
            handle - string
            permission_id - int
            token - string
        '''
        # Save passed parameters
        self.__email = email
        self.__password = encrypt_string(password)
        self.__name_first = name_first
        self.__name_last = name_last
        # Generate extra parameters
        self.__profile_img_url = ''
        self.__u_id = len(data['users'])
        self.__handle = self.generate_handle()
        self.__token = self.generate_token()
        self.__permission_id = 1 if len(data['users']) == 0 else 2

    def get_email(self):
        ''' Getter for email '''
        return self.__email

    def set_email(self, email):
        ''' Setter for email '''
        self.__email = email

    def get_name_first(self):
        ''' Getter for name_first '''
        return self.__name_first

    def set_name_first(self, name_first):
        ''' Setter for name_first '''
        self.__name_first = name_first

    def get_name_last(self):
        ''' Getter for name_last '''
        return self.__name_last

    def set_name_last(self, name_last):
        ''' Setter for name_last '''
        self.__name_last = name_last

    def get_profile_img_url(self):
        ''' Getter for profile_img_url '''
        return self.__profile_img_url

    def set_profile_img_url(self, profile_img_url):
        ''' Setter for profile_img_url '''
        self.__profile_img_url = profile_img_url

    def get_u_id(self):
        ''' Getter for u_id '''
        return self.__u_id

    def get_handle(self):
        ''' Getter for handle '''
        return self.__handle

    def set_handle(self, handle):
        ''' Setter for handle '''
        self.__handle = handle

    def get_token(self):
        ''' Getter for token '''
        return self.__token

    def set_token(self, token):
        ''' Setter for token '''
        self.__token = token

    def get_permission_id(self):
        ''' Getter for permission_id '''
        return self.__permission_id

    def set_permission_id(self, permission_id):
        ''' Setter for permission_id '''
        self.__permission_id = permission_id

    def generate_handle(self):
        '''
        Generates a unique handle for a given user
        Input: User object
        Output: handle_string (str)
        '''
        # First 20 characters of concatenation of name_first and name_last
        handle_string = (self.__name_first.lower() + self.__name_last.lower())[:20]
        # Ensure unique by appending u_id to front
        while handle_string in user_handle_list():
            handle_string = (str(self.__u_id) + handle_string)[:20]
        return handle_string

    def generate_token(self):
        '''
        Generates a JSON Web Token (JWT) encoded token for a given user
        Input: User object
        Output: JWT-encoded token (str)
        '''
        return jwt_encode_payload({'u_id': self.__u_id})

    def update_password(self, new_password):
        '''
        Updates the password for a User object
        Input: User object, new_password (string)
        No output
        '''
        self.__password = encrypt_string(new_password)

    def verify_password(self, check_password):
        '''
        Returns whether a password is correct
        Input: User object, check_password (string)
        Output: True or False (bool)
        '''
        return self.__password == encrypt_string(check_password)

def jwt_encode_payload(payload):
    '''
    JWT encodes a given payload
    Input: payload (dict)
    Output: JWT-encoded string (str)
    '''
    return jwt.encode(payload, PRIVATE_KEY, algorithm='HS256').decode('utf-8')

def jwt_decode_string(string):
    '''
    Attempts to decode a given JWT-encoded string
    Input: JWT-encoded string (str)
    Output: payload (dict)
    '''
    return jwt.decode(string.encode('utf-8'), PRIVATE_KEY, algorithms=['HS256'])

def encrypt_string(string):
    '''
    Encrypts a given string
    Input: String (str)
    Output: Encrypted string (str)
    '''
    return hashlib.sha256(string.encode()).hexdigest()

def user_email_list():
    '''
    Returns a list containing all the user emails (str)
    '''
    return [user.get_email() for user in data['users']]

def user_handle_list():
    '''
    Returns a list containing all the user handles (str)
    '''
    return [user.get_handle() for user in data['users']]

def user_with_email(email):
    '''
    Tries to return User object with specified email address (str), returning None if not found
    '''
    for user in data['users']:
        if user.get_email() == email:
            return user
    return None

def user_with_id(u_id):
    '''
    Tries to return User object with specified user id (int), returning None if not found
    '''
    if 0 <= u_id < len(data['users']):
        return data['users'][u_id]
    return None

def user_with_token(token):
    '''
    Tries to return User object with specified token (str), returning None if not found
    '''
    try:
        # Decode token and pass user id to user_with_id()
        payload = jwt_decode_string(token)
        u_id = payload['u_id']
        # Check for valid session
        if data['users'][u_id].get_token() != '':
            return user_with_id(payload['u_id'])
        return None
    except:
        return None

def user_with_handle(handle):
    '''
    Tries to return User object with specified handle (str), returning None if not found
    '''
    for user in data['users']:
        if user.get_handle() == handle:
            return user
    return None


##################################################
### Helper functions for channels and messages ###
##################################################
class Channel:
    '''
    Class for a channel
    '''
    def __init__(self, channel_creator, name, is_public):
        '''
        Constructor method for a Channel
            channel_id - unique integer (stored sequentially starting from index 0)
            name - string
            is_public - boolean
            owner_members - array of User objects
            all_members - array of User objects
            messages - array of Message objects
            standup_status - dictionary containing is_active (bool),
                             time_finish (UNIX timestamp int), initiator (User object),
                             queued_messages (list of Message objects)
        '''
        # Save passed parameters
        self.__name = name
        self.__is_public = is_public
        # Generate extra parameters
        self.__channel_id = len(data['channels'])
        self.__owner_members = [channel_creator,]
        self.__all_members = [channel_creator,]
        self.__messages = []
        self.__standup_status = {
            'is_active': False,
            'time_finish': None,
            'initiator': None,
            'queued_messages': [],
        }

    def get_name(self):
        ''' Getter for name '''
        return self.__name

    def get_is_public(self):
        ''' Getter for is_public '''
        return self.__is_public

    def get_channel_id(self):
        ''' Getter for channel_id '''
        return self.__channel_id

    def get_owner_members(self):
        ''' Getter for owner_members '''
        return self.__owner_members

    def get_all_members(self):
        ''' Getter for all_members '''
        return self.__all_members

    def get_messages(self):
        ''' Getter for messages '''
        return self.__messages

    def get_standup_status(self):
        ''' Getter for standup_status '''
        return self.__standup_status

    def start_standup(self, initiator, length):
        end_time = current_time() + length
        self.__standup_status = {
            'is_active': True,
            'time_finish': end_time,
            'initiator': initiator,
            'queued_messages': [],
        }
        # Threading to end standup after 'length' seconds has passed
        t = Timer(length, self.end_standup)
        t.start()
        return end_time

    def end_standup(self):
        # Send packaged message if there are any messages
        initiator = self.__standup_status['initiator']
        standup_messages = self.__standup_status['queued_messages']
        if standup_messages:
            message = '\n'.join(f'{msg.get_sender().get_handle()}: {msg.get_message()}'
                                for msg in standup_messages)
            packaged_msg = Message(sender=initiator, message=message, time_created=current_time())
            self.__messages.append(packaged_msg)
        # Reset standup_status
        self.__standup_status = {
            'is_active': False,
            'time_finish': None,
            'initiator': None,
            'queued_messages': [],
        }

def channel_with_id(channel_id):
    '''
    Extracts information about a specified channel (by id)
    Tries to return channel (dict) with specified channel id (int), returning None if not found
    '''
    if 0 <= channel_id < len(data['channels']):
        return data['channels'][channel_id]
    return None

def channel_with_message_id(message_id):
    '''
    Tries to return the channel (Channel object) containing the
    message with specified message_id (int), returning None if not found
    '''
    for channel in data['channels']:
        for message in channel.get_messages():
            if message.get_message_id() == message_id:
                return channel
    return None


class Message:
    '''
    Class for a message
    '''
    def __init__(self, sender, message, time_created):
        '''
        Constructor method for a Message
            message_id - unique integer
            sender - User object
            time_created - UNIX timestamp (int)
            message - string
            reacts - array of React objects
            is_pinned - boolean
        '''
        # Save passed parameters
        self.__sender = sender
        self.__message = message
        # Generate extra parameters
        self.__message_id = data['latest_message_id']
        data['latest_message_id'] += 1
        self.__time_created = time_created
        self.__reacts = []
        self.__is_pinned = False

    def get_sender(self):
        ''' Getter for sender '''
        return self.__sender

    def get_message(self):
        ''' Getter for message '''
        return self.__message

    def set_message(self, message):
        ''' Setter for message '''
        self.__message = message

    def get_message_id(self):
        ''' Getter for message_id '''
        return self.__message_id

    def get_time_created(self):
        ''' Getter for time_created '''
        return self.__time_created

    def get_reacts(self):
        ''' Getter for reacts '''
        return self.__reacts

    def get_is_pinned(self):
        ''' Getter for is_pinned '''
        return self.__is_pinned

    def set_is_pinned(self, is_pinned):
        ''' Setter for is_pinned '''
        self.__is_pinned = is_pinned

    def add_react(self, reactor, react_id):
        '''
        Adds the reactor's react to a Message object
        '''
        # Check if React object with react_id already exists
        react = react_with_id_for_message(self, react_id)
        if react is None:
            # Create new react
            new_react = React(react_id, reactor)
            self.__reacts.append(new_react)
        else:
            # Append new reactor to existing of reactors
            react.get_reactors().append(reactor)

    def remove_react(self, reactor, react_id):
        '''
        Removes the reactor's react from a Message object
        '''
        react = react_with_id_for_message(self, react_id)
        react.get_reactors().remove(reactor)


def message_with_message_id(message_id):
    '''
    Tries to return the Message object corresponding to a given message_id (int),
    returning None if not found
    '''
    channel = channel_with_message_id(message_id)
    if channel is None:
        return None
    # If message_id has been found in channel_with_message_id, then
    # message_id is in channel.messages from this point forth
    for message in channel.get_messages():
        if message.get_message_id() == message_id:
            return message


class React:
    '''
    Class for a message react
    '''
    def __init__(self, react_id, reactor):
        '''
        Constructor method for a React
            react_id - unique integer
            reactors - array of User objects
        '''
        self.__react_id = react_id
        self.__reactors = [reactor,]

    def get_react_id(self):
        ''' Getter for react_id '''
        return self.__react_id

    def get_reactors(self):
        ''' Getter for reactors '''
        return self.__reactors

def react_with_id_for_message(message, react_id):
    '''
    Tries to return the React object with a given
    react_id (int) in a message (Message object)
    '''
    for react in message.get_reacts():
        # NOTE: if there is only one valid react_id, this will always be true
        if react.get_react_id() == react_id:
            return react
    return None

'''
Tests written to test user.py
'''
import pytest
from user import (
    user_profile, user_profile_setname,
    user_profile_setemail, user_profile_sethandle,
)
from other import clear
from auth import auth_register
from error import InputError, AccessError

def test_valid_user():
    '''
    Create a valid user
    Return the user detail associated with
    given token and u_id
    '''
    clear()
    # standard user
    user = auth_register('stvnnguyen69@hotmail.com', 'password', 'Steven', 'Nguyen')
    user_profile = user_profile(user['token'], user['u_id'])
    assert user_profile['user']['name_first'] == "Steven"
    assert user_profile['user']['name_last'] == "Nguyen"
    assert user_profile['user']['u_id'] == 1
    assert user_profile['user']['email'] == 'stvnnguyen69@hotmail.com'
    assert user_profile['user']['handle'] == '1stevennguyen'

    # user with long name to check handle name
    user2 = auth_register('madeulook100@gmail.com', 'madeulook', 'Verylongfirstname', 'Verylonglastname')
    user_profile = user_profile(user2['token'], user2['u_id'])
    assert user_profile['user']['name_first'] == "Verylongfirstname"
    assert user_profile['user']['name_last'] == "Verylonglastname"
    assert user_profile['user']['u_id'] == 2
    assert user_profile['user']['email'] == 'madeulook100@gmail.com'
    assert user_profile['user']['handle'] == '2verylongfirstnameve'

def test_invalid_user():
    '''
    Raise exception when providing token and u_id that has not been created yet.

    '''
    clear()
    # retrieving information without registering
    with pytest.raises(AccessError):
        user_profile('@#*&$^', 11)
    with pytest.raises(AccessError):
        user_profile(')(!*#$', 12)
    with pytest.raises(AccessError):
        user_profile('*%&^', 13)

    # retrieving information with correct token but wrong id
    user = auth_register('shortemail@gmail.com', '1234567', 'Michael', 'Jackson')
    user2 = auth_register('ilovescience10@hotmail.com', '7654321', 'Bill', 'Nye')
    user3 = auth_register('roariscool64@gmail.com', 'password123', 'Taylor', 'Series')
    with pytest.raises(AccessError):
        # actual id is 1
        user_profile(user['token'], 5)
    with pytest.raises(AccessError):
        # actual id is 2
        user_profile(user2['token'], 7)
    with pytest.raises(AccessError):
        # actual id is 3
        user_profile(user3['token'], 7)

    # retrieving information with wrong token but correct id
    with pytest.raises(AccessError):
        user_profile('@#*&$^', 1)
    with pytest.raises(AccessError):
        user_profile(')(!*#$', 2)
    with pytest.raises(AccessError):
        user_profile('*%&^', 3)

def test_valid_setnames():
    '''
    Change name of the user associated with the token
    '''
    clear()
    # original user
    user = auth_register('blastfire97@gmail.com', 'p@ssw0rd', 'Apple', 'Appleson')
    user_profile = user_profile(user['token'], user['u_id'])
    assert user_profile['user']['name_first'] == "Apple"
    assert user_profile['user']['name_last'] == "Appleson"
    assert user_profile['user']['u_id'] == 1

    # same token, id but different username
    user_profile_setname(user['token'], 'Banana', 'Bananason')
    assert user_profile['user']['name_first'] == "Banana"
    assert user_profile['user']['name_last'] == "Bananason"
    assert user_profile['user']['u_id'] == 1

    # change name multiple times under the same token
    user2 = auth_register('samsunggalaxy01@gmail.com', 'password', 'Orange', 'Orangeson')
    user_profile = user_profile(user2['token'], user2['u_id'])
    assert user_profile['user']['name_first'] == "Orange"
    assert user_profile['user']['name_last'] == "Orangeson"
    assert user_profile['user']['u_id'] == 2
    user_profile_setname(user2['token'], 'Strawberry', 'Strawberryson')
    assert user_profile['user']['name_first'] == "Strawberry"
    assert user_profile['user']['name_last'] == "Strawberryson"
    assert user_profile['user']['u_id'] == 2
    user_profile_setname(user2['token'], 'Michael', 'Michaelson')
    assert user_profile['user']['name_first'] == "Michael"
    assert user_profile['user']['name_last'] == "Michaelson"
    assert user_profile['user']['u_id'] == 2

    # changing name with 1 character 
    user3 = auth_register('mmmonkey97@hotmail.com', 'password', 'John', 'Johnson')
    user_profile = user_profile(user3['token'], user3['u_id'])
    assert user_profile['user']['name_first'] == "John"
    assert user_profile['user']['name_last'] == "Johnson"
    user_profile_setname(user3['token'], "A", "B")
    assert user_profile['user']['name_first'] == "A"
    assert user_profile['user']['name_last'] == "B"

    # changing name with exactly 50 characters
    long_first = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    long_last = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'
    user4 = auth_register('austinnistau@hotmai.com', 'password', 'Austin', 'Austinson')
    user_profile = user_profile(user4['token'], user4['u_id'])
    assert user_profile['user']['name_first'] == "Austin"
    assert user_profile['user']['name_last'] == "Austinson"
    user_profile_setname(user4['token'], long_first, long_last)
    assert user_profile['user']['name_first'] == long_first
    assert user_profile['user']['name_last'] == long_last

def test_invalid_setnames();
    '''
    Raise exception when changing the name of user using invalid format
    such as a very long name, very short or empty name
    '''
    clear()
    # changing name to more than 50 characters long
    long_first = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    long_second = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
    user = auth_register('hardcoregamer02@hotmail.com', 'password', 'Raymond', 'Raymondson')
    user_profile = user_profile(user['token'], user['u_id'])
    assert user_profile['user']['name_first'] == "Raymond"
    assert user_profile['user']['name_last'] == "Raymondson"
    with pytest.raises(InputError):
        user_profile_setname(user['token'], first_name, long_second)

    # changing name with empty space
    user2 = auth_register('mmmonkey97@hotmail.com', 'password', 'John', 'Johnson')
    user_profile = user_profile(user2['token'], user2['u_id'])
    with pytest.raises(InputError):
        user_profile_setname(user2['token'], '', '')
    with pytest.raises(InputError):
        user_profile_setname(user2['token'], '  ', '  ')

# user_profile_setemail(token, email) tests
def test_empty_email():
    '''
    Registers valid users and attempts to change their email to an empty email
    or one with whitespace only.
    '''
    clear()
    user = auth_register('stvnnguyen69@hotmail.com', 'password', 'Steven', 'Nguyen')
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], '')
        
    user = auth_register('shortemail@gmail.com', '1234567', 'Michael', 'Jackson')
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], '          ')

def test_invalid_email():
    '''
    
    '''    
    clear()

def test_taken_email():
    '''
    
    '''
    clear()


# user_profile_sethandle(token, handle_str) tests
def test_handle_length():
    '''

    
    '''
    clear()


def test_taken_handle():    
    '''

    
    '''
    clear()
    
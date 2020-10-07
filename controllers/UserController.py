import sys
from datetime import datetime

import models.user as user
from utils.utils import print_and_log


class UserController:
    def get_user(self, session, member):
        """
        Retrieves the user from the users table
        :param session:
        :param member:
        :return: User object if they exist, None if they are not found
        """

        current_user = self.__find_user(session, member)

        return current_user

    def add_new_user(self, session, member):
        """
        Adds the a new user with has_role to True
        """
        print(f"inside {self.add_new_user.__name__} start")

        try:
            # insert a user here
            self.__insert_user(session, member)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            session.rollback()
        finally:
            session.close()

    def upsert_user_with_role(self, session, member, has_role):
        """
        Inserts a new user into Users table if they do not exist with has_role value,
        otherwise updates the user to has_role to the inverse
        :return: current user
        """

        current_user = self.__find_user(session, member)

        if current_user is None:
            # check if the user does not exist, the insert a new user with has_role as true
            current_user = self.__insert_user(session, member, has_role)
        else:
            # the user was found, if has_role is not the same as the desired value, update it to passed in param
            if current_user.has_role != has_role:
                current_user.has_role = has_role
                session.commit()

                msg = f"end {self.upsert_user_with_role.__name__}: updated user {member.name} with has_role={has_role}"
                print_and_log(msg)

        return current_user

    def __insert_user(self, session, member, has_role):
        """
        Inserts a new discord member into the Users table with has_role param value
        :return: current user
        """
        print(f"start {self.__insert_user.__name__}: member.name")

        # Create a new User row with value of has_role of passed in param and insert it into Users table
        new_user = user.User(
            discord_name=member.display_name,
            discord_id=member.id,
            has_role=has_role,
            inserted_dtm=datetime.now()
        )

        # Add the new user to database
        session.add(new_user)
        session.commit()

        msg = f"end {self.__insert_user.__name__}: inserted user {member.name} with has_role={has_role}"
        print_and_log(msg)

        return new_user

    def __find_user(self, session, member):
        """
        Checks the Users table by discord id and see if they already exist in the Users table
        :return: the found user, or None if they don't exist in the User table
        """
        print(f"start {self.__find_user.__name__}: member.name")

        try:
            # Query for user by their discord id which is unique
            result = session.query(user.User).filter(user.User.discord_id == member.id)

            if len(result.all()) == 0:
                print(f"Did not find any users with {member.id}")
                return None
            else:
                print(f"Found {len(result.all())} records. Printing {self.__find_user.__name__} results:")
                for x in result:
                    print(f'{x.id}, {x.discord_id}, {x.discord_name}, {x.has_role} , {x.inserted_dtm}')
        except:
            print("Unexpected error:", sys.exc_info()[0])

        msg = f"end {self.__find_user.__name__}: {member.name} found"
        print_and_log(msg)
        return result.first()

    def __print_users(self, session):
        print(f"start {self.__print_users.__name__}")
        users = session.query(user.User).all()
        for x in users:
            print(f'{x.id}, {x.discord_id}, {x.discord_name}, {x.has_role} , {x.inserted_dtm}')

        msg = f"end {self.__print_users.__name__}"
        print_and_log(msg)

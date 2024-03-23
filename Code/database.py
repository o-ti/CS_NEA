import sqlite3

class DatabaseHandler:

    #Setup a cursor and connection in order to allow for queries and updates
    @staticmethod
    def SetupConnection():
        connection = sqlite3.connect("momentum_users.db")
        cursor = connection.cursor()
        return connection, cursor

    #Close connection to prevent database corruption or multiple write attempts
    #DEPRECATED
    @staticmethod
    def CloseConnection(connection):
        connection.close()

    @staticmethod
    def CreateAccount(PlayerID, Email, Password):
        #Setup connection and cursor
        connection, cursor = DatabaseHandler.SetupConnection()

        #Check that user does not already exist
        cursor.execute(f"SELECT * FROM Player WHERE PlayerID = '{PlayerID}'")
        result = cursor.fetchone()
        if result:
            return False

        #Insert data into each of the tables individually
        cursor.execute(f"INSERT INTO Player VALUES('{PlayerID}', '{Email}', '{Password}')")
        cursor.execute(f"INSERT INTO PlayerXP VALUES('{PlayerID}', 0)")
        cursor.execute(f"INSERT INTO MMR VALUES('{PlayerID}', 1000)")
        cursor.execute(f"INSERT INTO Matches VALUES('{PlayerID}', 0, 0)")

        #Commit and close connection
        connection.commit()
        connection.close()
        return True

    #Will update an accounts statistics after a game
    @staticmethod
    def UpdateAccount(PlayerID, PlayerXP, MMR, MatchWon):
        #Setup connection and cursor
        connection, cursor = DatabaseHandler.SetupConnection()

        #Update each statistic
        cursor.execute(f"UPDATE PlayerXP SET PlayerXP = PlayerXP + {PlayerXP} WHERE PlayerID = '{PlayerID}'")
        cursor.execute(f"UPDATE MMR SET MMR = MMR + {MMR} WHERE PlayerID = '{PlayerID}'")
        cursor.execute(f"UPDATE Matches SET MatchesPlayed = MatchesPlayed + 1, MatchesWon = MatchesWon + {MatchWon} WHERE PlayerID = '{PlayerID}'")

        #Commit and close connection
        connection.commit()
        connection.close()
        #DatabaseHandler.CloseConnection(connection)

    #Will check that the user has entered the correct credentials
    @staticmethod
    def AuthenticateAccount(PlayerID, Password):
        #Setup connection and cursor
        connection, cursor = DatabaseHandler.SetupConnection()

        #Query player database
        result = cursor.execute(f"SELECT Password FROM Player WHERE PlayerID = '{PlayerID}'").fetchone()

        #Nothing to commit here, just close
        #DatabaseHandler.CloseConnection()
        connection.close()

        #Use of a guard clause instead of a double conditional
        if result == None:
            return [False, 'invalid_id']
        if Password == result[0]:
            return [True]
        return [False, 'invalid_password']

    #Get information about the player back
    @staticmethod
    def fetchUserInfo(PlayerID):
        connection, cursor = DatabaseHandler.SetupConnection()

        userInfo = {'PlayerID': PlayerID}

        result = cursor.execute(f"SELECT * FROM Player WHERE PlayerID = '{PlayerID}'")

        result = result.fetchone()

        userInfo['email'] = result[1]
        userInfo['password'] = result[2]

        return userInfo

    @staticmethod
    def getLeaderboardPlayers(n=5):
        connection, cursor = DatabaseHandler.SetupConnection()

        result = cursor.execute(f"SELECT PlayerID, MMR FROM MMR ORDER BY MMR DESC LIMIT {n}")

        result = result.fetchall()
        return result

#Test code - uncomment to test
#DatabaseHandler.UpdateAccount('san_tiwari', 1000, 300, 1)
if __name__ == "__main__":

    print(DatabaseHandler.getLeaderboardPlayers(n=5))
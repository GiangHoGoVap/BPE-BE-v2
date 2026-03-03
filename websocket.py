import select
import psycopg2
import socketio

HOST_DB_TEST = "localhost"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "1234"
POSTGRES_DB = "bpe"


def listenForChanges():
    try:
        connection = psycopg2.connect(
            host=HOST_DB_TEST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )

        cursor = connection.cursor()

        cursor.execute("LISTEN workspace_changes;")
        print("Waiting for notifications on channel 'workspace_changes'")
        while True:
            if select.select([connection], [], [], 5) == ([], [], []):
                print("Timeout")
            else:
                connection.poll()
                connection.commit()
                while connection.notifies:
                    notify = connection.notifies.pop(0)
                    print("Got NOTIFY:", notify.pid, notify.channel, notify.payload)
                    socketio.emit("workspace_changes", notify.payload)

    except (Exception, psycopg2.Error) as error:
        raise error

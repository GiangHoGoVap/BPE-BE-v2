from bpsky import bpsky
from bpsky import socketio
import os
import threading

from services.survey_service.cron.scheduling import Scheduling_send_email

if __name__ == "__main__":
    # bpsky.run(host="0.0.0.0", port=os.environ.get("PORT", 8000), debug=True)
    email_thread = threading.Thread(
        target=Scheduling_send_email.schedule_loop_send_emails_and_publish_survey
    )
    email_thread.daemon = True
    email_thread.start()

    # start thread to close survey:
    close_survey_thread = threading.Thread(
        target=Scheduling_send_email.schedule_loop_close_survey
    )
    close_survey_thread.daemon = True
    close_survey_thread.start()

    socketio.run(bpsky, host="0.0.0.0", port=os.environ.get("PORT", 8000), debug=True)

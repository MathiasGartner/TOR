import logging
log = logging.getLogger(__name__)

import yagmail

from tor.base.utils import Utils
import tor.TORSettings as ts

yag = None
try:
    yag = yagmail.SMTP(ts.MAIL_USERNAME, oauth2_file=ts.MAIL_OAUTH_FILE)
except Exception as e:
    log.warning("could not initialize MailManager")
    log.warning(f"{repr(e)}")

def trySendMessage(to, subject, contents, description):
    log.info("will send mail")
    if yag is not None:
        if ts.SEND_MAIL:
            try:
                yag.send(to=to, subject=subject, contents=contents)
                log.info(f"Mail \"{subject}\" sent to \"{to}\".")
            except Exception as e:
                log.warning(f"Could not send message \"{subject}\" to \"{to}\". Message: \"{contents}\"")
                log.warning(f"{repr(e)}")
        else:
            log.warning("Sending Mail Messages is disabled (SEND_MAIL = False)")
    else:
        log.warning("MailManager not initialized")

def sendTestMessage(to=ts.MAIL_RECIPIENTS):
    s = "TOR: test"
    b = "This is a test message from The Transparency of Randomness."
    trySendMessage(to, s, b, "Test message")

def sendDeactiveClient(clientIdentity, to=ts.MAIL_RECIPIENTS):
    s = f"TOR: deactivate client {clientIdentity.Id} ({clientIdentity.Material})"
    b = (f"<h3>The Transparency of Randomness has deactivated a client</h3>"
         f"<p>"
         f"<b>Client details:</b><br />"
         f"Id: {clientIdentity.Id}<br />"
         f"Position: {clientIdentity.Position}<br />"
         f"IP: {clientIdentity.IP}<br />"
         f"Material: {clientIdentity.Material}<br />"
         f"Latin: {clientIdentity.Latin}"
         f"</p>"
        )
    #TODO: add error log to message
    trySendMessage(to, s, b, "deactivate client")

def sendTestDeactiveClient(to=ts.MAIL_RECIPIENTS):
    cid = Utils.EmptyObject()
    setattr(cid, "Id", 11)
    setattr(cid, "IP", "192.134.34.23")
    setattr(cid, "Material", "Pfeffer")
    setattr(cid, "Position", 15)
    setattr(cid, "Latin", "Schinus")
    setattr(cid, "Id", 11)
    sendDeactiveClient(cid, to)

def sendStatisticMail(data, to=ts.MAIL_RECIPIENTS):
    s = "TOR: status report"
    b = "<table>"
    b = b + "<th><td>Position</td><td>Name</td><td>2 Hour</td><td></td><td>4 Hour</td><td></td><td>Day</td><td></td><td>Event</td><td></td></th>"
    for d in data:
        b = b + "<tr>"
        for text in d:
            b = b + "<td>" + str(text) + "</td>"
        b = b + "</tr>"
    b = b + "</table>"
    trySendMessage(to, s, b, "status report")

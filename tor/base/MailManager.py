import logging
log = logging.getLogger(__name__)

import yagmail

from tor.base.utils import Utils
import tor.TORSettings as ts

yag = None

def __initYag():
    try:
        yag = yagmail.SMTP(ts.MAIL_USERNAME, oauth2_file=ts.MAIL_OAUTH_FILE)
    except Exception as e:
        log.warning("could not initialize MailManager")
        log.warning("{}".format(repr(e)))

def __trySendMessage(to, subject, contents, description):
    if yag is None:
        __initYag()
    if yag is not None:
        try:
            yag.send(to=to, subject=subject, contents=contents)
        except Exception as e:
            log.warning("could not send message \"{}\"".format(description))
            log.warning("{}".format(repr(e)))
    else:
        log.warning("MailManager not initialized")

def sendTestMessage(to=ts.MAIL_RECIPIENTS):
    s = "TOR: test"
    b = "This is a test message from The Transparency of Randomness."
    __trySendMessage(to, s, b, "Test message")

def sendDeactiveClient(clientIdentity, to=ts.MAIL_RECIPIENTS):
    s = "TOR: deactivate client {} ({})".format(clientIdentity.Id, clientIdentity.Material)
    b = "<h3>The Transparency of Randomness has deactivated a client</h3>" \
        "<p><b>Client details:</b><br>Id: {}<br>Position: {}<br>IP: {}<br>Material: {}<br>Latin: {} </p>"\
        .format(clientIdentity.Id, clientIdentity.Position, clientIdentity.IP, clientIdentity.Material, clientIdentity.Latin)
    __trySendMessage(to, s, b, "deactivate client")

cid = Utils.EmptyObject()
setattr(cid, "Id", 11)
setattr(cid, "IP", "192.134.34.23")
setattr(cid, "Material", "Pfeffer")
setattr(cid, "Position", 15)
setattr(cid, "Latin", "Schinus")
setattr(cid, "Id", 11)
#sendDeactiveClient(cid)
import os
import smtplib
import ssl
import traceback
import PASSWORDS
from email.message import EmailMessage


def send_email(receiver_emails, subject, message, logger, attached_file=None, sender_email=None, port=465):
    logger.debug(">>>>send_email.send_mail begin")
    logger.info("Sending email")
    # Create a secure SSL context
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL("smtp.yandex.ru", port, context=context)
    # Try connect to server
    try:
        server.login(PASSWORDS.settings['ymail_login'], PASSWORDS.settings['ymail_password'])
    except Exception:
        logger.error("ERROR: Can't connect to SMTP server:\n" + traceback.format_exc())
    msg = EmailMessage()
    if sender_email is None:
        sender_email = PASSWORDS.settings['sender_email']
    msg["From"] = sender_email
    msg["Subject"] = subject
    msg.set_content(message)
    if attached_file is not None:
        logger.info(f"attach file: {attached_file}")
        msg.add_attachment(open(attached_file, "r").read(), filename=attached_file)
    else:
        logger.info("No attachments")
    logger.info(f"List emails: {receiver_emails}")
    for one_receiver in receiver_emails:
        msg['To'] = one_receiver
        try:
            server.sendmail(sender_email, one_receiver, msg.as_string())
        except Exception:
            logger.error(f"ERROR: Can't send email to {one_receiver}:\n" + traceback.format_exc())
    server.quit()
    logger.debug(">>>>send_email.send_mail end")


if __name__ == "__main__":
    import custom_logger

    program_file = os.path.realpath(__file__)
    logger = custom_logger.get_logger(program_file=program_file)

    receiver_emails = PASSWORDS.settings['recipient_emails']
    subject = "DEBUG: send_email"
    message = "DEBUG: send_email"
    # attached_file = None
    attached_file = logger.handlers[0].baseFilename
    send_email(receiver_emails, subject, message, logger, attached_file)

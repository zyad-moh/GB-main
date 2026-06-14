"""
Email Service for sending emails via SMTP
"""

import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails via Gmail SMTP.
    Supports both plain text and HTML emails.
    """

    GMAIL_SMTP_HOST = "smtp.gmail.com"
    GMAIL_SMTP_PORT = 587

    def __init__(
        self,
        smtp_host: str = GMAIL_SMTP_HOST,
        smtp_port: int = GMAIL_SMTP_PORT,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_address: Optional[str] = None,
    ):
        """
        Initialize EmailService.

        Args:
            smtp_host: SMTP server host (default: Gmail SMTP)
            smtp_port: SMTP server port (default: 587 for STARTTLS)
            smtp_username: SMTP authentication username
            smtp_password: SMTP authentication password
            from_address: Default from address for emails
        """
        if not smtp_host:
            raise ValueError("SMTP host is required")

        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_address = from_address

        logger.info(
            "EmailService initialized: host=%s, port=%s, username=%s, from=%s",
            smtp_host, smtp_port, smtp_username, from_address,
        )

    def test_connection(self) -> bool:
        """Test SMTP connection and authentication. Returns True if successful."""
        try:
            import ssl
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as smtp:
                smtp.starttls(context=context)
                if self.smtp_username and self.smtp_password:
                    smtp.login(self.smtp_username, self.smtp_password)
                logger.info("SMTP connection test PASSED: host=%s, user=%s", self.smtp_host, self.smtp_username)
                return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error("SMTP connection test FAILED (auth error): %s", e)
            return False
        except Exception as e:
            logger.error("SMTP connection test FAILED: %s", e)
            return False

    def send(
        self,
        to_address: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc_addresses: Optional[list] = None,
        bcc_addresses: Optional[list] = None,
    ) -> bool:
        """
        Send an email.

        Args:
            to_address: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            cc_addresses: Optional list of CC addresses
            bcc_addresses: Optional list of BCC addresses

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_address or "noreply@interview-agent.com"
            message["To"] = to_address

            if cc_addresses:
                message["Cc"] = ", ".join(cc_addresses)

            # Attach plain text part
            part1 = MIMEText(body, "plain")
            message.attach(part1)

            # Attach HTML part if provided
            if html_body:
                part2 = MIMEText(html_body, "html")
                message.attach(part2)

            # Build recipient list
            recipients = [to_address]
            if cc_addresses:
                recipients.extend(cc_addresses)
            if bcc_addresses:
                recipients.extend(bcc_addresses)

            # Send email
            logger.info(f"Sending email to {to_address}: {subject}")

            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as smtp:
                smtp.starttls(context=context)
                if self.smtp_username and self.smtp_password:
                    smtp.login(self.smtp_username, self.smtp_password)
                smtp.sendmail(
                    from_addr=self.from_address or "noreply@interview-agent.com",
                    to_addrs=recipients,
                    msg=message.as_string(),
                )

            logger.info(f"Email sent successfully to {to_address}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False

    def send_batch(
        self,
        recipients: list,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> dict:
        """
        Send emails to multiple recipients.

        Args:
            recipients: List of email addresses
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body

        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0, "errors": []}

        for recipient in recipients:
            try:
                if self.send(
                    to_address=recipient,
                    subject=subject,
                    body=body,
                    html_body=html_body,
                ):
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Failed to send to {recipient}")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error sending to {recipient}: {str(e)}")

        logger.info(
            f"Batch email send completed: {results['success']} success, {results['failed']} failed"
        )
        return results

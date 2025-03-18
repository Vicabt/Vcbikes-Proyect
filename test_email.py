import os
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create a simple Flask app
app = Flask(__name__)

# Configure Flask-Mail with values from .env
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

# Log the configuration (without showing the actual password)
logger.info(f"Mail Server: {app.config['MAIL_SERVER']}")
logger.info(f"Mail Port: {app.config['MAIL_PORT']}")
logger.info(f"Mail Username: {'Set' if app.config['MAIL_USERNAME'] else 'Not set'}")
logger.info(f"Mail Password: {'Set' if app.config['MAIL_PASSWORD'] else 'Not set'}")
logger.info(f"Mail Default Sender: {'Set' if app.config['MAIL_DEFAULT_SENDER'] else 'Not set'}")

# Initialize Flask-Mail
mail = Mail(app)

def test_send_email():
    """Test function to send a simple email"""
    try:
        with app.app_context():
            # Create a test email
            msg = Message(
                subject='Test Email from VcBikes',
                recipients=[app.config['MAIL_USERNAME']],  # Send to yourself for testing
                body='This is a test email to verify the email configuration is working correctly.'
            )
            
            # Send the email
            mail.send(msg)
            
        logger.info("Test email sent successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to send test email: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == '__main__':
    # Run the test
    test_send_email()

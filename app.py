import os
import dotenv
import requests,img2pdf
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print('Starting up bot...')
dotenv.load_dotenv()

TOKEN: Final = os.getenv('TOKEN') 
BOT_USERNAME: Final = '@image_to_pdfs_bot'


# Lets us use the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there! I\'m a bot that converts image to pdf. What\'s up?')

# Lets us use the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Just upload an image and i will convert it to PDF format')

async def convert_to_pdf(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """Convert the image sent by the user to PDF and send it back."""
    # Get the photo file and file_id from the message sent by the user
    photo = update.message.photo[-1].file_id

    recieved_file =await context.bot.get_file(photo)
    path = recieved_file.file_path

    print(recieved_file.file_path,'tests')
    
   # Download the image file
    image_file =requests.get(path).content
    with open('image.jpg', 'wb') as f:
        f.write(image_file)

    # Convert the image to PDF
    with open('image.pdf', 'wb') as f:
        f.write(img2pdf.convert('image.jpg'))
    
    # Send the PDF file to the user
    await context.bot.send_document(chat_id=update.message.chat_id, document=open('image.pdf', 'rb'))

    # Clean up the temporary files
    os.remove('image.jpg')
    os.remove('image.pdf')
    
def handle_response(text: str,update:Update) -> str:
    processed: str = text.lower()

    if 'hi' in processed:
        return f'Hi {update.message.chat.first_name.lower()} How are you'

    if 'how are you' in processed:
        return 'I\'m good!'

    return 'Sorry I don\'t understand'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get basic info of the incoming message
    message_type: str = update.message.chat.type
    text: str = update.message.text
    print(update.message)
    # React to group messages only if users mention the bot directly
    if message_type == 'group':
        # Replace with your bot username
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text,update)
        else:
            return  # We don't want the bot respond if it's not mentioned in the group
    else:
        response: str = handle_response(text,update)

    # Reply normal if the message is in private
    await update.message.reply_text(response)


# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO,convert_to_pdf))

    # Log all errors
    app.add_error_handler(error)

    print('Polling...')
    # Run the bot
    app.run_polling(poll_interval=5)
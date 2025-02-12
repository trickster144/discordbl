import discord
import mysql.connector
import asyncio

TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token
GUILD_ID = 123456789012345678  # Replace with your server ID

# Connect to MySQL database
db = mysql.connector.connect(
    host="YOUR_DB_HOST",
    user="YOUR_DB_USER",
    password="YOUR_DB_PASSWORD",
    database="YOUR_DB_NAME"
)

client = discord.Client(intents=discord.Intents.all())

async def fetch_unregistered_users():
    cursor = db.cursor()

    # Get all users from Discord (bot must have permissions)
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found. Ensure bot is in the server.")
        return

    all_users = {member.id: member for member in guild.members if not member.bot}

    # Fetch users who have signed up from the database
    cursor.execute("SELECT discord_id FROM event_signups")
    registered_users = {row[0] for row in cursor.fetchall()}  # Store as set

    # Find unregistered users
    unregistered_users = [user for user_id, user in all_users.items() if user_id not in registered_users]
    
    return unregistered_users

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    unregistered_users = await fetch_unregistered_users()

    if not unregistered_users:
        print("All users are registered.")
    else:
        for user in unregistered_users:
            try:
                await user.send(f"Hey {user.name}, don't forget to sign up for the upcoming event! Register here: https://yourwebsite.com/events")
                print(f"Sent reminder to {user.name}")
                await asyncio.sleep(2)  # Prevent rate limits
            except discord.Forbidden:
                print(f"Cannot DM {user.name}. They may have DMs disabled.")

    await client.close()

client.run(TOKEN)

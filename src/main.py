from datetime import datetime

from discord import (
    Intents,
    Client,
    Interaction,
    app_commands,
    Object,
    Member,
    VoiceState,
    Permissions,
)

from BotConfig import BotConfig
from gpt import GPTClient
from util import (
    calculate_download_duration,
    list_to_string,
    is_str_with_twitter_url,
    replace_twitter_urls_in_str,
)

config = BotConfig()

intents = Intents.default()
intents.message_content = True
intents.voice_states = True

client: Client = Client(intents=intents)
client.tree = app_commands.CommandTree(client)

gpt_client = GPTClient()


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    # Saves the list of al the channels that the bot has permission to see
    config.set_authorized_channel_set(set(client.get_all_channels()))
    print(f"Message channels are {[x.name for x in config.get_message_channels()]}")
    my_guild = Object(config.get_guild_id())
    client.tree.copy_global_to(guild=my_guild)
    await client.tree.sync(guild=my_guild)
    print("Commands synced")


@client.event
async def on_message(message):
    # Process the message if it is sent from a tracked channel
    if config.has_x_message_channel(message.channel.id):
        # Reply with updated content if the message has the twitter url in it
        if is_str_with_twitter_url(message.content):
            print(f"Replacing twitter urls in message {message.id}")
            updated_message_content = replace_twitter_urls_in_str(message.content)
            await message.channel.send(updated_message_content, reference=message)


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    if before.channel is after.channel:
        return

    message: str
    # Sets message for the voice change activity
    match (before.channel, after.channel):
        case (None, after_channel):
            message = f"{member.display_name} entered {after_channel.name}"
        case (before_channel, None):
            message = f"{member.display_name} left {before_channel.name}"
        case (before_channel, after_channel):
            message = f"{member.display_name} switched from {before_channel.name} to {after_channel.name}"
        case _:
            print(f"Member: {member} Before: {before} After: {after}")
            return

    # Creates a union of members in both the before and after channel
    channels_members_list = []
    if after.channel:
        channels_members_list.extend(after.channel.members)
    if before.channel:
        channels_members_list.extend(before.channel.members)

    # For each message channel that has subscribed to the bot sends the message
    for message_channel in config.get_message_channels():
        # Gets the final list of mentions to add to the message
        final_mention_list = __get_mention_list(member.mention, channels_members_list, message_channel.id)

        # Checks if all the members in the text channel has permission to see the Voice channels that are in the message
        if __members_have_permission_to_view_voice_channel(message_channel, after.channel, before.channel):
            await message_channel.send(f"{list_to_string(final_mention_list)} {message}")


# Filters the mention list so that if anyone is already in a channel related to the event they are not mentioned
def __get_mention_list(member_mention, channel_members: list, channel_id: int) -> list:
    present_members_in_channels = [member_mention]
    present_members_in_channels.extend(list(map(lambda member: member.mention, channel_members)))
    return list(
        filter(
            lambda mention: mention not in present_members_in_channels,
            config.get_mentions(channel_id),
        )
    )


# Checks whether all the members of the text channel has permission to see the Voice channels that are in the message
def __members_have_permission_to_view_voice_channel(message_channel, after_channel, before_channel) -> bool:
    has_permission_to_view = True
    members = list(filter(lambda member: not member.bot, message_channel.members))
    for member in members:
        if after_channel:
            after_permissions: Permissions = after_channel.permissions_for(member)
            if not after_permissions.view_channel:
                has_permission_to_view = False
                break
        if before_channel:
            before_permissions: Permissions = before_channel.permissions_for(member)
            if not before_permissions.view_channel:
                has_permission_to_view = False
                break
    return has_permission_to_view


# Subscribe the text channel for messages from the bot
@client.tree.command()
async def subscribe(interaction: Interaction):
    config.add_message_channel(interaction.channel.id)
    await interaction.response.send_message(f"Subscribed to channel {interaction.channel}")


# Unsubscribe the text channel for messages from the bot
@client.tree.command()
async def unsubscribe(interaction: Interaction):
    config.remove_message_channel(interaction.channel.id)
    await interaction.response.send_message(f"Unsubscribed to channel {interaction.channel}")


# Set a user to be mentioned in the messages
@client.tree.command()
async def mention_me(interaction: Interaction):
    channel_id = interaction.channel_id
    mention = interaction.user.mention

    is_added = config.add_mention_to_channel(mention, channel_id)
    if is_added:
        await interaction.response.send_message(f"{interaction.user.mention} is going to be mentioned from now on.")
    else:
        await interaction.response.send_message(f"{interaction.user.mention} is already added.")


# Set a user to not be mentioned in the messages
@client.tree.command()
async def unmention_me(interaction: Interaction):
    channel_id = interaction.channel_id
    mention = interaction.user.mention

    is_removed = config.remove_mention_from_channel(mention, channel_id)
    if is_removed:
        await interaction.response.send_message(f"{interaction.user.mention} is not going to be mentioned from now on.")
    else:
        await interaction.response.send_message(
            f"{interaction.user.mention} is not found in the mention list for the channel."
        )


# Subscribe the text channel for messages from the bot
@client.tree.command()
async def convert_x_messages(interaction: Interaction):
    config.add_x_message_channel(interaction.channel.id)
    await interaction.response.send_message(f"Listening x messages in {interaction.channel}")


# Ask a question to GPT
@client.tree.command(description="Ask a question to Chat GPT")
async def ask_gpt(interaction: Interaction, query: str):
    await gpt(interaction, query)


@client.tree.command(description="Ask a question to Chat GPT to get a code snippet only")
async def ask_gpt_code(interaction: Interaction, query: str):
    await gpt(interaction, query, True)


async def gpt(interaction: Interaction, query: str, code=False):
    if interaction.channel_id != config.get_gpt_channel_id():
        await interaction.response.send_message("Not available in this channel")
        return
    if len(query) > config.get_gpt_query_char_limit():
        await interaction.response.send_message(f"Query cant be longer than 200 characters. Your is {len(query)}")
        return
    if gpt_client.total_queries_length() > config.get_gpt_total_char_limit():
        await interaction.response.send_message("Too many queries sent wait an hour before sending another message")
        return
    history = [
        {
            "role": "system",
            "content": "All answers must be shorter than 2000 characters.",
        }
    ]

    if code:
        history.append(
            {
                "role": "system",
                "content": "Only respond to questions with code snippets and nothing else.",
            }
        )

    length = len(history[0]["content"])
    await interaction.response.defer()
    response = gpt_client.ask_question(query, history=history)
    length += len(response)
    await interaction.followup.send(f"Query:{query}\n\nAlper GPT: {response}")
    gpt_client.clean_queries()
    gpt_client.queries[datetime.now()] = length


# Ask a question to GPT
@client.tree.command(description="How long would it take to download?")
async def how_long_to_download(interaction: Interaction, speed_in_mbit: str, size_in_gb: str):
    try:
        minutes = calculate_download_duration(speed_in_mbit, size_in_gb)
        await interaction.response.send_message(f"It would take {minutes} minutes")
    except ZeroDivisionError:
        await interaction.response.send_message("Your internet is down (speed cannot be zero)")
    except ValueError:
        await interaction.response.send_message("Speed and size should be numeric values")
    except Exception:
        await interaction.response.send_message("Unknown error")


client.run(config.get_bot_token())

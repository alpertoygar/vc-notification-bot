from discord import Intents, Client, Interaction, app_commands, Object, Member, VoiceState

from BotConfig import BotConfig
from util import list_to_string

config = BotConfig()

intents = Intents.default()
intents.message_content = True
intents.voice_states = True

client = Client(intents=intents)
client.tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    config.set_authorized_channel_set(client.get_all_channels())
    print(f'Message channels are {[x.name for x in config.get_message_channels()]}')
    my_guild = Object(config.get_guild_id())
    client.tree.copy_global_to(guild=my_guild)
    await client.tree.sync(guild=my_guild)
    print('Commands synced')


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    if before.channel is after.channel:
        return

    message: str

    match (before.channel, after.channel):
        case (None, after_channel):
            message = f'{member.display_name} entered {after_channel.name}'
        case (before_channel, None):
            message = f'{member.display_name} left {before_channel.name}'
        case (before_channel, after_channel):
            message = f'{member.display_name} switched from {before_channel.name} to {after_channel.name}'

    for message_channel in config.get_message_channels():
        await message_channel.send(f'{list_to_string(config.get_mentions())} {message}')


@client.tree.command()
async def subscribe(interaction: Interaction):
    config.add_message_channel(interaction.channel.id)
    await interaction.response.send_message(f'Subscribed to channel {interaction.channel}')


@client.tree.command()
async def unsubscribe(interaction: Interaction):
    config.remove_message_channel(interaction.channel.id)
    await interaction.response.send_message(f'Unsubscribed to channel {interaction.channel}')


@client.tree.command()
async def mention_me(interaction: Interaction):
    config.add_mention(interaction.user.mention)
    await interaction.response.send_message(f'{interaction.user.mention} is going to be mentioned from now on.')


@client.tree.command()
async def unmention_me(interaction: Interaction):
    config.remove_mention(interaction.user.mention)
    await interaction.response.send_message(f'{interaction.user.mention} is not going to be mentioned from now on.')


@client.tree.command()
@app_commands.describe(
    arg='arg'
)
async def list(interaction: Interaction, arg: str):
    await interaction.response.send_message(arg)

client.run(config.get_bot_token())

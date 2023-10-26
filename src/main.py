from discord import Intents, Client, Interaction, app_commands, Object, Member, VoiceState, Permissions

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

    present_members_in_channels = []

    if after.channel:
        present_members_in_channels.extend(list(map(lambda member: member.mention, after.channel.members)))
    if before.channel:
        present_members_in_channels.extend(list(map(lambda member: member.mention, before.channel.members)))

    final_mention_list = list(filter(lambda mention: mention not in present_members_in_channels, config.get_mentions()))

    for message_channel in config.get_message_channels():
        has_permission_to_view = True
        members = list(filter(lambda member: not member.bot, message_channel.members))
        for member in members:
            print(member)
            after_permissions: Permissions = after.channel.permissions_for(member)
            print(after_permissions.view_channel)
            before_permissions: Permissions = before.channel.permissions_for(member)
            print(before_permissions.view_channel)
            if not after_permissions.view_channel or not before_permissions.view_channel:
                has_permission_to_view = False
                break
        if has_permission_to_view:
            await message_channel.send(f'{list_to_string(final_mention_list)} {message}')


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
async def list_words(interaction: Interaction, arg: str):
    await interaction.response.send_message(arg)

client.run(config.get_bot_token())

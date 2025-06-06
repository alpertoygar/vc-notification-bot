import json
import os


class BotConfig:
    def __init__(self):
        self.__message_channels: set = set()
        self.__x_message_channels: set = set()
        self.__channels_with_mentions: dict[int, list[str]] = dict()
        self.__bot_token: str
        self.__guild_id: int
        self.__gpt_channel_id: int
        self.__gpt_model_code: str
        self.__gpt_model_base: str
        self.__gpt_query_token_limit: int
        self.__gpt_total_token_limit: int
        self.__config_path = os.path.join(os.getcwd(), "config.json")
        self.__load_config()
        self.__authorized_channel_set: set = set()

    def __load_config(self):
        try:
            with open(self.__config_path, "r+") as config_file:
                config_data = json.load(config_file)
                if "channels_with_mentions" in config_data:
                    self.__channels_with_mentions = {
                        int(channel_id): mentions
                        for channel_id, mentions in dict(config_data["channels_with_mentions"]).items()
                    }  # Update channels with mentions
                if "message_channels" in config_data:
                    self.__message_channels = set(config_data["message_channels"])  # Update message channels
                if "x_message_channels" in config_data:
                    self.__x_message_channels = set(config_data["x_message_channels"])  # Update message channels
                if "bot_token" in config_data:
                    self.__bot_token = config_data["bot_token"]
                else:
                    raise ValueError("You must have bot token in your config")
                if "guild_id" in config_data:
                    self.__guild_id = config_data["guild_id"]
                else:
                    raise ValueError("You must have guild id in your config")
                if "gpt_channel_id" in config_data:
                    self.__gpt_channel_id = config_data["gpt_channel_id"]
                if "gpt_model_code" in config_data:
                    self.__gpt_model_code = config_data["gpt_model_code"]
                if "gpt_model_base" in config_data:
                    self.__gpt_model_base = config_data["gpt_model_base"]
                if "gpt_query_token_limit" in config_data:
                    self.__gpt_query_token_limit = config_data["gpt_query_token_limit"]
                if "gpt_total_token_limit" in config_data:
                    self.__gpt_total_token_limit = config_data["gpt_total_token_limit"]
        except FileNotFoundError:
            print(f"Config file not found at {self.__config_path}")
        except json.JSONDecodeError:
            print("Invalid JSON in the config file")

    def __save_config(self):
        config_data = {
            "channels_with_mentions": self.__channels_with_mentions,
            "message_channels": list(self.__message_channels),
            "x_message_channels": list(self.__x_message_channels),
            "bot_token": self.__bot_token,
            "guild_id": self.__guild_id,
            "gpt_model_code": self.__gpt_model_code,
            "gpt_model_base": self.__gpt_model_base,
            "gpt_query_token_limit": self.__gpt_query_token_limit,
            "gpt_total_token_limit": self.__gpt_total_token_limit,
        }

        try:
            with open(self.__config_path, "w+") as config_file:
                json.dump(config_data, config_file, indent=4)
            print(f"Config saved to {self.__config_path}")
        except Exception as e:
            print(f"Error saving config to {self.__config_path}: {str(e)}")

    def get_guild_id(self):
        return self.__guild_id

    def get_bot_token(self):
        return self.__bot_token

    def get_gpt_channel_id(self):
        return self.__gpt_channel_id

    def get_gpt_model_code(self):
        return self.__gpt_model_code

    def get_gpt_model_base(self):
        return self.__gpt_model_base

    def get_gpt_query_token_limit(self):
        return self.__gpt_query_token_limit

    def get_gpt_total_token_limit(self):
        return self.__gpt_total_token_limit

    def set_authorized_channel_set(self, channel_list: set):
        self.__authorized_channel_set = channel_list

    def add_mention_to_channel(self, mention: str, channel_id: int):
        # no mention is added for channel yet
        if channel_id not in self.__channels_with_mentions:
            self.__channels_with_mentions[channel_id] = [mention]
            self.__save_config()
            return True

        # mention is not added for channel yet
        if mention not in self.__channels_with_mentions[channel_id]:
            self.__channels_with_mentions[channel_id].append(mention)
            self.__save_config()
            return True

        # mention is already added for channel
        return False

    def remove_mention_from_channel(self, mention: str, channel_id: int):
        # no mention is added for channel yet
        if channel_id not in self.__channels_with_mentions:
            self.__save_config()
            return False

        # mention is not added for channel yet
        if mention not in self.__channels_with_mentions[channel_id]:
            self.__channels_with_mentions[channel_id].append(mention)
            self.__save_config()
            return False

        # mention is already added for channel
        self.__channels_with_mentions[channel_id].remove(mention)

        # remove channel entry from dictionary if mention list is empty
        if len(self.__channels_with_mentions[channel_id]) == 0:
            del self.__channels_with_mentions[channel_id]

        self.__save_config()
        return True

    def get_mentions(self, channel_id: int):
        if channel_id in self.__channels_with_mentions:
            return self.__channels_with_mentions[channel_id]

        return []

    def add_message_channel(self, channel_id: int):
        if channel_id not in self.__message_channels:
            self.__message_channels.add(channel_id)
            self.__save_config()

    def get_message_channels(self):
        test = list(
            filter(
                lambda channel: channel.id in self.__message_channels,
                list(self.__authorized_channel_set),
            )
        )
        return test

    def add_x_message_channel(self, channel_id: int):
        if channel_id not in self.__x_message_channels:
            self.__x_message_channels.add(channel_id)
            self.__save_config()

    def has_x_message_channel(self, channel_id) -> bool:
        return channel_id in self.__x_message_channels

    def remove_message_channel(self, channel_id):
        if channel_id in self.__message_channels:
            self.__message_channels.remove(channel_id)
            self.__save_config()

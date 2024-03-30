class PersonalPrompt:

    status_prompt = ["default"]
    default_prompt = '\033[0m[ \033[31mTheTruckOfAlmendruc\033[0m > \033[33m'
    prompt_server = '\033[0m[ \033[31mTheTruckOfAlmendruc\033[35m/\033[0m \033[36mServer\033[0m\033[0m > \033[33m'

    def __init__(self):
        pass
    
    def _get_prompt_server_with_user(self, user):
        return '\033[0m[ \033[31mTheTruckOfAlmendruc\033[35m/\033[0m \033[36mServer [{0}]\033[0m\033[0m > \033[33m'.format(user)

    def prompt(self):
        if self.status_prompt[0] == "default":
            return self.default_prompt

        elif self.status_prompt[0] == "server":
            return self.prompt_server
        
        elif self.status_prompt[0] == "withuser":
            prompt = self._get_prompt_server_with_user(self.status_prompt[1])
            return prompt

    def prompt_change_status(self, value):
        value_split = value.split()

        if value_split[0] == "default":
            self.status_prompt.clear()
            self.status_prompt.append(value)

        elif value_split[0] == "server":
            self.status_prompt.clear()
            self.status_prompt.append(value)

        elif value_split[0] == "withuser":
            self.status_prompt.clear()
            if (len(value_split)) > 1:
                self.status_prompt.append(value_split[0])
                self.status_prompt.append(value_split[1])
            else:
                self.status_prompt.append(value_split[0])
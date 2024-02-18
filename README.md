# miniframework_miniapp for Telegram Bot
This is a concept of how to develop a miniapp with minimal organization.

## Basic structure
- Imports
    - Here we import the necessary libraries, models, types, and Components.

- basic_comands
    - Here we define the basic commands that the bot will have. You can add more commands and rules, like custom commands for different types of users.

- Webapp messages handler
    - Here you can define actions for webapp_data, sent by the user in json format.
    - Action can be a lambda function that runs a Component or any function.

- Any message handler
    - You can set a handler for any message, as well as for any command. Here it's generally used for the custom commands and MainMenu component.

- Callbacks
    - Here you register all the callbacks that the bot will have. You can do this inside components, but it's better to have a centralized place for this, and you avoid losing track of the callbacks when the project grows and restart your bot.
    - Basically you define a dict options, where the key is the callback_data and the value is a lambda function that runs a Component.

- COMPONENTS
    
    Components can be called passing this instructions (from App.custom_bot.CustomBot):

    - bot: the main instance of the bot running.
    - userid: the user id that is running the component.
    - call (CallbackQuery): the previous callback query that called the component, if any. It's used to edit the message, for example. Just a reference.
    - startFrom: method reference to start the component. It's the first method that will be called when the component is called. It's for the case when you want to start the component from a specific point, not from the beginning, like when you want to edit a message and start the component from the last step.


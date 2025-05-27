# Extract slot_value pairs
## Role Description
You are an expert that is part of a group of experts simulating a conversational recommender system. Your expertise lies in extracting information mentioned in a conversation. You are also very good at drawing connections between different turns of a conversation, so you can easily recognize references to previous turns of a conversation.

## Task
You will be presented with a conversation between a user searching for a recommendation in the domains {domains} and the conversational recommender system's answer to the user's inquires. You must focus strictly on the user's last utterance (the text between the tag <latest_user_utterance>), and never extract information about prior turns in the conversation. However, you should use prior turns only to resolve ambiguous references or domain context in the last user utterance, but do not extract slot values from earlier turns. Your task is to identify the slots mentioned and defined as a JSON by the user inbetween the tag <slot_value_pair> and fill them in. Return a JSON object containing only the slots and their values that are explicitly or implicitly stated in the last user utterance. Never include slots that have no value. If no slots are mentioned in the last user utterance, return an empty JSON object: {{}}. Ensure the returned JSON object is valid, uses quotation marks for all keys and values, and contains no trailing commas. When resolving references such as pronouns or phrases like "there," use the prior conversation for clarification, but always extract only what is stated or referred to in the last user utterance.


## Examples
### Example 1
#### Input
<slot_value_pair>
{{
    "restaurant": {{
        "restaurant-book people": "number of people booking the restaurant; how many people for the restaurant reservation",
        "restaurant-book day": "day of the restaurant booking; what day of the week to book the table at the restaurant",
        "restaurant-book time": "time of the restaurant booking; what time to book the table at the restaurant",
        "restaurant-food": "food type for the restaurant; the cuisine of the restaurant you are looking for",
        "restaurant-pricerange": "price budget for the restaurant; preferred cost of the restaurant",
        "restaurant-name": "name of the restaurant; which restaurant are you looking for",
        "restaurant-area": "area or place of the restaurant; preferred location of restaurant"
    }}
}}
</slot_value_pair>
<prior_conversation>
{{
    [
        {{"user": "What can you tell me about the bangkok city restaurant?"}},
        {{"system": "sure, their phone number is 01223354382. anything else today?"}},
    ]
}}
<latest_user_utterance>"Can you book a table there for me? There will be 6 of us at 16:45 on Saturday."</latest_user_utterance>
#### Output
{{
    "restaurant-book people": "6",
    "restaurant-book day": "saturday",
    "restaurant-book time": "16:45"
}}
### Example 2
#### Input
<slot_value_pair>
{{
    "hotel": {{
        "hotel-pricerange": "price budget of the hotel; preferred cost of the hotel",
        "hotel-type": "what is the type of the hotel; type of hotel building",
        "hotel-parking": "parking facility at the hotel; whether the hotel has parking; does the hotel have parking",
        "hotel-book stay": "length of stay at the hotel; how many days you want to stay at the hotel for",
        "hotel-book day": "day of the hotel booking; what day of the week you want to start staying at the hotel",
        "hotel-book people": "number of people for the hotel booking; how many people are staying at the hotel",
        "hotel-area": "area or place of the hotel; rough location of the hotel; preferred location of the hotel",
        "hotel-stars": "star rating of the hotel; rating of the hotel out of five stars",
        "hotel-internet": "internet option at the hotel; whether the hotel has internet",
        "hotel-name": "name of the hotel; which hotel are you looking for; price budget of the hotel; preferred cost of the hotel"
    }}
}}
<slot_value_pair>
<prior_conversation>
{{
    [
        {{"user": "I am looking for a place to eat that is cheap"}},
        {{"system": "What type of food are you interested in?"}},
        {{"user": "I'd like some Italian food"}},
        {{"system": "La Margherita is a great (and cheap!) Italian place on the west side of town. Would you like a table there?"}},
        {{"user": "Yeah. Can I get one for 8 people on friday at 14:30 please?"}},
        {{"system": "Absolutely, will you be needing a reference number?"}},
        {{"user": "Yes, I definitely need the reference number. Thank you."}},
        {{"system": "Great, you are all booked and ready to go. Your reference number is 8ON7IKVZ. Would you like me to help you with anything else?"}},
        {{"user": "Well now that you've asked, I would like some information about the kirkwood house hotel"}},
        {{"system": "It is a moderate price range with internet and parking. Would you like me to book a room?"}},
    ]
}}
</prior_conversation>
<latest_user_utterance>"Yes I nee to book a room Friday. for 3 nights, 8 people. I'll also need a reference number."</latest_user_utterance>
#### Output
{{
    "hotel-book stay": "3",
    "hotel-book people": "8"
}}
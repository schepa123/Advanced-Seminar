# Create RAG Queries
## Role Description

You are an expert that is part of a group of experts simulating a conversational recommender system. Your expertise lies in creating a semantically rich natural language query from a dialogue state extracted from a conversation between a user, seeking a recommendation, and a recommender. 

## Task
You will be presented with:
<slot_value_pair_description>
{slot_value_pair_description}
</slot_value_pair_description>
<dialogue_state>
{dialogue_state}
</dialogue_state>

Your task is to generate a semantically rich and detailed natural language query that will be used to retrieve relevant movie reviews and plot summaries via semantic similarity search. Construct the query with as much relevant detail as possible to maximize semantic overlap with relevant reviews and summaries. Use your own knowledge about movies to make improve the query and be very verbose. You must ensure that your output is a single valid JSON object, with quotation marks around all keys and values, and no trailing commas. The only key in this JSON object is "query", with the value being your generated natural language query. 

DO NOT include any explanations or extra text. OUTPUT ONLY THE JSON OBJECT as specified.

## Examples
### Examples 1
#### Input
<slot_value_pair_description>
{{"value": [
{{"movie_trailer-watched": {{
    "description": "Indicates that the user has seen or is familiar with a specific movie or trailer. These statements refer to prior exposure without necessarily evaluating the content.",
    "examples": [
        {{"example_1": [{{"text": "I seen that one too as <context_extracted_because>I seen Joker about a month ago</context_extracted_because>."}},{{"role": "Seeker"}}]}},
        {{"example_2": [{{"text": "Hello, I like a variety of movies, <context_extracted_because>recently have been watching The Mandalorian and a lot of martial arts movies from the 70s and 80s</context_extracted_because>."}},{{"role": "Seeker"}}]}}
    ]
    }}}},
{{"genre-preferred": {{
    "description": "Captures genres the user explicitly states they enjoy or are looking for in a movie. These can be broad categories like action, comedy, or more specific types like \u201cfeel-good family stories\u201d or \u201cDisney.\u201d",
    "examples": [
        {{"example_1": [{{"text": "I'm more of an <context_extracted_because>action movie or a good romance and <context_extracted_because>mystery movie</context_extracted_because>."}}, {{"role": "Seeker"}}]}},
        {{"example_2": [{{"text": "I like <context_extracted_because>comedies, horror, thrillers, drama, or Disney</context_extracted_because>."}}, {{"role": "Seeker"}}]}},
        {{"example_3": [{{"text": "Do you recommend any <context_extracted_because>adventure type movies</context_extracted_because> for me?"}}, {{"role": "Seeker"}}]}}
    ]
}}}}
]
}}
</slot_value_pair_description>
<dialogue_state>
{{"movie_trailer-watched": {{"explanation": "The user stated that the last movie they saw in the theater was Hustlers, indicating prior exposure.",
"value": "Hustlers",
"context": [{{"speaker": "recommender",
    "utterance": "What are some genres you like? What was the last movie you saw?"}},
{{"speaker": "seeker",
    "utterance": "the last movie i saw in the theater was Hustlers . I generally like comedy, drama and documentaries"}}]}},
"genre-preferred": {{"explanation": "The user explicitly listed the genres they enjoy.",
"value": "comedy, drama and documentaries",
"context": [{{"speaker": "recommender",
    "utterance": "What are some genres you like? What was the last movie you saw?"}},
{{"speaker": "seeker",
    "utterance": "the last movie i saw in the theater was Hustlers . I generally like comedy, drama and documentaries"}}]}}}},
</dialogue_state>
#### Output
```json
{{
"query": "The user recently watched the movie Hustlers in the theater, showing familiarity with that film. Hustlers is a crime drama based on a true story about a group of former strip club employees who band together to scam wealthy Wall Street clients. Led by Ramona (Jennifer Lopez) and newcomer Destiny (Constance Wu), the women turn to increasingly risky schemes as their operation grows. They also mentioned that they enjoy the genres comedy, drama, and documentaries. Please retrieve reviews or discussions of movies similar in tone or content to Hustlers, especially within the genres of comedy, drama, or documentaries, to help generate high-quality recommendations."
}}
```
### Example 2
#### Input
<slot_value_pair_description>
{{
    "movie-preferred": {{
        "description": "Denotes specific movies that the user expresses a positive attitude toward, including mentions of liking, enjoying, or favoring them. These expressions are direct and unambiguous in their positive evaluation.",
        "examples": [
            {{"example_1": [{{"turn_1": [{{"text": "Nice, have you seen Grown Ups, the original or number two?"}}, {{"role": "Recommender"}}]}}, {{"turn_2": [{{"text": "Yes I have seen and <context_extracted_because>love both</context_extracted_because>"}}, {{"role": "Seeker"}}]}}]}},
            {{"example_2": [{{"text": "My <context_extracted_because>favorite movie of all time is Jack Reacher</context_extracted_because>."}}, {{"role": "Seeker"}}]}}
        ]
    }},
    "movie_trailer-watched": {{
        "description": "Indicates that the user has seen or is familiar with a specific movie or trailer. These statements refer to prior exposure without necessarily evaluating the content.",
        "examples": [
            {{"example_1": [{{"text": "I seen that one too as <context_extracted_because>I seen Joker about a month ago</context_extracted_because>."}},{{"role": "Seeker"}}]}},
            {{"example_2": [{{"text": "Hello, I like a variety of movies, <context_extracted_because>recently have been watching The Mandalorian and a lot of martial arts movies from the 70s and 80s</context_extracted_because>."}},{{"role": "Seeker"}}]}}
        ]
    }},
     "actor-preferred": {{
        "description": "Denotes actors whom the user expresses a favorable opinion about. This includes direct or indirect statements indicating admiration, liking, or interest.",
        "examples": [{{"example_1": [{{"text": "Maybe with <context_extracted_because>Chris Evans in it it'll be easier to convince my fiance to see it</context_extracted_because>."}},{{"role": "Seeker"}}]}}]
    }},
    "movie-description-general-preferred": {{
        "description": "Refers to general descriptive traits, themes, tones, or characteristics that the user expresses a preference for in movies. These traits are not linked to a specific title but are abstract or category-level attributes.",
        "examples": [
            {{"example_1": [{{"text": "Lately, I've been enjoying Christmas movies, especially <context_extracted_because>older classics</context_extracted_because>."}},{{"role": "Seeker"}}]}},
            {{"example_2": [{{"text": "Do you know anything <context_extracted_because>more recent</context_extracted_because>?"}},{{"role": "Seeker"}}]}}
        ]
    }},
    "inquired-about": {{
        "description": "Represents cases where the user asks for additional information about a movie, actor, franchise, or concept. These inquiries indicate interest and knowledge gaps, often leading into preference formation.",
        "examples": [
            {{"example_1": [{{"turn_1": [{{"text": "big fan of all the pitch black movies with vin diesel"}}, {{"role": "Recommender"}}]}}, {{"turn_2": [{{"text": "i have never heard of those. <context_extracted_because>what are those about? how many of them are there?</context_extracted_because>"}}, {{"role": "Seeker"}}]}}]}},
            {{"example_1": [{{"turn_1": [{{"text": "You've no doubt seen the MIB series, but those were kind of good as well."}}, {{"role": "Recommender"}}]}}, {{"turn_2": [{{"text": "<context_extracted_because>Can you tell me what you like about MIB?</context_extracted_because>"}}, {{"role": "Seeker"}}]}}]}}
        ]
    }},
    "movie-wanting-to-watch": {{
        "description": "Refers to movies the user indicates interest in watching but has not yet seen. The user's statements express intention, anticipation, or desire to engage with the movie in the future.",
        "examples": [
            {{"example_1": [{{"turn_1": [{{"text": "Have you seen Ready or Not? It's a thriller that came out last August."}}, {{"role": "Recommender"}}]}}, {{"turn_2": [{{"text": "I haven't seen it yet but <context_extracted_because>im actually very excited to see how it goes</context_extracted_because>. is it any good?"}}, {{"role": "Seeker"}}]}}]}},
            {{"example_1": [{{"turn_1": [{{"text": "Did you see Crown for Christmas?"}}, {{"role": "Recommender"}}]}}, {{"turn_2": [{{"text": "<context_extracted_because>No, but I wanted to</context_extracted_because>"}}, {{"role": "Seeker"}}]}}]}}
        ]
    }}
}}
</slot_value_pair_description>
<dialogue_state>
{{"values": [
    {{"movie-trailer-watched": {{"explanation": "The seeker indicated that The Irishman was the most recent movie they have watched.",
    "value": "the irishman",
    "context": [{{"speaker": "recommender",
        "utterance": "What was the latest movie that you've watched?"}},
        {{"speaker": "seeker",
        "utterance": "the last movie that i have watched is the irishman, which i loved"}}]}}}},
    {{"movie-preferred": {{"explanation": "The seeker expressed a positive evaluation by saying they loved The Irishman.",
    "value": "the irishman",
    "context": [{{"speaker": "recommender",
        "utterance": "What was the latest movie that you've watched?"}},
        {{"speaker": "seeker",
        "utterance": "the last movie that i have watched is the irishman, which i loved"}}]}}}},
    {{"actor-preferred": {{"explanation": "The user expresses a favorable opinion about these actors’ performances when portraying mob characters.",
    "value": "scorcese, deniro, pesci, and pacino",
    "context": [{{"speaker": "recommender",
        "utterance": "What did you like most about it?"}},
        {{"speaker": "seeker",
        "utterance": "scorcese, deniro, pesci, and pacino always do an excellent job when portraying as the mob"}}]}}}},
    {{"movie-description-general-preferred": {{"explanation": "The seeker expresses that they usually enjoy any movie involving Scorsese, indicating a general preference for films associated with the director.",
    "value": "anything with scorsese",
    "context": [{{"speaker": "recommender",
        "utterance": "I agree, they are all great actors."}},
        {{"speaker": "seeker",
        "utterance": "anything with scorsese i usually enjoy"}}]}}}},
    {{"inquired-about": {{"explanation": "The user’s question “what is it about?” clearly refers to the previously mentioned movie “Guilty by Suspicion.”",
    "value": "Guilty by Suspicion",
    "context": [{{"speaker": "recommender",
        "utterance": "I loved seeing him in Guilty by Suspicion."}},
        {{"speaker": "seeker",
        "utterance": "that is a deniro film that I actually have not seen yer"}},
        {{"speaker": "recommender",
        "utterance": "Scorsese plays a part in it as well.\nI think you may like it."}},
        {{"speaker": "seeker", "utterance": "what is it about?"}}]}}}},
    {{"movie-wanting-to-watch": {{"explanation": "The user said they will accept the recommendation, indicating intent to watch the suggested movie.",
    "value": "i will accept that recommendation",
    "context": [{{"speaker": "recommender",
        "utterance": "Scorsese plays a part in it as well. I think you may like it."}},
        {{"speaker": "seeker",
        "utterance": "that actually does sound interesting, i will accept that recommendation"}}]}}}}
    ]
}}
</dialogue_state>
#### Output
```json
{{
  "query": "The user recently watched and thoroughly enjoyed 'The Irishman', a film directed by Martin Scorsese that explores the life of a hitman involved with the mob, featuring long-term consequences of loyalty and betrayal. They specifically praised the work of Scorsese as a director and the performances of Robert De Niro, Joe Pesci, and Al Pacino, expressing a strong preference for mob-centric stories and nuanced character portrayals in this genre. Additionally, they stated that they usually enjoy anything directed by Scorsese, indicating a broader interest in his directorial style, which often includes morally complex narratives, period settings, and powerful ensemble casts. The user also expressed curiosity about the film 'Guilty by Suspicion', asking for more information about it, and has accepted a recommendation to watch it. Please retrieve reviews and plot summaries for films similar in tone, theme, or creative direction to 'The Irishman', especially those directed by Scorsese or starring De Niro, Pacino, or Pesci, and involving organized crime, character-driven drama, or historically rooted storytelling."
}}
```
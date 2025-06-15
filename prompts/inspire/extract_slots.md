# Extract slot_value pairs

## Role Description
You are an expert that is part of a group of experts simulating a conversational recommender system. Your expertise lies in extracting information mentioned in a conversation. You are also very good at drawing connections between different turns of a conversation, so you can easily recognize references to previous turns of a conversation.

## Task
You will be presented with:

<slot_value_pair>
{slot_value_pair}
</slot_value_pair>
<prior_conversation>
{prior_conversation}
</prior_conversation>
<latest_user_utterance>{latest_user_utterance}</latest_user_utterance>


- **Focus strictly** on the text between `<latest_user_utterance>…</latest_user_utterance>`.
- Do **not** extract slots from earlier turns, but you may use prior turns (`{prior_conversation}`) to resolve ambiguities in the latest user utterance. If a slot value in the latest user utterance refers to content from previous turns (e.g., a pronoun, ellipsis, or reference like "that" or "the earlier movie"), you may quote from those previous turns within the `context` to ensure clarity, but only slots explicitly or implicitly present in the latest utterance should be extracted.
- Slots can appear as a question from the Recommender, with the value being in the answer of the seeker. Pay close attention to such dialog links.
- Extract the full exchange involving the relevant utterance(s) for the slot, with the speakers clearly and explicitly marked for each turn. This context should reveal how the slot value is supported or clarified.
- Identify only those slots (defined in `{slot_value_pair}`) that are explicitly or implicitly mentioned in the `{latest_user_utterance}`. Do not infer or hallucinate values not clearly present.
- The tag `<context_extracted_because>` in the examples of `slot_value_pair` specifies the text that triggered the extraction.
- If multiple slot/value pairs appear in the latest user utterance, extract each as a separate entry in the output JSON.
- Return only a JSON object mapping each extracted slot to an object with three keys:
  1. `"explanation"`: A concise (≤2 sentences) reason why you extracted that slot/value from the latest utterance.
  2. `"value"`: The exact text (or normalized form) that triggered the extraction (as marked by the <context_extracted_because> tag).
  3. `"context"`: The surrounding context of the value, using a list of objects for each speaker/utterance involved in establishing the slot's meaning. This context can span multiple conversation turns.
- Omit any slots that have no value.
- If no slots appear in the latest utterance, return
{{"None": {{"explanation": "None", "value": "None", "context": [{{"speaker": "None", "utterance": "None"}}]}}}}.
- Return only a valid JSON object as output. All keys and values must be enclosed with double quotes and there must be no trailing commas.
- Do not include any free text, commentary, or formatting outside of the JSON object.


## Examples
### Example 1
#### Input
<slot_value_pair>
{{
    "genre-preferred": {{
        "description": "Captures genres the user explicitly states they enjoy or are looking for in a movie. These can be broad categories like action, comedy, or more specific types like \u201cfeel-good family stories\u201d or \u201cDisney.\u201d",
        "examples": [
            {{"example_1": [{{"text": "I'm more of an <context_extracted_because>action movie or a good romance and <context_extracted_because>mystery movie</context_extracted_because>."}}, {{"role": "Seeker"}}]}},
            {{"example_2": [{{"text": "I like <context_extracted_because>comedies, horror, thrillers, drama, or Disney</context_extracted_because>."}}, {{"role": "Seeker"}}]}},
            {{"example_3": [{{"text": "Do you recommend any <context_extracted_because>adventure type movies</context_extracted_because> for me?"}}, {{"role": "Seeker"}}]}}
        ]
    }},
    "movie-preferred": {{
        "description": "Denotes specific movies that the user expresses a positive attitude toward, including mentions of liking, enjoying, or favoring them. These expressions are direct and unambiguous in their positive evaluation.",
        "examples": [
            {{"example_1": [{{"turn_1": [{{"text": "Nice, have you seen Grown Ups, the original or number two?"}}, {{"role": "Recommender"}}]}}, {{"turn_2": [{{"text": "Yes I have seen and <context_extracted_because>love both</context_extracted_because>"}}, {{"role": "Seeker"}}]}}]}},
            {{"example_2": [{{"text": "My <context_extracted_because>favorite movie of all time is Jack Reacher</context_extracted_because>."}}, {{"role": "Seeker"}}]}}
        ]
    }}
}}
</slot_value_pair>
<prior_conversation>
{{'speaker': 'recommender', 'utterance': 'Hey! How are you doing?'}}
{{'speaker': 'seeker', 'utterance': 'I am great, i am actually looking for a movie recommendation?'}}
{{'speaker': 'recommender', 'utterance': ''What type of movies are you into?'}}
{{'speaker': 'seeker', 'utterance': ''well i like romantic and comedies'}}
{{'speaker': 'recommender', 'utterance': 'What is your favorite comedy?'}}
</prior_conversation>
<latest_user_utterance>to all the boys i've loved before</latest_user_utterance>

#### Output
```json
{{
  "movie-preferred": {{
    "explanation": "The seeker stated that to all the boys i've loved before is their favorite movie.",
    "value": "to all the boys i've loved before",
    "context": [
        {{"speaker": "recommender", "utterance": "What is your favorite comedy?"}},
        {{"speaker": "seeker", "utterance": "to all the boys i've loved before"}}
    ]
  }}
}}
```

### Example 2
#### Input
<slot_value_pair>
{{
    "movie-description-movie_specific-preferred": {{
    "description": "Refers to descriptive feedback or evaluative statements in which the user identifies specific qualities they liked in a particular movie. The description is tied directly to a named title.",
    "examples": [
            {{"example_1": [
                {{"turn_1": [{{"text": "It takes place in florida, big hurricane hits houses near swamp and they become infested with man eating aligators."}},{{"role": "Recommender"}}]}},
                {{"turn_2": [{{"text": "<context_extracted_because>sounds interesting</context_extracted_because>"}},{{"role": "Seeker"}}]}}
            ]}},
            {{"example_2": [
                {{"text": "Deadpool because it did a <context_extracted_because>great job of mashing comedy and action together</context_extracted_because>."}},{{"role": "Seeker"}}
            ]}}
    ]
    }},
    "movie_trailer-watched": {{
    "description": "Indicates that the user has seen or is familiar with a specific movie or trailer. These statements refer to prior exposure without necessarily evaluating the content.",
    "examples": [
        {{"example_1": [{{"text": "I seen that one too as <context_extracted_because>I seen Joker about a month ago</context_extracted_because>."}},{{"role": "Seeker"}}]}},
        {{"example_2": [{{"text": "Hello, I like a variety of movies, <context_extracted_because>recently have been watching The Mandalorian and a lot of martial arts movies from the 70s and 80s</context_extracted_because>."}},{{"role": "Seeker"}}]}}
    ]
    }}
}}
</slot_value_pair>
<prior_conversation>
{{'speaker': 'recommender', 'utterance': 'Hi! What kind of movies do you like?'}}
{{'speaker': 'speaker', 'utterance': 'I like all kind of movies'}}
{{'speaker': 'recommender', 'utterance': 'What about You Were Never Really Here?'}}
{{'speaker': 'speaker', 'utterance': 'I haven't heard about that movie, what's it about?'}}
{{'speaker': 'recommender', 'utterance': 'It's a pretty gritty action thriller starring Joaquin Phoenix, where he plays a former mercenary who deals with his trauma by taking down a human trafficking network and rescuing the girls they had captive.
Would you be interested in watching the trailer?'}}
</prior_conversation>
<latest_user_utterance>Sounds similar to Taken, but sure, I'll give it a go.</latest_user_utterance>

#### Output
```json
{{
  "movie-description-movie_specific-preferred": {{
    "explanation": "The user said that they are interested in the movie.",
    "value": "It's a pretty gritty action thriller starring Joaquin Phoenix, where he plays a former mercenary who deals with his trauma by taking down a human trafficking network and rescuing the girls they had captive.",
    "context": [
        {{"speaker": "recommender", "utterance": "It's a pretty gritty action thriller starring Joaquin Phoenix, where he plays a former mercenary who deals with his trauma by taking down a human trafficking network and rescuing the girls they had captive.Would you be interested in watching the trailer?"}},
        {{"speaker": "seeker", "utterance": "Sounds similar to Taken, but sure, I'll give it a go."}}
    ]
  }}
}}
```
### Example 3
#### Input
<slot_value_pair>
{{
"movie-description-general-preferred": {{
"description": "Refers to general descriptive traits, themes, tones, or characteristics that the user expresses a preference for in movies. These traits are not linked to a specific title but are abstract or category-level attributes.",
"examples": [
    {{"example_1": [{{"text": "Lately, I've been enjoying Christmas movies, especially <context_extracted_because>older classics</context_extracted_because>."}},{{"role": "Seeker"}}]}},
    {{"example_2": [{{"text": "Do you know anything <context_extracted_because>more recent</context_extracted_because>?"}},{{"role": "Seeker"}}]}}
]}},
 "actor-preferred": {{
    "description": "Denotes actors whom the user expresses a favorable opinion about. This includes direct or indirect statements indicating admiration, liking, or interest.",
    "examples": [{{"example_1": [{{"text": "Maybe with <context_extracted_because>Chris Evans in it it'll be easier to convince my fiance to see it</context_extracted_because>."}},{{"role": "Seeker"}}]}}]
 }}
}}
</slot_value_pair>
<prior_conversation>
{{'speaker': 'recommender', 'utterance': 'hi how are you doing?'}}
{{'speaker': 'speaker', 'utterance': 'fantastic and yourself?'}}
{{'speaker': 'recommender', 'utterance': 'sure, but first what kind of movies do you like to watch?'}}
</prior_conversation>
<latest_user_utterance>I preffer some risque humor or some off the wall comical set off circumstances.</latest_user_utterance>

#### Output
```json
{{
  "movie-description-general-preferred": {{
    "explanation": "The user clearly stated his preferences for comedies",
    "value": "risque humor or some off the wall comical set off circumstances",
    "context": [
        {{"speaker": "seeker", "utterance": "I preffer some risque humor or some off the wall comical set off circumstances."}}
    ]
  }}
}}
```
### Example 4
<slot_value_pair>
{{"inquired-about":
  "description": "Represents cases where the user asks for additional information about a movie, actor, franchise, or concept. These inquiries indicate interest and knowledge gaps, often leading into preference formation.",
  "examples": [
    {{"example_1": [{{"turn_1": [{{"text": "big fan of all the pitch black movies with vin diesel?"}}, {{"role": "Recommender"}}]}}, {{"turn_2": [{{"text": "i have never heard of those. <context_extracted_because>what are those about? how many of them are there?</context_extracted_because>}}, {{"role": "Seeker"}}]}}]}},
    {{"example_1": [{{"turn_1": [{{"text": "You've no doubt seen the MIB series, but those were kind of good as well."}}, {{"role": "Recommender"}}]}}, {{"turn_2": [{{"text": "<context_extracted_because>Can you tell me what you like about MIB?</context_extracted_because>}}, {{"role": "Seeker"}}]}}]}}
  ]
}}
</slot_value_pair>
<prior_conversation>
{{'speaker': 'recommender',
'utterance': 'I loved seeing him in Guilty by Suspicion.',
'recommend': True,
'movies': ['Guilty by Suspicion (1991)']}},
{{'speaker': 'seeker',
'utterance': '\nthat is a deniro film that I actually have not seen yer',
'recommend': False}},
{{'speaker': 'recommender',
'utterance': 'Scorsese plays a part in it as well.\nI think you may like it.',
'recommend': False}},
<prior_conversation>
<latest_user_utterance>
what is it about
</latest_user_utterance>

#### Output
```json
{{"inquired-about": {{
  "explanation": "The user is clearly asking for more information about Guilty",
  "value": "Guilty by Suspicion",
  "context": [
    {{"speaker": "recommender", "utterance": "I loved seeing him in Guilty by Suspicion."}},
    {{"speaker": "seeker", "utterance": "\nthat is a deniro film that I actually have not seen yer"}},
    {{"speaker": "recommender", "utterance": "Scorsese plays a part in it as well.\nI think you may like it."}},
    {{"speaker": "seeker", "utterance": "what is it about"}}
  ]
}}
}}
```
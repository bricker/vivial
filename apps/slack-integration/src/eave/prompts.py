def build_prompt(formatted_conversation: str) -> str:
    instructions = (
        "Extract the most important information from this conversation. "
        "First create a 2 to 10 word title for the conversation, "
        "then extract a single category (for example: Technical, Product, Administrative, System Design, Marketing, Engineering, Design), "
        "then extract a list of 3 topics, "
        "then extract a list of 1 to 5 tags, each 1 or 2 words, "
        "then extract a 1-paragraph summary of the conversation, "
        "then extract the outcome of this conversation, "
        "then extract a list of action items (if any), "
        "then extract additional information that someone may want to look up in the future. "
        'Ignore messages that contain the text "EAVE:". '
        "Ignore short messages that only serve to get another person's attention "
        '(for example: "cc @Bryan", "@Lana FYI", and "@Leilenah ^" should be ignored). '
        "Exclude action items that only serve to notify someone about the conversation."
    )

    formatting = (
        "Desired format:\n"
        "Title: -||-\n"
        "Category: -||-\n"
        "Topics: <comma_separated_list_of_topics>\n"
        "Tags: <comma_separated_list_of_tags>\n"
        "Summary: -||-\n"
        "Outcome: -||-\n"
        "Action Items:\n"
        "1. <action_item_1>\n"
        "2. <action_item_2>\n"
        "n. <action_item_n>\n"
        "Additional information:\n"
        "<unstructured_additional_information>"
    )

    context = 'Conversation: """\n' f"{formatted_conversation}\n" '"""'

    return f"{instructions}\n\n" f"{formatting}\n\n" f"{context}\n\n"


## OLD: Decision prompt
# - Message from Alice: How much should we spend on advertising this month?
# - Message from Bob: Maybe somewhere around $100? @Charlie what do you think?
# - Message from Charlie: I think that's too much. Let's start with $50 bucks and go from there.
# - Message from Bob: :thumbsup:
# - Message from Alice: Sure. We actually have $25 in credits from Google Ads. Should we include that?
# - Message from Bob: Oh, nice.
# - Message from Charlie: Nice! Yes, go ahead.
# - Message from Alice: :thumbsup:

# The final decisions made in the above conversation are:
# 1. Spend $50 on advertising this month.
# 2. Include the $25 in credits from Google Ads, for a total of $75.

# The following is a conversation between colleagues:
# - Message from Alice: @Bob which font do you want me to use for the logo?
# - Message from Bob: Is Helvetica available?
# - Message from Charlie: No, we can't use that. Let's use Pattaya instead.
# - Message from Bob: Sure
# - Message from Bob: Actually, I'm not a huge fan. Maybe Roboto?
# - Message from Charlie: I don't really like Roboto, but we can use it for now and revisit later.
# - Message from Alice: Got it, thanks!

# The final decisions made in the above conversation are:
# 1. Use Roboto
# 2. Revisit this decision at a later time.

# The following is a conversation between colleagues:
# {}"

# The final decisions made in the above conversation are:

# def build_steps_prompt(formatted_conversation: str):
#     return f"""The following is a conversation between colleagues:
# - Message from Alice: Where can I find the Load Balancer configuration?
# - Message from Bob: @Alice login to the GCP console, then go to Network Services > Cloud Load Balancer
# - Message from Alice: Got it, thanks!
# - Message from Alice: @Bob I don't see it, do I need any specific permissions?
# - Message from Bob: Yes, one sec
# - Message from Bob: @Alice okay, check again. I added the "loadbalancer.viewer" role
# - Message from Alice: I see it now, thank you!

# The steps to accomplish the task in the above conversation are:
# 1. Login to GCP dev console
# 2. Navigate to Network Services
# 3. Navigate to Cloud Load Balancer

# The following is a conversation between colleagues:
# - Message from Alice: Bone-in, skin-on chicken breast were on sale, anybody know how to cook i
# - Message from Bob: @Alice Sear it skin-side-down in a hot pan with oil for a minute or two, flip it over, then throw the pan in the oven at 350 for about 15 minutes
# - Message from Bob: Add salt/pepper/oregano/whatever else you want. Hard to over-season.
# - Message from Alice: ooo, thank you! I'll try it out.
# - Message from Alice: Yo, that was DELICIOUS! So simple.

# The steps to accomplish the task in the above conversation are:
# 1. Add oil to the pan
# 2. Place the chicken breast skin-side down
# 3. Wait about 2 minutes, until the chicken skin is crispy
# 4. Flip the chicken over
# 5. Place the pan in a 350 degree oven for about 15 minutes
# 6. Add seasoning.

# The following is a conversation between colleagues:
# {formatted_conversation}

# The steps to accomplish the task in the above conversation are:
# """

# def build_summary_prompt(formatted_conversation: str):
#     return f"""The following is a conversation between colleagues:
# - Message from Alice: How much should we spend on advertising this month?
# - Message from Bob: Maybe somewhere around $100? @Charlie what do you think?
# - Message from Charlie: I think that's too much. Let's start with $50 bucks and go from there.
# - Message from Bob: :thumbsup:
# - Message from Alice: Sure. We actually have $25 in credits from Google Ads. Should we include that?
# - Message from Bob: Oh, nice.
# - Message from Charlie: Nice! Yes, go ahead.
# - Message from Alice: :thumbsup:

# The summary of the above conversation is:
# Alice, Bob, and Charlie discussed advertising spending for this month.

# The following is a conversation between colleagues:
# - Message from Alice: @Bob which font do you want me to use for the logo?
# - Message from Bob: Is Helvetica available?
# - Message from Charlie: No, we can't use that. Let's use Pattaya instead.
# - Message from Bob: Sure
# - Message from Bob: Actually, I'm not a huge fan. Maybe Roboto?
# - Message from Charlie: I don't really like Roboto, but we can use it for now and revisit later.
# - Message from Alice: Got it, thanks!

# The summary of the above conversation is:
# Alice, Bob, and Charlie discussed which font to use for the logo.

# The following is a conversation between colleagues:
# {formatted_conversation}

# The summary of the above conversation is:
# """

# def build_topic_prompt(formatted_conversation: str):
#     return f"""The following is a conversation between colleagues:
# - Message from Alice: How much should we spend on advertising this month?
# - Message from Bob: Maybe somewhere around $100? @Charlie what do you think?
# - Message from Charlie: I think that's too much. Let's start with $50 bucks and go from there.
# - Message from Bob: :thumbsup:
# - Message from Alice: Sure. We actually have $25 in credits from Google Ads. Should we include that?
# - Message from Bob: Oh, nice.
# - Message from Charlie: Nice! Yes, go ahead.
# - Message from Alice: :thumbsup:

# The topic of the above conversation is:
# Advertising Spending

# The following is a conversation between colleagues:
# - Message from Alice: @Bob which font do you want me to use for the logo?
# - Message from Bob: Is Helvetica available?
# - Message from Charlie: No, we can't use that. Let's use Pattaya instead.
# - Message from Bob: Sure
# - Message from Bob: Actually, I'm not a huge fan. Maybe Roboto?
# - Message from Charlie: I don't really like Roboto, but we can use it for now and revisit later.
# - Message from Alice: Got it, thanks!

# The topic of the above conversation is:
# Logo Font

# The following is a conversation between colleagues:
# {formatted_conversation}

# The topic of the above conversation is:
# """

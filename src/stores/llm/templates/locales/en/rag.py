# for prompt ( system , documents(chunks) , footer )
from string import Template
system_prompt=Template("\n".join([# to join list element in one string (i don't know why not use traditional string)
"You are an assistant to generate a response for the user.",
])) # using Template for substitution

document_prompt = Template("\n".join([
"## Document No: $doc_num",
"### Content: $chunck_text",
]
))

footer_prompt = Template("\n".join([
    "## query :",
    "$query",
    ""
    "## Answer:",
]))
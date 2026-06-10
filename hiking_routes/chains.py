import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_anthropic import ChatAnthropic

from hiking_routes.models import Router, HikingDatabaseQuery


prompt = ChatPromptTemplate.from_template(
    """
    User question: {question}    
    """
)

router_model = ChatAnthropic(
    model='claude-haiku-4-5',
    max_tokens=128,
    api_key=os.environ.get('ANTHROPIC_API_KEY')
).with_structured_output(Router)


query_model = ChatAnthropic(
    model='claude-haiku-4-5',
    max_tokens=128,
    api_key=os.environ.get('ANTHROPIC_API_KEY')
).with_structured_output(HikingDatabaseQuery)


def route(input_dict: dict):
    """
    input_dict assumes the keys routing, question
    """
    if input_dict['routing'].route == 'irrelevant':
        return 'Please ask a question relevant with finding a hiking route'
    if input_dict['routing'].route == 'more_information':
        return 'Give more information about what you want'
    if input_dict['routing'].route == 'query':
        return prompt | query_model


chain = (
    {'question': RunnablePassthrough()}
    | RunnablePassthrough.assign(routing = prompt | router_model)
    | RunnableLambda(route)
)

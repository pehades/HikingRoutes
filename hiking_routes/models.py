from typing import Literal, Optional

from pydantic import BaseModel, Field


class Router(BaseModel):

    route: Literal['irrelevant', 'more_information', 'query'] = Field(
        ..., description="""
        Given a user question choose which action to take
        - irrelevant: The user asked something that is not related to finding a hiking/walking route
        - more information: The user asked about a recommendation for hiking route but they did not provide much information. 
        Examples: 'Find me a route' [does not provide specific area], 'Where can I walk in Greece?' [lacks more specific area], 
        'Routes for Parnitha' [does not provide length of path]
        - query: The user question is enough to provide information for a handful of hiking routes. 
        Examples: 'Find me small paths near Parnassos', 'Day trails near Sparti' 
        """
    )


class HikingDatabaseQuery(BaseModel):

    trail_possible_areas: list[str] = Field(
        ...,
        description="""
        Given a user query, identify inside the name of the areas mentioned.
        """
    )

    trail_length_min: Optional[int] = Field(
        ...,
        description="""
        Optional. Minimum number of kilometers a hiking trail should be. Provide if user mentions phrases like
        long trail, all day hike etc. 
        """
    )

    trail_length_max: Optional[int] = Field(
        ...,
        description="""
        Optional. Minimum number of kilometers a hiking trail should be. Provide if user mentions phrases like
        small trail, quick route etc. 
        """
    )


class UserRequest(BaseModel):
    query: str
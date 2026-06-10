import uvicorn
from fastapi import FastAPI
from langchain_core.runnables import RunnableLambda

from hiking_routes.chains import chain
from hiking_routes.factories import Factory
from hiking_routes.models import UserRequest, HikingDatabaseQuery

app = FastAPI()

trail_finder = Factory.get_local_trail_finder()

full_chain = chain | RunnableLambda(
    lambda x: trail_finder.find_trail(x) if isinstance(x, HikingDatabaseQuery) else x
)


@app.post('/query', response_model=list[Trail])
def query(user_request: UserRequest):
    print('invoking chain')
    return {'answer': full_chain.invoke({'question': user_request.query})}


if __name__ == '__main__':
    uvicorn.run(app, port=5000)

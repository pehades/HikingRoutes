import uvicorn
from fastapi import FastAPI

from hiking_routes.chains import chain
from hiking_routes.models import UserRequest

app = FastAPI()


@app.post('/query')
def query(user_request: UserRequest):
    print('invoking chain')
    return {
        'answer': chain.invoke({'question': user_request.query})
    }


if __name__ == '__main__':
    uvicorn.run(app, port=5000)

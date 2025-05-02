# FastAPI Hello World

This is a simple FastAPI web application that displays "Hello World" on the home page.

## Project Structure

```
fastapi-hello-world
├── app
│   ├── main.py
│   └── __init__.py
├── requirements.txt
└── README.md
```

## Requirements

To run this application, you need to have Python installed along with the following dependencies:

- FastAPI
- Uvicorn

You can install the required packages using pip:

```
pip install -r requirements.txt
```

## Running the Application

To start the FastAPI application, run the following command:

```
uvicorn app.main:app --reload
```

After the server starts, you can access the application at `http://127.0.0.1:8000`. You should see "Hello World" displayed on the home page.

## License

This project is licensed under the MIT License.
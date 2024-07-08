cd hatespeech
python -m gunicorn hatespeech.asgi:application -k uvicorn.workers.UvicornWorker
cd ..
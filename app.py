"""Lightweight compatibility wrapper. The real app is in the `h3ru` package."""

from h3ru import app  # type: ignore

if __name__ == '__main__':
    import uvicorn, os
    cert = os.environ.get('SSL_CERTFILE')
    key = os.environ.get('SSL_KEYFILE')
    uvicorn.run('h3ru:app', host='0.0.0.0', port=int(os.environ.get('PORT', 8001)), ssl_certfile=cert, ssl_keyfile=key)

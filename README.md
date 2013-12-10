Usage
-----

$ python measure.py

You need to have [http2 compression test](https://github.com/http2/compression-test) in your python path.

This script measures the size of HEADERS SPDY frame containing WebSocket frame headers.
Notice this script measures the size of HEADERS frame (including SPDY header).
To encode a WebSocket frame, you need additional 8 bytes for each SPDY DATA frame containing the data of the WebSocket frame.


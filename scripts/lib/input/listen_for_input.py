from http.server import HTTPServer, BaseHTTPRequestHandler

class _RequestHandler(BaseHTTPRequestHandler):
    """
    HTTPリクエストを処理するクラス
    """
    data_handler = None

    def do_POST(self):
        """
        テキスト入力を受け取るメソッド
        """
        # リクエストボディの読み取り
        content_length = int(self.headers["Content-Length"])
        user_input = self.rfile.read(content_length).decode("utf-8")

        # データハンドラに渡す
        response_message = _RequestHandler.data_handler(user_input)

        # ステータスコードとヘッダーの送信
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()

        # レスポンスボディの送信（必要に応じて）
        self.wfile.write(response_message.encode("utf-8"))

        
def listen_for_input(listening_ip, listening_port, data_handler):
    """
    テキスト入力を受け取るための HTTP サーバを起動する
    @param listening_ip IP address to listen on
    @param listening_port Port to listen on
    @param data_handler
    """

    if not listening_ip or not listening_port:
        """
        IP アドレスまたはポート番号が指定されていない場合はエラーを出力
        """
        raise ValueError("listening_ip または listening_port が指定されていません")

    if not data_handler:
        """
        データハンドラが指定されていない場合はエラーを出力
        """
        raise ValueError("data_handler が指定されていません")

    _RequestHandler.data_handler = data_handler

    # HTTP サーバを起動
    httpd = HTTPServer(server_address=(listening_ip, listening_port), RequestHandlerClass=_RequestHandler)
    httpd.serve_forever()

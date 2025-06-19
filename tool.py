import requests
from datetime import datetime
from typing import Dict, Any

# Difyのツール基盤クラスをインポート
from core.tools.tool.tool import Tool, ToolInvokeMessage
from core.tools.tool.tool_manager import ToolManager

# ツールで使うライブラリをここに列挙する
# Difyはこれを見て、必要なライブラリを自動でインストールしてくれる
ToolManager.register_tool_importer(
    'youtube_tool',
    {
        'requests': '2.31.0' # バージョン指定を推奨
    }
)

class YouTubeTool(Tool):
    # APIキーを受け取るための設定
    _provider_name = 'youtube'
    _provider_credentials: Dict[str, Any]
    
    # ツールが呼び出されたときに実行されるメインの処理
    def _invoke(self, user_id: str, tool_parameters: Dict[str, Any]) -> ToolInvokeMessage:
        """
        user_id: ユーザーID
        tool_parameters: __init__.pyで定義したinputsがここに入ってくる
        """
        # 1. パラメータとAPIキーを取得
        channel_id = tool_parameters.get('channelId', '')
        start_date_str = tool_parameters.get('startDate', '')
        end_date_str = tool_parameters.get('endDate', '')
        
        # Difyに保存されたAPIキーを取得
        youtube_api_key = self._provider_credentials.get('api_key')

        if not all([channel_id, start_date_str, end_date_str, youtube_api_key]):
            return self.create_text_message("エラー: 必要なパラメータまたはAPIキーが不足しています。")

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return self.create_text_message("エラー: 日付の形式が正しくありません。YYYY-MM-DDで入力してください。")

        # --- ここからYouTube Data APIとの連携ロジック ---
        YOUTUBE_API_BASE_URL = 'https://www.googleapis.com/youtube/v3'
        
        # 2. チャンネルIDからアップロード動画の再生リストIDを取得
        search_url = f"{YOUTUBE_API_BASE_URL}/channels"
        search_params = {'part': 'contentDetails', 'id': channel_id, 'key': youtube_api_key}
        search_response = requests.get(search_url, params=search_params).json()
        
        if 'items' not in search_response or not search_response['items']:
            return self.create_text_message(f"エラー: チャンネルが見つかりません (ID: {channel_id})")
            
        playlist_id = search_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # 3. 再生リストIDから動画一覧を取得
        video_list_url = f"{YOUTUBE_API_BASE_URL}/playlistItems"
        video_params = {'part': 'snippet,contentDetails', 'playlistId': playlist_id, 'maxResults': 50, 'key': youtube_api_key}
        video_list_response = requests.get(video_list_url, params=video_params).json()

        video_ids = [item['contentDetails']['videoId'] for item in video_list_response.get('items', [])]
        
        # 4. 動画IDリストから各動画の詳細情報を取得
        video_details_url = f"{YOUTUBE_API_BASE_URL}/videos"
        details_params = {'part': 'snippet,statistics', 'id': ','.join(video_ids), 'key': youtube_api_key}
        details_response = requests.get(video_details_url, params=details_params).json()

        # 5. 期間でフィルタリングして結果を整形
        results = []
        for video in details_response.get('items', []):
            published_at = datetime.fromisoformat(video['snippet']['publishedAt'].replace('Z', ''))
            
            if start_date <= published_at <= end_date:
                stats = video.get('statistics', {})
                results.append({
                    "title": video['snippet']['title'],
                    "publishedAt": video['snippet']['publishedAt'],
                    "viewCount": int(stats.get('viewCount', 0)),
                    "likeCount": int(stats.get('likeCount', 0)),
                    "commentCount": int(stats.get('commentCount', 0)),
                })
        
        # DifyにJSON形式で結果を返す
        return self.create_json_message(results)
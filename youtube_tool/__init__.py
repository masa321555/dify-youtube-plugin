from .tool import YouTubeTool
from .icon_data import ICON_DATA  # 別ファイルからアイコンデータを読み込む

# この中にツールの情報をすべて記述する
tool_config = {
    # ユーザーが見るツールの名前
    "name": "youtube_channel_analyzer",
    # ツールを何に使うか、AIへの説明
    "description": "ユーザーが指定したYouTubeチャンネルID(channelId)、取得開始日(startDate)、取得終了日(endDate)を基に、期間内に公開された動画の情報を取得します。",
    # 人間が見るツールの名前
    "user_description": "YouTubeチャンネル動画分析",
    # アイコン情報
    "icon": ICON_DATA,
    "icon_background": "#FF0000",
    # ツールが受け取るパラメータ（入力）の定義
    "inputs": [
        {
            "name": "channelId",
            "type": "string",
            "label": "チャンネルID",
            "required": True,
            "description": "分析したいYouTubeチャンネルのID (例: UCD-miitqNY3nyukJ4Fnf4_A)"
        },
        {
            "name": "startDate",
            "type": "string",
            "label": "取得開始日",
            "required": True,
            "description": "取得開始日 (YYYY-MM-DD形式)"
        },
        {
            "name": "endDate",
            "type": "string",
            "label": "取得終了日",
            "required": True,
            "description": "取得終了日 (YYYY-MM-DD形式)"
        }
    ],
    # ツールが返すデータ（出力）の定義
    "outputs": [
        {
            "name": "videos",
            "type": "json",
            "label": "動画リスト"
        }
    ],
    # ユーザーにAPIキーを入力させるための設定
    "credentials_for_provider": {
        "youtube": {
            "label": "YouTube Data API Key",
            "type": "secret-input",
            "required": True,
            "config_keys": ["api_key"]
        }
    },
    # ツール本体のクラスを指定
    "tool_class": YouTubeTool
}

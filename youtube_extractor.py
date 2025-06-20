import json
import requests
from datetime import datetime
from typing import Any, Dict, List
from dify_plugin import Tool


class YouTubeExtractorTool(Tool):
    """YouTube Data APIを使用してチャンネルの動画情報を取得するツール"""
    
    def _invoke(self, user_id: str, tool_parameters: Dict[str, Any]) -> str:
        """
        ツールのメイン実行メソッド
        
        Args:
            user_id: ユーザーID
            tool_parameters: ツールパラメータ
                - channel_id: YouTubeチャンネルID
                - start_date: 取得開始日 (YYYY-MM-DD)
                - end_date: 取得終了日 (YYYY-MM-DD)
                
        Returns:
            str: JSON形式の動画情報リスト
        """
        try:
            # パラメータの取得と検証
            channel_id = tool_parameters.get('channel_id', '').strip()
            start_date = tool_parameters.get('start_date', '').strip()
            end_date = tool_parameters.get('end_date', '').strip()
            
            # YouTube API Keyの取得
            api_key = self.runtime.credentials.get('youtube_api_key')
            if not api_key:
                return json.dumps({
                    "error": "YouTube Data API キーが設定されていません。プラグイン設定でAPIキーを入力してください。"
                }, ensure_ascii=False, indent=2)
            
            # 入力値の検証
            validation_error = self._validate_inputs(channel_id, start_date, end_date)
            if validation_error:
                return json.dumps({"error": validation_error}, ensure_ascii=False, indent=2)
            
            # 日付の変換
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            
            # YouTube Data API v3のベースURL
            base_url = "https://www.googleapis.com/youtube/v3"
            
            # 1. チャンネル情報の取得
            channel_info = self._get_channel_info(base_url, api_key, channel_id)
            if 'error' in channel_info:
                return json.dumps(channel_info, ensure_ascii=False, indent=2)
            
            # 2. チャンネルの動画リストを取得
            videos = self._get_channel_videos(base_url, api_key, channel_id, start_datetime, end_datetime)
            if 'error' in videos:
                return json.dumps(videos, ensure_ascii=False, indent=2)
            
            # 3. 各動画の詳細統計情報を取得
            detailed_videos = self._get_video_statistics(base_url, api_key, videos)
            
            # 4. 結果をフォーマット
            result = {
                "channel_info": channel_info,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "total_videos": len(detailed_videos),
                "videos": detailed_videos
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": f"予期しないエラーが発生しました: {str(e)}"
            }, ensure_ascii=False, indent=2)
    
    def _validate_inputs(self, channel_id: str, start_date: str, end_date: str) -> str:
        """入力値の検証"""
        if not channel_id:
            return "チャンネルIDが入力されていません。"
        
        if not start_date or not end_date:
            return "開始日と終了日の両方を入力してください。"
        
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_dt > end_dt:
                return "開始日は終了日より前の日付である必要があります。"
                
        except ValueError:
            return "日付はYYYY-MM-DD形式で入力してください。"
        
        return None
    
    def _get_channel_info(self, base_url: str, api_key: str, channel_id: str) -> Dict[str, Any]:
        """チャンネル基本情報の取得"""
        try:
            url = f"{base_url}/channels"
            params = {
                'part': 'snippet,statistics',
                'id': channel_id,
                'key': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('items'):
                return {"error": f"チャンネルID '{channel_id}' が見つかりません。正しいチャンネルIDを入力してください。"}
            
            channel = data['items'][0]
            snippet = channel['snippet']
            statistics = channel['statistics']
            
            return {
                "channel_id": channel_id,
                "title": snippet.get('title', ''),
                "description": snippet.get('description', '')[:200] + '...' if len(snippet.get('description', '')) > 200 else snippet.get('description', ''),
                "published_at": snippet.get('publishedAt', ''),
                "subscriber_count": statistics.get('subscriberCount', 'N/A'),
                "video_count": statistics.get('videoCount', 'N/A'),
                "view_count": statistics.get('viewCount', 'N/A')
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"チャンネル情報の取得に失敗しました: {str(e)}"}
    
    def _get_channel_videos(self, base_url: str, api_key: str, channel_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """指定期間のチャンネル動画リストを取得"""
        try:
            all_videos = []
            next_page_token = None
            
            # RFC 3339形式に変換
            published_after = start_date.isoformat() + 'Z'
            published_before = end_date.replace(hour=23, minute=59, second=59).isoformat() + 'Z'
            
            while True:
                url = f"{base_url}/search"
                params = {
                    'part': 'snippet',
                    'channelId': channel_id,
                    'type': 'video',
                    'order': 'date',
                    'publishedAfter': published_after,
                    'publishedBefore': published_before,
                    'maxResults': 50,
                    'key': api_key
                }
                
                if next_page_token:
                    params['pageToken'] = next_page_token
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                for item in data.get('items', []):
                    video_info = {
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'][:100] + '...' if len(item['snippet']['description']) > 100 else item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt'],
                        'thumbnail_url': item['snippet']['thumbnails'].get('medium', {}).get('url', '')
                    }
                    all_videos.append(video_info)
                
                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break
                
                # API制限を考慮して最大200件まで
                if len(all_videos) >= 200:
                    break
            
            return all_videos
            
        except requests.exceptions.RequestException as e:
            return {"error": f"動画リストの取得に失敗しました: {str(e)}"}
    
    def _get_video_statistics(self, base_url: str, api_key: str, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """動画の統計情報を取得"""
        if 'error' in videos:
            return videos
        
        try:
            detailed_videos = []
            
            # 動画IDを50件ずつのバッチで処理（YouTube API制限）
            for i in range(0, len(videos), 50):
                batch_videos = videos[i:i+50]
                video_ids = [video['video_id'] for video in batch_videos]
                
                url = f"{base_url}/videos"
                params = {
                    'part': 'statistics',
                    'id': ','.join(video_ids),
                    'key': api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                # 統計情報をマッピング
                stats_dict = {}
                for item in data.get('items', []):
                    video_id = item['id']
                    statistics = item['statistics']
                    stats_dict[video_id] = {
                        'view_count': int(statistics.get('viewCount', 0)),
                        'like_count': int(statistics.get('likeCount', 0)),
                        'comment_count': int(statistics.get('commentCount', 0))
                    }
                
                # 元の動画情報と統計情報を結合
                for video in batch_videos:
                    video_id = video['video_id']
                    stats = stats_dict.get(video_id, {
                        'view_count': 0,
                        'like_count': 0,
                        'comment_count': 0
                    })
                    
                    # 日付をフォーマット
                    published_date = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
                    
                    detailed_video = {
                        'video_id': video_id,
                        'title': video['title'],
                        'description': video['description'],
                        'published_date': published_date,
                        'published_datetime': video['published_at'],
                        'view_count': stats['view_count'],
                        'like_count': stats['like_count'],
                        'comment_count': stats['comment_count'],
                        'thumbnail_url': video['thumbnail_url'],
                        'video_url': f"https://www.youtube.com/watch?v={video_id}"
                    }
                    detailed_videos.append(detailed_video)
            
            # 公開日時でソート（新しい順）
            detailed_videos.sort(key=lambda x: x['published_datetime'], reverse=True)
            
            return detailed_videos
            
        except requests.exceptions.RequestException as e:
            return {"error": f"動画統計情報の取得に失敗しました: {str(e)}"}
        except Exception as e:
            return {"error": f"統計情報処理中にエラーが発生しました: {str(e)}"}
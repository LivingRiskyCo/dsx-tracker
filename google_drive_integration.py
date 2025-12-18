"""
Google Drive integration for video access
"""

import streamlit as st
import gdown
import os
from typing import Optional, List, Dict
import tempfile
from pathlib import Path
import re

class GoogleDriveAccess:
    def __init__(self):
        # Use Streamlit Cloud persistent storage if available
        import os
        if os.path.exists("/mount/src"):
            # Streamlit Cloud - use persistent storage
            self.temp_dir = Path("/mount/src/data/videos")
        else:
            # Local development
            self.temp_dir = Path(tempfile.gettempdir()) / "dsx_videos"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_file_id(self, drive_url: str) -> Optional[str]:
        """
        Extract file ID from Google Drive URL
        
        Supports formats:
        - https://drive.google.com/file/d/FILE_ID/view
        - https://drive.google.com/open?id=FILE_ID
        - https://drive.google.com/uc?id=FILE_ID
        - FILE_ID (direct)
        """
        # Direct file ID
        if len(drive_url) == 33 and drive_url.isalnum():
            return drive_url
        
        # Extract from URL patterns
        patterns = [
            r'/file/d/([a-zA-Z0-9_-]+)',
            r'[?&]id=([a-zA-Z0-9_-]+)',
            r'/open\?id=([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, drive_url)
            if match:
                return match.group(1)
        
        return None
    
    def get_video_url(self, file_id: str, direct: bool = False) -> str:
        """
        Get video URL from Google Drive file ID
        
        Args:
            file_id: Google Drive file ID
            direct: If True, use direct download URL (requires public access)
        
        Returns:
            URL for video access
        """
        if direct:
            # Try multiple URL formats for better compatibility
            # Format 1: Direct download (works if file is publicly shared)
            url1 = f"https://drive.google.com/uc?export=download&id={file_id}"
            # Format 2: Alternative direct download
            url2 = f"https://drive.google.com/uc?id={file_id}"
            # Return the first one (we'll try both in the calling code)
            return url1
        else:
            # Preview/embed URL (better for streaming, but may not work in Streamlit)
            return f"https://drive.google.com/file/d/{file_id}/preview"
    
    def get_streamable_video_url(self, file_id: str) -> str:
        """
        Get a video URL that works with Streamlit's video player
        Uses gdown to create a temporary direct link
        """
        # For Streamlit, we need a direct MP4 URL
        # Google Drive direct download URL (requires public sharing)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    
    def download_video(self, file_id: str, output_path: Optional[str] = None) -> str:
        """
        Download video from Google Drive
        
        Args:
            file_id: Google Drive file ID
            output_path: Optional output path (defaults to temp directory)
        
        Returns:
            Path to downloaded video file
        """
        if output_path is None:
            output_path = self.temp_dir / f"{file_id}.mp4"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use gdown to download
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, str(output_path), quiet=False)
        
        return str(output_path)
    
    def list_videos_in_folder(self, folder_id: str) -> List[Dict]:
        """
        List videos in a Google Drive folder
        
        Note: This requires Google Drive API. For now, we'll use a simpler approach
        where users provide file IDs directly.
        """
        # TODO: Implement Google Drive API integration if needed
        # For now, return empty list - users will provide file IDs directly
        return []
    
    def get_video_info(self, file_id: str) -> Dict:
        """Get video information (placeholder for future API integration)"""
        return {
            'file_id': file_id,
            'url': self.get_video_url(file_id),
            'direct_url': self.get_video_url(file_id, direct=True)
        }
    
    def extract_frame(self, file_id: str, frame_num: int, fps: float = 30.0) -> Optional[bytes]:
        """
        Extract a specific frame from video
        
        Args:
            file_id: Google Drive file ID
            frame_num: Frame number to extract
            fps: Frames per second (default 30)
        
        Returns:
            Frame image as bytes (JPEG), or None if extraction fails
        """
        try:
            import cv2
            import numpy as np
            from io import BytesIO
            import tempfile
            
            # Download video if not already cached
            video_path = self.temp_dir / f"{file_id}.mp4"
            if not video_path.exists():
                self.download_video(file_id, str(video_path))
            
            # Open video
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                return None
            
            # Calculate timestamp from frame number
            timestamp = frame_num / fps
            
            # Seek to frame
            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
            
            # Read frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                return None
            
            # Convert to JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            return buffer.tobytes()
            
        except Exception as e:
            print(f"Error extracting frame: {e}")
            return None


import json
import os


class ContentManager:
    """Load and manage external content files."""

    def __init__(self, content_dir='CCJ/Content'):
        self.content_dir = content_dir
        self.content = {}
        self.load_all()

    def load_all(self):
        """Load all content files."""
        files = ['content.json']
        for file in files:
            path = os.path.join(self.content_dir, file)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.content.update(json.load(f))

    def get(self, key, default=''):
        """Get content by dot notation key."""
        keys = key.split('.')
        value = self.content
        for k in keys:
            value = value.get(k, default)
            if value == default:
                return default
        return value

    def reload(self):
        """Reload content (useful during development)."""
        self.content = {}
        self.load_all()